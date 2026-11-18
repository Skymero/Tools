# Action Item
- Finish the TTS_gen Google Drive-backed chapter-to-video automation so Windows Task Scheduler can safely discover, snapshot, render, verify, upload, and complete one chapter job per run without duplicate work, leaked credentials, or undocumented manual steps.

## Audit Summary

| Area | Current evidence | Status | Consequence |
|------|------------------|--------|-------------|
| Kokoro narration CLI | `text_to_speech_kokoro.py` exists with 11 passing stdlib tests; live `sample-heart.wav` and `sample-bella.wav` prove local synthesis | Implemented and tested | Narration stage is reusable by the worker |
| Manual render path | `create_mp4.py` + authored `video-timeline.json`; committed `output.mp4` is historical evidence | Partially usable | Only a manual render exists; not unattended/concurrent safe |
| FFmpeg/FFprobe | `ffmpeg -version` / `ffprobe -version` fail on PATH | Missing prerequisite | Rendering, MP3, and probing are blocked |
| Planned modules | `render_chapter.py`, `run_drive_queue.py`, `google_drive_client.py`, `gemini_client.py`, `langflow_client.py`, `timeline_validator.py`, `media_probe.py`, `scene_audio.py` do not exist | Missing | Entire automation layer is unbuilt |
| Runtime/config surface | `incoming`, `work`, `output`, `failed`, `completed`, `logs`, `.env.example`, automation config, credentials/token storage, SQLite ledger do not exist | Missing | No job contract, state, or secrets handling exists |
| Cloud dependencies | No Google Drive, Gemini, or Langflow dependency set, integration, or tests | Missing | Cloud transport and planning are entirely unbuilt |
| Technical guide PDF | Thorough for original scripts but stale: no Kokoro, cloud trust boundaries, scheduler, Drive, Gemini, Langflow, or current tests; still says four scripts / no automated tests | Stale | New developers get an inaccurate picture |
| Chapter workflow PDF | Useful one-page target-state diagram | Aspirational | Contract-light; does not separate built vs pending |
| Scheduler PDF | Depends on missing `render_chapter.py --once`, local folders/logs, and FFmpeg | Premature | Following it today cannot succeed |
| Google Drive PDF | Clear five-page target design; explicitly says it is unimplemented. Proposes `run_drive_queue.py --once` calling `render_chapter.py --job-dir`, Drive input/output folders, local reusable artifacts, stable upload IDs, resumable upload retries | Unimplemented design | Good blueprint; needs contracts before coding |
| Gemini/Langflow PDF | Six-page setup/design using official `gemini-3.5-flash-lite`, currently listed by Google | Untested here | Model is real but unproven against this project |
| Gemini quota design | 80% quota gate is a local policy, not a provider guarantee; active limits vary by project/model; local ledger cannot see unrelated usage; dedicated project mitigates but does not eliminate reconciliation | Under-specified | Needs configured current limits plus reconciliation |
| Langflow usage metadata | Unknown whether Langflow exposes the Gemini usage metadata needed to reconcile reservations | Open question | Must be answered by a spike before Phase 2 is coded; use `countTokens` for complete input estimation, not character guesses |
| OAuth durability | OAuth Testing-mode refresh tokens can expire after seven days; PDF acknowledges expiry but does not close the operational decision | Unresolved | Durable scheduled Drive automation needs explicit consent-screen/publishing/reauthorization strategy |
| Drive scopes | Design combines `drive.readonly` for inputs and `drive.file` for app-created outputs | Workable but broad | Input read access and unpublished manuscript/API data egress need explicit stakeholder approval and documentation |
| Scheduler contract | Two contracts conflict: old PDF schedules `render_chapter.py --once`; Drive PDF schedules `run_drive_queue.py --once` calling `render_chapter.py --job-dir` | Conflicting | Revised contract: Drive queue is the scheduler entry point; renderer is a single staged-job worker; optional separate local-only mode |
| One-page PDF sources | New PDFs contain embedded Mermaid `.mmd` attachments but no standalone source/generator in repo; existing text extraction has malformed apostrophes/arrows/ligatures | Unmaintainable | Search/copy/accessibility degraded; needs externalized MMD + generators |
| Exact contracts | No Drive job fingerprint, SQLite schema, remote-change policy, paragraph export contract for native Google Docs, upload checksum/size confirmation, or secret rotation procedure | Missing | Ambiguity would be baked into code |
| Test coverage | 11 tests cover only Kokoro; nothing covers render, Drive, Gemini, Langflow, quota ledger, idempotency, scheduler, or E2E | Narrow | Regressions would be invisible |
| Git hygiene | Current Kokoro/docs/PDF work is modified or untracked | Pending | Release hygiene remains incomplete |

## Documentation Evaluation

| Document | Strengths | Gaps/Risks | Required correction |
|----------|-----------|------------|---------------------|
| `TTS_gen_Technical_Guide.pdf` | Excellent evidence ladder and implementation grounding; every claim cites source files | Stale: predates Kokoro, tests, and the entire automation/cloud design | Regenerate to cover Kokoro, current tests, orchestrator, Drive/Gemini/Langflow cloud trust boundaries, and clearly label current vs planned |
| `TTS_gen_Chapter_Video_Workflow.pdf` | Good staged retry concept and clear one-page target flow | Aspirational; does not mark implemented vs pending; contract-light; malformed text extraction | Rebuild from committed generator + external `.mmd` source; add current-vs-pending labels and links to the contract doc |
| `TTS_gen_Windows_Task_Scheduler_Setup.pdf` | Correct no-overlap setting and concrete GUI steps | Schedules the wrong entry point for the Drive design; depends on missing files/folders/FFmpeg; corrupted glyphs | Update entry point to `run_drive_queue.py --once`; withhold "ready" status until prerequisites exist; fix glyphs; add editable generator |
| Google Drive design PDF (five pages) | Stable output ID / resumable retry design; explicit unimplemented disclaimer; sensible `drive.readonly` + `drive.file` split | No fingerprint/schema/remote-change policy; OAuth seven-day expiry unresolved; input-scope and manuscript-egress approvals undocumented | Adopt as Phase 1 blueprint after Task 1 closes contracts: fingerprint, SQLite schema, version recheck, auth strategy, privacy approvals |
| Gemini/Langflow design PDF (six pages) | Official current model; model discovery fallback; structured output; dedicated project concept; SQLite reservations; saves raw output before retry | 80% gate described without caveat; usage-metadata exposure through Langflow unproven; untested against this project | Keep the design; add the Task 13 feasibility spike, `countTokens` estimation, configured current limits, and reconciliation limits disclaimer |

