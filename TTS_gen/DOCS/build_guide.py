"""Build the TTS_gen technical guide PDF with reportlab."""
import textwrap
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, Image, Preformatted, PageBreak,
                                KeepTogether)

OUT = r"C:\Users\ricky\Tools\TTS_gen\DOCS\TTS_gen_Technical_Guide.pdf"
DIAG = r"C:\Users\ricky\Tools\TTS_gen\DOCS\diagrams"

styles = getSampleStyleSheet()
H1 = ParagraphStyle('H1x', parent=styles['Heading1'], fontSize=18, spaceBefore=18, spaceAfter=8, textColor=colors.HexColor('#1a2a4a'))
H2 = ParagraphStyle('H2x', parent=styles['Heading2'], fontSize=14, spaceBefore=14, spaceAfter=6, textColor=colors.HexColor('#23406e'))
H3 = ParagraphStyle('H3x', parent=styles['Heading3'], fontSize=11.5, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor('#33507f'))
BODY = ParagraphStyle('Bodyx', parent=styles['BodyText'], fontSize=9.5, leading=13.5, spaceAfter=6)
SMALL = ParagraphStyle('Smallx', parent=BODY, fontSize=8.5, leading=11.5)
CELL = ParagraphStyle('Cellx', parent=BODY, fontSize=8, leading=10.5, spaceAfter=0)
CELLH = ParagraphStyle('CellHx', parent=CELL, textColor=colors.white, fontName='Helvetica-Bold')
CODE = ParagraphStyle('Codex', parent=styles['Code'], fontName='Courier', fontSize=7.5, leading=9.5, backColor=colors.HexColor('#f4f4f4'), borderPadding=6, spaceAfter=8, leftIndent=4)
TITLE = ParagraphStyle('Titlex', parent=styles['Title'], fontSize=24, leading=30, spaceAfter=12)
CAP = ParagraphStyle('Capx', parent=SMALL, alignment=1, textColor=colors.HexColor('#555555'), spaceBefore=2, spaceAfter=10)

story = []

def h1(t): story.append(Paragraph(t, H1))
def h2(t): story.append(Paragraph(t, H2))
def h3(t): story.append(Paragraph(t, H3))
def p(t): story.append(Paragraph(t, BODY))
def ps(t): story.append(Paragraph(t, SMALL))
def cap(t): story.append(Paragraph(t, CAP))

def code(txt, width=92):
    out = []
    for line in txt.strip('\n').split('\n'):
        if len(line) <= width:
            out.append(line)
        else:
            indent = len(line) - len(line.lstrip())
            wrapped = textwrap.wrap(line, width=width,
                                    subsequent_indent=' ' * (indent + 4),
                                    break_long_words=False, break_on_hyphens=False)
            out.extend(wrapped or [line])
    story.append(Preformatted('\n'.join(out), CODE))

def table(headers, rows, widths):
    data = [[Paragraph(h, CELLH) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c), CELL) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#23406e')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef2f8')]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#b9c4d6')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))

def img(path, max_w=6.6*inch, max_h=8.6*inch):
    from PIL import Image as PILImage
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(max_w / w, max_h / h)
    story.append(Image(path, width=w*scale, height=h*scale))

PAGE_W = 7.0 * inch  # usable width roughly

# ============================== COVER ==============================
story.append(Spacer(1, 2 * inch))
story.append(Paragraph('TTS_gen', TITLE))
story.append(Paragraph('Technical Guide — Text-to-Speech & Narrated Video Pipeline', H2))
story.append(Spacer(1, 0.3 * inch))
p('Project root: <font face="Courier">C:\\Users\\ricky\\Tools\\TTS_gen</font>')
p('This guide describes a small but complete content-production pipeline: four Python '
  'command-line utilities that convert text files into MP3 narration (online via Google '
  'TTS or offline via the OS speech engine), translate scripts into Spanish and Portuguese, '
  'and assemble narrated MP4 slideshows with Ken Burns-style motion effects using ffmpeg. '
  'It is written so a new developer can configure, run, verify, extend, and troubleshoot '
  'the project without relying on undocumented tribal knowledge.')
p('All statements in this document are grounded in the repository source files; where a '
  'behavior is inferred rather than explicit in code, it is labelled as such.')
story.append(PageBreak())

# ============================== 1. OVERVIEW ==============================
h1('1. Project Overview')
p('TTS_gen is a personal tooling project for producing narrated video chapters from written '
  'fiction. The canonical production example in the repository is "The Botany Diaries" '
  'chapter 1: a narration script (<font face="Courier">botany-diaries-ch1.txt</font>) is '
  'synthesized to <font face="Courier">botany-diaries-ch1.mp3</font> (43 MB, ~15 minutes), '
  'then combined with fourteen illustrated PNG panels and a scene timeline to produce '
  '<font face="Courier">output.mp4</font>, a 1080x1920 portrait video suitable for '
  'shorts/reels distribution.')
p('The project is deliberately simple: no build system, no package layout, no test suite, '
  'no configuration files. Each script is a self-contained CLI entry point that validates '
  'its inputs, performs one transformation, writes an artifact, and exits 0/1. Understanding '
  'the project means understanding the four scripts and the timeline JSON contract that '
  'binds narration, imagery, and timing.')

