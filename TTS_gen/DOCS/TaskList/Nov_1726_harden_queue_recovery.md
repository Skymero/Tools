# Action Item
- Harden Drive queue recovery so completed jobs cannot starve later work and
  retries reuse the recorded upload identity safely.

## Task Title: Select the oldest eligible unfinished version
- **task description**: Walk folders oldest-first, skip completed or exhausted
  versions, and require a `RETRY` marker before reviving failures.
- **Location**: `run_drive_queue.py`
- **Expected outcome**: One eligible job is processed; held work never blocks a
  later eligible folder.
- **implementation pseudocode in natural language**: fingerprint each candidate,
  load its durable row, skip terminal/held versions, consume `RETRY`, then stop
  after selecting one job.
- **comprehensive task explanation**: Looking only at the first Drive folder
  causes permanent starvation once that folder completes.

## Task Title: Resume upload with the same Drive ID
- **task description**: Set the durable stage to uploading on every upload pass,
  query the persisted ID, and update that file when it already exists.
- **Location**: `run_drive_queue.py`; `google_drive_client.py`
- **Expected outcome**: Upload retries create no duplicate and completion uses a
  valid atomic transition.
- **implementation pseudocode in natural language**: read the saved ID; query it;
  update if present or create with the reserved ID if absent; confirm metadata;
  transition uploading to completed.
- **comprehensive task explanation**: A retry can follow a timeout after Drive
  accepted bytes, so blind create is unsafe.

## Task Title: Surface retained orphan workspaces
- **task description**: Compare work directories with recorded snapshot paths
  and report unmatched directories without deleting them.
- **Location**: `run_drive_queue.py`
- **Expected outcome**: Recovery evidence remains intact and visible.
- **implementation pseudocode in natural language**: enumerate direct workspace
  children, compare exact recorded paths, and print a review message.
- **comprehensive task explanation**: Automated deletion would destroy the very
  artifacts needed to diagnose an interrupted run.

## Status
- [x] Implemented.