## Delivery Strategy

Four phase gates, each independently verifiable:

- **Phase 0 — Local MVP**: authored timeline, local staged job, full chapter only. No Drive, no Langflow, no teaser. Proves the worker, validator, renderer, and probe.
- **Phase 1 — Drive transport**: Drive Incoming folder -> local snapshot -> local worker -> verified upload -> stable completion. Drive becomes the control plane.
- **Phase 2 — Gemini/Langflow planning**: quota gate, real Langflow flow, captured raw output, validated generated timeline.
- **Phase 3 — Optional vertical teaser**.

Full-chapter output dimensions are an explicit Task 1 decision gate: the current renderer always emits 1080x1920 portrait while the teaser is explicitly vertical — the contract must say whether the chapter keeps 1080x1920, changes, or becomes configurable.

After Phase 1 the scheduler entry point is `run_drive_queue.py --once`; `render_chapter.py --job-dir` is the local single-job worker it calls. An optional clearly-separated local-only mode may exist only if the contract approves it.

## Task Title: Approve architecture, privacy, and acceptance contract
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** `DOCS/automation-contract.md` records the implementation authorization and conservative decisions. Account-owner OAuth consent, provider terms acceptance, and real-service acceptance remain manual.
- **Task description**: Produce the human-approved contract that every later task implements. Decide full-chapter output dimensions, the four phase gates, Drive-as-control-plane architecture, whether a local-only mode exists, the complete job lifecycle, the manual platform-upload terminal boundary, and the privacy decisions: unpublished-manuscript egress to Drive/Gemini, Gemini free-tier data-use implications, and approval of the `drive.readonly` input scope.
- **Location**: new `DOCS/automation-contract.md`; read all five PDFs (`TTS_gen_Technical_Guide.pdf`, `TTS_gen_Chapter_Video_Workflow.pdf`, `TTS_gen_Windows_Task_Scheduler_Setup.pdf`, the Google Drive design PDF, the Gemini/Langflow design PDF) in `DOCS/`.
- **Expected outcome**: A committed contract document with a Mermaid state diagram (never ASCII art) covering job states, explicit approvals for scope and data egress, the dimension decision, and the rule that `run_drive_queue.py --once` is the scheduler entry point after Phase 1. Signed off by a human before any coding.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Read all five design and guide PDFs
    Record the full-chapter dimension decision
    Draw the job lifecycle as a Mermaid state diagram
    Declare Drive the scheduler control plane after Phase 1
    Decide whether a separate local-only mode is allowed
    Record the manual-upload terminal boundary
    Record stakeholder approval for Drive read scope and manuscript egress
    Record the Gemini free-tier data-use decision
    Get explicit human sign-off before implementation begins
END
  }
  ```
- **Comprehensive task explanation**: Nothing else can start until this exists — Task 3's env names, Task 4's schema, Task 6's dimension handling, and Task 9's scope choice all cite this document. The audit shows two conflicting scheduler contracts; this task resolves them permanently: `run_drive_queue.py --once` is scheduled, `render_chapter.py --job-dir` is a worker it invokes on one staged directory. Write the lifecycle as a Mermaid `stateDiagram-v2` with states: discovered, snapshotting, ready, rendering, verifying, uploading, completed, failed, auth-attention, quota-hold. Dependencies: none — this is the root gate.
- **Verification**: `Test-Path DOCS/automation-contract.md` is True; `Select-String -Path DOCS/automation-contract.md -Pattern 'stateDiagram|run_drive_queue.py --once|render_chapter.py --job-dir|drive.readonly'` returns matches; the doc names the dimension decision and has a recorded sign-off line; no code task begins without it.

## Task Title: Install and verify local media prerequisites
**Status (2026-11-17): MANUAL REQUIRED.** Kokoro and SoundFile import successfully, but FFmpeg and FFprobe are not on PATH. Installation and scheduled-account verification require the operator/admin.
- **Task description**: Make FFmpeg and FFprobe available on PATH for the account that will run the scheduled task, and re-verify the existing `.venv` Kokoro environment. The install itself is a human/admin step — never bypass permissions.
- **Location**: machine-level FFmpeg install; `.venv/` at project root; `sample-heart.wav`.
- **Expected outcome**: `ffmpeg -version` and `ffprobe -version` succeed from a fresh PowerShell under the current user and under the scheduled task account. `.venv` Python imports `kokoro` and `soundfile`; `soundfile.info` confirms `sample-heart.wav` is 24 kHz mono PCM16.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Ask a human or admin to install FFmpeg and FFprobe on PATH
    Open a fresh PowerShell window
    Confirm ffmpeg -version prints a version
    Confirm ffprobe -version prints a version
    Repeat both checks under the scheduled task account if it differs
    Run the .venv Python and import kokoro and soundfile
    Read sample-heart.wav metadata with soundfile.info
    Confirm 24000 Hz, mono, PCM_16
END
  }
  ```
- **Comprehensive task explanation**: FFmpeg absence was confirmed in the audit; every render/probe task is blocked until this is done. If the install needs rights you do not have, stop and hand back to the human — do not work around it. Dependencies: none (independent of Task 1 but required before Tasks 6-8 can verify).
- **Verification**: `ffmpeg -version` and `ffprobe -version` each exit 0 in a fresh PowerShell; `.\.venv\Scripts\python.exe -c "import kokoro, soundfile"` exits 0; `.\.venv\Scripts\python.exe -c "import soundfile as sf; print(sf.info('sample-heart.wav'))"` reports `24000 Hz`, `1` channel, `PCM_16`.