h2('1.1 Repository map')
table(['Path', 'Kind', 'Role in the system'],
      [['text_to_speech.py', 'Python CLI', 'Online TTS. Reads a .txt file, calls Google TTS via gTTS, saves .mp3.'],
       ['text_to_speech_offline.py', 'Python CLI', 'Offline TTS. Uses pyttsx3 -> OS speech engine (SAPI5 on Windows). Supports voice/rate/volume flags and --list-voices.'],
       ['translate_text.py', 'Python CLI', 'Translates a .txt file to Spanish and Portuguese via deep-translator GoogleTranslator; writes *_spanish.txt and *_portuguese.txt.'],
       ['create_mp4.py', 'Python CLI', 'Video assembly. ffmpeg-python pipeline: per-scene image segments with motion effects, concat, duration matching, audio mux.'],
       ['requirements.txt', 'Config', 'Pinned deps: gTTS==2.5.1, deep-translator==1.11.4, pyttsx3==2.90, ffmpeg-python==0.2.0.'],
       ['video-timeline.json', 'Data contract', 'Scene list consumed by create_mp4.py: image, start/end seconds, motion, intensity.'],
       ['video-editing-timeline.md', 'Docs', 'Human-authored editorial plan mapping images to narrative beats; the JSON timeline was derived from this table.'],
       ['Chapter1-imgs/', 'Assets', 'Fourteen BD-CH1-img-*.png illustrations (~1.1-1.5 MB each) referenced by the timeline.'],
       ['botany-diaries-ch1.txt / .mp3', 'Assets', 'Chapter narration source and its synthesized audio (the production input/output pair).'],
       ['botany-diaries-trailer.txt', 'Asset', 'Shorter trailer script, presumably for a teaser video (no trailer MP3/MP4 is committed).'],
       ['sample.txt / sample.mp3', 'Fixture', 'Minimal smoke-test pair for text_to_speech.py.'],
       ['output.mp4', 'Artifact', 'Committed build output (55 MB) — evidence the pipeline ran end-to-end at least once.'],
       ['mp4-template.json', 'Stub', 'Empty file (0 bytes). Placeholder for a future reusable timeline template; currently unused.'],
       ['hello_world_ricardo.cpp / test.exe', 'Scratch', 'Unrelated C++ learning artifact and its compiled binary; not part of the pipeline.'],
       ['README.md', 'Docs', 'User-facing docs for text_to_speech.py only; does not cover the other three scripts.']],
      [1.55*inch, 0.8*inch, 4.65*inch])

# ============================== 2. SETUP ==============================
h1('2. Environment Setup and Dependencies')
h2('2.1 Prerequisites')
table(['Requirement', 'Version', 'Why', 'How to verify'],
      [['Python', '3.6+ (3.10 confirmed on this machine)', 'All scripts are stdlib + pip packages.', 'python --version'],
       ['pip packages', 'see requirements.txt', 'gTTS, deep-translator, pyttsx3, ffmpeg-python.', 'pip list | findstr /i "gtts deep pyttsx ffmpeg"'],
       ['ffmpeg binary', 'any recent build, on PATH', 'create_mp4.py shells out through ffmpeg-python; the wheel does NOT bundle ffmpeg.', 'ffmpeg -version'],
       ['ffprobe', 'bundled with ffmpeg', 'Used to probe audio/video durations in create_mp4.py.', 'ffprobe -version'],
       ['Internet connection', 'n/a', 'gTTS and GoogleTranslator are online services. The pyttsx3 path is the offline fallback.', 'ping translate.google.com'],
       ['OS speech voices', 'SAPI5 voices on Windows', 'pyttsx3 delegates synthesis to installed system voices.', 'python text_to_speech_offline.py --list-voices']],
      [1.3*inch, 1.35*inch, 2.8*inch, 1.55*inch])
h2('2.2 Install')
code('''cd C:\\Users\\ricky\\Tools\\TTS_gen
pip install -r requirements.txt

# ffmpeg is an external dependency. On Windows, either:
#   winget install ffmpeg          (or)   choco install ffmpeg
# then verify:
ffmpeg -version
ffprobe -version''')
p('Note: the environment where this guide was generated did not have ffmpeg on PATH, yet '
  'a committed output.mp4 exists — so at least one machine in the project history had a '
  'working ffmpeg install. Treat "ffmpeg on PATH" as a hard precondition for create_mp4.py; '
  'the script fails late (first ffmpeg invocation) rather than at startup if it is missing.')
h2('2.3 Configuration surface')
p('There are no environment variables, .env files, or config modules. All behavior is '
  'parameterized through command-line arguments and two hard-coded constant blocks:')
table(['Constant / parameter', 'Location', 'Value', 'Effect'],
      [['OUTPUT_WIDTH', 'create_mp4.py:13', '1080', 'Portrait frame width for every scene.'],
       ['OUTPUT_HEIGHT', 'create_mp4.py:14', '1920', 'Portrait frame height (9:16, shorts/reels format).'],
       ['OUTPUT_FPS', 'create_mp4.py:15', '30', 'Frame rate for image loops and zoompan filters.'],
       ['temp_dir', 'create_mp4.py:87', "'temp_segments'", 'Working directory for intermediate mp4s; created under CWD.'],
       ['slow=False', 'text_to_speech.py:45', 'False', 'Normal gTTS speech rate.'],
       ['crf=23, preset=medium', 'create_mp4.py:165-166', 'x264 defaults', 'Quality/speed tradeoff for all encodes.'],
       ['audio_bitrate', 'create_mp4.py:219', "192k", 'AAC bitrate in the final mux.']],
      [1.5*inch, 1.55*inch, 1.35*inch, 2.6*inch])

# ============================== 3. CLI REFERENCE ==============================
h1('3. Command-Line Reference')
h2('3.1 text_to_speech.py — online TTS (gTTS)')
code('''python text_to_speech.py <input_file> [output_file] [language]

# Examples
python text_to_speech.py sample.txt
python text_to_speech.py botany-diaries-ch1.txt botany-diaries-ch1.mp3 en''')
p('Defaults: output file = input basename with .mp3; language = en. The script validates '
  'existence and non-emptiness, prints character count, synthesizes via gTTS at normal '
  'speed, and exits 0 on success. Any failure prints an error and exits 1 — there is no '
  'distinction between exit codes for different failure classes.')
h2('3.2 text_to_speech_offline.py — offline TTS (pyttsx3)')
code('''python text_to_speech_offline.py --list-voices
python text_to_speech_offline.py <input_file> [output_file] [voice_index] [rate] [volume]

# Example: default voice, 150 wpm, 90% volume
python text_to_speech_offline.py input.txt output.mp3 0 150 0.9''')
p('Positional numeric arguments are parsed unconditionally — passing a non-integer voice '
  'index raises ValueError from int() outside the try block, which crashes with a traceback '
  'rather than a friendly error. Voice index is bounds-checked; out-of-range prints a '
  'warning and falls back to the default voice rather than failing.')
