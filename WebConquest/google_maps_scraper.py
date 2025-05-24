import csv
import time
import re
import os
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
SEARCH_QUERIES = ["HIGH END CONSULTANTS in tucson arizona", "welders in tucson arizona", "woodworkers in tucson arizona", "real estate agents in tucson arizona", "counselors in tucson arizona", "landscapers in tucson arizona", "car detailers in tucson arizona", "accountants in tucson arizona", "attorneys in tucson arizona", "plumbers in tucson arizona", "visual artists in tucson arizona", "dry cleaners in tucson arizona", "3D printer businesses in tucson arizona", "yoga studios in tucson arizona", "massage therapists in tucson arizona", "auto repair shops in tucson arizona", "donut shops in tucson arizona", "esthetician in tucson arizona", "pool maintanence in tucson arizona", "Deli stores in tucson arizona", "doggy day care centers in tucson arizona", "chiropractitioners in tucson arizona", "pawn shops in tucson arizona"  ]
DELAY_BETWEEN_ACTIONS = 5  # seconds (increased for better loading)
MAX_RESULTS = 3000  # Maximum number of results to process
MAX_SCROLL_ATTEMPTS = 20  # Increased scrolling to find more results
MAX_PAGINATION_PAGES = 60  # Number of pagination pages to navigate
CLICK_RETRY_ATTEMPTS = 5  # Number of times to retry clicking a stale element
WAIT_TIMEOUT = 10  # Maximum seconds to wait for an element


def setup_headless_browser():
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