## Task Title: Define dependencies, secrets, and configuration
**Status (2026-11-17): COMPLETE.** Pinned Drive requirements, placeholder-only environment/config examples, external secrets policy, and ignore rules are implemented.
- **Task description**: Pin the cloud dependency set, define every environment variable name (no values), and establish where secrets live. Document in the contract why the official Google client libraries are required — stdlib `urllib` is insufficient for OAuth token exchange/refresh and resumable uploads — before adding them.
- **Location**: new `requirements-drive.txt`; new `.env.example`; new `automation-config.example.json`; `.gitignore`; `DOCS/automation-contract.md`.
- **Expected outcome**: `requirements-drive.txt` pins the official Google client libraries (`google-api-python-client`, `google-auth`, `google-auth-oauthlib`). `.env.example` defines names only: Drive incoming/finished/Gemini-output folder IDs, `LANGFLOW_BASE_URL`, `LANGFLOW_FLOW_ID`, `LANGFLOW_API_KEY`, `GEMINI_MODEL`, `GEMINI_API_KEY`, local root paths, output dimensions, export flags. OAuth client JSON and refresh tokens are stored outside the repo under an approved user-local directory (e.g., `%LOCALAPPDATA%\TTS_gen\secrets`). `.gitignore` covers credential files, token stores, SQLite db, and all runtime dirs. Contract documents API-key restriction, rotation, and log-redaction rules.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Write requirements-drive.txt with pinned official Google libraries
    Write .env.example listing every variable name with comments and no values
    Write automation-config.example.json using relative paths
    Record the approved user-local secrets directory outside the repo
    Update .gitignore for credentials tokens database and runtime folders
    Document API key restriction rotation and redaction rules in the contract
    Confirm no real secret value exists anywhere in the repository
END
  }
  ```
- **Comprehensive task explanation**: The no-third-party-deps rule yields here only after documenting the stdlib gap: OAuth refresh flows and resumable upload sessions are exactly what `google-auth`/`google-api-python-client` exist for — writing them by hand would be the riskier choice. Every secret reads from the environment or the user-local store at runtime; a leaked `.env` must be impossible to commit. Dependencies: Task 1 (env names and scope choices come from the contract).
- **Verification**: `Test-Path requirements-drive.txt, .env.example, automation-config.example.json` all True; `Select-String -Path .env.example -Pattern '='` shows placeholder text only, no real values; `git check-ignore -v .env` and the secrets directory path are ignored; `Select-String -Path DOCS/automation-contract.md -Pattern 'stdlib|resumable|rotation'` documents the decisions.

## Task Title: Create local folders and durable SQLite state schema
**Status (2026-11-17): COMPLETE.** `job_store.py` implements WAL/foreign keys, schema versioning, jobs/files/reservations, deterministic fingerprints, and atomic transitions. Runtime directories are created on demand and ignored.
- **Task description**: Build the runtime folder tree and `job_store.py`, the SQLite-backed ledger that makes every job transition durable and every quota reservation auditable.
- **Location**: runtime folders `incoming/`, `work/`, `output/`, `failed/`, `completed/`, `logs/`; new `job_store.py`; SQLite db under an ignored runtime path.
- **Expected outcome**: `job_store.py` exposes typed functions to create/transition job records. Schema tracks: Drive folder ID + deterministic input fingerprint as job identity; file IDs, versions, and checksums; local snapshot paths; stage/status/attempt counters; quota reservations; Gemini raw output path; output Drive file IDs; timestamps and error text. WAL mode, transactional multi-row updates, atomic single-statement status transitions, and a `schema_version` row with a migration hook. Runtime dirs are git-ignored (`.gitkeep` only where an empty dir is part of the interface).
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Create the six runtime folders and ignore rules
    Open the SQLite database with WAL mode and foreign keys on
    Create the schema_version table and apply migrations
    Create the jobs table keyed by Drive folder ID plus input fingerprint
    Create the job_files table for file IDs versions and checksums
    Create the reservations table for quota holds
    Expose transactional helpers to claim transition and complete jobs
    Make every status change a single atomic statement
    Verify a crash between statements leaves a consistent record
END
  }
  ```
- **Comprehensive task explanation**: SQLite via stdlib `sqlite3` is the right tool — no ORM, no server. The fingerprint (e.g., sorted `fileId+modifiedTime+md5` hash of the job's input set) is what makes "same job" deterministic across runs; the Drive PDF calls for this but leaves it unspecified — pin the exact formula in the contract before coding. Dependencies: Task 1 (schema fields), Task 3 (db location, ignore rules).
- **Verification**: `python -c "import job_store; job_store.init('work/test.db')"` exits 0 and creates the schema; `python -m unittest tests.test_job_store -v` passes create/transition/reserve cases; `.gitignore` matches `work/`, `logs/`, `*.db`; `Select-String -Path DOCS/automation-contract.md -Pattern 'fingerprint'` shows the pinned formula.

## Task Title: Implement strict timeline and scene-plan validation
**Status (2026-11-17): COMPLETE.** Strict authored-timeline and scene-plan validation plus unit coverage are implemented.
- **Task description**: Build `timeline_validator.py` covering both authored `video-timeline.json` and Phase 2 generated scene plans. In automation mode nothing is silently defaulted.
- **Location**: new `timeline_validator.py`; new `tests/test_timeline_validator.py`.
- **Expected outcome**: `validate_timeline(...)` enforces all existing rules (nonempty scenes, required image, path containment, finite numerics, `end > start`, allowed motion set, image existence, 30fps contiguity, audio-duration tolerance) plus scene-plan rules: paragraph ranges are one-based inclusive, completely cover the source without overlap, reference only the declared artwork ID inventory, and carry valid motion/intensity. Every rejection names the scene and field.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Load the JSON and require the expected top-level shape
    For each scene validate image start end motion and intensity strictly
    Resolve image paths inside the declared images directory only
    Require scenes ordered and contiguous within one frame at 30fps
    Require total duration to match probed audio within tolerance
    For scene plans additionally require:
      paragraph ranges are one-based inclusive
      ranges cover every paragraph exactly once without overlap
      every referenced artwork ID exists in the job inventory
    Reject unknown keys rather than silently defaulting them
    Return the normalized plan or one clear validation error
END
  }
  ```
- **Comprehensive task explanation**: This extends the previous audit's validator design with the scene-plan contract Task 15 needs — paragraph-range validation is the guard that keeps Langflow output honest before any synthesis. Tests use real temporary JSON and real temporary files; no fabricated production data. Dependencies: Task 1 (tolerance values, motion set).
- **Verification**: `python -m unittest tests.test_timeline_validator -v` passes; a misspelled `motoin` key is rejected by name; an overlapping or gapped paragraph range is rejected; `python -c "import timeline_validator"` exits 0.

## Task Title: Harden create_mp4.py for unattended isolated rendering
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** Isolated temporary rendering, strict validation, tool preflight, captured diagnostics, and duration enforcement are implemented. A real render is blocked only by the manual FFmpeg prerequisite.
- **Task description**: Refactor `create_mp4.py` for concurrent-safe, diagnosable, contract-driven rendering while preserving the manual CLI.
- **Location**: `create_mp4.py`; new `tests/test_create_mp4.py`.
- **Expected outcome**: Per-job `tempfile.TemporaryDirectory(dir=<staged job dir>)` replaces global `temp_segments/`; cleanup in `finally`; ffmpeg/ffprobe checked up front via `shutil.which`; FFmpeg stderr captured into raised errors (no `quiet=True` swallowing); strict validation via `timeline_validator`; output dimensions resolved from the Task 1 contract decision; material duration mismatches fail instead of silently looping; existing positional CLI still works.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Check ffmpeg and ffprobe exist before any work
    Validate the timeline with timeline_validator
    Create a TemporaryDirectory inside the staged job directory
    Render each scene segment into that directory
    Attach captured ffmpeg stderr to any raised error
    Compare probed video and audio durations
    Fail when the mismatch exceeds tolerance instead of looping
    Mux narration and write the final MP4
    Clean the temporary directory in a finally block
    Keep the manual command-line interface working
END
  }
  ```
