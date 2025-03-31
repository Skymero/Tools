"""
Module to check if a website uses dynamic content loading with JavaScript.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def check_website_dynamic(url, wait_time=1):
    """
    Check if a website loads content dynamically.
    
    Args:
        url (str): The website URL to check
        wait_time (int): Time to wait for dynamic changes in seconds
        
    Returns:
        bool: True if the website is dynamic, False otherwise
    """
    # Set up Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    try:
        # Load the website
        driver.get(url)
        
        # Capture the initial HTML content
        initial_html = driver.page_source
        
        # For CSS, monitor the body element
        body_elem = driver.find_element(By.TAG_NAME, "body")
        initial_bg_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color');",
            body_elem
        )
        
        # Wait for potential dynamic changes
        time.sleep(wait_time)
        
        # Capture the updated HTML content
        updated_html = driver.page_source
        
        # Check computed CSS property again
        updated_bg_color = driver.execute_script(
            "return window.getComputedStyle(arguments[0]).getPropertyValue('background-color');",
            body_elem
        )
        
        # Compare for changes
        html_changed = initial_html != updated_html
        css_changed = initial_bg_color != updated_bg_color
        
        # Also check for AJAX requests
        ajax_requests = driver.execute_script(
            "return window.performance.getEntriesByType('resource')"
            ".filter(r => r.initiatorType === 'xmlhttprequest').length > 0"
        )
        
        # Check DOM modifications
        dom_modified = driver.execute_script(
            """
            const observer = new MutationObserver(() => {});
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true
            });
            // Return if any mutations were observed
            return observer.takeRecords().length > 0;
            """
        )
        
        return html_changed or css_changed or ajax_requests or dom_modified
        
    finally:
        # Clean up
        driver.quit()