h2('3.3 translate_text.py — localization')
code('''python translate_text.py <input_file> [output_spanish] [output_portuguese]

python translate_text.py botany-diaries-ch1.txt
# -> botany-diaries-ch1_spanish.txt, botany-diaries-ch1_portuguese.txt''')
p('Target languages are hard-coded to es and pt. The function returns a results dict; '
  'main() exits 0 only when both translations succeed, so a partial success (Spanish written, '
  'Portuguese network-failed) exits 1 while leaving a file on disk. Callers should check '
  'both the exit code and the output files.')
h2('3.4 create_mp4.py — narrated video assembly')
code('''python create_mp4.py <audio_file> <images_dir> <timeline_file> [output_file]

python create_mp4.py botany-diaries-ch1.mp3 Chapter1-imgs video-timeline.json output.mp4''')
p('Pipeline: validate inputs -> load timeline -> for each scene, loop the image at 30 fps, '
  'letterbox to a 1080x1920 canvas, apply a zoompan/pan/fps filter, encode an H.264 segment '
  'into temp_segments/ -> concatenate segments -> probe audio vs video duration and loop '
  'the video if it is shorter -> mux with AAC 192k audio -> delete all intermediates. '
  'Total wall-clock is dominated by x264 encoding; expect roughly real-time or slower '
  'on a modest machine for a 15-minute output.')

# ============================== 4. ARCHITECTURE ==============================
h1('4. Architecture and System Context')
p('TTS_gen is a single-host, file-centric batch pipeline. There is no server, daemon, '
  'database, queue, or scheduler — the "system" is the composition of four CLI scripts '
  'over the local filesystem, two Google web endpoints, the OS speech stack, and the '
  'ffmpeg subprocess. The trust boundaries are therefore simple but worth stating '
  'explicitly: anything sent to gTTS or GoogleTranslator leaves the machine as plaintext '
  'to a third-party service, and ffmpeg executes with the full privileges of the invoking '
  'user on paths derived from JSON input.')
img(DIAG + r'\d1_architecture.png')
cap('Figure 1 — Principal components and trust boundaries.')
h3('Natural-language pseudocode')
code('''{
START
  Receive a command from the user in PowerShell

  If the user requests online text-to-speech:
    Read the local text file
    Send the text through the gTTS library to the Google TTS service
    Save the returned narration as a local MP3 file

  If the user requests offline text-to-speech:
    Read the local text file
    Send the text to the installed operating-system speech engine through pyttsx3
    Save the generated narration as a local audio file

  If the user requests translation:
    Read the local text file
    Send the text through deep-translator to the Google Translate service
    Save the Spanish and Portuguese translations as local text files

  If the user requests video creation:
    Read the narration MP3, image directory, and timeline JSON
    Ask ffmpeg to render temporary video segments from the images
    Combine the temporary segments with the narration
    Save the completed local MP4 file
END
}''')

h2('4.1 Component-responsibility table')
table(['Component', 'Responsibility', 'Inputs', 'Outputs', 'Trust / credential boundary', 'Source location'],
      [['CLI entry points (main() in each script)', 'Parse argv, map to function call, translate boolean result to exit code.', 'argv', 'exit 0/1, usage text', 'User-local; no privileges beyond the invoking shell.', 'Bottom of each .py file'],
       ['text_to_speech()', 'Validate + read text, synthesize speech, persist mp3.', '.txt path, output path, lang code', '.mp3 file', 'Sends full script text to Google TTS endpoint (unauthenticated, but third-party egress).', 'text_to_speech.py:11'],
       ['text_to_speech_offline()', 'Validate + read text, configure voice/rate/volume, synthesize via OS engine.', '.txt path, output path, voice_index, rate, volume', 'audio file (format = engine default)', 'Fully local; uses installed SAPI5 voices.', 'text_to_speech_offline.py:12'],
       ['list_available_voices()', 'Enumerate and print installed OS voices.', '--list-voices flag', 'stdout list', 'Local.', 'text_to_speech_offline.py:90'],
       ['translate_text() / translate_file()', 'Auto-detect source language, translate to es + pt, write files.', '.txt path, optional output paths', 'two .txt files, results dict', 'Sends full text to Google Translate endpoint.', 'translate_text.py:11, 33'],
       ['fit_to_portrait_canvas()', 'scale (decrease) -> pad (centered, black) -> setsar 1.', 'ffmpeg stream', 'ffmpeg stream', 'Pure filter graph; local.', 'create_mp4.py:18'],
       ['create_video_from_timeline()', 'Orchestrate segment render, concat, duration match, mux, cleanup.', 'mp3, images dir, timeline JSON, output path', '.mp4 + temp_segments/ during run', 'Executes ffmpeg subprocesses; reads attacker-controllable JSON if timeline is untrusted.', 'create_mp4.py:40'],
       ['ffmpeg / ffprobe binaries', 'All media decode/encode/probe work.', 'filter graphs + file paths', 'media files', 'Runs with user privileges; invoked with concat safe=0 so absolute paths are allowed.', 'external dependency'],
       ['video-timeline.json', 'Scene script: the contract binding images to narration time.', 'authored JSON', 'scenes[] consumed at runtime', 'Untrusted input surface; every field is validated only loosely (see 4.3).', 'repo root'],
       ['video-editing-timeline.md', 'Editorial source of truth for the JSON timeline.', 'narrative plan', 'scene table -> JSON', 'Human-authored; the JSON was transcribed from it.', 'repo root']],
      [1.15*inch, 1.5*inch, 1.0*inch, 0.95*inch, 1.35*inch, 1.05*inch])

h2('4.2 Principal data flow')
p('The dominant flow is the chapter pipeline (Figure 8 in the workflow atlas): a .txt '
  'narration is synthesized to .mp3 by whichever TTS path the operator chooses; the mp3, '
  'an image directory, and the timeline JSON converge in create_mp4.py, which emits the '
  'final .mp4. The two Google egress points (TTS, Translate) only ever see script text — '
  'images and audio never leave the machine. The intermediate artifact chain is: '
  'txt -> mp3 -> temp_segments/segment_*.mp4 -> video_only.mp4 -> output.mp4, with all '
  'intermediates deleted on the success path.')
