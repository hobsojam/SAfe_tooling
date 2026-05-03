Run a compact CI check — lint, format, types, tests — and report only failures.

Execute each step below as a single Bash call, in order. Do NOT show the raw output to the user — capture it, analyse it, and produce a compact summary table at the end.

## Steps

**1. Ruff lint**
```bash
python -m ruff check . 2>&1
```
Record exit code. On failure keep only lines matching `error` or the `Found N error` summary line.

**2. Ruff format**
```bash
python -m ruff format --check . 2>&1
```
Record exit code. On failure keep only the list of files that would be reformatted.

**3. mypy**
```bash
python -m mypy safe/ 2>&1 | tail -30
```
Record exit code. Keep only lines that contain `error:` or the final `Found N error` line.

**4. pytest**
```bash
python -m pytest -q --tb=line 2>&1 | tail -40
```
Record exit code. Keep only FAILED lines, the short `-- Captured` blocks, and the final summary line (`N passed`, `N failed`).

## Output format

After all four steps, output **only** this (no other prose):

```
| Check          | Result  | Details                            |
|----------------|---------|------------------------------------|
| ruff lint      | ✓ PASS  |                                    |
| ruff format    | ✗ FAIL  | 3 files would be reformatted       |
| mypy           | ✓ PASS  |                                    |
| pytest         | ✗ FAIL  | 2 failed, 420 passed               |
```

If any check failed, add a **Failures** section listing only the actionable error lines (file:line:col message), grouped by check. Keep each error to one line. Cap at 20 errors per check.

If all checks pass, output only the table with all ✓ PASS rows — nothing else.
