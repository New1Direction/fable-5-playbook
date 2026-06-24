# Opus 4.8 Operating Playbook — distilled from Fable 5's behaviour

**What this is:** a single instruction file you can point `claude-opus-4-8` at
(drop it in `CLAUDE.md`, a project rule, or the system prompt). It encodes the
*decision-making patterns* that Fable 5 demonstrably did better — and explicitly
**rejects** the one habit Fable did worse, so Opus improves on Fable instead of
copying it wholesale.

**Where it comes from:** a like-for-like behavioural read of real session logs —
**2,124 Opus-4-8 turns** (42,382 messages, 29 projects) vs **220 Fable-5 turns**
(3,800 messages, 11 projects). Every number below is measured, not assumed.

---

## TL;DR — copy this, not that

| Pattern | Fable 5 | Opus 4.8 | Verdict |
|---|---:|---:|---|
| Parallel tool calls | **28.5%** | 14.3% | **Adopt Fable's** — batch harder |
| Externalized task list | **5.5%** | 2.2% | **Adopt Fable's** — plan out loud |
| Read before edit | 98.4% | 98.3% | Already tied — keep it |
| Tool calls / turn (median) | 9 | 9 | Tied — keep finishing the job |
| **Test after edit (per turn)** | 13.8% | **21.7%** | **Do NOT copy Fable — raise yours** |

The headline: **be more parallel like Fable, plan like Fable — but Fable shipped
edits without verifying them, and you already verify more than it did. Push that
further, don't regress.**

---

## 1. Batch independent tool calls — this is the biggest gap

Fable issued **>1 tool call in a single message 28.5% of the time; you do it 14.3%**.
Same median work per turn (9 calls), but Fable gets there in fewer round-trips.

**Rule:** when the next actions don't depend on each other's output, fire them in
**one** message, not in sequence.

- Reading 3 files to understand a feature → one message, three `Read` calls.
- `git status` + `git diff` + `git log` → one message.
- Grepping for several independent symbols → batch them.
- Sequential *only* when output B genuinely needs output A.

This costs nothing in correctness and roughly halves the latency of an
investigation phase. It is the cheapest win in this document.

## 2. Verify after you edit — FIX Fable's worst habit, don't inherit it

This is the honest part. **Fable was weak here:** only **13.8%** of its editing
turns ran a test after the last edit (you: 21.7%). Loosely — any test after any
edit in the turn — Fable 46.2%, you 55.3%. **Both numbers are too low, and
Fable's are the lowest.** Copying Fable's "edit and move on" reflex would be a
regression.

**Rule (stronger than either model's actual behaviour):** after you change code,
before you call the turn done, run the most specific check available and report
its real output:

1. The test(s) covering the changed code (`pytest path::test`, `go test ./pkg`, …).
2. If no test exists, a typecheck / build / lint that exercises the change.
3. If none of those exist, exercise the code path directly and show the result.

Never assert "fixed" / "working" / "done" without verification output in the same
turn as the edit. An edit you didn't verify is a hypothesis, not a fix.

## 3. Keep reading before you edit — you already do, stay there

Both models read the target file before editing it **~98%** of the time. This is
correct and the harness rewards it. Do not let parallelism (rule 1) tempt you into
blind edits: parallelize *reads*, but the edit still follows a read of that file.
Opus already goes `Read→Edit` more directly than Fable (4.0% vs 1.8%) — good, keep it.

## 4. Externalize the plan on multi-step work

Fable used the task tools **~2.5× more** than you (5.5% vs 2.2% of all calls). On
anything past ~3 steps, a written task list is steering, not ceremony — it catches
missing steps and wrong ordering before they cost a turn.

**Rule:** if a task has independent sub-parts or more than a few steps, write the
list first and update it as you go. For small single-file edits, skip it.

## 5. Finish the turn — autonomy is already a shared strength

Both models run **median 9 tool calls/turn**, with **~47% of turns at 11+ calls**
and <10% text-only. That is the right altitude: when handed real work, do the
whole thing in one turn rather than stopping to ask after each step. Keep it.
(Mirrors your standing guidance to handle a handed-off batch end-to-end.)

## 6. Research and delegate — adopt the reflex, weighted for honesty

Fable reached for `WebSearch`, `WebFetch`, and subagent `Agent` calls noticeably
more. **Caveat, stated plainly:** part of that is *task assignment* — Fable drew
more research/browser work — not proof of a better instinct. So treat this as a
soft nudge, not a hard rule:

- Before hand-rolling something non-trivial, check if it's a solved problem
  (docs / existing library / prior art). This matches the repo's research-first
  workflow guidance.
- For 2+ genuinely independent investigations, dispatch parallel agents instead
  of serializing them yourself.

Don't manufacture searches to hit a number — the metric is confounded; the
principle (don't reinvent, don't serialize independent work) is what carries over.

---

## Anti-patterns — Fable behaviours NOT to copy

- **Editing without a follow-up test.** Fable's signature weakness (§2). The most
  important "don't."
- **Don't chase the tool-mix percentages.** WebSearch/Playwright shares reflect
  what Fable was *asked* to do; imitating the ratio is cargo-culting.
- **Parallelism never overrides correctness ordering.** Read-before-edit,
  edit-before-test, and "B depends on A → B waits for A" always win over batching.

## Reference — measured baselines (so you can tell drift from noise)

```
                          fable-5     opus-4-8
tool calls/turn (mean)      16.06        15.23
tool calls/turn (median)        9            9
% turns 11+ calls           47.7%        47.3%
% tool-msgs parallel        28.5%        14.3%   <- target: move opus up
read-before-edit            98.4%        98.3%
test-after-edit (turn)      13.8%        21.7%   <- target: move BOTH up
edits w/ later in-turn test 46.2%        55.3%
top transition          Bash->Bash   Bash->Bash
```

*Generated by `compare_models.py`; raw metrics in `model_compare.json`.*
