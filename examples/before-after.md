# Before / after

Illustrative, not a verbatim log. It shows the behavior shift the playbook is
trying to produce on a small task: "the `parse_config` test is failing, fix it."

## Before (default habits)

1. Read `config.py`.
2. Read `test_config.py`.
3. Read `defaults.py`.
4. "I think the bug is in `parse_config`. Want me to change it?"
5. (after you say yes) Edit `config.py`.
6. "Fixed the off-by-one in the key lookup."

Six round trips. Three of them were independent reads that could have been one
message. It asked permission mid-task, and it declared the fix without running
the test.

## After (with the playbook)

1. One message: three `Read` calls (`config.py`, `test_config.py`,
   `defaults.py`) plus `git diff`, all at once.
2. A short plan: "1) reproduce, 2) fix the key lookup in `parse_config`, 3) run
   the test." Then `pytest tests/test_config.py::test_parse_config` to reproduce
   the failure.
3. Edit `config.py`.
4. Re-run `pytest tests/test_config.py::test_parse_config`, paste the passing
   output, and report exactly what changed.

Same fix, fewer round trips, no mid-task permission stop, and the claim of
"fixed" arrives with a green test in the same turn.

## What changed

| | Before | After |
|---|---|---|
| Reads | one per message | batched into one message |
| Plan | none | written before editing |
| Permission stop | mid-task | none needed |
| Verification | none | test re-run, output shown |
