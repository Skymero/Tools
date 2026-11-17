# Text to Speech Converter

A simple Python tool that converts text files to MP3 audio using the Google Text-to-Speech (gTTS) library.

## Features

- Convert any text file to MP3 audio
- Support for multiple languages
- Simple command-line interface
- Error handling for missing files and empty content

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

## Requirements

- Python 3.6+
- gTTS library
- Internet connection (gTTS requires internet to access Google's TTS API)

## Error Handling

The script handles the following errors:
- Missing input file
- Empty input file
- Network connectivity issues
- Invalid language codes

## Notes

- The conversion requires an active internet connection as gTTS uses Google's online TTS service
- Large text files may take longer to process
- The output MP3 quality depends on Google's TTS service
