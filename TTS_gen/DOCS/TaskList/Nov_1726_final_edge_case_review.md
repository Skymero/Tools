# Action Item
- Close final worker/queue edge cases found during release review.

## Task Title: Keep worker cleanup inside the complete failure boundary
- **task description**: Parse `job.json` inside the guarded worker path and use a
  dedicated logger whose handler closes in `finally`.
- **Location**: `render_chapter.py`; `tests/test_render_chapter.py`
- **Expected outcome**: Malformed job metadata writes a failed state and never
  leaks a Windows file handle or mutates unrelated root logging.
- **implementation pseudocode in natural language**: create a job-specific
  logger; enter try; parse configuration; execute stages; record any exception;
  close and detach the handler in finally.
- **comprehensive task explanation**: Configuration is untrusted job input and
  belongs inside the same durable failure boundary as every other stage.

## Task Title: Reject ambiguous chapter snapshots
- **task description**: Count native-Doc/plain-text chapter candidates and
  require exactly one.
- **Location**: `run_drive_queue.py`
- **Expected outcome**: A job cannot silently overwrite one chapter source with
  another based on API list order.
- **implementation pseudocode in natural language**: increment for each chapter
  candidate; fail above one; fail at zero; download only the unique source.
- **comprehensive task explanation**: Drive child ordering is not an editorial
  selection contract.

## Task Title: Preserve quota-hold semantics
- **task description**: Catch the quota gate's distinct exception before the
  generic failure handler.
- **Location**: `run_drive_queue.py`
- **Expected outcome**: Policy/configuration holds become `quota_hold` without
  consuming a generic retry attempt.
- **implementation pseudocode in natural language**: catch QuotaHoldError; write
  status and stage quota_hold; re-raise for the scheduler exit/log.
- **comprehensive task explanation**: Quota availability is not a render defect
  and must remain operationally distinguishable.

## Status
- [x] Implemented.
