# Contributing

Thanks for helping. The single most valuable contribution here is not a star, it
is a second data point. The playbook is built from one person's logs; independent
results either make it trustworthy or tell us where it is wrong.

## Share validation results

1. Run the comparison against your own Claude Code logs:

   ```bash
   python3 scripts/compare_models.py
   ```

   It is hardcoded to compare `claude-fable-5` and `claude-opus-4-8`. Edit the
   `models` list in `scripts/compare_models.py` to compare whatever models you
   have logs for.

2. Open an issue with the `validation wanted` label and paste the aggregate
   numbers (parallel rate, read-before-edit, test-after-edit, tool cadence).
   Aggregate stats only, please: no project names, code, or session content.

Or skip the script and post a plain before/after from your own runs: what the
agent did with and without the playbook in `CLAUDE.md`.

## Add an adapter

The rules are written for Claude Code's `CLAUDE.md`, but the habits are general.
Adapters for other agents (Cursor rules, Windsurf, Continue, custom system
prompts) are welcome. Open an issue with `adapter wanted`, or send a PR adding an
`adapters/<tool>.md`.

## Improve the benchmark

The measurement is deliberately simple. If you can make `compare_models.py` more
accurate (better test-command detection, more tools, cleaner turn segmentation),
open an issue with `benchmark`, or send a PR. Keep the output aggregate-only.

## Ground rules

- Aggregate data only. Never commit logs, source code, or session content.
- No star-trading, no spam, no buying engagement. Real results only.
- Keep prose plain and human.

## Labels

| Label | Use it for |
|---|---|
| `good first issue` | small, well-scoped starting points |
| `validation wanted` | sharing before/after or measured results |
| `adapter wanted` | porting the rules to another agent |
| `benchmark` | improving the comparison script or metrics |
