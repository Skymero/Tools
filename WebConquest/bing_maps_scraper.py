import csv
import time
import re
import os
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException

# --- CONFIG ---
# SEARCH_QUERY = "private practice doctors glendale arizona"
#SEARCH_QUERIES = ["HIGH END CONSULTANTS in tucson arizona", "welders in tucson arizona", "woodworkers in tucson arizona", "real estate agents in tucson arizona", "counselors in tucson arizona", "landscapers in tucson arizona", "car detailers in tucson arizona", "accountants in tucson arizona", "attorneys in tucson arizona", "plumbers in tucson arizona", "visual artists in tucson arizona", "dry cleaners in tucson arizona", "3D printer businesses in tucson arizona", "yoga studios in tucson arizona", "massage therapists in tucson arizona", "auto repair shops in tucson arizona", "donut shops in tucson arizona", "esthetician in tucson arizona", "pool maintanence in tucson arizona", "Deli stores in tucson arizona", "doggy day care centers in tucson arizona", "chiropractitioners in tucson arizona", "pawn shops in tucson arizona"  ]
SEARCH_QUERIES = ["attorneys in arizona", "welders in phoenix az"]
DELAY_BETWEEN_ACTIONS = random.randint(4, 20)  # seconds (increased for better loading)
MAX_RESULTS = 2 # Maximum number of results to process
MAX_SCROLL_ATTEMPTS = 5  # Increased scrolling to find more results
MAX_PAGINATION_PAGES = 60  # Number of pagination pages to navigate
CLICK_RETRY_ATTEMPTS = 5  # Number of times to retry clicking a stale element
WAIT_TIMEOUT = 10  # Maximum seconds to wait for an element

# ---------------------------------------------------------------------------
#  Bing‑specific helper functions
# ---------------------------------------------------------------------------
def instagramFinder(businessName: str) -> str:
    """Return the Instagram username for ``businessName`` using **Bing** search."""
    driver = setup_headless_browser()
    username = "not_found"

    try:
        query = f"{businessName} site:instagram.com"
        driver.get(f"https://www.bing.com/search?q={query.replace(' ', '+')}")
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "instagram.com" in href and "/search?" not in href:
                m = re.search(r"instagram\.com/([^/?&#]+)", href)
                if m:
                    username = m.group(1)
                    break
    except Exception as e:
        print(f"[instagramFinder] {e}")
    finally:
        driver.quit()

    return username
def setup_headless_browser():
    """
    Set up a headless Chrome browser instance for web scraping.

    The browser is configured to be headless, use a specific user agent, and
    set a fixed window size. The browser is also configured to not use a
    sandbox, which can be useful for avoiding detection by websites.

    Returns:
        A headless Chrome browser instance.
    """
    options = Options()
    # Commenting out headless mode for testing - can see what's happening
    # options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--no-sandbox')
    options.add_argument('--log-level=3')
    # Add user agent to avoid detection
    options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36')
    service = Service(executable_path="./chromedriver.exe")
    browser = webdriver.Chrome(service=service, options=options)
    return browser