- **Comprehensive task explanation**: The shared `temp_segments/` directory is the biggest concurrency hazard; per-job temp dirs inside the already-claimed workspace remove it. Dimensions become a parameter resolved from config so the Task 1 decision is code-configurable, not hard-coded. Add narrow tests on filter/command construction plus one real short render that skips when FFmpeg is absent. Dependencies: Tasks 1, 2, 5.
- **Verification**: `python -m unittest tests.test_create_mp4 -v` passes (render gate skips cleanly without FFmpeg); `Select-String -Path create_mp4.py -Pattern 'temp_segments'` shows no remaining global; the documented positional CLI still reaches validation; `git diff create_mp4.py` preserves existing behavior for manual flags.

## Task Title: Implement FFprobe media verification
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** JSON probing and chapter-output verification are implemented and unit tested. Real local media acceptance requires FFprobe installation.
- **Task description**: Build `media_probe.py` so every produced artifact is machine-verified before a job may complete or upload.
- **Location**: new `media_probe.py`; new `tests/test_media_probe.py`.
- **Expected outcome**: `probe_media(path)` parses `ffprobe -of json`; `verify_chapter_output(path, expectations)` enforces exactly one video and one audio stream, nonzero duration, expected width/height/fps/codecs, video-audio duration agreement within tolerance, and nonzero file size — raising clear errors otherwise.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Run ffprobe with JSON output on the media file
    Fail on ffprobe errors or unparseable JSON
    Require exactly one video stream and one audio stream
    Require nonzero format duration
    Check width height fps and codec names against expectations
    Check stream durations agree within tolerance
    Check file size is greater than zero
    Return the parsed probe data
END
  }
  ```
- **Comprehensive task explanation**: Exit codes cannot prove a watchable file. Tests generate a real one-second fixture clip with FFmpeg during setup and also probe the committed `sample.mp3` — real media, never fabricated probe output. This module also measures per-scene clip durations in Task 16. Dependencies: Task 2.
- **Verification**: `python -m unittest tests.test_media_probe -v` passes; a deliberately truncated file raises a verification error; probing `sample.mp3` returns the expected codec/duration fields.

## Task Title: Implement local worker render_chapter.py --job-dir (Phase 0)
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** The single-job worker, state/log files, artifact reuse, verification, and failure retention are implemented. Real render acceptance requires FFmpeg/FFprobe.
- **Task description**: Build the single-job worker that renders one already-staged job directory. It never scans queues — the Drive queue calls it.
- **Location**: new `render_chapter.py`; staged job dirs under `work/`; `tests/test_render_chapter.py`.
- **Expected outcome**: `render_chapter.py --job-dir <path>` reads `chapter.txt`, `images/`, authored `video-timeline.json`, optional `job.json`; synthesizes one Kokoro narration via the existing `create_narration`; probes it; validates the timeline; renders; verifies with `media_probe`; writes artifacts + `state.json` + per-job log; exits 0 on success, nonzero with preserved intermediates on failure. An optional clearly-separate local-only `--once` mode exists only if the Task 1 contract approves it.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Parse --job-dir and confirm the staged directory is complete
    Load the job state and open the per-job log
    Read chapter.txt and the optional job.json overrides
    Require an authored video-timeline.json for the MVP
    Synthesize one Kokoro narration file into the workspace
    Probe the narration duration
    Validate the timeline against images and audio
    Render the chapter with the hardened create_mp4
    Verify the output with media_probe
    Write final artifacts and state and exit 0
    On failure record the error keep intermediates and exit nonzero
END
  }
  ```
- **Comprehensive task explanation**: This is the Drive PDF's worker role: one directory in, one verified MP4 out. Reuse `text_to_speech_kokoro.create_narration` and the hardened `create_mp4` functions by import — no duplicated logic. Because it takes an explicit directory, it is trivially testable and can be run by hand for diagnosis. Dependencies: Tasks 1-7.
- **Verification**: stage a real job (`sample.txt` + two `Chapter1-imgs` images + hand-authored 2-scene `video-timeline.json`) and run `.\.venv\Scripts\python.exe render_chapter.py --job-dir work\test-job` — exits 0 with a verified MP4; a job missing the timeline exits nonzero with intermediates preserved; `python -m unittest tests.test_render_chapter -v` passes.

## Task Title: Implement durable Google Desktop OAuth setup
**Status (2026-11-17): IMPLEMENTED; MANUAL SETUP REQUIRED.** Interactive setup and noninteractive refresh/auth-attention behavior are coded. Consent and production/test publishing decisions must be exercised by the account owner.
- **Task description**: Build `google_drive_auth.py` with an interactive setup command and noninteractive scheduled refresh, plus the operational plan for Testing-mode token expiry.
- **Location**: new `google_drive_auth.py`; credential/token storage under the approved user-local directory from Task 3.
- **Expected outcome**: A `--setup-auth` command performs the Desktop OAuth consent flow once and stores the refresh token outside the repo; runtime code refreshes noninteractively. Scopes are exactly `drive.readonly` + `drive.file`. The contract records the chosen strategy for OAuth consent-screen Testing-mode seven-day refresh-token expiry (publish the app vs documented periodic reauthorization). A refresh failure raises a distinct auth-attention status — never an interactive prompt under the scheduler. Setup verifies the app can create its Finished Videos and Gemini Outputs folders so `drive.file` can manage them.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Load the OAuth client JSON from the approved secrets directory
    For setup run the local consent flow and store the refresh token
    Request exactly drive.readonly and drive.file scopes
    At runtime load the stored token and refresh silently
    If refresh fails raise the auth-attention status instead of prompting
    During setup create or locate the app output folders
    Record the expiry strategy chosen in the contract