p('A secondary flow is localization: translate_text.py forks the script into es/pt text '
  'files that feed back into text_to_speech.py with the matching language code, enabling '
  'a parallel narrated video per language with no other changes.')

h2('4.3 Evidence ladder')
p('Because the pipeline crosses local code, a subprocess, and third-party web endpoints, '
  '"it worked" can mean several different things. When verifying a run, climb this ladder '
  'rather than trusting the earliest signal:')
table(['Rung', 'Evidence', 'How to obtain it', 'What it does NOT prove'],
      [['1. Local code success', 'Script printed success line and exited 0.', 'echo $LASTEXITCODE (PowerShell)', 'Says nothing about artifact contents.'],
       ['2. Artifact exists', 'Expected .mp3/.txt/.mp4 present on disk.', 'dir / Test-Path', 'File may be empty or truncated.'],
       ['3. Provider acceptance', 'gTTS/Translate returned 2xx (implicit in success path).', 'No code evidence — inferred from success.', 'Does not prove content fidelity.'],
       ['4. Media integrity', 'ffprobe reports expected duration/streams.', 'ffprobe -v quiet -show_format output.mp4', 'Container valid, not watchable quality.'],
       ['5. User-visible outcome', 'Playback shows synced narration + intended motion per scene.', 'Manual review of output.mp4', '—'],
       ['6. Durable confirmation', 'output.mp4 committed in git history (55 MB) exists as prior proof of a full pass.', 'git log -- output.mp4', 'Only proves past, not current, state.']],
      [1.15*inch, 1.9*inch, 2.15*inch, 1.8*inch])

# ============================== 5. ADR ==============================
h1('5. Architecture Decision Record Summary')
p('No ADR documents exist in the repository, so the table below is reconstructed from '
  'implementation evidence. Alternatives marked "possible" were never recorded as rejected; '
  'they are inferred options, not history.')
table(['Decision', 'Current approach', 'Repository evidence', 'Rationale (inferred)', 'Alternatives', 'Tradeoffs', 'Status / risk'],
      [['Online TTS via gTTS', 'Google TTS through the gTTS wrapper library.', 'requirements.txt: gTTS==2.5.1; text_to_speech.py:45.', 'Free, zero credentials, good voice quality vs OS voices.', 'Possible: paid APIs (Azure, Polly, ElevenLabs).', 'No API key to manage, but undocumented endpoint can break or rate-limit.', 'Active. Risk: gTTS depends on an unofficial endpoint; large texts may be chunked/throttled by the service.'],
       ['Offline fallback TTS', 'pyttsx3 -> SAPI5.', 'text_to_speech_offline.py; pyttsx3==2.90.', 'Pipeline must work without internet; also avoids sending text to Google.', 'Possible: local neural TTS (Coqui, Piper).', 'OS voices sound robotic; output container/codec is engine-defined, not guaranteed mp3.', 'Active. Risk: voice list and output format vary across machines — not reproducible.'],
       ['Translation via deep-translator', 'GoogleTranslator, source auto-detect, hard-coded es+pt targets.', 'translate_text.py:26, 76-88.', 'Simplest free translate path for the two languages needed.', 'Possible: argostranslate (offline), DeepL API.', 'No keys; but brittle web-scraping backend and fixed language pair.', 'Active. Risk: hard-coded languages mean editing code to add a locale.'],
       ['ffmpeg-python wrapper', 'Build filter graphs in Python, shell out to ffmpeg.', 'create_mp4.py:10, 115-225.', 'Keeps orchestration in Python while ffmpeg does the heavy lifting.', 'Possible: raw ffmpeg CLI scripts, moviepy.', 'Readable graphs; but ffmpeg-python 0.2.0 is stale and error output is silenced (quiet=True), hiding ffmpeg diagnostics.', 'Active. Risk: quiet=True swallows the stderr you need most when debugging.'],
       ['Portrait 1080x1920 @30fps', 'Hard-coded canvas, letterboxed with black bars.', 'create_mp4.py:13-15, fit_to_portrait_canvas.', 'Targets shorts/reels; letterboxing preserves source aspect.', 'Possible: crop-to-fill, parameterized canvas.', 'Any aspect works without stretching; waste pixels as bars.', 'Active. Risk: constants baked in — landscape output requires a code change.'],
       ['Timeline JSON as scene contract', 'scenes[] with image/start/end/motion/intensity.', 'video-timeline.json; validation at create_mp4.py:77-100.', 'Decouples editorial timing (video-editing-timeline.md) from render code.', 'Possible: EDL formats, in-code scene list.', 'JSON is editable without touching Python; loose schema means typos surface late.', 'Active. Risk: start/end only affect segment duration — scene gaps/overlaps in the timeline are ignored (see 7.4 invariants).'],
       ['Per-segment encode + concat demuxer', 'Render each scene to its own mp4, then concat.', 'create_mp4.py:110-193.', 'Isolates filter graphs per scene; concat demuxer is fast.', 'Possible: single filter_complex graph over all images.', 'Simple mental model; N+1 ffmpeg invocations is slower and temp-heavy.', 'Active. Risk: failed run leaves temp_segments/ behind; cleanup only runs on success.'],
       ['Video looped to match audio', 'If video shorter than audio, concat video with itself ceil+1 times.', 'create_mp4.py:208-211.', 'Guarantees output is never shorter than narration.', 'Possible: fail on mismatch, freeze last frame.', 'Graceful but may visibly loop mid-narration.', 'Active. Risk: a too-short video silently loops — verify scene sum vs audio length before rendering.']],
      [0.95*inch, 1.05*inch, 1.0*inch, 0.95*inch, 0.9*inch, 1.1*inch, 1.05*inch])

