# CLAUDE.md

> Example project `CLAUDE.md` that pairs a short project brief with the Fable
> Playbook operating rules. Copy it into your repo and edit the Project section.
> The rules below are the condensed playbook; the full reasoning and the measured
> baselines live in [OPUS_FABLE_PLAYBOOK.md](../OPUS_FABLE_PLAYBOOK.md).

## Project

- **What this is:** <one line about your app or service>
- **Stack:** <language / framework / package manager>
- **Run tests:** `<your test command>`
- **Build / typecheck:** `<your build or typecheck command>`
- **Conventions:** <anything the agent should never break>

## How to work in this repo

1. **Batch independent tool calls.** When the next actions do not depend on each
   other's output, fire them in one message: read several files at once, run
   `git status` + `git diff` + `git log` together, grep multiple symbols in one
   go. Go sequential only when step B genuinely needs step A's output.

2. **Read before you edit.** Always read the target file before changing it.
   Parallelize the reads, but the edit still follows a read of that file.

3. **Plan out loud on multi-step work.** If a task has independent sub-parts or
   more than about three steps, write the task list first and update it as you go.
   Skip it for small single-file edits.

4. **Verify before you claim done.** After changing code, run the most specific
   check available and report its real output, in the same turn as the edit: the
   test covering the change, else a typecheck / build / lint, else exercise the
   code path directly. Never say "fixed" or "done" without verification output in
   that turn. An edit you did not verify is a hypothesis, not a fix.

5. **Finish the turn.** When handed real work, do the whole thing in one turn
   rather than stopping to ask after each step.

6. **Do not reinvent.** Before hand-rolling something non-trivial, check for an
   existing library, docs, or prior art. Dispatch parallel agents for two or more
   genuinely independent investigations instead of serializing them yourself.
