#!/usr/bin/env python3
"""compare_models.py — identical behavioural read across two models, side by side.

Runs the exact same measurement used in fable5_audit.py (turn segmentation,
tool sequencing, read-before-edit / test-after-edit ratios, transitions) for any
two models and prints a side-by-side comparison plus the deltas. Also dumps the
raw metric dicts to model_compare.json for the playbook step.
"""

from __future__ import annotations

import glob
import json
import os
import re
import statistics
from collections import Counter

PROJECTS = os.path.expanduser("~/.claude/projects")
OUT_JSON = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_compare.json")

EDIT_TOOLS = {"Edit", "MultiEdit", "NotebookEdit"}
WRITE_TOOLS = {"Write"}
READ_TOOLS = {"Read"}
TEST_RE = re.compile(
    r"\b(pytest|py\.test|python\s+-m\s+(unittest|pytest)|unittest|jest|vitest|mocha|"
    r"jasmine|cargo\s+(test|nextest)|go\s+test|rspec|phpunit|dotnet\s+test|"
    r"\./gradlew\s+\S*test|gradle\s+\S*test|mvn\s+\S*test|ctest|rails\s+test|"
    r"rake\s+test|npm\s+(run\s+)?test|npm\s+t\b|pnpm\s+(run\s+)?test|yarn\s+test|"
    r"bun\s+test|tox|nose2)\b",
    re.IGNORECASE,
)


def is_real_user_prompt(rec):
    if rec.get("type") != "user" or rec.get("isMeta"):
        return False
    msg = rec.get("message")
    if not isinstance(msg, dict) or msg.get("role") != "user":
        return False
    c = msg.get("content")
    if isinstance(c, str):
        return bool(c.strip())
    if isinstance(c, list):
        return any(isinstance(b, dict) and b.get("type") == "text" and (b.get("text") or "").strip() for b in c)
    return False


def tool_field(name, ti):
    if not isinstance(ti, dict):
        return None, None
    path = ti.get("file_path") or ti.get("notebook_path") or ti.get("path")
    return path, (ti.get("command") if name == "Bash" else None)


def assistant_tools(msg):
    tools = []
    c = msg.get("content")
    if not isinstance(c, list):
        return tools
    for b in c:
        if isinstance(b, dict) and b.get("type") == "tool_use":
            name = b.get("name", "tool")
            p, cmd = tool_field(name, b.get("input"))
            tools.append((name, p, cmd))
    return tools


def segment_turns(path, model):
    turns, cur = [], None

    def close():
        if cur and cur["nf"] > 0:
            turns.append(cur)

    with open(path, encoding="utf-8") as f:
        for raw in f:
            raw = raw.strip()
            if not raw:
                continue
            try:
                rec = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if is_real_user_prompt(rec):
                close()
                cur = {"prompt": True, "n": 0, "nf": 0, "seq": [], "ids": {}}
                continue
            if rec.get("type") == "assistant":
                msg = rec.get("message")
                if not isinstance(msg, dict):
                    continue
                if cur is None:
                    cur = {"prompt": False, "n": 0, "nf": 0, "seq": [], "ids": {}}
                cur["n"] += 1
                if msg.get("model") == model:
                    cur["nf"] += 1
                    tools = assistant_tools(msg)
                    cur["seq"].extend(tools)
                    mid = msg.get("id") or f"noid-{cur['n']}"
                    cur["ids"][mid] = cur["ids"].get(mid, 0) + len(tools)
        close()
    return turns