# ============================== 6/7. WORKFLOW ATLAS ==============================
h1('6. Execution Lifecycle (State Model)')
p('All four scripts share the same coarse lifecycle; modeling it once clarifies where '
  'every failure in the atlas terminates. The process is a finite batch: argument parse, '
  'input validation, read, provider/engine I/O, write, exit. Every failure path converges '
  'on the same terminal state — print error, return False (or empty results dict), exit 1.')
img(DIAG + r'\d6_state.png')
cap('Figure 2 — Shared script lifecycle. There is no retry, resume, or checkpointing anywhere in the project.')
h3('Natural-language pseudocode')
code('''{
START
  Read the command-line arguments

  If required arguments are missing:
    Display usage instructions
    Exit with a failure status

  Validate every required input

  If an input is missing, empty, or structurally invalid:
    Display the validation error
    Exit with a failure status

  Read the validated input data

  If the selected workflow uses an online provider:
    Send the request to the provider
    If the provider or network fails:
      Display the error
      Exit with a failure status

  Otherwise:
    Process the request with the local speech engine or ffmpeg
    If local processing fails:
      Display the error
      Exit with a failure status

  Write the resulting artifact to disk
  Display a success message
  Exit with a success status
END
}''')
p('Security/integrity invariants of the lifecycle: (a) no output file is written before '
  'input validation passes; (b) failure is always loud on stdout but never leaves partial '
  'mp3s from the gTTS path (save() is atomic-ish at the end), while the video path CAN '
  'leave partial segments in temp_segments/; (c) exit code 1 is the only failure signal — '
  'automation must not distinguish failure classes by exit code alone.')

h1('7. Workflow Atlas')

h2('7.1 Online text-to-speech')
ps('Implemented by text_to_speech() in text_to_speech.py:11-61; CLI wiring at :64-84.')
img(DIAG + r'\d2_tts_sequence.png')
cap('Figure 3 — gTTS synthesis sequence.')
h3('Natural-language pseudocode')
code('''{
START
  Read the input text-file path from the command line
  Use the provided output path or derive an MP3 path from the input filename
  Use the provided language code or default to English

  If the input file does not exist:
    Display a file-not-found error
    Exit with a failure status

  Read the file as UTF-8 text and remove surrounding whitespace

  If the text is empty:
    Display an empty-file error
    Exit with a failure status

  Create a normal-speed gTTS request with the text and language
  Send the text to the Google TTS service
  Receive the generated MP3 audio
  Save the MP3 to the selected output path
  Display a success message
  Exit with a success status
END
}''')
p('Normal behavior: after existence and emptiness checks, the whole file is read into '
  'memory and passed to gTTS in one call; the library tokenizes, issues HTTPS requests to '
  'the Google TTS endpoint, and tts.save() writes the mp3. There is no chunking logic in '
  'the script — gTTS internally splits on punctuation, but very large files still hit '
  'service-side limits.')
p('Failure branches: missing file and empty file are pre-flight failures (exit 1, no '
  'network touched). Any gTTS/network error lands in the broad except Exception branch — '
  'same exit code, no retry. There are no terminal-state distinctions to recover from; '
  're-running the command is the only remediation.')
ps('The structured pseudocode above is derived directly from the current implementation.')
ps('Invariants: input file is read fully as UTF-8 before any network call; output name '
   'derivation splits on the last dot, so a file with no extension produces "<name>.mp3" '
   'fine but "archive.tar.txt" yields "archive.tar.mp3". Evidence boundary: success '
   'proves Google accepted the text and an mp3 landed on disk — rungs 1-3 of the ladder; '
   'audio quality still requires playback (rung 5).')

h2('7.2 Offline text-to-speech')
ps('Implemented by text_to_speech_offline() and list_available_voices() in '
   'text_to_speech_offline.py:12-111.')
img(DIAG + r'\d3_offline_sequence.png')
cap('Figure 4 — pyttsx3/SAPI5 offline synthesis sequence.')
h3('Natural-language pseudocode')
code('''{
START
  Read the command-line arguments

  If the user requested the available voice list:
    Initialize the local speech engine
    Read every installed operating-system voice
    Display each voice index, name, language, and gender
    Exit with a success status

  Read the input path and optional output, voice, rate, and volume values
  Validate that the input file exists and contains text
  Initialize the local pyttsx3 speech engine

  If a voice index was provided:
    If the index identifies an installed voice:
      Select that voice
    Otherwise:
      Display a warning and keep the default voice

  If a speech rate was provided:
    Set the requested words-per-minute rate

  If a volume was provided:
    Set the requested volume

  Queue the text for file output
  Run the speech engine until synthesis finishes
  Save the generated local audio file
  Display a success message
  Exit with a success status
END
}''')
p('Normal behavior: pyttsx3.init() binds the OS speech driver (SAPI5 on Windows). '
  'Optional voice index, rate (wpm), and volume (0.0-1.0) are applied as engine properties, '
  'then save_to_file + runAndWait() blocks until the engine finishes writing. The '
  '--list-voices mode short-circuits before any file work.')
p('Failure branches: same validation failures as the online path. Additional failure '
  'surface: int()/float() conversion of argv happens in main() BEFORE the guarded '
  'function, so malformed numeric args traceback instead of exiting 1 cleanly. An '
  'out-of-range voice index is a warning, not an error — arguably a data-integrity '
  'hazard since the run "succeeds" with the wrong voice.')
ps('The structured pseudocode above is derived directly from the current implementation.')
ps('Invariants: no network anywhere — safe for sensitive scripts. Output format is '
   'whatever the OS engine emits for a .mp3 path; on SAPI5 this is commonly WAV data '
   'regardless of extension — verify with ffprobe before feeding it to create_mp4.py '
   '(ffmpeg sniffs content, so a mislabeled WAV still works, but file association '
   'confuses humans). Evidence boundary: rungs 1-2 only; the engine writes directly, '
   'so success means "engine reported done".')

