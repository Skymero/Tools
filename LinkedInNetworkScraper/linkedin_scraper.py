import time
import re
import csv
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import config

def login(driver):
    """Log in to LinkedIn using credentials from config."""
    driver.get("https://www.linkedin.com/login")
    time.sleep(2)
    email_elem = driver.find_element(By.ID, "username")
    email_elem.send_keys(config.EMAIL)
    pwd_elem = driver.find_element(By.ID, "password")
    pwd_elem.send_keys(config.PASSWORD)
    pwd_elem.send_keys(Keys.RETURN)
    time.sleep(5)

def get_connection_urls(driver):
    """Load all connections and return list of profile URLs."""
    driver.get("https://www.linkedin.com/mynetwork/invite-connect/connections/")
    time.sleep(5)
    # Scroll to load more connections
    scroll_pause = 2
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
    # Parse page source
    soup = BeautifulSoup(driver.page_source, "html.parser")
    profile_urls = []
    for a in soup.select("a.mn-connection-card__link"):
        href = a.get("href")
        if href and href.startswith("/in/"):
            profile_urls.append("https://www.linkedin.com" + href)
    return list(set(profile_urls))

def get_experiences(driver, profile_url):
    """Scrape the Experience section of a profile page."""
    driver.get(profile_url + "detail/experience/")
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    companies = []
    for a in soup.find_all("a", href=re.compile(r"/company/")):
        name = a.get_text().strip()
        href = a.get("href")
        url = "https://www.linkedin.com" + href.split("?")[0]
        companies.append((name, url))
    return list(set(companies))

def main():
    """Main execution: login, fetch connections, scrape experiences, save CSV."""
    # Initialize Chrome WebDriver with GPU disabled to suppress warnings
    opts = Options()
    opts.add_argument("--disable-gpu")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    try:
        login(driver)
        profiles = get_connection_urls(driver)
        all_companies = set()
        for url in profiles:
            try:
                experiences = get_experiences(driver, url)
                for comp in experiences:
                    all_companies.add(comp)
            except Exception as e:
                print(f"Error scraping {url}: {e}")
        # Write results to CSV
        with open("companies.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Company Name", "LinkedIn URL"])
            for name, link in sorted(all_companies):
                writer.writerow([name, link])
        print("Saved companies.csv")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
