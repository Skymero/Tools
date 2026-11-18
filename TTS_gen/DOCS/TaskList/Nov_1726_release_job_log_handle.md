# Action Item
- Ensure `render_chapter.py` releases its per-job log handle on every success
  and failure path so Windows can archive, retry, or remove a workspace.

## Task Title: Close job logging handlers deterministically
- **task description**: Add one cleanup helper that flushes, closes, and removes
  every handler installed for the current job, and invoke it before returning or
  re-raising.
- **Location**: `render_chapter.py`; `tests/test_render_chapter.py`
- **Expected outcome**: A failed render writes `state.json` and `job.log`, then a
  Windows process can immediately delete or move the job directory.
- **implementation pseudocode in natural language**:
  - After configuring per-job logging, keep cleanup reachable from all exits.
  - Flush each active handler, close it, and detach it from the root logger.
  - Run cleanup after success and after recording a failure.
  - Exercise the failure path inside `TemporaryDirectory`; its automatic cleanup
    is the regression assertion.
- **comprehensive task explanation**: Windows denies deletion of an open file.
  Python's process-global logging handlers otherwise retain `job.log` after the
  function returns, which breaks recovery and test cleanup.

## Status
- [x] Implemented and covered by `test_missing_timeline_records_failure`.