END
  }
  ```
- **Comprehensive task explanation**: The seven-day Testing-mode expiry is the top operational risk the Drive PDF leaves open — an unattended task silently dying every week is the failure mode. The Task 1 contract must pick: publish the app to Production status, or accept documented periodic reauthorization. `drive.file` can only see files the app itself created, so the output folders must be app-created — setup proves this. Dependencies: Tasks 1, 3.
- **Verification**: `python google_drive_auth.py --setup-auth` completes against the real dev project (human-assisted, once); a subsequent `python -c "from google_drive_auth import get_credentials; print(get_credentials().valid)"` prints True without prompting; simulating a revoked token raises auth-attention, not a browser prompt; no credential file appears under the repo in `git status`.

## Task Title: Implement Google Drive client primitives
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** Listing, metadata, download/export, stable IDs, resumable create/update, classification, confirmation, and normalization are implemented. Real dev-endpoint acceptance remains manual.
- **Task description**: Build `google_drive_client.py` — thin wrappers over the official API for every Drive operation the queue needs.
- **Location**: new `google_drive_client.py`; unit tests with a fake transport, plus one real dev-endpoint integration test.
- **Expected outcome**: Primitives cover: list children by parent with `trashed=false`, fetch metadata with explicit `fields` (id/name/mimeType/modifiedTime/md5Checksum/size), export a native Google Doc as `text/plain`, download blob files, generate upload IDs, resumable upload with retryable-error classification and bounded backoff, and post-upload confirmation of parent/file ID/name/size/checksum where available. The contract gains the native-Doc paragraph-normalization rules (blank-line handling, numbering) and the remote-version recheck policy.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Build the Drive service from the stored credentials
    List children of a folder filtered to non-trashed items
    Fetch file metadata requesting explicit fields
    Export a native Google Doc as plain text
    Download binary file contents
    Request generated upload IDs for stable outputs
    Perform resumable uploads with bounded backoff on retryable errors
    Confirm uploaded file parent ID name size and checksum
    Return structured results or raise classified errors
END
  }
  ```
- **Comprehensive task explanation**: Keep this layer dumb — all policy lives in the queue. Two details the PDFs leave open are pinned here in the contract: how a native Google Doc becomes paragraphs (export `text/plain`, split on blank lines, strip numbering — verified against a real dev document in Task 16), and how the queue detects an input changed mid-staging (recheck `modifiedTime` before marking ready). Explicit `fields` on every call avoids multi-MB responses. Dependencies: Task 9.
- **Verification**: `python -m unittest tests.test_google_drive_client -v` passes unit tests; the real dev test lists the configured Incoming folder and exports a real test Doc when `DRIVE_INCOMING_FOLDER_ID` (from Task 3 config) is set — substitute the configured value; error classification maps 429/5xx to retryable and 401/403 to auth-attention.

## Task Title: Implement Drive queue run_drive_queue.py --once (Phase 1)
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** Oldest-eligible selection, fingerprinting, snapshot/recheck, single-job rendering, verified stable-ID upload, and no-work behavior are implemented. Real Drive E2E remains manual.
- **Task description**: Build the scheduler entry point that discovers, fingerprints, snapshots, renders, verifies, uploads, and completes exactly one Drive job per invocation.
- **Location**: new `run_drive_queue.py`; uses Tasks 4, 8, 9, 10; `tests/test_run_drive_queue.py`.
- **Expected outcome**: Loads state, lists the configured Incoming folder, deterministically chooses the oldest eligible job folder, fingerprints input versions into SQLite, stages an isolated local snapshot, rechecks remote versions before marking ready, calls `render_chapter.py --job-dir` on the snapshot, verifies and uploads to the app-created Finished Videos folder with stable generated IDs, records output IDs, and completes the job. No eligible work exits 0 with no side effects. An input changed mid-run becomes a new fingerprint — a requeue, never a mixed snapshot.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Acquire the single-process lock and load the job store
    List the Drive Incoming folder for eligible job folders
    If none exist log no work and exit 0
    Choose the oldest eligible folder deterministically
    Fingerprint its input files and record the job
    Stage an isolated local snapshot of all inputs
    Recheck remote file versions against the fingerprint
    If inputs changed requeue as a new version and exit cleanly
    Mark the snapshot ready and call the local worker
    Verify the produced MP4 with media_probe
    Upload to the app-created output folder using stable IDs
    Confirm upload metadata and record output Drive IDs
    Mark the job completed and release the lock
END
  }
  ```
- **Comprehensive task explanation**: The snapshot boundary is the core invariant: the worker only ever sees the frozen local copy, so an author editing the Doc mid-run can never contaminate the render — the recheck turns it into a separate job version instead. Deterministic oldest-first keeps behavior predictable. One job per run bounds execution for the 5-minute trigger. Dependencies: Tasks 1, 4, 8, 9, 10.
- **Verification**: with the configured `DRIVE_INCOMING_FOLDER_ID` (substitute the Task 3 value), `.\.venv\Scripts\python.exe run_drive_queue.py --once` on an empty folder exits 0; a real staged Drive job completes end-to-end with output IDs in SQLite; `python -m unittest tests.test_run_drive_queue -v` passes no-work, claim, and changed-mid-run cases.

## Task Title: Implement idempotency, upload retry, and recovery
**Status (2026-11-17): COMPLETE.** Stable ID query/update, verified artifact reuse, explicit RETRY, maximum attempts, orphan reporting, durable transitions, and process locking are implemented.
- **Task description**: Make reruns free of duplicate work and crashes recoverable by humans.
- **Location**: `run_drive_queue.py`, `job_store.py`; `DOCS/automation-contract.md`; tests.
- **Expected outcome**: A verified local MP4 is reused when only the upload failed; stable generated Drive IDs mean a retried upload replaces rather than duplicates; the saved output ID is queried before any retry; orphaned local workspaces are logged and held for human recovery; max attempts is enforced; retry is an explicit documented action; failed jobs and raw outputs are never auto-deleted; all DB transitions are atomic; a file-based single-machine lock runs alongside the scheduler no-overlap setting.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Acquire the single-process lock file or exit immediately
    On startup log orphaned workspaces and leave them for humans
    Resume a job from its recorded stage not from scratch
    Reuse a verified local MP4 when only upload failed
    Query the saved stable output ID before any upload retry
    Retry the upload against the same ID so nothing duplicates
    Increment attempt and enforce the maximum
    Record failures atomically and retain all artifacts
    Require an explicit documented retry marker to requeue
    Release the lock in a finally block
END
  }
  ```