def search_bing_maps(browser, query):
    """
    Search **Bing Maps** for *query* and return a list (≤ ``MAX_RESULTS``)
    of result elements (``WebElement`` instances).

    The routine navigates to **https://www.bing.com/maps**, types the query in
    the site’s search box, waits for the result list to render, then scrolls
    and paginates until either the desired number of unique businesses is
    collected or ``MAX_PAGINATION_PAGES`` is reached.
    """
    browser.get("https://www.bing.com/maps")
    time.sleep(DELAY_BETWEEN_ACTIONS)
    print(f"Searching on Bing Maps for: {query}")

    # 1️⃣  Enter the query in Bing Maps’ search bar ---------------------------------
    try:
        # The input can be reliably grabbed by id="maps_sb" in 2025 UI.
        search_box = browser.find_element(By.ID, "maps_sb")
    except NoSuchElementException:
        # Fallback selector – any visible search <input> element.
        search_box = browser.find_element(By.XPATH, "//input[@type='search']")

    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)
    print("Query submitted… waiting for results panel")

    time.sleep(DELAY_BETWEEN_ACTIONS * 2)

    # 2️⃣  Collect results ------------------------------------------------------------
    all_result_blocks = []
    current_page = 1

    while current_page <= MAX_PAGINATION_PAGES and len(all_result_blocks) < MAX_RESULTS:
        print(f"\n— Bing page {current_page} —")

        # Locate the results list.  UI uses <ul class="entityList"> as of 2025.
        results_panel = None
        selectors = [
            "//ul[contains(@class, 'entityList')]",
            "//div[@aria-label='Results list']",
            "//div[@role='feed']"
        ]
        for sel in selectors:
            panels = browser.find_elements(By.XPATH, sel)
            if panels:
                results_panel = panels[0]
                break

        # Graceful degradation – scroll whole page if panel not located
        if not results_panel:
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        else:
            # Scroll inside panel to lazy‑load additional rows
            for _ in range(MAX_SCROLL_ATTEMPTS):
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", results_panel)
                time.sleep(1.5)

        # Capture list items (role=listitem) or anchor tiles linking to details
        item_selectors = [
            "//ul[contains(@class,'entityList')]/li",
            "//li[@role='listitem']",
            "//a[contains(@class,'bioCard')]"
        ]
        new_blocks = []
        for sel in item_selectors:
            try:
                els = browser.find_elements(By.XPATH, sel)
                if els:
                    new_blocks = els
                    break
            except Exception:
                continue

        # De‑duplicate by element id / href
        existing_ids = {b.id for b in all_result_blocks}
        for block in new_blocks:
            if block.id not in existing_ids:
                all_result_blocks.append(block)
                existing_ids.add(block.id)
            if len(all_result_blocks) >= MAX_RESULTS:
                break

        print(f"Collected {len(all_result_blocks)} unique businesses so far")

        if len(all_result_blocks) >= MAX_RESULTS:
            break

        # 3️⃣  Paginate – Bing uses a next‑page chevron button inside the panel
        try:
            next_btn = browser.find_element(By.XPATH, "//button[@title='Next page']")
            if next_btn.is_enabled():
                browser.execute_script("arguments[0].click();", next_btn)
                current_page += 1
                time.sleep(DELAY_BETWEEN_ACTIONS * 2)
                continue
        except NoSuchElementException:
            pass  # no paginator => break
        print("No further pages or next button not found – stopping pagination")
        break

    print(f"Returning {min(len(all_result_blocks), MAX_RESULTS)} Bing result elements")
    return all_result_blocks[:MAX_RESULTS]


def extract_business_info(result_block):
    """
    Extract **name**, **phone**, and **website** from a single Bing Maps result
    block.

    Bing’s HTML is a little different from Google’s; the title appears inside a
    descendant with class *entityTitle* (or an `<h3>`).  A phone icon button is
    usually rendered with `aria-label` containing the digits, and the website
    link has `aria-label="Website"` or appears inside `data-url` attributes.
    """
    info = {"name": "", "phone": "", "website": None}

    # --- Name ---------------------------------------------------------------------
    try:
        title_el = result_block.find_element(By.XPATH,
                                             ".//span[contains(@class,'entityTitle')] | .//h3")
        info["name"] = title_el.text.strip()
    except Exception:
        # Fallback – first visible line of text inside card
        text_lines = result_block.text.split("\n")
        if text_lines:
            info["name"] = text_lines[0].strip()

    # Click card to open details pane / pop‑out ------------------------------------
    browser = result_block.parent
    click_script = "arguments[0].click();"
    try:
        browser.execute_script(click_script, result_block)
    except StaleElementReferenceException:
        pass
    time.sleep(DELAY_BETWEEN_ACTIONS)

    # The side‑pane now contains richer HTML we can mine ---------------------------
    page_source = browser.page_source

    # --- Phone --------------------------------------------------------------------
    phone_patterns = [
        r"\(\d{3}\)\s?\d{3}-\d{4}",  # (123) 456‑7890
        r"\d{3}-\d{3}-\d{4}",          # 123‑456‑7890
        r"\+1\s\d{3}-\d{3}-\d{4}"     # +1 123‑456‑7890
    ]
    for pat in phone_patterns:
        match = re.search(pat, page_source)
        if match:
            info["phone"] = match.group(0)
            break
    
    # --- Instagram ------------------------------------------------------------------
    try:
        userIG = instagramFinder(info["name"])
        if userIG != "not_found":
            info["Instagram"] = userIG
        if userIG == "not_found":
            info["Instagram"] = 'not_found'
    except Exception:
        info["Instagram"] = 'not_found'

    # --- Website ------------------------------------------------------------------
    try:
        website_link = browser.find_element(By.XPATH,
                                            "//a[contains(@aria-label,'Website')] | //a[contains(text(),'Website')]")
        href = website_link.get_attribute("href")
        if href and not href.startswith("https://www.bing.com"):
            info["website"] = href
    except NoSuchElementException:
        # Fallback regex in page_source
        site_match = re.search(r"https?://[\w.-]+", page_source)
        if site_match:
            info["website"] = site_match.group(0)

    return info


