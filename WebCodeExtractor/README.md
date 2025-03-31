# Lupin the 1st - Website Content Extractor

A powerful Python tool that extracts HTML, CSS, and JavaScript code from websites.

## Features

- Intelligently detects if a website uses dynamic content loading
- Extracts HTML, CSS, and JavaScript from both static and dynamic websites
- Downloads all associated assets (stylesheets, scripts, images)
- Generates a comprehensive PDF report of the extracted content
- Works with both static (BeautifulSoup) and dynamic (Selenium) websites

## Installation

1. Clone this repository:
   ```
   git clone <repository-url>
   cd WebExtractor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the tool from the command line:

```
python lupin.py <website-url> [options]
```

### Options

- `-o, --output`: Specify the output directory (default: `output`)
- `--pdf`: Generate a PDF report of the extracted content

### Examples

Extract content from a website and save to the default output directory:
```
python lupin.py https://example.com
```

Extract content and specify a custom output directory:
```
python lupin.py https://example.com -o my_extraction
```

Extract content and generate a PDF report:
```
python lupin.py https://example.com --pdf
```

## How It Works

1. **Dynamic Detection**: The tool first checks if the website loads content dynamically using JavaScript.
2. **Content Extraction**: Based on the detection, it uses either BeautifulSoup (for static sites) or Selenium (for dynamic sites) to extract the content.
3. **Asset Download**: All linked assets (CSS, JavaScript, images) are downloaded and saved locally.
4. **PDF Generation**: If requested, a comprehensive PDF report is generated with all the extracted content.

## Requirements

- Python 3.7+
- Required Python packages (see `requirements.txt`):
  - requests
  - beautifulsoup4
  - selenium
  - webdriver-manager
  - fpdf

## License

This project is licensed under the MIT License - see the LICENSE file for details.