def search_google_maps(browser, query):
    """
    Search Google Maps for a given query and return a list of up to MAX_RESULTS
    business listings as Selenium WebDriver elements. The search query is used
    to navigate to the Google Maps search page and the results are collected
    while scrolling through the results panel. The function takes a maximum
    number of results to process and a maximum number of pagination pages to
    navigate. The results are returned as a list of Selenium WebDriver elements
    which can be used to extract further information.
    """
    browser.get("https://www.google.com/maps")
    time.sleep(DELAY_BETWEEN_ACTIONS)
    print(f"Searching for: {query}")
    
    # Handle potential cookie consent or popup
    try:
        consent_buttons = browser.find_elements(By.XPATH, '//button[contains(text(), "Accept") or contains(text(), "I agree")]')
        if consent_buttons:
            consent_buttons[0].click()
            time.sleep(2)
    except Exception as e:
        print(f"No consent popup or error handling it: {e}")
    
    # Find and use the search box
    try:
        search_box = browser.find_element(By.ID, "searchboxinput")
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        print("Search query submitted")
    except Exception as e:
        print(f"Error with search box: {e}")
        return []
        
    # Wait longer for results to load
    time.sleep(DELAY_BETWEEN_ACTIONS * 3)
    print("Waiting for results to load...")
    
    all_result_blocks = []
    current_page = 1
    
    while current_page <= MAX_PAGINATION_PAGES and len(all_result_blocks) < MAX_RESULTS:
        print(f"\n--- Processing page {current_page} of results ---")
        
        # Try to find the results panel
        results_panel = None
        try:
            # Multiple possible selectors for the results panel
            selectors = [
                '//div[contains(@aria-label, "Results for")]',
                '//div[@role="feed"]',
                '//div[contains(@class, "section-result-content")]',
                '//div[@class="section-layout-root"]'
            ]
            
            for selector in selectors:
                elements = browser.find_elements(By.XPATH, selector)
                if elements:
                    results_panel = elements[0]
                    print(f"Found results panel with selector: {selector}")
                    break
                    
            if not results_panel:
                print("Could not find results panel with any selector")
                # Try scrolling the whole page instead
                for _ in range(MAX_SCROLL_ATTEMPTS):
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
        except Exception as e:
            print(f"Error finding results panel: {e}")
        
        # Scroll in the results panel if found, otherwise scroll the whole page
        print("Scrolling to load more results...")
        try:
            if results_panel:
                for i in range(MAX_SCROLL_ATTEMPTS):
                    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", results_panel)
                    print(f"Scroll attempt {i+1}/{MAX_SCROLL_ATTEMPTS}")
                    time.sleep(2)  # Longer pause between scrolls
            else:
                # Scroll the whole page
                for i in range(MAX_SCROLL_ATTEMPTS):
                    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    print(f"Page scroll attempt {i+1}/{MAX_SCROLL_ATTEMPTS}")
                    time.sleep(2)
        except Exception as e:
            print(f"Error while scrolling: {e}")
        
        # Try multiple selectors for business listings
        selectors = [
            '//div[contains(@aria-label, "Results for")]/div[contains(@role, "article")]',
            '//div[@role="article"]',
            '//div[contains(@class, "dbg0pd")]',  # Business names sometimes have this class
            '//a[contains(@href, "maps/place")]'  # Links to business details
        ]
        
        print("Attempting to find business listings...")
        result_blocks = []
        for selector in selectors:
            try:
                elements = browser.find_elements(By.XPATH, selector)
                if elements:
                    print(f"Found {len(elements)} business listings with selector: {selector}")
                    result_blocks = elements
                    break
            except Exception as e:
                print(f"Error with selector {selector}: {e}")
        
        # Add these results to our total
        if result_blocks:
            # Filter out duplicate entries that might already be in all_result_blocks
            # This is a basic deduplication using href attributes
            existing_hrefs = set()
            for existing_block in all_result_blocks:
                try:
                    href = existing_block.get_attribute('href')
                    if href:
                        existing_hrefs.add(href)
                except Exception:
                    pass
                    
            for block in result_blocks:
                try:
                    href = block.get_attribute('href')
                    if href and href not in existing_hrefs:
                        all_result_blocks.append(block)
                        existing_hrefs.add(href)
                        if len(all_result_blocks) >= MAX_RESULTS:
                            break
                except Exception:
                    all_result_blocks.append(block)
                    
            print(f"Added new unique results. Total results so far: {len(all_result_blocks)}")
        
        # Take screenshot for each page
        browser.save_screenshot(f"google_maps_result_page{current_page}.png")
        print(f"Screenshot saved as google_maps_result_page{current_page}.png")
        
        # Check if we have enough results already
        if len(all_result_blocks) >= MAX_RESULTS:
            print(f"Reached maximum result limit of {MAX_RESULTS}")
            break
            
        # Try to navigate to next page of results if available
        if current_page < MAX_PAGINATION_PAGES:
            try:
                # Look for next button with multiple possible selectors
                next_button_selectors = [
                    '//button[@aria-label="Next"]',
                    '//button[@jsaction="pane.paginationSection.nextPage"]',
                    '//button[contains(@class, "next-page")]',
                    '//button[contains(text(), "Next")]',
                    '//button[contains(@aria-label, "Next page")]',
                ]
                
                next_button = None
                for selector in next_button_selectors:
                    buttons = browser.find_elements(By.XPATH, selector)
                    if buttons and len(buttons) > 0:
                        next_button = buttons[0]
                        break
                        
                if next_button and next_button.is_enabled():
                    print("Clicking next page button...")
                    # Use JavaScript click to avoid interception issues
                    browser.execute_script("arguments[0].click();", next_button)
                    time.sleep(DELAY_BETWEEN_ACTIONS * 2)  # Wait for next page to load
                    current_page += 1
                else:
                    print("No more pages available or next button not found")
                    break
            except Exception as e:
                print(f"Error navigating to next page: {e}")
                break
        else:
            print(f"Reached maximum pagination limit of {MAX_PAGINATION_PAGES} pages")
            break
    
    # Return results up to the maximum
    max_to_return = min(len(all_result_blocks), MAX_RESULTS)
    print(f"Final count: Returning {max_to_return} business listings out of {len(all_result_blocks)} found across {current_page} pages")
    return all_result_blocks[:max_to_return]


