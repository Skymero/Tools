# Project Overview
Tool Name: Lupin the 1st

## Description
This project is a python project that extracts all of a website's  HTML, CSS, and javascript code from a provided link as an input?


## Function List

### CheckDynamic
- checks for websites where assets or HTML content are loaded dynamically with JavaScript. If so, use Selenium, else use beautifulsoup for a static website

### Downloading HTML:
The script uses the requests library to fetch the HTML content of the given URL and saves it locally in an output folder.

### Extracting CSS and JavaScript Links:
It parses the HTML with BeautifulSoup.

For CSS, it looks for <link> tags with rel="stylesheet".
For JavaScript, it finds <script> tags that have a src attribute.

### Downloading Assets:
Using the urljoin function from Python’s urllib.parse module ensures that any relative URLs are converted to absolute ones.
Each asset is then downloaded and saved in its respective folder (output/css or output/js).

### Generate PDF
consolidatesCHTML, CSS, and JavaScript code into a pdf file


## Example Code Snippets

### Selenium
```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://example.com")

# Give the page some time to load dynamic content
driver.implicitly_wait(5)
html_content = driver.page_source

soup = BeautifulSoup(html_content, "html.parser")
# Then proceed as before to extract assets...

driver.quit()

```

### BeautifulSoup
```python
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_file(url, folder, filename):
    """Download a file from a URL and save it locally."""
    response = requests.get(url)
    if response.status_code == 200:
        os.makedirs(folder, exist_ok=True)
        filepath = os.path.join(folder, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(response.text)
        print(f"Downloaded {url} to {filepath}")
    else:
        print(f"Failed to download {url}")

def extract_and_download_assets(url):
    # Fetch the main HTML content
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return
    
    html_content = response.text
    
    # Save the HTML file
    os.makedirs("output", exist_ok=True)
    with open(os.path.join("output", "page.html"), "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Downloaded main HTML.")

    # Parse HTML to extract assets
    soup = BeautifulSoup(html_content, "html.parser")

    # Extract and download CSS files
    css_links = [link.get('href') for link in soup.find_all("link", rel="stylesheet") if link.get('href')]
    for idx, css_link in enumerate(css_links):
        full_css_url = urljoin(url, css_link)
        download_file(full_css_url, "output/css", f"style_{idx}.css")

    # Extract and download JS files
    js_links = [script.get('src') for script in soup.find_all("script", src=True)]
    for idx, js_link in enumerate(js_links):
        full_js_url = urljoin(url, js_link)
        download_file(full_js_url, "output/js", f"script_{idx}.js")

if __name__ == "__main__":
    # Replace this URL with the website you want to download assets from
    website_url = "https://example.com"
    extract_and_download_assets(website_url)

```

### Check Dynamic
```python
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialize Selenium WebDriver (make sure you have the appropriate driver installed)
driver = webdriver.Chrome()  # or webdriver.Firefox() based on your setup

# The website URL you want to test
url = "https://example.com"
driver.get(url)

# Allow some time for initial page load
time.sleep(2)

# Capture the initial HTML content
initial_html = driver.page_source

# For CSS, we pick an element to monitor (for example, the <body> tag)
body_elem = driver.find_element(By.TAG_NAME, "body")
# Get the computed background-color of the body element as an example property
initial_bg_color = driver.execute_script(
    "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color');",
    body_elem
)

# Wait for a few seconds to allow dynamic changes to occur
time.sleep(5)

# Capture the updated HTML content
updated_html = driver.page_source

# Check computed CSS property again
updated_bg_color = driver.execute_script(
    "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color');",
    body_elem
)

# Compare the HTML to see if it has changed
if initial_html != updated_html:
    print("The website's HTML has dynamically changed.")
else:
    print("The website's HTML remains unchanged.")

# Compare the CSS computed property for changes
if initial_bg_color != updated_bg_color:
    print("The website's CSS (background-color) has dynamically changed.")
else:
    print("The website's CSS (background-color) remains unchanged.")

# Clean up
driver.quit()

```

### Generate PDF
```python
from fpdf import FPDF

# Create a subclass of FPDF to customize header/footer if needed
class PDF(FPDF):
    def header(self):
        # Set up a logo, title, or other header content here if desired
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "My PDF Document", ln=True, align="C")
        self.ln(10)

    def footer(self):
        # Add a page number at the bottom of each page
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# Initialize PDF object
pdf = PDF()
pdf.add_page()
pdf.set_font("Arial", size=12)

# Sample content to add to the PDF
content = (
    "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
    "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
)

# Add content to the PDF using multi_cell for automatic text wrapping
pdf.multi_cell(0, 10, content)

# Save the PDF to a file
pdf.output("example_document.pdf")

print("PDF generated successfully as 'example_document.pdf'")

```
