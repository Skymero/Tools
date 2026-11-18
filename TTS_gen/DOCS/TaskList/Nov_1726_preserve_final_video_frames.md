# Action Item
- Prevent FFmpeg's `-shortest` mux behavior from dropping valid final video
  frames after pre-mux duration validation has already passed.

## Task Title: Mux validated streams without a second shortening rule
- **task description**: Remove `-shortest` from the final stream-copy/AAC mux.
- **Location**: `create_mp4.py`; real acceptance workspace under
  `work/manual-acceptance/`
- **Expected outcome**: The final H.264 and AAC streams remain within the
  validator's one-frame duration contract instead of losing two video frames.
- **implementation pseudocode in natural language**:
  - Validate the concatenated video duration against narration first.
  - Refuse the render if that pre-mux mismatch exceeds one frame.
  - Mux the already accepted video stream and encoded AAC narration without
    asking FFmpeg to independently truncate at an audio packet boundary.
  - Probe the finished MP4 and require stream duration agreement.
- **comprehensive task explanation**: The real 20.325-second acceptance render
  passed the pre-mux duration check, but `-shortest` produced a 20.266667-second
  video stream beside 20.325-second AAC - a 0.058333-second loss. Removing the
  redundant truncation preserves the validated 30 fps frame sequence.

## Status
- [x] Implemented; real acceptance rerun required.
