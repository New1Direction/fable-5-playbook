# Fable 5 Playbook

An operating playbook for `claude-opus-4-8`. It encodes the decision-making
patterns that made Fable 5 feel good to work with, distilled from a side-by-side
behavioral read of real session logs.

> In my own testing, pointing Opus 4.8 at this playbook gets the closest to a
> Fable 5 like experience I have found so far.

## What it's for

Large models can do the same work in very different ways. This playbook captures
the specific working habits that made Fable 5 pleasant in practice and turns them
into standing instructions for Opus 4.8:

- Batch independent tool calls instead of going one at a time
- Write the plan out loud on anything past a few steps
- Read a file before editing it
- Run a real check after an edit and report the output, never claim "done" on an
  unverified change
- Finish the task in one turn instead of stopping to ask after every step

It also rejects the one thing Fable did worse, shipping edits without verifying
them, so Opus builds on Fable rather than copying it wholesale.

## How to use it

Put the playbook somewhere the model reads as standing guidance, then work
normally:

- `CLAUDE.md` at the project or user level (Claude Code)
- a project rule file
- the system prompt of your own Opus 4.8 integration

No tooling or setup. The rules are written to be followed directly.

Full text: [OPUS_FABLE_PLAYBOOK.md](OPUS_FABLE_PLAYBOOK.md)

## Where it comes from

Every claim in the playbook is measured, not assumed. It is based on an aggregate
behavioral comparison of real Opus 4.8 and Fable 5 session logs: turn counts, tool
sequencing, parallel call rates, and read-before-edit and test-after-edit ratios.
The comparison reports only aggregate statistics. No project names, code, or
session content are included.