h2('7.3 Translation')
ps('Implemented by translate_text() and translate_file() in translate_text.py:11-101.')
img(DIAG + r'\d4_translate_sequence.png')
cap('Figure 5 — Two-target translation sequence.')
h3('Natural-language pseudocode')
code('''{
START
  Read the input text-file path
  Use the provided output paths or derive Spanish and Portuguese filenames

  If the input file does not exist or contains no text:
    Display the validation error
    Mark both translations as failed
    Exit with a failure status

  Send the source text to Google Translate with automatic source-language detection
  Request a Spanish translation
  Save the returned Spanish text as UTF-8
  Mark the Spanish translation as successful

  Send the same source text to Google Translate again
  Request a Portuguese translation
  Save the returned Portuguese text as UTF-8
  Mark the Portuguese translation as successful

  If both translations succeeded:
    Display a completion message
    Exit with a success status
  Otherwise:
    Preserve any translation that was already written
    Display the error
    Exit with a failure status
END
}''')
p('Normal behavior: one read, then two independent GoogleTranslator round-trips '
  '(auto-detected source to es, then to pt), each written to its own file immediately. '
  'The default output names derive from the input basename.')
p('Failure branches: validation failures produce a results dict of {False, False} and '
  'exit 1. A mid-flight failure (e.g., network drop during the Portuguese leg) leaves '
  'the Spanish file on disk with results {True, False} -> exit 1. This is the only '
  'script where a failed exit can leave a valid partial artifact — and also the only '
  'script where "success" is a conjunction of two remote calls.')
ps('The structured pseudocode above is derived directly from the current implementation.')
ps('Invariants: each output file is complete or absent — writes happen after the full '
   'translation string returns, never streamed. The same input text is sent to Google '
   'twice (no reuse). Evidence boundary: rungs 1-3; translation correctness is not '
   'machine-verifiable in-repo.')

h2('7.4 Narrated video assembly (create_mp4.py)')
ps('Implemented by create_video_from_timeline() and fit_to_portrait_canvas() in '
   'create_mp4.py:18-246.')
img(DIAG + r'\d5_mp4_flow.png')
cap('Figure 6 — Full render pipeline: per-scene segments, concat, duration matching, mux, cleanup.')
h3('Natural-language pseudocode')
code('''{
START
  Read the audio path, image-directory path, timeline path, and output path
  Verify that the audio, image directory, and timeline exist
  Load the timeline JSON

  If the timeline has no non-empty scenes list:
    Display a timeline error
    Exit with a failure status

  Create the temporary segment directory

  For each scene in timeline order:
    Read its image, start time, end time, motion, and intensity
    Calculate the scene duration as end time minus start time

    If the image field is missing or the image file does not exist:
      Display the scene error
      Exit with a failure status

    Loop the still image at 30 frames per second
    Scale the image without stretching and pad it to a 1080 by 1920 portrait frame

    If motion is push_in:
      Gradually increase the zoom, stopping at 1.5 times
    Else if motion is pull_out:
      Gradually decrease the zoom, stopping at 1.0 times
    Else if motion is pan_left:
      Apply the left-pan position
    Else if motion is pan_right:
      Apply the right-pan position
    Otherwise:
      Keep the scene static at 30 frames per second

    Encode the scene as an H.264 temporary segment for the calculated duration

  Write every segment path to the concat list
  Concatenate all segments into a video-only MP4
  Measure the audio duration and video duration

  If the video is shorter than the audio:
    Repeat the video enough times to cover the narration

  Combine the video with AAC narration and write the final MP4
  Delete all temporary segments, the concat list, and the video-only file
  Remove the temporary directory
  Display a success message
  Exit with a success status
END
}''')
p('Normal behavior: each scene becomes an independent libx264 encode. The image loops '
  'at 30 fps, is scaled down to fit 1080x1920 without distortion, padded with black to '
  'fill the frame, then passed through a motion filter. push_in/pull_out animate zoom '
  'by +/- intensity per frame (clamped at 1.5x and 1.0x); pan_left/pan_right translate '
  'across the frame at zoom 1.0 — note that with the image already fitted to exactly '
  '1080x1920 there is no overscan to pan across, so pan scenes effectively render near-'
  'static unless the source image exceeds the canvas (inferred from the zoompan x/y '
  'expressions; the committed output.mp4 shows the intended result anyway). Any '
  'unrecognized motion string silently becomes static.')
p('After all segments exist, the concat demuxer assembles video_only.mp4. Both durations '
  'are probed; if video < audio the video is self-concatenated int(audio/video)+1 times, '
  'then muxed with the mp3 as AAC 192k — shortest=None is passed explicitly, meaning the '
  'output is NOT trimmed to the shorter stream, so a video longer than audio leaves '
  'trailing silent footage and a shorter one relies on the loop. Finally, every '
  'intermediate (segments, concat.txt, video_only.mp4, temp dir) is deleted.')
p('Failure branches: per-scene validation (missing image field, missing image file) '
  'aborts mid-loop, leaving already-encoded segments in temp_segments/ — the cleanup '
  'code is on the success path only, so crashed runs leak temporaries that the next run '
  'harmlessly overwrites. ffmpeg failures raise ffmpeg.Error into the broad except, '
  'with quiet=True discarding the stderr that would explain it. There is no resume: '
  'a 14-scene render that dies on scene 13 re-encodes all 13 on retry.')
ps('The structured pseudocode above is derived directly from the current implementation.')
ps('Invariants: (a) scene start/end define segment DURATION only — the JSON fields look '
   'like absolute timeline positions but only (end-start) is used; gaps or overlaps '
   'between consecutive scenes are silently collapsed, so scenes must tile the timeline '
   'contiguously to match the narration. (b) total video length = sum(durations), '
   'independent of the start values. (c) image aspect is never distorted — letterboxing '
   'guarantees it. (d) All encodes share identical codec params, so concat demuxer '
   '(stream copy is implied by matching params but re-encode is actually performed — '
   'vcodec=libx264 on the concat output re-encodes). Evidence boundary: success = '
   'rungs 1-4 (file exists, ffprobe-parseable); editorial sync requires human playback.')