- **Comprehensive task explanation**: Resumability is the whole point of the Drive design's "local reusable artifacts + stable upload IDs" idea — this task implements it concretely. The two overlap defenses (file lock + scheduler setting) guard against manual runs colliding with triggered runs. Dependency: Task 11.
- **Verification**: tests simulate upload-failure-then-retry (no re-render, same Drive ID), an orphaned workspace (logged, untouched), and lock contention (second instance exits immediately); `python -m unittest tests.test_run_drive_queue -v` passes; contract documents the retry marker and max-attempts values.

## Task Title: Run Gemini/Langflow quota feasibility spike before coding Phase 2
**Status (2026-11-17): MANUAL REQUIRED.** `DOCS/spikes/README.md` defines the evidence and redaction contract. A real configured Gemini/Langflow call is required; no provider result was fabricated.
- **Task description**: Answer the open questions the audit flagged before any quota code is written. This is a documented experiment, not production code.
- **Location**: spike notes appended to `DOCS/automation-contract.md`; temporary script under `DOCS/spikes/`.
- **Expected outcome**: Confirmed the official model name is available for the actual key via the models list API; measured real input tokens with `countTokens` on the complete request (instructions + schema + content — never character guesses); recorded the project's actual current limits from AI Studio; determined definitively whether Langflow responses expose Gemini usage metadata; chose and documented either flow-instrumentation or direct-Gemini orchestration for the reconciliation path. Findings cover RPM/TPM/RPD, cooldown behavior, reservation strategy, stale-reservation release, and the explicit limitation that the local ledger cannot see unrelated usage.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    List models for the actual API key and confirm the target model
    Send the complete planned request to countTokens and record the count
    Record the actual project limits from the AI Studio console
    Make one real Langflow dev call and inspect the response for usage fields
    If usage metadata is absent decide flow instrumentation or direct API
    Document the reservation reconciliation and stale-release rules
    Record that the ledger cannot see usage outside this automation
    Record that the 80 percent gate is policy not a provider guarantee
END
  }
  ```
- **Comprehensive task explanation**: The audit found the quota design is the weakest link — it assumes facts not yet proven. A real `countTokens` call gives the true reservation size; a real Langflow call answers whether actual usage can be reconciled or whether the flow must return `usage_metadata` explicitly. Do not write Phase 2 code until the findings are in the contract. Dependencies: Task 1, Task 3 (env names), real dev credentials.
- **Verification**: `Select-String -Path DOCS/automation-contract.md -Pattern 'countTokens|usage|RPM|reconcil'` shows recorded findings; the chosen orchestration approach (flow instrumentation vs direct API) is named; the spike outputs are committed under `DOCS/spikes/` with secrets redacted.

## Task Title: Implement Gemini quota ledger and gate
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** `countTokens`, transactional 80-percent policy reservation, reconciliation/release helpers, missing-config hold, and tests are implemented. Real usage-metadata reconciliation awaits the manual spike.
- **Task description**: Build `gemini_quota.py` — a transactional SQLite check-and-reserve gate driven by `countTokens`, per the spike findings.
- **Location**: new `gemini_quota.py`; extends `job_store.py` reservations table; `tests/test_gemini_quota.py`.
- **Expected outcome**: One transaction checks configured limits for the specific model/project and records a reservation before any call; rolling RPM/TPM/RPD windows; `countTokens` drives input estimates; all planned attempts for a job reserve at once; actual usage reconciles against reservations when metadata exists (per Task 13's decision); stale reservations release after a configured TTL; missing config or ledger holds the job safely in quota-hold — never a silent bypass; no provider retry without an existing reservation. The 80% threshold is documented as policy only, not a guarantee of provider acceptance or free cost.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Load the configured model and project specific limits
    Estimate input tokens with countTokens on the full request
    In one transaction check rolling windows and insert a reservation
    If limits or ledger are unavailable hold the job in quota-hold
    Reserve for every planned attempt before the first call
    After each call reconcile actual usage when metadata exists
    Release stale reservations after the configured TTL
    Never issue a provider retry without a live reservation
END
  }
  ```
- **Comprehensive task explanation**: The single-transaction check+insert is what prevents two overlapping claims from both passing under a near-full window. Limits live in config, not code, because Google changes them per model/tier — values come from the spike, not defaults. Tests use a controlled clock plus one real dev acceptance call per Task 13's findings; no fabricated quota data. Dependencies: Tasks 4, 13.
- **Verification**: `python -m unittest tests.test_gemini_quota -v` passes (controlled-clock window rollover, concurrent reservation race, stale release, hold-on-missing-config); a real dev `countTokens`+generate sequence reconciles recorded vs actual tokens within the documented tolerance; `Select-String -Path gemini_quota.py -Pattern '80|policy'` shows the policy comment.

## Task Title: Build and version the real Langflow scene-planner contract
**Status (2026-11-17): IMPLEMENTED TEMPLATE; MANUAL EXPORT REQUIRED.** The client, raw-response preservation, nested parser, strict validation, prompt hash, and schema template exist. A genuine secret-free flow export and captured sanitized response require the manual spike.
- **Task description**: Pin the Langflow flow as versioned, testable contract: exported flow JSON (sans secrets) in the repo, structured output schema, exact request/response shape, and a real-endpoint test.
- **Location**: new `langflow_client.py`; `DOCS/langflow-flow.json` (exported, secret-free); contract schema section; `tests/test_langflow_client.py`.
- **Expected outcome**: Client posts paragraph-indexed prose + artwork inventory to `/api/v1/run/{flow_id}` with configured model/temperature/max-output settings; response extraction walks the documented nested path to structured JSON; the flow version and prompt hash are recorded per job; strict scene-plan validation (Task 5) runs on output; raw response is saved to disk before validation. Unit tests parse a sanitized captured real response (permitted only after a genuine successful dev call); the real endpoint test validates against the dev flow.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Load flow ID base URL and API key from environment
    Build the request with paragraphs and artwork inventory
    Call the real flow endpoint with a timeout
    Save the raw response body to the job workspace
    Extract the structured output from the documented nested path
    Validate the plan with timeline_validator scene-plan rules
    Record the flow version and prompt hash in job state
    Return the validated plan or hold the job with the raw output kept
