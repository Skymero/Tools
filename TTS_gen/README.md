# Text to Speech Converter

A simple Python tool that converts text files to MP3 audio using the Google Text-to-Speech (gTTS) library.

## Features

- Convert any text file to MP3 audio
- Support for multiple languages
- Simple command-line interface
- Error handling for missing files and empty content
- Offline Kokoro narration with strict WAV output
- Strict authored/generated timeline validation
- Isolated chapter rendering with FFprobe acceptance checks
- Durable SQLite job state and idempotent Google Drive queue processing
- Optional quota-gated Gemini/Langflow scene planning
- Scripted Windows Task Scheduler registration

## Automation status

The automation code is implemented, but this checkout is not operational until
the manual prerequisites and service acceptance checks in
`DOCS/automation-contract.md` are complete. In particular, FFmpeg and FFprobe
are not currently available on PATH for this account. Unit tests never contact
Drive, Gemini, or Langflow.

The supported entry points are:

```powershell
# Local Phase 0: render exactly one frozen staged job
.\.venv\Scripts\python.exe .\render_chapter.py --job-dir .\work\example

# Phase 1+: process at most one eligible Drive folder
.\.venv\Scripts\python.exe .\run_drive_queue.py --once

# Test without contacting external services
python -m unittest discover -s tests -p "test_*.py" -v
```

Copy `.env.example` and `automation-config.example.json` for the complete
configuration surface. Secrets belong under
`%LOCALAPPDATA%\TTS_gen\secrets`, outside the repository. Gemini/Langflow
planning remains disabled unless `ENABLE_GEMINI_PLANNING=true` and the manual
feasibility spike has been recorded.

## Installation

1. Install Python 3.6 or higher if not already installed
2. Install the required dependency:

```bash
pip install -r requirements.txt
```

Or install directly:

```bash
pip install gTTS
```

## Usage

### Basic Usage

Convert a text file to MP3 (output file will have same name as input with .mp3 extension):

```bash
python text_to_speech.py input.txt
```

### Specify Output File

Convert with custom output filename:

```bash
python text_to_speech.py input.txt output.mp3
```

### Specify Language

Convert with a specific language code:

```bash
python text_to_speech.py input.txt output.mp3 en
```

Common language codes:
- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `zh` - Chinese
- `ja` - Japanese
- `ko` - Korean

## Example

Create a text file named `sample.txt` with your content, then run:

```bash
python text_to_speech.py sample.txt
```

This will create `sample.mp3` in the same directory.

## Kokoro neural narration (optional)

`text_to_speech_kokoro.py` is an optional offline alternative to gTTS that uses
the Kokoro-82M neural TTS model running locally on CPU. It produces
higher-quality narration than the OS voices and never sends your text to a
third-party service. Defaults: voice `af_heart`, language `en-us`, speed `1.0`,
WAV output, CPU device, 24 kHz mono PCM16 audio.

### Setup (Windows PowerShell)

Kokoro 0.9.4 requires Python 3.10–3.12. Create a dedicated virtual
environment and install the base plus optional dependencies:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install -r requirements-kokoro.txt
ffmpeg -version
ffprobe -version
```

eSpeak NG (x64) is required for Kokoro's phonemizer fallback; install it from
https://github.com/espeak-ng/espeak-ng/releases before running synthesis.

The first synthesis run downloads the model and voice weights from
`hexgrad/Kokoro-82M`, so an internet connection is needed once; subsequent
runs are fully offline.

### Usage

```powershell
python text_to_speech_kokoro.py INPUT [OUTPUT] [--voice VOICE] [--lang LANGUAGE] [--speed SPEED]
```

Examples:

```powershell
# Default voice (af_heart) to WAV — no ffmpeg needed
.\.venv\Scripts\python.exe text_to_speech_kokoro.py sample.txt sample-heart.wav

# A different Kokoro voice
.\.venv\Scripts\python.exe text_to_speech_kokoro.py sample.txt sample-bella.wav --voice af_bella

# MP3 output (requires ffmpeg on PATH)
.\.venv\Scripts\python.exe text_to_speech_kokoro.py sample.txt sample-heart.mp3

# Check the produced duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 sample-heart.wav
```

WAV output needs no external tools; MP3 output requires `ffmpeg` on PATH.
Blank lines and punctuation in the source text shape Kokoro's phrasing —
short paragraphs with normal sentence punctuation narrate most naturally.
Because Kokoro's pace differs from gTTS, `video-timeline.json` scene durations
must be regenerated from the Kokoro audio before rendering a narrated video.

## Requirements

- Python 3.6+
- gTTS library
- Internet connection (gTTS requires internet to access Google's TTS API)
- Optional, for `text_to_speech_kokoro.py`: Python 3.10–3.12, the packages in
  `requirements-kokoro.txt` (kokoro, soundfile, misaki[en]), eSpeak NG x64,
  and ffmpeg on PATH only when writing MP3 output

## Error Handling

The script handles the following errors:
- Missing input file
- Empty input file
- Network connectivity issues
- Invalid language codes

`text_to_speech_kokoro.py` additionally reports: unsupported output extension
(only `.wav`/`.mp3`), missing output directory, voice/language mismatches
(the voice's first letter must match the selected language), missing ffmpeg
for MP3 output, missing Kokoro dependencies, and synthesis runs that produce
no audio. All errors exit 1 with a concise stderr message.

## Notes

- The conversion requires an active internet connection as gTTS uses Google's online TTS service
- Large text files may take longer to process
- The output MP3 quality depends on Google's TTS service



# Google drive folder structure

TTS_gen/
  Incoming/
    botany-diaries-ch01/
      chapter.txt
      video-timeline.json
      images/
        BD-CH1-img-1.png
        BD-CH1-img-2.png

    botany-diaries-ch02/
      chapter.txt
      video-timeline.json
      images/
        BD-CH2-img-1.png
        BD-CH2-img-2.png

    botany-diaries-ch03/
      chapter.txt
      video-timeline.json
      images/
        BD-CH3-img-1.png