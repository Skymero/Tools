# Advanced Audio Analysis Tool

A comprehensive audio analysis tool that processes audio files and extracts musical and acoustic characteristics for each note in sequence. This tool enables musicians, producers, and researchers to obtain an in-depth breakdown of sound elements using both classical signal processing and modern machine learning techniques.

## Workflow
- each feature is executed individually by the user according to their needs using args.parse_args()


## Features

For every distinct note detected in an audio file, this tool extracts:

1. **Pitch and Musical Note**
   - Pitch in Hertz (Hz)
   - Western musical note (e.g., C4, A#3)
   - Duration in seconds

2. **Instrument Identification**
   - Classification of instrument or sound source
   - Timbral profile analysis

3. **Timbre and Harmonic Content**
   - Overtone analysis
   - Spectral brightness
   - Tone richness/dullness classification

4. **Envelope (ADSR)**
   - Attack time
   - Decay time
   - Sustain level
   - Release time

5. **Vibrato**
   - Pitch modulation rate and depth

6. **Reverb**
   - Reverberation time (RT60)
   - Early reflections and decay tail analysis

7. **Distortion**
   - Harmonic clipping, saturation, or fuzz detection

8. **Filtering**
   - Spectral shaping identification
   - Filter sweep tracking

9. **Dynamics**
   - Loudness in LUFS or RMS
   - Compression/expansion detection

10. **Articulation**
    - Playing style classification

11. **Texture**
    - Voice/instrument layering detection

12. **Space and Positioning**
    - Spatial positioning analysis

13. **Emotion**
    - Emotional character inference from tone, dynamics, and performance

14. **Chord Progression**
    - Chord progression analysis

15. **Melody**
    - Melody analysis

16. **Rhythm**
    - Rhythm analysis

17. **Tempo**
    - Tempo analysis

18. **Key**
    - Key analysis


## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/audio-analyzer.git
cd audio-analyzer

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Command Line Interface

```bash
# Basic usage
python -m audio_analyzer.cli input.wav

# Specify output format
python -m audio_analyzer.cli input.wav --output-format json

# Analyze specific segment
python -m audio_analyzer.cli input.wav --start 10.5 --end 25.0

# Save visualization
python -m audio_analyzer.cli input.wav --visualize --output-image waveform.png
```

### Python API

```python
from audio_analyzer.core.analyzer import AudioAnalyzer

# Initialize analyzer
analyzer = AudioAnalyzer()

# Analyze file
results = analyzer.analyze_file('path/to/audio.mp3')

# Print results
print(results)
```

## Supported Formats

- WAV
- MP3
- FLAC

## Dependencies

- Python 3.10+
- librosa, aubio, crepe, essentia, pydub
- scikit-learn, torch
- Other dependencies listed in requirements.txt

## Tutorial: Getting Started with Lavoe Audio Analyzer

This tutorial will guide you through the main features of Lavoe Audio Analyzer with practical examples.

### 1. Basic Audio Analysis

Analyze a complete audio file and view the results:

```bash
# Basic analysis with default settings
python -m audio_analyzer.cli your_audio_file.wav

# Get detailed output in JSON format
python -m audio_analyzer.cli your_audio_file.wav --output-format json > analysis_results.json
```

### 2. Analyzing Specific Audio Segments

Focus on a particular section of your audio file:

```bash
# Analyze only between 30 to 45 seconds
python -m audio_analyzer.cli your_audio_file.wav --start 30 --end 45

# Get a quick overview of the first minute
python -m audio_analyzer.cli your_audio_file.wav --end 60 --summary
```

### 3. Visualizing Audio Features

Generate visual representations of the audio analysis:

```bash
# Save waveform visualization
python -m audio_analyzer.cli your_audio_file.wav --visualize --output-image waveform.png

# Generate spectral analysis
python -m audio_analyzer.cli your_audio_file.wav --spectrogram --output-image spectrogram.png
```

### 4. Advanced Feature Extraction

Extract specific musical features:

```bash
# Get chord progression analysis
python -m audio_analyzer.cli your_audio_file.wav --features chords

# Analyze emotional content
python -m audio_analyzer.cli your_audio_file.wav --features emotion

# Get key and scale information
python -m audio_analyzer.cli your_audio_file.wav --features key
```

### 5. Batch Processing

Process multiple files at once:

```bash
# Process all WAV files in a directory
for file in /path/to/audio/files/*.wav; do
    python -m audio_analyzer.cli "$file" --output-format json > "${file%.wav}_analysis.json"
done
```

### 6. Using the Python API

For more advanced usage, you can integrate the analyzer into your Python code:

```python
from audio_analyzer.core.analyzer import AudioAnalyzer
import json

# Initialize the analyzer
analyzer = AudioAnalyzer()

# Analyze a file with all features
results = analyzer.analyze_file(
    'your_audio_file.wav',
    features=['pitch', 'chords', 'emotion', 'key'],
    start_time=30.0,  # Optional: start time in seconds
    end_time=45.0     # Optional: end time in seconds
)

# Save results to a file
with open('analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

# Access specific features
print(f"Detected key: {results['key']['estimated_key']}")
print(f"Tempo: {results['tempo']['bpm']} BPM")
```

### 7. Real-time Analysis

For real-time audio analysis (requires additional setup):

```python
from audio_analyzer.core.realtime import RealtimeAnalyzer
import sounddevice as sd

# Initialize real-time analyzer
rt_analyzer = RealtimeAnalyzer()

# Start analysis on default input device
rt_analyzer.start()

# The analyzer will run in a separate thread
# You can access the latest analysis results:
current_analysis = rt_analyzer.get_latest_analysis()

# Remember to stop the analyzer when done
rt_analyzer.stop()
```

## License

[MIT License](LICENSE)
