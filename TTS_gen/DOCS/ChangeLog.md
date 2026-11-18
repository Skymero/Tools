# TTS_gen Change Log

## 2026-11-17 - Chapter automation implementation

- Added the approved automation/privacy/acceptance contract and configuration
  examples with external secret storage.
- Added strict timeline and scene-plan validation, FFprobe media verification,
  isolated FFmpeg rendering, and a single staged-job worker.
- Added durable SQLite jobs/files/quota reservations and deterministic Drive
  fingerprints.
- Added noninteractive Drive OAuth behavior, Drive primitives, one-job queue,
  stable upload IDs, explicit retry, maximum attempts, orphan reporting, and a
  process lock.
- Added opt-in Gemini `countTokens`, local quota policy, Langflow raw-response
  preservation, measured scene audio/timeline generation, and optional teaser
  rendering.
- Added repeatable Windows Task Scheduler register/status/unregister scripts.
- Regenerated all five PDFs from committed source and externalized Mermaid
  diagrams.
- Expanded the local suite from 11 to 32 passing tests.

Manual release gates remain: install FFmpeg/FFprobe; run local render, OAuth,
Drive, Gemini/Langflow, and scheduler acceptance; decide scratch/generated-media
policy; and create the release commit.
