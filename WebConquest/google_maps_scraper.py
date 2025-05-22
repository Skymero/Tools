import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException

# --- CONFIG ---
SEARCH_QUERY = "small businesses in tempe, az"
DELAY_BETWEEN_ACTIONS = 5  # seconds (increased for better loading)
MAX_RESULTS = 500  # Maximum number of results to process
MAX_SCROLL_ATTEMPTS = 20  # Increased scrolling to find more results
MAX_PAGINATION_PAGES = 3  # Number of pagination pages to navigate


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
        main_window = result_block.parent.current_window_handle
        
        # Use JavaScript to click instead of regular click to avoid interception
        try:
            # First try JavaScript click which bypasses interception
            result_block.parent.execute_script("arguments[0].click();", result_block)
        except Exception as e:
            print(f"JavaScript click failed, trying alternative: {e}")
            try:
                # Try clicking any overlaying elements first
                overlay_buttons = result_block.parent.find_elements(By.XPATH, '//button[@class="e2moi"]')
                if overlay_buttons:
                    print("Clicking overlay button first")
                    result_block.parent.execute_script("arguments[0].click();", overlay_buttons[0])
                    time.sleep(1)
                # Then try clicking the listing again
                result_block.parent.execute_script("arguments[0].click();", result_block)
            except Exception as e2:
                print(f"All click attempts failed: {e2}")
                # Just continue with what data we have
                return info
                
        time.sleep(DELAY_BETWEEN_ACTIONS)  # Wait for details to load
        
        # Check if new tab/window opened
        handles = result_block.parent.window_handles
        if len(handles) > 1:
            # Switch to the new tab/window
            detail_window = [h for h in handles if h != main_window][0]
            result_block.parent.switch_to.window(detail_window)
        
        # Now in detail view, try to extract info from the page
        page_source = result_block.parent.page_source
        
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
                elements = result_block.parent.find_elements(By.XPATH, selector)
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
            result_block.parent.switch_to.window(main_window)
            
    except Exception as e:
        print(f"Error during detail extraction: {e}")
    
    return info


def categorize_and_save_to_csv(businesses):
    with open("with_website.csv", "w", newline='', encoding='utf-8') as f_with, \
         open("without_website.csv", "w", newline='', encoding='utf-8') as f_without:
        writer_with = csv.writer(f_with)
        writer_without = csv.writer(f_without)
        writer_with.writerow(["Name", "Phone", "Website"])
        writer_without.writerow(["Name", "Phone"])
        for biz in businesses:
            if biz["website"]:
                writer_with.writerow([biz["name"], biz["phone"], biz["website"]])
            else:
                writer_without.writerow([biz["name"], biz["phone"]])


def main():
    browser = setup_headless_browser()
    try:
        results = search_google_maps(browser, SEARCH_QUERY)
        businesses = []
        for result in results:
            info = extract_business_info(result)
            businesses.append(info)
        categorize_and_save_to_csv(businesses)
        print(f"Done! {len(businesses)} businesses processed.")
    finally:
        browser.quit()


if __name__ == "__main__":
    main()