h2('7.5 Timeline data model')
ps('Consumed by create_mp4.py:80-107; authored against video-editing-timeline.md.')
img(DIAG + r'\d7_er.png')
cap('Figure 7 — The scenes[] contract: fields, defaults, and file relationships.')
h3('Natural-language pseudocode')
code('''{
START
  Load the timeline object
  Read its scenes list

  For each scene in the scenes list:
    Read the optional scene name for progress logging
    Read the required image filename
    Resolve the filename inside the selected image directory
    Use the provided start time or default to zero seconds
    Use the provided end time or default to five seconds
    Use the provided motion or default to static
    Use the provided intensity or default to 0.05
    Pair the scene with the narration audio supplied on the command line

  Pass the resolved scenes and narration to the video-rendering workflow
END
}''')
p('The schema is enforced loosely: only "scenes" (non-empty array) and per-scene "image" '
  '(non-empty, resolvable file) are validated. name is documentation-only (used in the '
  'progress print). start/end, motion, and intensity all have defaults, so a minimal '
  'scene is just {"image": "x.png"} -> a 5-second static shot. This is convenient for '
  'authoring but means a typo like "motoin": "push_in" silently yields static footage — '
  'the most likely silent-failure mode in the whole project.')

h2('7.6 End-to-end chapter pipeline')
ps('Spans all four scripts; the committed artifacts make this the canonical worked example.')
img(DIAG + r'\d8_pipeline.png')
cap('Figure 8 — The Botany Diaries chapter-1 flow, plus localization and offline branches.')
h3('Natural-language pseudocode')
code('''{
START
  Write or select the chapter narration text

  If an online English narration is required:
    Convert the chapter text to an English MP3 with gTTS
  Else if an offline narration is required:
    Convert the chapter text with the installed operating-system voice

  If localized editions are required:
    Translate the source text into Spanish and Portuguese
    Convert each translated text file into narration with its matching language code

  Gather the chapter narration MP3
  Gather the fourteen chapter images
  Load the fourteen-scene timeline covering zero through 900 seconds
  Render each timed image scene with its configured motion
  Concatenate the rendered scenes
  Combine the scene video with the narration audio
  Save the final 1080 by 1920, 30-frames-per-second H.264 and AAC MP4
  Play the completed video and confirm narration, scene timing, and motion quality
END
}''')
p('This is the workflow the other four serve. The 14-scene timeline (0-900 s) pairs the '
  '~15-minute gTTS narration with fourteen illustrations; the committed output.mp4 '
  'demonstrates a full pass through rung 6 of the evidence ladder. For a new chapter: '
  'write the .txt, synthesize mp3, place images in a directory, author a timeline whose '
  'scenes tile the narration contiguously (mind invariant 7.4-a), render, and review '
  'playback before publishing.')

# ============================== 8. TESTING ==============================
h1('8. Testing and Verification')
p('There is no automated test suite, no CI, and no test framework in the repository. '
  'Verification is manual and artifact-based. Recommended verification protocol:')
code('''# Smoke test the online TTS path (uses the committed fixture pair)
python text_to_speech.py sample.txt
# Expected: "Successfully created audio file: sample.mp3", exit 0

# Offline path: enumerate voices, then synthesize
python text_to_speech_offline.py --list-voices
python text_to_speech_offline.py sample.txt sample_offline.wav 0 150 0.9

# Translation (network-dependent)
python translate_text.py sample.txt

# Media integrity check on any produced artifact
ffprobe -v error -show_format -show_streams output.mp4

# Negative tests worth running before trusting automation:
python text_to_speech.py does_not_exist.txt     # expect error + exit 1
python text_to_speech.py empty.txt              # expect "Input file is empty" + exit 1''')
p('A practical regression check for the video path is to render a single-scene timeline '
  'against sample.mp3 before committing to a 15-minute encode — it exercises the entire '
  'create_mp4.py code path in seconds.')

# ============================== 9. BUILD/DEPLOY ==============================
h1('9. Build, Packaging, and Deployment')
p('There is nothing to build or deploy in the conventional sense: scripts run in place '
  'from a git checkout. "Deployment" is copying the directory (or cloning Skymero/Tools) '
  'onto a machine with Python 3.10+, pip deps, and ffmpeg. The only artifacts are the '
  'media outputs themselves, which are committed to git — note that output.mp4 (55 MB) '
  'and the mp3s (43 MB) make the repo heavy; a .gitignore + Git LFS policy would be a '
  'reasonable future hardening, not current behavior.')

# ============================== 10. OPERATIONS ==============================
h1('10. Operations and Troubleshooting')
h2('10.1 Troubleshooting matrix')
table(['Symptom', 'Likely cause', 'Where it lives', 'Fix / diagnostic'],
      [['"An error occurred during conversion" from text_to_speech.py', 'No internet, Google TTS rate-limiting, or invalid lang code.', 'text_to_speech.py:59 (broad except)', 'Check connectivity; try a shorter text; verify lang code; re-run later.'],
       ['create_mp4.py fails immediately at first scene', 'ffmpeg/ffprobe not on PATH.', 'ffmpeg-python shim -> subprocess', 'ffmpeg -version must work in the same shell; reinstall/add to PATH.'],
       ['create_mp4.py prints generic "error occurred during video creation"', 'ffmpeg stderr suppressed by quiet=True.', 'create_mp4.py:168,192,224', 'Temporarily change .run(quiet=True) to .run() to surface the ffmpeg error.'],
       ['Scene renders static despite "motion" set', 'Typo in motion key or value; unlisted values fall to fps-only branch.', 'create_mp4.py:155-156', 'Valid values: push_in, pull_out, pan_left, pan_right. Check JSON key spelling.'],
       ['Narration drifts out of sync with images', 'Timeline start/end not treated as absolute; only duration matters.', 'create_mp4.py:103', 'Ensure scenes tile 0..N contiguously: each scene start == previous end.'],
       ['Video loops or has trailing silence', 'Sum(scene durations) != audio duration.', 'create_mp4.py:208-222', 'Sum end-start values and compare to ffprobe of the mp3; adjust timeline.'],
       ['temp_segments/ left behind', 'A scene failed mid-run; cleanup is success-path only.', 'create_mp4.py:227-233', 'Delete temp_segments manually; safe — next run overwrites.'],
       ['"Voice index out of range" warning', 'voice_index >= installed voice count.', 'text_to_speech_offline.py:56-57', 'Run --list-voices and pick a valid index; run still succeeds with default voice.'],
       ['Offline output will not play in some players', 'SAPI5 may write WAV data to a .mp3-named file.', 'text_to_speech_offline.py:71', 'ffprobe the file; if WAV, rename to .wav — ffmpeg content-sniffs so create_mp4.py still works.'],
       ['exit 1 from translate_text.py but a file exists', 'One of two translations succeeded.', 'translate_text.py:74-88', 'Check which *_spanish/_portuguese file exists; re-run (idempotent overwrite).'],
       ['Traceback instead of clean error (offline script)', 'Non-numeric voice/rate/volume arg crashes int()/float() before guarded code.', 'text_to_speech_offline.py:135-137', 'Pass numeric args only; this is a known unhandled edge.'],
       ['gTTS output audio truncated/robotic on huge files', 'Service-side limits on request size.', 'gTTS internals', 'Split the source .txt into parts, synthesize each, concat mp3s with ffmpeg.']],
      [1.55*inch, 1.5*inch, 1.35*inch, 2.6*inch])

