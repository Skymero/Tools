"""
Module to extract HTML, CSS, and JavaScript from websites.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def download_file(url, folder, filename, session=None):
    """
    Download a file from a URL and save it locally.
    
    Args:
        url (str): The URL of the file to download
        folder (str): The folder to save the file in
        filename (str): The name to save the file as
        session (requests.Session, optional): Session object for making requests
        
    Returns:
        str: The path to the downloaded file, or None if download failed
    """
    try:
        if session is None:
            session = requests
            
        response = session.get(url, timeout=10)
        if response.status_code == 200:
            os.makedirs(folder, exist_ok=True)
            filepath = os.path.join(folder, filename)
            
            # Determine if content is binary or text
            content_type = response.headers.get('content-type', '').lower()
            is_binary = not ('text' in content_type or 
                            'javascript' in content_type or 
                            'json' in content_type or 
                            'xml' in content_type or
                            'css' in content_type)
            
            mode = 'wb' if is_binary else 'w'
            encoding = None if is_binary else 'utf-8'
            
            with open(filepath, mode, encoding=encoding) as f:
                if is_binary:
                    f.write(response.content)
                else:
                    f.write(response.text)
                    
            print(f"Downloaded {url} to {filepath}")
            return filepath
        else:
            print(f"Failed to download {url}, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading {url}: {str(e)}")
        return None

def get_filename_from_url(url, default_name=None, default_ext=None):
    """
    Extract a filename from a URL, or generate one if not possible.
    
    Args:
        url (str): The URL to extract filename from
        default_name (str, optional): Default name if extraction fails
        default_ext (str, optional): Default extension if extraction fails
        
    Returns:
        str: The extracted or generated filename
    """
    parsed_url = urlparse(url)
    path = parsed_url.path
    
    # Try to extract filename from path
    if path and '/' in path:
        filename = path.split('/')[-1]
        if '.' in filename:
            return filename
    
    # If we couldn't extract a filename with extension
    if default_name is None:
        # Generate a hash of the URL
        import hashlib
        default_name = hashlib.md5(url.encode()).hexdigest()[:10]
        
    if default_ext is None:
        # Try to guess extension from content type
        if 'css' in url:
            default_ext = '.css'
        elif 'js' in url:
            default_ext = '.js'
        else:
            default_ext = '.txt'
            
    return f"{default_name}{default_ext}"

def extract_static_website(url, output_dir):
    """
    Extract content from a static website using BeautifulSoup.
    
    Args:
        url (str): The URL of the website to extract
        output_dir (str): The directory to save extracted files
        
    Returns:
        dict: A dictionary of extracted file paths by type
    """
    # Create session for maintaining cookies
    session = requests.Session()
    
    # Fetch the main HTML content
    response = session.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return {}
    
    html_content = response.text
    
    # Save the HTML file
    html_dir = os.path.join(output_dir, "html")
    os.makedirs(html_dir, exist_ok=True)
    html_path = os.path.join(html_dir, "page.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Downloaded main HTML to {html_path}")

    # Parse HTML to extract assets
    soup = BeautifulSoup(html_content, "html.parser")
    
    extracted_files = {
        'html': [html_path],
        'css': [],
        'js': [],
        'images': [],
        'other': []
    }

    # Extract and download CSS files
    css_dir = os.path.join(output_dir, "css")
    css_links = [link.get('href') for link in soup.find_all("link", rel="stylesheet") if link.get('href')]
    for idx, css_link in enumerate(css_links):
        full_css_url = urljoin(url, css_link)
        filename = get_filename_from_url(css_link, f"style_{idx}", ".css")
        css_path = download_file(full_css_url, css_dir, filename, session)
        if css_path:
            extracted_files['css'].append(css_path)

    # Extract and download JS files
    js_dir = os.path.join(output_dir, "js")
    js_links = [script.get('src') for script in soup.find_all("script", src=True)]
    for idx, js_link in enumerate(js_links):
        full_js_url = urljoin(url, js_link)
        filename = get_filename_from_url(js_link, f"script_{idx}", ".js")
        js_path = download_file(full_js_url, js_dir, filename, session)
        if js_path:
            extracted_files['js'].append(js_path)
    
    # Extract and download images
    img_dir = os.path.join(output_dir, "images")
    img_links = [img.get('src') for img in soup.find_all("img", src=True)]
    for idx, img_link in enumerate(img_links):
        full_img_url = urljoin(url, img_link)
        filename = get_filename_from_url(img_link, f"image_{idx}", ".jpg")
        img_path = download_file(full_img_url, img_dir, filename, session)
        if img_path:
            extracted_files['images'].append(img_path)

    # Extract inline CSS and JavaScript
    inline_css_dir = os.path.join(output_dir, "css")
    inline_js_dir = os.path.join(output_dir, "js")
    
    # Extract inline CSS
    inline_css = soup.find_all("style")
    for idx, style in enumerate(inline_css):
        if style.string:
            inline_css_path = os.path.join(inline_css_dir, f"inline_style_{idx}.css")
            os.makedirs(inline_css_dir, exist_ok=True)
            with open(inline_css_path, "w", encoding="utf-8") as f:
                f.write(style.string)
            print(f"Extracted inline CSS to {inline_css_path}")
            extracted_files['css'].append(inline_css_path)
    
    # Extract inline JavaScript
    inline_js = [script for script in soup.find_all("script") if not script.get('src') and script.string]
    for idx, script in enumerate(inline_js):
        if script.string:
            inline_js_path = os.path.join(inline_js_dir, f"inline_script_{idx}.js")
            os.makedirs(inline_js_dir, exist_ok=True)
            with open(inline_js_path, "w", encoding="utf-8") as f:
                f.write(script.string)
            print(f"Extracted inline JavaScript to {inline_js_path}")
            extracted_files['js'].append(inline_js_path)
    
    return extracted_files

def extract_dynamic_website(url, output_dir):
    """
    Extract content from a dynamic website using Selenium.
    
    Args:
        url (str): The URL of the website to extract
        output_dir (str): The directory to save extracted files
        
    Returns:
        dict: A dictionary of extracted file paths by type
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
        
        # Wait for the page to load fully
        driver.implicitly_wait(5)
        
        # Get the fully rendered HTML content
        html_content = driver.page_source
        
        # Create BeautifulSoup object from the rendered HTML
        soup = BeautifulSoup(html_content, "html.parser")
        
        # Save the HTML file
        html_dir = os.path.join(output_dir, "html")
        os.makedirs(html_dir, exist_ok=True)
        html_path = os.path.join(html_dir, "page.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Downloaded main HTML to {html_path}")
        
        extracted_files = {
            'html': [html_path],
            'css': [],
            'js': [],
            'images': [],
            'other': []
        }
        
        # Get all network resources loaded by the page
        resources = driver.execute_script(
            "return window.performance.getEntriesByType('resource');"
        )
        
        # Create a session for downloading files
        session = requests.Session()
        
        # Extract resource URLs by type
        for resource in resources:
            try:
                resource_url = resource['name']
                resource_type = resource.get('initiatorType', '')
                
                if 'css' in resource_url.lower() or resource_type == 'css':
                    # CSS resource
                    css_dir = os.path.join(output_dir, "css")
                    filename = get_filename_from_url(resource_url, f"style_{len(extracted_files['css'])}", ".css")
                    css_path = download_file(resource_url, css_dir, filename, session)
                    if css_path:
                        extracted_files['css'].append(css_path)
                        
                elif 'js' in resource_url.lower() or resource_type == 'script':
                    # JavaScript resource
                    js_dir = os.path.join(output_dir, "js")
                    filename = get_filename_from_url(resource_url, f"script_{len(extracted_files['js'])}", ".js")
                    js_path = download_file(resource_url, js_dir, filename, session)
                    if js_path:
                        extracted_files['js'].append(js_path)
                        
                elif any(img_ext in resource_url.lower() for img_ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']):
                    # Image resource
                    img_dir = os.path.join(output_dir, "images")
                    filename = get_filename_from_url(resource_url, f"image_{len(extracted_files['images'])}")
                    img_path = download_file(resource_url, img_dir, filename, session)
                    if img_path:
                        extracted_files['images'].append(img_path)
                        
                else:
                    # Other resource
                    other_dir = os.path.join(output_dir, "other")
                    filename = get_filename_from_url(resource_url, f"resource_{len(extracted_files['other'])}")
                    other_path = download_file(resource_url, other_dir, filename, session)
                    if other_path:
                        extracted_files['other'].append(other_path)
            except Exception as e:
                print(f"Error processing resource: {str(e)}")
        
        # Extract inline CSS and JavaScript (similar to static extraction)
        inline_css_dir = os.path.join(output_dir, "css")
        inline_js_dir = os.path.join(output_dir, "js")
        
        # Extract inline CSS
        inline_css = soup.find_all("style")
        for idx, style in enumerate(inline_css):
            if style.string:
                inline_css_path = os.path.join(inline_css_dir, f"inline_style_{idx}.css")
                os.makedirs(inline_css_dir, exist_ok=True)
                with open(inline_css_path, "w", encoding="utf-8") as f:
                    f.write(style.string)
                print(f"Extracted inline CSS to {inline_css_path}")
                extracted_files['css'].append(inline_css_path)
        
        # Extract inline JavaScript
        inline_js = [script for script in soup.find_all("script") if not script.get('src') and script.string]
        for idx, script in enumerate(inline_js):
            if script.string:
                inline_js_path = os.path.join(inline_js_dir, f"inline_script_{idx}.js")
                os.makedirs(inline_js_dir, exist_ok=True)
                with open(inline_js_path, "w", encoding="utf-8") as f:
                    f.write(script.string)
                print(f"Extracted inline JavaScript to {inline_js_path}")
                extracted_files['js'].append(inline_js_path)
        
        return extracted_files
        
    finally:
        # Clean up
        driver.quit()