def audit(model):
    files = glob.glob(os.path.join(PROJECTS, "**", "*.jsonl"), recursive=True)
    m = {
        "model": model, "files": 0, "projects": set(),
        "logical": 0, "records": 0, "turns": 0, "turns_main": 0, "turns_sub": 0,
        "prompts_main": 0, "tools_total": 0, "tool_freq": Counter(),
        "tpt": [], "permsg": [], "bigrams": Counter(), "first": Counter(), "last": Counter(),
        "edits_total": 0, "edits_after_read": 0, "writes_total": 0, "writes_after_read": 0,
        "turns_with_edit": 0, "turns_edit_then_test": 0, "edit_ops": 0, "edit_then_test_ops": 0,
        "buckets": Counter(),
    }
    for path in files:
        try:
            data = open(path, encoding="utf-8").read()
        except Exception:
            continue
        if model not in data:
            continue
        is_sub = "/subagents/" in path or "/workflows/" in path
        project = os.path.relpath(path, PROJECTS).split(os.sep)[0]
        turns = segment_turns(path, model)
        if not turns:
            continue
        m["files"] += 1
        m["projects"].add(project)
        seen_read = set()
        for t in turns:
            m["turns"] += 1
            m["turns_sub" if is_sub else "turns_main"] += 1
            if t["prompt"] and not is_sub:
                m["prompts_main"] += 1
            m["logical"] += len(t["ids"])
            m["records"] += t["nf"]
            m["permsg"].extend(t["ids"].values())
            seq = t["seq"]
            names = [s[0] for s in seq]
            m["tpt"].append(len(seq))
            n = len(seq)
            m["buckets"]["0" if n == 0 else "1-2" if n <= 2 else "3-5" if n <= 5 else "6-10" if n <= 10 else "11+"] += 1
            for nm in names:
                m["tool_freq"][nm] += 1
            if names:
                m["first"][names[0]] += 1
                m["last"][names[-1]] += 1
            for a, b in zip(names, names[1:]):
                m["bigrams"][(a, b)] += 1
            edit_idxs = []
            for idx, (nm, p, _c) in enumerate(seq):
                if nm in READ_TOOLS and p:
                    seen_read.add(p)
                elif nm in WRITE_TOOLS:
                    m["writes_total"] += 1
                    if p and p in seen_read:
                        m["writes_after_read"] += 1
                    if p:
                        seen_read.add(p)
                    edit_idxs.append(idx)
                elif nm in EDIT_TOOLS:
                    m["edits_total"] += 1
                    if p and p in seen_read:
                        m["edits_after_read"] += 1
                    if p:
                        seen_read.add(p)
                    edit_idxs.append(idx)
            if edit_idxs:
                m["edit_ops"] += len(edit_idxs)
                m["turns_with_edit"] += 1
                last_edit = max(edit_idxs)
                test_idxs = [i for i, (nm, _p, cmd) in enumerate(seq) if nm == "Bash" and cmd and TEST_RE.search(cmd)]
                if any(i > last_edit for i in test_idxs):
                    m["turns_edit_then_test"] += 1
                for ei in edit_idxs:
                    if any(ti > ei for ti in test_idxs):
                        m["edit_then_test_ops"] += 1
    m["tools_total"] = sum(m["tool_freq"].values())
    m["projects"] = len(m["projects"])
    return m


def pct(a, b):
    return (100.0 * a / b) if b else 0.0


def summarize(m):
    tpt = m["tpt"]
    tu = [x for x in tpt if x > 0]
    permsg = m["permsg"]
    tool_msgs = sum(1 for c in permsg if c > 0)
    parallel = sum(1 for c in permsg if c > 1)
    total = m["tools_total"]
    s = {
        "model": m["model"], "files": m["files"], "projects": m["projects"],
        "logical_msgs": m["logical"], "turns": m["turns"],
        "turns_main": m["turns_main"], "turns_sub": m["turns_sub"], "prompts_main": m["prompts_main"],
        "msgs_per_prompt": m["logical"] / m["prompts_main"] if m["prompts_main"] else 0,
        "tools_total": total,
        "tpt_mean": statistics.mean(tpt) if tpt else 0,
        "tpt_median": statistics.median(tpt) if tpt else 0,
        "tpt_max": max(tpt) if tpt else 0,
        "tu_mean": statistics.mean(tu) if tu else 0,
        "tu_median": statistics.median(tu) if tu else 0,
        "parallel_pct": pct(parallel, tool_msgs),
        "pct_turns_11plus": pct(m["buckets"]["11+"], m["turns"]),
        "pct_turns_textonly": pct(m["buckets"]["0"], m["turns"]),
        "read_before_edit_pct": pct(m["edits_after_read"], m["edits_total"]),
        "edits_total": m["edits_total"],
        "test_after_edit_turn_pct": pct(m["turns_edit_then_test"], m["turns_with_edit"]),
        "turns_with_edit": m["turns_with_edit"],
        "edit_then_test_ops_pct": pct(m["edit_then_test_ops"], m["edit_ops"]),
        "tool_shares": {k: pct(v, total) for k, v in m["tool_freq"].most_common(10)},
        "bigrams": {f"{a}->{b}": pct(c, sum(m["bigrams"].values())) for (a, b), c in m["bigrams"].most_common(10)},
        "first": dict(m["first"].most_common(4)),
        "last": dict(m["last"].most_common(4)),
    }
    return s


