# Import standard library modules
import time        # For adding delays
import re          # For regular expressions
import csv         # For CSV file operations

# Import Selenium components for web automation
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

# Import BeautifulSoup for HTML parsing
from bs4 import BeautifulSoup

# Import local configuration
import config

def setup_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    
    # Use the specific version from LinkedInNetworkScraper
    service = Service(ChromeDriverManager(version="136.0.7103.49").install())
    return webdriver.Chrome(service=service, options=options)


def get_price_from_url(driver, url):
    """
    Navigate to the given URL, wait for the page to load, and extract the first price found.
    
    Args:
        driver: Selenium WebDriver instance
        url (str): The URL to scrape for prices
        
    Returns:
        str: The first price found (with $) or 'N/A' if no price found or error occurs
    """
    try:
        driver.get(url)  # Navigate to the URL
        time.sleep(config.TIME_DELAY)  # Wait for the page to load
        page = driver.page_source  # Get the page HTML source
        
        # Search for price pattern in the page source
        # Matches: $12.34, $ 5, $1.99, etc.
        match = re.search(r"\$\s?[0-9]+(?:\.[0-9]{2})?", page)
        
        # Return the matched price (stripped of whitespace) or 'N/A' if no match
        return match.group().strip() if match else 'N/A'
    except Exception:
        # Return 'N/A' if any error occurs during the process
        return 'N/A'


def main():
    """
    Main function that orchestrates the price comparison process.
    Reads items from file, scrapes prices from different stores, and saves results to CSV.
    """
    # Read grocery items from text file
    with open(config.ITEMS_FILE, 'r') as f:
        # Create a list of non-empty, stripped lines from the file
        items = [line.strip() for line in f if line.strip()]

    # Open CSV file for writing comparison results
    with open(config.OUTPUT_CSV, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)  # Create CSV writer object
        # Write header row with column names
        writer.writerow(['Item', 'Albertsons', "Fry's", 'Walmart'])

        # Initialize the WebDriver
        driver = setup_driver()
        
        # Process each grocery item
        for item in items:
            print(f"Searching prices for: {item}")
            
            # URL-encode the search query (replace spaces with %20)
            query = item.replace(' ', '%20')
            
            # Define search URLs for each store using the query
            urls = {
                'Albertsons': f"{config.ALBERTSONS_URL}/shop/search-results.html?searchTerm={query}",
                "Fry's":    f"{config.FRYS_URL}/shop/search-results.html?searchTerm={query}",
                'Walmart':   f"{config.WALMART_URL}/search/?query={query}"
            }

            # Dictionary to store prices for the current item
            prices = {}
            
            # Get price from each store
            for store, url in urls.items():
                prices[store] = get_price_from_url(driver, url)

            # Write a row to CSV with item and its prices from all stores
            writer.writerow([
                item, 
                prices['Albertsons'], 
                prices["Fry's"], 
                prices['Walmart']
            ])
        
        # Close the WebDriver when done with all items
        driver.quit()

    # Print confirmation message with output file path
    print(f"Price comparison saved to {config.OUTPUT_CSV}")

# Standard Python idiom to execute main() when script is run directly
if __name__ == '__main__':
    main()
