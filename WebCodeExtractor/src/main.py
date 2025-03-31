#!/usr/bin/env python3
"""
Lupin the 1st - Website Content Extractor
A tool that extracts HTML, CSS, and JavaScript code from a website.
"""

import os
import argparse
from check_dynamic import check_website_dynamic
from extractor import extract_static_website, extract_dynamic_website
from pdf_generator import generate_pdf

def main():
    """Main entry point for the Lupin the 1st tool."""
    parser = argparse.ArgumentParser(
        description="Lupin the 1st - Extract HTML, CSS, and JavaScript from websites"
    )
    parser.add_argument("url", help="URL of the website to extract")
    parser.add_argument(
        "-o", "--output", 
        default="output", 
        help="Output directory for extracted files (default: output)"
    )
    parser.add_argument(
        "--pdf", 
        action="store_true", 
        help="Generate a PDF report of the extracted content"
    )
    args = parser.parse_args()

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    print(f"Extracting content from {args.url}")
    
    # Check if the website is dynamic
    is_dynamic = check_website_dynamic(args.url)
    
    if is_dynamic:
        print("Detected dynamic website. Using Selenium for extraction...")
        extracted_files = extract_dynamic_website(args.url, args.output)
    else:
        print("Detected static website. Using BeautifulSoup for extraction...")
        extracted_files = extract_static_website(args.url, args.output)
    
    print(f"Extraction complete. Files saved to {args.output}")
    
    # Generate PDF if requested
    if args.pdf:
        pdf_path = os.path.join(args.output, "website_content.pdf")
        generate_pdf(extracted_files, pdf_path)
        print(f"PDF report generated at {pdf_path}")

if __name__ == "__main__":
    main()