END
  }
  ```
- **Comprehensive task explanation**: Saving raw output before validation is the key debug property from the Gemini PDF — when a plan fails validation, the raw response is evidence. The exported flow JSON makes prompt/schema changes reviewable diffs; record its version/hash per job so "which prompt made this plan" is answerable later. Dependencies: Tasks 5, 13.
- **Verification**: `python -m unittest tests.test_langflow_client -v` passes parser tests on the captured sanitized fixture; the marked real test (`-k Integration`) runs only when `LANGFLOW_BASE_URL`/`LANGFLOW_FLOW_ID`/`LANGFLOW_API_KEY` (Task 3 names, substitute configured values) are set and returns a valid plan; raw output file exists after the run.

## Task Title: Generate scene audio and cumulative timeline (Phase 2)
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** Verbatim paragraph extraction, per-scene Kokoro synthesis, measured cumulative timing, concatenation, and strict validation are implemented. Real multi-scene acceptance needs FFmpeg and the manual Doc-export check.
- **Task description**: Turn a validated scene plan into a measured-durations timeline, replacing hand-authoring.
- **Location**: new `scene_audio.py` (or cohesive functions in `render_chapter.py`); `tests/test_scene_audio.py`.
- **Expected outcome**: For each planned scene, extract the original prose verbatim by paragraph range, synthesize one Kokoro clip, probe its real duration with `media_probe`, concatenate clips in order into the chapter narration, accumulate `start`/`end` cumulatively, compensate only for 30fps frame rounding, reject larger drift, and write a generated `video-timeline.json` that passes `timeline_validator`. The native Google Doc export's paragraph behavior is verified with a real exported dev document so paragraph indexes align with what the planner saw.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Extract each scene paragraph range verbatim from the exported text
    Synthesize one Kokoro clip per scene into the workspace
    Probe every clip for its real duration
    Concatenate the clips in order into one narration file
    Accumulate start and end from measured durations
    Compensate only for frame rounding and reject larger drift
    Write the generated video-timeline.json
    Validate it with the same validator as authored timelines
    Hand the validated timeline to the normal render path
END
  }
  ```
- **Comprehensive task explanation**: Measuring clips removes the fragility of hand-timed scenes; cumulative accumulation guarantees contiguity by construction. The Doc-export check matters because paragraph indexing must be identical between the Langflow prompt and the extraction here — test it once against a real exported document. Dependencies: Tasks 5, 7, 8, 10 (export), 15.
- **Verification**: integration test synthesizes 2–3 real short scenes producing a contiguous generated timeline whose sum matches the concatenated audio within one frame; the generated file passes `timeline_validator`; `python -m unittest tests.test_scene_audio -v` passes.

## Task Title: Archive Gemini outputs and upload verified chapter artifacts
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** Raw output is persisted before validation, reused locally, uploaded with a stable ID, and recorded with final artifacts. Real service acceptance remains manual.
- **Task description**: Wire the archival/confirmation half of the Drive design: raw planner output and final artifacts are uploaded with stable IDs and confirmed metadata — integrating Tasks 10–16 rather than duplicating clients.
- **Location**: `run_drive_queue.py` orchestration; configured Drive Gemini Outputs folder; state records.
- **Expected outcome**: Raw `gemini-output.json` is saved locally first, then uploaded via stable generated ID to the configured Gemini Outputs path keyed by job fingerprint/export type; upload retry is independent of any new Gemini call; only a validated plan becomes `scene-plan.json`; the final MP4 upload is confirmed (ID/name/size/checksum where available) and all output Drive IDs land in job state.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Save the raw Gemini response locally once
    Upload it to the Gemini Outputs folder with a stable generated ID
    Retry that upload independently without any new Gemini call
    Promote only a validated plan to scene-plan.json
    Verify the final MP4 with media_probe
    Upload it to Finished Videos with its stable generated ID
    Confirm uploaded parent ID name size and checksum
    Record every output Drive ID in the job state
END
  }
  ```
- **Comprehensive task explanation**: "Archive raw, promote validated" keeps a clean separation: the raw file is forensic evidence; `scene-plan.json` is the contract-compliant artifact. Stable IDs mean re-runs overwrite rather than duplicate — combined with Task 12's query-before-retry, Drive stays clean. Dependencies: Tasks 10–16.
- **Verification**: a Phase-2 integration run leaves `gemini-output.json` locally and remotely under the same stable ID; forcing an upload failure then re-running retries the upload without a second planner call (assert the Gemini call count); job state lists all output IDs.

## Task Title: Implement optional vertical teaser (Phase 3)
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** Explicit opt-in, required authored teaser inputs, separate narration/timeline/render/verification, and fail-the-job policy are implemented. Real render acceptance needs FFmpeg.
- **Task description**: Add an opt-in teaser render as a separate verified artifact — never a silent extra.
- **Location**: `render_chapter.py`, `run_drive_queue.py`, job inputs, contract.
- **Expected outcome**: Job opts in explicitly via its declared job metadata. Teaser source is authored input or a real Langflow excerpt (no fabricated scripts). Teaser gets its own audio, timeline, render at the portrait teaser dimensions, `media_probe` verification, and stable upload IDs. The Task 1 failure policy (fail job vs complete-with-warning) is implemented exactly; a requested teaser is never silently omitted.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Read the job metadata for an explicit teaser opt-in
    If not requested finish after the chapter upload
    Obtain the teaser script from the approved source
    Synthesize teaser narration and validate its timeline
    Render the teaser at the portrait teaser dimensions
    Verify the teaser output with media_probe
    Apply the contracted failure policy on teaser failure
    Upload with stable IDs and record them in state
END
  }
  ```
- **Comprehensive task explanation**: Teaser multiplies render time and adds an editorial-source question, which is why it waits for Phase 3. The failure policy is whatever Task 1 decided — implement it literally. Dependencies: Tasks 8, 11, and optionally 15-17 when teaser planning uses Langflow.
- **Verification**: a job without opt-in produces only the chapter; an opted-in job produces a second verified artifact; a forced teaser failure follows the documented policy exactly; tests cover all three paths.