def row(label, a, b, fmt="{:.1f}"):
    fa = fmt.format(a) if isinstance(a, float) else str(a)
    fb = fmt.format(b) if isinstance(b, float) else str(b)
    print(f"  {label:<32} {fa:>14} {fb:>14}")


def main():
    models = ["claude-fable-5", "claude-opus-4-8"]
    summaries = {}
    raw = {}
    for mdl in models:
        print(f"scanning {mdl} ...", flush=True)
        a = audit(mdl)
        summaries[mdl] = summarize(a)
        raw[mdl] = {"tool_shares": summaries[mdl]["tool_shares"], "bigrams": summaries[mdl]["bigrams"]}
    f, o = summaries["claude-fable-5"], summaries["claude-opus-4-8"]

    print("\n" + "=" * 64)
    print(f"  {'METRIC':<32} {'FABLE-5':>14} {'OPUS-4-8':>14}")
    print("=" * 64)
    print("\n CORPUS")
    row("files", f["files"], o["files"])
    row("projects", f["projects"], o["projects"])
    row("logical assistant msgs", f["logical_msgs"], o["logical_msgs"])
    row("turns (main / subagent)", f"{f['turns_main']}/{f['turns_sub']}", f"{o['turns_main']}/{o['turns_sub']}")
    row("human prompts (main)", f["prompts_main"], o["prompts_main"])
    row("msgs per human prompt", f["msgs_per_prompt"], o["msgs_per_prompt"], "{:.1f}")

    print("\n CADENCE / RHYTHM")
    row("total tool calls", f["tools_total"], o["tools_total"])
    row("tool calls/turn (mean)", f["tpt_mean"], o["tpt_mean"], "{:.2f}")
    row("tool calls/turn (median)", f["tpt_median"], o["tpt_median"], "{:.0f}")
    row("tool calls/turn (max)", f["tpt_max"], o["tpt_max"])
    row("% turns with 11+ calls", f["pct_turns_11plus"], o["pct_turns_11plus"], "{:.1f}%")
    row("% turns text-only", f["pct_turns_textonly"], o["pct_turns_textonly"], "{:.1f}%")
    row("% tool-msgs parallel", f["parallel_pct"], o["parallel_pct"], "{:.1f}%")

    print("\n RATIOS (order discipline)")
    row("read-before-edit", f["read_before_edit_pct"], o["read_before_edit_pct"], "{:.1f}%")
    row("  (edit ops measured)", f["edits_total"], o["edits_total"])
    row("test-after-edit (turn)", f["test_after_edit_turn_pct"], o["test_after_edit_turn_pct"], "{:.1f}%")
    row("  (editing turns)", f["turns_with_edit"], o["turns_with_edit"])
    row("edits w/ later in-turn test", f["edit_then_test_ops_pct"], o["edit_then_test_ops_pct"], "{:.1f}%")

    print("\n TOOL MIX (% of all tool calls)")
    keys = list(dict.fromkeys(list(f["tool_shares"]) + list(o["tool_shares"])))
    for k in keys[:12]:
        row(k, f["tool_shares"].get(k, 0.0), o["tool_shares"].get(k, 0.0), "{:.1f}%")

    print("\n ACTION SEQUENCES (top transitions, % of all)")
    keys = list(dict.fromkeys(list(f["bigrams"]) + list(o["bigrams"])))
    for k in keys[:12]:
        row(k, f["bigrams"].get(k, 0.0), o["bigrams"].get(k, 0.0), "{:.1f}%")

    print("\n TURN SHAPE")
    print(f"  fable starts: {f['first']}  ends: {f['last']}")
    print(f"  opus  starts: {o['first']}  ends: {o['last']}")

    json.dump(summaries, open(OUT_JSON, "w"), indent=2)
    print(f"\nmetrics dumped to {OUT_JSON}")


if __name__ == "__main__":
    main()