def extract_business_info(result_block):
    """
    Extracts business information from a Google Maps result block
    :param result_block: Selenium WebElement representing the result block
    :return: dict with extracted information including name, phone, and website
    :raises: Exception if detail extraction fails
    """
    info = {"name": "", "phone": "", "website": None}
    
    # First get basic details directly from the listing
    try:
        # New approach to get the href attribute which often contains the business name
        href = result_block.get_attribute('href')
        if href and '/maps/place/' in href:
            # Extract business name from URL
            business_name_from_url = href.split('/maps/place/')[1].split('/')[0]
            business_name_from_url = business_name_from_url.replace('+', ' ')
            business_name_from_url = business_name_from_url.split(',')[0]  # Remove address parts
            if business_name_from_url:
                info["name"] = business_name_from_url
                print(f"Found business name from URL: {info['name']}")
    except Exception as e:
        print(f"Error extracting from URL: {e}")
    
    # If we couldn't get name from URL, try direct text content
    if not info["name"]:
        try:
            # Try to get direct text content of the element
            text_content = result_block.text
            if text_content:
                # The first line is often the business name
                lines = text_content.split('\n')
                if lines and lines[0].strip():
                    info["name"] = lines[0].strip()
                    print(f"Found business name from text: {info['name']}")
        except Exception as e:
            print(f"Error getting text content: {e}")
    
    # If still no name, try specific selectors
    if not info["name"]:
        name_selectors = [
            './/div[contains(@class, "fontHeadlineSmall")]',
            './/div[@role="heading"]',
            './/h3',
            './/div[contains(@class, "dbg0pd")]'
        ]
        
        for selector in name_selectors:
            try:
                elements = result_block.find_elements(By.XPATH, selector)
                if elements and elements[0].text.strip():
                    info["name"] = elements[0].text.strip()
                    print(f"Found business name from selector: {info['name']}")
                    break
            except Exception:
                continue
    
    # Click on the listing to get more details
    try:
        if info["name"]:
            print(f"Clicking on listing for: {info['name']}")
        else:
            print("Clicking on unnamed listing")
            
        # Store the current window handle before clicking
        browser = result_block.parent
        main_window = browser.current_window_handle
        
        # Create a reference to find the element again if it becomes stale
        element_xpath = None
        element_reference = None
        
        # Try to get a unique identifier for this element to find it again if needed
        try:
            # Get attributes that might help us identify this element later
            element_text = result_block.text
            element_class = result_block.get_attribute('class')
            element_aria_label = result_block.get_attribute('aria-label')
            
            # Build potential XPath expressions to find this element again
            xpath_candidates = []
            
            if element_aria_label:
                xpath_candidates.append(f"//div[@aria-label='{element_aria_label}']")
                
            if element_class:
                xpath_candidates.append(f"//div[@class='{element_class}']")
            
            if element_text and len(element_text) > 0:
                # Use the first line of text which is often the business name
                first_line = element_text.split('\n')[0].strip()
                if first_line:
                    xpath_candidates.append(f"//div[contains(text(), '{first_line}')]")
                    xpath_candidates.append(f"//div[.//text()[contains(., '{first_line}')]]")
            
            # If we have candidates, save the first one for future reference
            if xpath_candidates:
                element_xpath = xpath_candidates[0]
                print(f"Created reference XPath: {element_xpath}")
        except Exception as e:
            print(f"Error creating element reference: {e}")
        
        # Function to attempt clicking with retries
        def click_with_retry(element, max_attempts=CLICK_RETRY_ATTEMPTS):
            for attempt in range(max_attempts):
                try:
                    # First try JavaScript click which bypasses interception
                    browser.execute_script("arguments[0].click();", element)
                    return True
                except StaleElementReferenceException:
                    print(f"Stale element on attempt {attempt+1}, refreshing reference...")
                    # If we have an XPath, try to find the element again
                    if element_xpath:
                        try:
                            # Wait for the element to be present again
                            wait = WebDriverWait(browser, WAIT_TIMEOUT)
                            refreshed_element = wait.until(EC.presence_of_element_located((By.XPATH, element_xpath)))
                            element = refreshed_element  # Update the reference
                            continue  # Try again with the new reference
                        except (TimeoutException, NoSuchElementException):
                            print("Could not find element with saved XPath")
                    return False
                except Exception as e:
                    print(f"Click error on attempt {attempt+1}: {e}")
                    if attempt == max_attempts - 1:
                        return False
                    time.sleep(1)  # Brief pause before retrying
            return False
        
        # First attempt: Try direct click with retry logic
        click_success = click_with_retry(result_block)
        
        # Second attempt: If direct click failed, try alternative approaches
        if not click_success:
            print("Direct click failed, trying alternatives...")
            
            # Try clicking any overlaying elements first
            try:
                overlay_buttons = browser.find_elements(By.XPATH, '//button[@class="e2moi"]')
                if overlay_buttons:
                    print("Clicking overlay button first")
                    click_with_retry(overlay_buttons[0])
                    time.sleep(1)
            except Exception:
                pass
                
            # Try to find a clickable element within the result block
            try:
                clickable_elements = result_block.find_elements(By.XPATH, './/a | .//button')
                if clickable_elements:
                    print(f"Trying to click child element, found {len(clickable_elements)} options")
                    click_with_retry(clickable_elements[0])
            except StaleElementReferenceException:
                print("Result block became stale when finding child elements")
                # If we have an XPath, try one final approach with the parent
                if element_xpath:
                    try:
                        wait = WebDriverWait(browser, WAIT_TIMEOUT)
                        parent_element = wait.until(EC.presence_of_element_located((By.XPATH, element_xpath)))
                        click_with_retry(parent_element)
                    except Exception as e:
                        print(f"Final click attempt failed: {e}")
                        return info  # Continue with what data we have
            except Exception as e:
                print(f"Error finding clickable children: {e}")
                return info  # Continue with what data we have
                
        time.sleep(DELAY_BETWEEN_ACTIONS)  # Wait for details to load
        
        # Check if new tab/window opened
        handles = result_block.parent.window_handles
        if len(handles) > 1:
            # Switch to the new tab/window
            detail_window = [h for h in handles if h != main_window][0]
            browser.switch_to.window(detail_window)
        
        # Now in detail view, try to extract info from the page
        # Wait for the page to load completely
        try:
            wait = WebDriverWait(browser, WAIT_TIMEOUT)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except Exception as e:
            print(f"Error waiting for detail page to load: {e}")
            
        page_source = browser.page_source
        
        # Extract phone number from page source
        phone_patterns = [
            r'\(\d{3}\)\s\d{3}-\d{4}',  # (123) 456-7890
            r'\d{3}-\d{3}-\d{4}',          # 123-456-7890
            r'\+1\s\d{3}-\d{3}-\d{4}'      # +1 123-456-7890
        ]
        
        for pattern in phone_patterns:
            import re
            matches = re.findall(pattern, page_source)
            if matches:
                info["phone"] = matches[0]
                print(f"Found phone from pattern: {info['phone']}")
                break
        
        # Extract website URL
        # First try to find the website button and click it
        website_buttons = [
            '//a[contains(@aria-label, "Website")]',
            '//a[contains(@data-item-id, "authority")]',
            '//a[contains(text(), "Website")]',
            '//button[contains(text(), "Website")]'
        ]
        
        for selector in website_buttons:
            try:
                elements = browser.find_elements(By.XPATH, selector)
                if elements:
                    # Either get href directly or check if it's a button that needs clicking
                    href = elements[0].get_attribute('href')
                    if href and not href.startswith('https://www.google.com'):
                        info["website"] = href
                        print(f"Found website: {info['website']}")
                        break
            except Exception:
                continue
        
        # If no website found yet, look for patterns in page source
        if not info["website"]:
            website_patterns = [
                r'href="(https?://[^"]+)"[^>]*>\s*Website\s*<',
                r'data-url="(https?://[^"]+)"'
            ]
            
            for pattern in website_patterns:
                import re
                matches = re.findall(pattern, page_source)
                if matches:
                    for match in matches:
                        if not match.startswith('https://www.google.com'):
                            info["website"] = match
                            print(f"Found website from pattern: {info['website']}")
                            break
                    if info["website"]:
                        break
        
        # Return to main window if we switched
        if len(handles) > 1:
            browser.switch_to.window(main_window)
            
    except Exception as e:
        print(f"Error during detail extraction: {e}")
    
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
        writer_without.writerow(["Name", "Phone"])
        # Count for statistics
        without_website_count = 0
        for biz in businesses:
            print(f"Business record: {biz}")  # DEBUG: Show the business dict
            if not biz.get("website"):
                writer_without.writerow([biz.get("name", ""), biz.get("phone", "")])
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
            results = search_google_maps(browser, SEARCH_QUERY)
            
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