def categorize_and_save_to_csv(businesses, search_query=None):
    # Use the search query to create a filename-friendly string
    """
    Categorize the businesses into two CSV files based on whether they have a
    website or not. The files are saved in the "results" directory with
    filenames based on the search query.

    Args:
        businesses (list[dict]): A list of dictionaries containing business
            information, with each dictionary having at least the keys "name"
            and "phone". The dictionary may also contain the key "website" if
            the business has a website.
        search_query (str, optional): The search query used to obtain the
            businesses. If not provided, the global SEARCH_QUERY variable is
            used.

    """
    if search_query is None:
        search_query = SEARCH_QUERY  # Default to global SEARCH_QUERY if not provided
    
    # Convert the search query to a valid filename by replacing invalid characters
    # and converting to lowercase for consistency
    filename_base = re.sub(r'[^\w\s-]', '', search_query.lower())
    filename_base = re.sub(r'[\s-]+', '_', filename_base)
    
    # Create output directory if it doesn't exist
    output_dir = 'results'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create the filenames with the search query
    # with_website_filename = os.path.join(output_dir, f"{filename_base}_with_website.csv")  # COMMENTED OUT: Disabling generation of with_website CSV file
    without_website_filename = os.path.join(output_dir, f"{filename_base}_without_website.csv")
    
    print(f"Saving results to:\n - {without_website_filename}")  # COMMENTED OUT: Removed with_website_filename
    
    # Save the data to the CSV files
    with open(without_website_filename, "w", newline='', encoding='utf-8') as f_without:
        writer_without = csv.writer(f_without)
        writer_without.writerow(["Name", "Phone", "Instagram"])
        # Count for statistics
        without_website_count = 0
        for biz in businesses:            
            print(f"Business record: {biz}")  # DEBUG: Show the business dict
            if not biz.get("website"):
                writer_without.writerow([biz.get("name", ""), biz.get("phone", ""), biz.get("Instagram", "")])
                without_website_count += 1
        # print(f"Saved {with_website_count} businesses with websites")  # COMMENTED OUT
        print(f"Saved {without_website_count} businesses without websites")
    # COMMENTED OUT: All logic for with_website_filename CSV file

def main():
    
    """
    Main entry point for the script. Uses the configured SEARCH_QUERIES to search
    Google Maps, processes each result to extract business information, and saves
    the results to CSV files named after the search query.

    The function catches any exceptions that occur during execution and prints
    an error message before quitting the Selenium browser session.
    """
    browser = setup_headless_browser()
    try:
        for SEARCH_QUERY in SEARCH_QUERIES:
            # Search for businesses using the configured query
            print(f"Starting search for: {SEARCH_QUERY}")
            results = search_bing_maps(browser, SEARCH_QUERY)
            
            # Process each result to extract business information
            businesses = []
            for i, result in enumerate(results):
                print(f"Processing business {i+1}/{len(results)}...")
                info = extract_business_info(result)
                businesses.append(info)
            
            # Save the results to CSV files named after the search query
            categorize_and_save_to_csv(businesses, SEARCH_QUERY)
            print(f"Done! {len(businesses)} businesses processed.")
    except Exception as e:
        print(f"An error occurred during execution: {e}")
    finally:
        browser.quit()


if __name__ == "__main__":
    main()
