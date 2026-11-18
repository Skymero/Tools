"""Render Mermaid diagrams to PNG via the mermaid.ink service."""
import base64
import json
import urllib.request
import zlib

# Mermaid source for each diagram, keyed by output filename
DIAGRAMS = {
    "d1_architecture": """flowchart LR
    subgraph User["User / Operator"]
        CLI["Command Line<br/>(powershell)"]
    end
    subgraph Scripts["TTS_gen scripts"]
        TTS_ON["text_to_speech.py<br/>(gTTS wrapper)"]
        TTS_OFF["text_to_speech_offline.py<br/>(pyttsx3 wrapper)"]
        TR["translate_text.py<br/>(deep-translator)"]
        MP4["create_mp4.py<br/>(ffmpeg-python)"]
    end
    subgraph Local["Local filesystem"]
        TXT["Text files (*.txt)"]
        IMGS["Image assets<br/>(Chapter1-imgs/)"]
        TL["video-timeline.json<br/>(scene script)"]
        MP3["MP3 narration (*.mp3)"]
        VID["MP4 video (output.mp4)"]
        TMP["temp_segments/<br/>(intermediate)"]
    end
    subgraph External["External services (trust boundary)"]
        GTTS["Google TTS API<br/>(via gTTS)"]
        GTR["Google Translate<br/>(web endpoint)"]
    end
    subgraph OS["Operating system"]
        SAPI["SAPI5 / system<br/>speech engine"]
        FF["ffmpeg binary<br/>(subprocess)"]
    end
    CLI --> TTS_ON
    CLI --> TTS_OFF
    CLI --> TR
    CLI --> MP4
    TXT --> TTS_ON --> MP3
    TXT --> TTS_OFF --> SAPI --> MP3
    TXT --> TR --> GTR
    TR --> TXT
    TTS_ON --> GTTS
    MP3 --> MP4
    IMGS --> MP4
    TL --> MP4
    MP4 --> FF
    FF --> TMP --> VID""",
    "d2_tts_sequence": """sequenceDiagram
    autonumber
    actor U as User (CLI)
    participant S as text_to_speech.py
    participant FS as Local filesystem
    participant G as gTTS library
    participant API as Google TTS endpoint
    U->>S: python text_to_speech.py input.txt [out.mp3] [lang]
    S->>FS: os.path.exists(input_file)?
    alt file missing
        S-->>U: FileNotFoundError, exit code 1
    end
    S->>FS: read UTF-8 text, strip()
    alt empty file
        S-->>U: ValueError Input file is empty, exit 1
    end
    S->>G: gTTS(text, lang, slow=False)
    G->>API: HTTPS request (tokenized text)
    API-->>G: audio stream (MP3)
    G->>FS: tts.save(output_file)
    S-->>U: Successfully created audio file, exit 0""",
    "d3_offline_sequence": """sequenceDiagram
    autonumber
    actor U as User (CLI)
    participant S as text_to_speech_offline.py
    participant P as pyttsx3 engine
    participant OS as OS speech engine (SAPI5)
    participant FS as Local filesystem
    U->>S: text_to_speech_offline.py in.txt [out] [voice] [rate] [vol]
    alt --list-voices flag
        S->>P: pyttsx3.init() then getProperty('voices')
        P->>OS: enumerate installed voices
        S-->>U: print voice list, exit 0
    end
    S->>FS: validate + read text
    S->>P: pyttsx3.init()
    opt voice_index provided
        S->>P: setProperty('voice', voices[i].id)
    end
    opt rate / volume provided
        S->>P: setProperty('rate' / 'volume', value)
    end
    S->>P: engine.save_to_file(text, output)
    P->>OS: synthesize audio
    S->>P: engine.runAndWait()
    P->>FS: write audio file
    S-->>U: success, exit 0""",
    "d4_translate_sequence": """sequenceDiagram
    autonumber
    actor U as User (CLI)
    participant S as translate_text.py
    participant DT as deep-translator GoogleTranslator
    participant G as Google Translate endpoint
    participant FS as Local filesystem
    U->>S: python translate_text.py input.txt [es_out] [pt_out]
    S->>FS: validate + read text
    S->>DT: GoogleTranslator(source=auto, target=es)
    DT->>G: translate request
    G-->>DT: Spanish text
    S->>FS: write {base}_spanish.txt
    S->>DT: GoogleTranslator(source=auto, target=pt)
    DT->>G: translate request
    G-->>DT: Portuguese text
    S->>FS: write {base}_portuguese.txt
    S-->>U: results dict - exit 0 only if both true""",
    "d5_mp4_flow": """flowchart TD
    A["Start: parse CLI args<br/>audio, images_dir, timeline, output"] --> B{"Inputs exist?<br/>audio / images dir / timeline"}
    B -- no --> E1["FileNotFoundError<br/>print error, return False, exit 1"]
    B -- yes --> C["Load timeline JSON<br/>require non-empty 'scenes' array"]
    C -- invalid --> E2["ValueError<br/>return False, exit 1"]
    C -- valid --> D["mkdir temp_segments/"]
    D --> F["For each scene i:<br/>image, start, end, motion, intensity"]
    F --> G{"image field present<br/>and file exists?"}
    G -- no --> E3["ValueError /<br/>FileNotFoundError<br/>abort, exit 1"]
    G -- yes --> H["Loop image @30fps<br/>scale+pad to 1080x1920 portrait"]
    H --> I{"motion type?"}
    I -- push_in --> J1["zoompan zoom+intensity<br/>clamped 1.5"]
    I -- pull_out --> J2["zoompan zoom-intensity<br/>clamped 1.0"]
    I -- pan_left --> J3["zoompan<br/>x = iw-iw/zoom"]
    I -- pan_right --> J4["zoompan<br/>x = 0"]
    I -- static/other --> J5["fps filter only"]
    J1 --> K["Encode segment_i.mp4<br/>libx264, yuv420p, crf23, t=duration"]
    J2 --> K
    J3 --> K
    J4 --> K
    J5 --> K
    K --> F
    F -- all scenes done --> L["Write concat.txt<br/>concat demuxer -> video_only.mp4"]
    L --> M["ffprobe audio + video durations"]
    M --> N{"video shorter<br/>than audio?"}
    N -- yes --> O["Loop video via concat<br/>int(audio/video)+1 copies"]
    N -- no --> P["keep as-is"]
    O --> Q["Mux video + AAC 192k audio<br/>-> output.mp4"]
    P --> Q
    Q --> R["Delete segments, concat.txt,<br/>video_only.mp4, temp dir"]
    R --> S["Return True, exit 0"]""",
    "d6_state": """stateDiagram-v2
    [*] --> ArgParse: process launched
    ArgParse --> Validating: argv ok
    ArgParse --> UsageExit: argc too small
    UsageExit --> [*]: exit 1
    Validating --> Reading: inputs exist
    Validating --> Failed: missing file / empty text / bad timeline
    Reading --> Processing: text or scenes loaded
    Processing --> NetworkIO: gTTS / translator path
    Processing --> LocalIO: pyttsx3 / ffmpeg path
    NetworkIO --> Failed: network or HTTP error
    LocalIO --> Failed: engine or ffmpeg error
    NetworkIO --> Writing: provider returned data
    LocalIO --> Writing: engine produced output
    Writing --> Succeeded: artifact saved
    Failed --> [*]: print error, return False, exit 1
    Succeeded --> [*]: exit 0""",
    "d7_er": """erDiagram
    TIMELINE ||--|{ SCENE : "contains scenes[]"
    TIMELINE {
        string root_key  "scenes"
    }
    SCENE {
        string name      "optional label for logging"
        string image     "required filename in images_dir"
        number start     "seconds, default 0"
        number end       "seconds, default 5"
        string motion    "push_in | pull_out | pan_left | pan_right | static"
        number intensity "default 0.05, zoompan step"
    }
    SCENE ||--|| IMAGE_FILE : "resolves to"
    IMAGE_FILE {
        string path "images_dir/image"
    }
    TIMELINE ||--|| AUDIO_FILE : "paired at CLI"
    AUDIO_FILE {
        string path "mp3 narration"
        float duration "probed by ffprobe"
    }""",
    "d8_pipeline": """flowchart LR
    subgraph Pipeline["End-to-end Botany Diaries chapter pipeline"]
        A["botany-diaries-ch1.txt<br/>narration script"] --> B["text_to_speech.py<br/>gTTS, lang=en"]
        B --> C["botany-diaries-ch1.mp3<br/>43 MB, ~15 min"]
        C --> F["create_mp4.py"]
        D["Chapter1-imgs/<br/>BD-CH1-img-1..14.png"] --> F
        E["video-timeline.json<br/>14 scenes, 0-900 s"] --> F
        F --> G["output.mp4<br/>1080x1920, 30fps<br/>H.264 + AAC 192k"]
    end
    subgraph Optional["Optional localization branch"]
        A2["source .txt"] --> T["translate_text.py"] --> A3["_spanish.txt<br/>_portuguese.txt"] --> B2["text_to_speech.py<br/>lang=es / pt"] --> C2["localized .mp3"]
    end
    subgraph Offline["Offline fallback branch"]
        A4[".txt"] --> O["text_to_speech_offline.py<br/>pyttsx3 / SAPI5"] --> C4[".mp3 / .wav"]
    end""",
}


def encode_b64(source: str) -> str:
    # plain base64url of JSON {"code","mermaid"} object (non-pako endpoint)
    payload = json.dumps({"code": source, "mermaid": {"theme": "default"}})
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("ascii")


def encode_pako(source: str) -> str:
    payload = json.dumps({"code": source, "mermaid": {"theme": "default"}})
    return base64.urlsafe_b64encode(zlib.compress(payload.encode("utf-8"), 9)).decode("ascii")


def main():
    for name, src in DIAGRAMS.items():
        url = f"https://mermaid.ink/img/{encode_b64(src)}?type=png&bgColor=white"
        out = f"C:/Users/ricky/Tools/TTS_gen/DOCS/diagrams/{name}.png"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(out, "wb") as f:
            f.write(data)
        print(name, len(data), "bytes")


if __name__ == "__main__":
    main()
