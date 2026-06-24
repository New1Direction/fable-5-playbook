# Claude Code Fable Playbook

Make Opus behave more like the best parts of Fable 5: fewer round trips, clearer
plans, safer edits, and verified fixes.

A drop-in `CLAUDE.md` that gets your coding agent to plan, batch tools, read
before editing, and verify changes. Built from an aggregate comparison of
**2,124 Opus 4.8 turns vs 220 Fable 5 turns** of real coding-agent logs.

## Try it in 30 seconds

For Claude Code, save the playbook as `CLAUDE.md` in your project:

```bash
curl -L https://raw.githubusercontent.com/New1Direction/fable-5-playbook/main/OPUS_FABLE_PLAYBOOK.md -o CLAUDE.md
```

Then work normally. The playbook pushes the model to:

- batch independent tool calls
- write a plan for multi-step work
- read files before editing
- verify changes before claiming completion

You can also drop it at the user level, in a project rule file, or in the system
prompt of your own Opus integration. No tooling or setup; the rules are written
to be followed directly.

## Why this exists

The biggest difference between the two models was not "intelligence." It was
operating style.

| Behavior | Fable 5 | Opus 4.8 | Playbook action |
|---|---:|---:|---|
| Parallel tool calls | 28.5% | 14.3% | Batch harder |
| Externalized task list | 5.5% | 2.2% | Plan out loud |
| Read before edit | 98.4% | 98.3% | Keep it |
| Test after edit | 13.8% | 21.7% | Do not copy Fable; verify more |

Fable got to the same amount of work in fewer round trips and planned out loud
more often. But it also shipped edits without checking them, and Opus already
verifies more than Fable did. So the playbook adopts Fable's batching and
planning habits while pushing verification further than either model actually
managed.

Full text: [OPUS_FABLE_PLAYBOOK.md](OPUS_FABLE_PLAYBOOK.md)

## Examples

- [`examples/CLAUDE.md`](examples/CLAUDE.md): a realistic project `CLAUDE.md`
  that pairs a short project brief with the playbook rules.
- [`examples/before-after.md`](examples/before-after.md): the same small task
  handled with and without the playbook.

## Reproduce the numbers

Every claim is measured, not assumed. The comparison reports aggregate
statistics only: no project names, code, or session content.

- Aggregate metrics: [`data/model_compare.json`](data/model_compare.json)
- The script that produced them: [`scripts/compare_models.py`](scripts/compare_models.py)

The script segments real Claude Code session logs into turns and measures turn
cadence, parallel tool-call rate, read-before-edit and test-after-edit ratios,
and tool transitions for each model.

```bash
python3 scripts/compare_models.py
```

It reads your local `~/.claude/projects` logs and is hardcoded to compare
`claude-fable-5` and `claude-opus-4-8`. Edit the `models` list near the bottom
to compare whatever models you have logs for.

## Help validate it

This is one person's measurement across their own logs. The most useful thing
you can contribute is a second data point, not a star:

- Run `scripts/compare_models.py` against your own logs and share the aggregate
  numbers.
- Or post a plain before/after from your own Claude Code runs.

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues labeled `validation wanted` and
`adapter wanted` are good places to start. Please do not star-trade or spam;
real results are worth more.

## License

[MIT](LICENSE)
