# Image Text Extractor

A Python application that extracts text from images using OCR (Optical Character Recognition).

## Features

- Extract text from various image formats
- Preprocess images to improve OCR accuracy
- Output extracted text as a list
- Command-line interface for easy usage

## Requirements

- Python 3.10 or higher
- Tesseract OCR engine

## Installation

1. Clone the repository or download the source code

2. Set up a virtual environment and activate it:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install the required dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

4. Install Tesseract OCR:
   - Download and install Tesseract from: https://github.com/UB-Mannheim/tesseract/wiki
   - Ensure the tesseract executable is in your PATH or provide its path when using the application

## Usage

### Basic Usage

```powershell
python main.py path/to/your/image.jpg
```

### Advanced Usage

```powershell
python -m ImageTextExtractor.image_text_extractor path/to/your/image.jpg --tesseract-path "C:\Program Files\Tesseract-OCR\tesseract.exe" --no-preprocess
```

### Arguments

- `image_path`: Path to the input image
- `--tesseract-path`: (Optional) Path to the tesseract executable
- `--no-preprocess`: (Optional) Skip image preprocessing

## Sample Code

```python
from ImageTextExtractor.image_text_extractor import ImageTextExtractor

# Initialize the extractor
extractor = ImageTextExtractor()

# Extract text from an image and get it as a list
text_list = extractor.extract_text_as_list("path/to/your/image.jpg")

# Print the extracted text
for i, line in enumerate(text_list, 1):
    print(f"{i}. {line}")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