## Task Title: Register and validate Windows Task Scheduler
**Status (2026-11-17): SCRIPTS COMPLETE; MANUAL REGISTRATION REQUIRED.** Register, status, and unregister scripts are committed. Registration and scheduled-account E2E intentionally were not performed automatically.
- **Task description**: Register the five-minute trigger only after the Drive queue has passed a manual end-to-end run.
- **Location**: new `DOCS/register-task.ps1`, `DOCS/unregister-task.ps1`, `DOCS/task-status.ps1` (or equivalent XML); project root as working directory.
- **Expected outcome**: Standalone editable scripts register/uninstall/status the task: absolute `.venv\Scripts\python.exe` + `run_drive_queue.py --once`, `Start in` = project root, 5-minute repetition, `Do not start a new instance`, explicit scheduled-account notes, documented network/awake/power behavior. Manual validation covers: no-work run, one real Drive job, two jobs across two runs, upload-retry resumption, auth-attention surfacing, quota-hold surfacing, Last Run Result, and logs.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Confirm run_drive_queue --once has passed manually end-to-end
    Write registration with absolute python and script paths
    Set the working directory to the project root
    Configure the five-minute repeating trigger
    Set the do-not-start-a-new-instance policy
    Document account network awake and power requirements
    Register the task and record uninstall and status commands
    Run it once with no work and confirm clean exit
    Let it claim one real Drive job
    Stage two jobs and confirm one completes per run
    Confirm overlap suppression auth-attention and quota-hold surface correctly
    Verify Last Run Result and job logs for every outcome
END
  }
  ```
- **Comprehensive task explanation**: Scripting registration makes it reviewable and repeatable — a PDF screenshot guide cannot be diffed. The two-layer overlap defense (scheduler setting + Task 12 file lock) is verified by triggering during a running instance. The scheduled account must independently pass Task 2's checks and have read access to the Task 3 secrets directory. Dependencies: Tasks 9, 11, 12.
- **Verification**: `.\DOCS\register-task.ps1` exits 0; `Get-ScheduledTask` lists it; `schtasks /Run /TN "<name from the script>"` then `Get-ScheduledTaskInfo` reports LastRunResult 0 on no-work; a staged Drive job completes through the task; `.\DOCS\unregister-task.ps1` removes it cleanly.

## Task Title: Complete E2E tests, reconcile five PDFs, and release
**Status (2026-11-17): AUTOMATED PORTION COMPLETE.** Unit suite, five regenerated PDFs, generator, external Mermaid sources, clean extraction, and glyph checks are complete. Full render/cloud/scheduler tiers, scratch/media policy approval, and commit/release remain manual.
- **Task description**: Finish the test matrix, bring all documentation in line with the implemented system, and prepare the release.
- **Location**: `tests/`; `DOCS/` (all five PDFs + new generator scripts); `DOCS/ChangeLog.md`; repository root.
- **Expected outcome**: Test tiers — fast unit (always), local integration (needs `.venv`/FFmpeg), real dev-service (needs env config), long full-render (manual). All named failure cases covered: no work, partial job, claim, happy paths (authored and generated), invalid timeline/plan, missing image, TTS failure, FFmpeg failure, probe failure, upload failure+resume, auth-attention, quota-hold, retry, duplicate prevention, two queued jobs. All five PDFs regenerated from committed generator sources with embedded `.mmd` files externalized, glyph corruption fixed, current-vs-planned labels, correct scheduler entry point, and cloud trust boundaries documented. Scratch files (`hello_world_ricardo.cpp`, `test.exe`, `mp4-template.json`) and the generated-media policy decided with explicit approval; changelog updated; only intended files committed.
- **Implementation pseudocode in natural language**:
  ```text
  {
START
    Complete the test matrix across all named failure cases
    Separate fast local real-dev and long-render test tiers
    Extract embedded Mermaid sources into committed .mmd files
    Write generator scripts for every one-page PDF
    Update the technical guide for Kokoro cloud boundaries tests and orchestration
    Label current versus planned components in every document
    Correct the scheduler entry point and fix text extraction corruption
    Regenerate all five PDFs and verify clean extraction
    Decide scratch files and media policy with explicit approval
    Update the changelog run diff checks and commit only intended files
END
  }
  ```
- **Comprehensive task explanation**: This is the release gate. Every earlier task's contract text now becomes documentation truth — the guide must describe the Drive control plane, OAuth boundary, quota ledger semantics, and current test suite, with Phase 2/3 features marked by status. No fake production data anywhere in tests; real dev services validate provider behavior. Dependencies: all prior tasks.
- **Verification**: `python -m unittest discover -s tests -p "test_*.py" -v` green (integration/dev tiers skip cleanly when prerequisites absent); each generator script exits 0 and reproduces its committed PDF; pypdf text extraction of regenerated PDFs shows no replacement-glyph artifacts; `git diff --check` clean; `git status` contains only intended changes; `DOCS/ChangeLog.md` has the release entry.

## Definition of Done

- [ ] Human-approved architecture/privacy/OAuth/quota/dimension contract exists and is signed off.
- [ ] A fresh PowerShell window and the scheduled account both resolve `ffmpeg -version` and `ffprobe -version`.
- [ ] A Phase 0 local staged job succeeds end-to-end; no-work and partial-job behavior are safe.
- [ ] A Drive folder snapshot is stable; remote edits during a run never mix into it.
- [ ] Stable output IDs mean reruns create no Drive duplicates.
- [ ] Upload failures resume without re-rendering or re-calling Gemini.
- [ ] An OAuth refresh failure surfaces as auth-attention, never an interactive scheduler hang.
- [ ] Quota ledger check/reserve/reconcile works and the 80% threshold is documented as policy only.
- [ ] Raw Gemini output is saved once and reused; an invalid plan is held, never rendered.
- [ ] Two Drive jobs complete across two separate `--once` runs with no duplicate work.
- [ ] The scheduled task repeats every five minutes without overlapping instances.
- [ ] Phase 2 and Phase 3 remain optional later gates, not MVP blockers, until explicitly enabled.
- [ ] All five PDFs match the implementation, extract cleanly, and have editable sources committed.
- [ ] All tests pass and `git status` contains only intentional artifacts.
