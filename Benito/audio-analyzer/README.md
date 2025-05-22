# Advanced Audio Analysis Tool

A comprehensive audio analysis tool that processes audio files and extracts musical and acoustic characteristics for each note in sequence. This tool enables musicians, producers, and researchers to obtain an in-depth breakdown of sound elements using both classical signal processing and modern machine learning techniques.

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

## License

[MIT License](LICENSE)