h2('10.2 Operational notes')
p('Cost of a run: the video path is encode-bound; a 14-scene/15-minute output performs '
  '15 ffmpeg invocations (14 segments + 1 concat + mux) and re-encodes every frame twice '
  '(segment, then concat output). Disk headroom needed is roughly 2x the intermediate '
  'video size plus the final file. There is no logging framework — all observability is '
  'stdout print lines; redirect stdout to a file for long renders.')
p('Idempotency: all scripts overwrite their outputs freely (ffmpeg .overwrite_output()). '
  'Re-running is always safe but never resumable. There is no deduplication: running '
  'text_to_speech.py twice on the same file performs two full paid-in-latency round '
  'trips to Google.')

# ============================== 11. SECURITY ==============================
h1('11. Security Notes')
p('No secrets, credentials, or auth tokens exist anywhere in the project — both Google '
  'integrations use unauthenticated public endpoints. The real security considerations are:')
p('1. Data egress: the full text of any script processed by text_to_speech.py or '
  'translate_text.py is sent to Google. For unpublished manuscripts this is a '
  'confidentiality boundary — use text_to_speech_offline.py for sensitive content.')
p('2. Input trust: video-timeline.json controls file paths and ffmpeg parameters; only '
  'the image field is validated. Do not render timelines from untrusted sources without '
  'review. The concat demuxer runs with safe=0, accepting absolute paths.')
p('3. Subprocess surface: ffmpeg executes with user privileges on paths assembled from '
  'JSON fields; the risk is limited to the filesystem scope of the invoking user.')
p('4. Committed binary artifacts: test.exe and the large media files are opaque blobs in '
  'git; hello_world_ricardo.cpp shows test.exe is benign scratch work, but binary '
  'artifacts in VCS remain an audit smell worth cleaning up.')

# ============================== 12. APPENDIX ==============================
h1('12. Appendix')
h2('12.1 Timeline JSON schema (observed)')
code('''{
  "scenes": [
    {
      "name": "conservatory_exterior",   // optional, log label only
      "image": "BD-CH1-img-9.png",       // REQUIRED, must exist in images_dir
      "start": 0,                        // seconds; only end-start is used
      "end": 35,                         // seconds; duration = end - start
      "motion": "push_in",               // push_in|pull_out|pan_left|pan_right|*
      "intensity": 0.06                  // zoompan step per frame, default 0.05
    }
  ]
}''')
h2('12.2 Function index')
table(['Function', 'File:line', 'Signature', 'Returns'],
      [['text_to_speech', 'text_to_speech.py:11', '(input_file, output_file, language="en")', 'bool'],
       ['main', 'text_to_speech.py:64', '()', 'exits 0/1'],
       ['text_to_speech_offline', 'text_to_speech_offline.py:12', '(input_file, output_file, voice_index, rate, volume)', 'bool'],
       ['list_available_voices', 'text_to_speech_offline.py:90', '()', 'list of voices'],
       ['translate_text', 'translate_text.py:11', '(input_text, target_language)', 'str (raises on error)'],
       ['translate_file', 'translate_text.py:33', '(input_file, output_file_es, output_file_pt)', 'dict {spanish, portuguese}'],
       ['fit_to_portrait_canvas', 'create_mp4.py:18', '(video_stream)', 'filtered stream'],
       ['create_video_from_timeline', 'create_mp4.py:40', '(audio_file, images_dir, timeline_file, output_file)', 'bool']],
      [1.7*inch, 1.85*inch, 2.3*inch, 1.15*inch])
h2('12.3 Dependency pin table')
table(['Package', 'Pin', 'Used by', 'Notes'],
      [['gTTS', '2.5.1', 'text_to_speech.py', 'Unofficial Google TTS client; endpoint stability is external risk.'],
       ['deep-translator', '1.11.4', 'translate_text.py', 'Wraps web translate endpoints; GoogleTranslator class.'],
       ['pyttsx3', '2.90', 'text_to_speech_offline.py', 'Cross-platform offline TTS; SAPI5 backend on Windows.'],
       ['ffmpeg-python', '0.2.0', 'create_mp4.py', 'Pythonic ffmpeg graph builder; does NOT include the ffmpeg binary.']],
      [1.3*inch, 0.7*inch, 1.8*inch, 3.2*inch])

def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(colors.HexColor('#777777'))
    canvas.drawString(0.75*inch, 0.45*inch, 'TTS_gen Technical Guide — generated from repository source')
    canvas.drawRightString(7.75*inch, 0.45*inch, f'Page {doc.page}')
    canvas.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=letter,
                        leftMargin=0.75*inch, rightMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch,
                        title='TTS_gen Technical Guide')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print('Wrote', OUT)
