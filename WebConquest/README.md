# Webconquest

A tool that uses either webscraping methods or APIs similar to google places to extract business information from businesses that meet the search criteria and then exports the data to a CSV file.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```python
from my_package import example

example.hello_world()
```

## Project Structure

```
python_template/
├── my_package/
│   ├── __init__.py
│   ├── example.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
│   ├── __init__.py
│   └── test_example.py
├── google_maps_scraper.py
├── README.md
├── requirements.txt
├── setup.py
└── .gitignore
```
# Webconquest

A tool that uses either webscraping methods or APIs similar to google places to extract business information from businesses that meet the search criteria and then exports the data to a CSV file. For the following purposes:
1. find businesses in a specified area that do not have websites
2. find businesses in a specified area that have an events calendar in their website
3. extract the businesses contact information, website link, social media accounts
4. sort the data into CSV files

## 1. Business Website checker

This tool automates the process of searching for businesses in a specified geolocation area, extracts their contact information, and sorts them into two CSV files based on whether they have a website or not.

### How to Use

1. **Set up the environment:**
    - Ensure you have Python 3 installed.
    - Create and activate a virtual environment (already set up as `.venv`).
    - Install dependencies:
      ```powershell
      .venv\Scripts\activate
      pip install -r requirements.txt
      ```

2. **Download ChromeDriver:**
    - The correct version of ChromeDriver should be present in your project directory as `chromedriver.exe`.
    - Make sure your installed Chrome version matches the driver version.

3. **Edit the search query (optional):**
    - Open `google_maps_scraper.py`.
    - Change the `SEARCH_QUERY` variable to your desired business/location.

4. **Run the script:**
    ```powershell
    python google_maps_scraper.py
    ```

5. **View results:**
    - After running, check for two files in your project directory:
      - `with_website.csv`: Businesses with a website
      - `without_website.csv`: Businesses without a website

### Troubleshooting
- If you get errors about ChromeDriver, ensure the version matches your Chrome browser.
- Google may block automated scraping. If you see CAPTCHAs or missing results, try running the script more slowly or use a different network.
- For large-scale or production use, consider using an official API or a service like SerpAPI.

### Disclaimer
This tool is for educational and demonstration purposes. Automated scraping of Google Maps may violate their terms of service.

### How it works

1. **Headless Browser Setup**: The script uses Selenium to launch a headless Chrome browser (with a locally downloaded ChromeDriver) to avoid opening a visible browser window.

2. **Automated Search**: It navigates to [Google Maps](https://www.google.com/maps), enters the search query (e.g., `coffee shops near Winston-Salem, NC`), and waits for the results to load.

3. **Result Extraction**: The script scrolls through the results panel to load multiple business listings. For each listing, it attempts to extract:
   - Business name
   - Phone number
   - Website URL (if available)

4. **Data Categorization**: It categorizes businesses into two groups:
   - Those **with** a website
   - Those **without** a website

5. **CSV Output**: The results are saved into two files:
   - `with_website.csv`: Contains name, phone, and website columns
   - `without_website.csv`: Contains name and phone columns

6. **Browser Cleanup**: The browser is closed after processing.

### Notes
- The script is designed for demonstration and small-scale use. For production or large-scale scraping, consider using official APIs or third-party services.
- Google may block automated scraping. Use delays and avoid aggressive querying to reduce the risk.

### Development

To install the package in development mode:

```bash
pip install -e .
```

### Testing

```bash
pytest tests/
```

## 2. Event Calendar checker
 the user enters a search query is entered and the script will search for businesses that meet the search criteria that have an event calendar on their website in specified cities and export the data to a CSV file.
