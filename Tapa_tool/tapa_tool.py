#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tapa Tool

This module provides functionality to:
1. Extract parts requirements from documents
2. Search for matching parts on Mouser.com
3. Verify TAA compliance of found parts
4. Output TAA compliant parts to a structured format
"""

import os
import re
import csv
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime
import argparse
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tapa_tool.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("tapa_tool")

class RequirementsExtractor:
    """Extract parts requirements from specification documents."""
    
    def __init__(self, file_path: str):
        """
        Initialize with the path to the requirements document.
        
        Args:
            file_path (str): Path to the requirements document
        """
        self.file_path = file_path
        
    def extract(self) -> Dict[str, Dict[str, Any]]:
        """
        Extract parts requirements from the document.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of requirements by ID
        """
        # Check if file exists
        if not os.path.exists(self.file_path):
            logger.error(f"File not found: {self.file_path}")
            return {}
        
        # Determine file type based on extension
        _, file_ext = os.path.splitext(self.file_path)
        
        if file_ext.lower() in ['.txt', '.md']:
            return self._extract_from_text()
        elif file_ext.lower() in ['.csv']:
            return self._extract_from_csv()
        elif file_ext.lower() in ['.json']:
            return self._extract_from_json()
        else:
            logger.error(f"Unsupported file type: {file_ext}")
            return {}
    
    def _extract_from_text(self) -> Dict[str, Dict[str, Any]]:
        """Extract requirements from a text file."""
        requirements = {}
        
        try:
            with open(self.file_path, 'r') as f:
                content = f.read()
            
            # Try to extract requirements based on line format
            current_req_id = None
            current_req = {}
            
            # Check if the text has simple format like "REQ-001: Component description" on each line
            simple_req_pattern = re.compile(r'^([A-Za-z0-9\-_]+):\s*(.+)$', re.MULTILINE)
            simple_matches = simple_req_pattern.findall(content)
            
            if simple_matches:
                # Simple format detected
                for req_id, desc in simple_matches:
                    requirements[req_id] = {'description': [desc.strip()]}
                    
                    # Try to extract more structured info from the description
                    part_info = desc.split(',')
                    if len(part_info) > 1:
                        component_type = part_info[0].strip()
                        requirements[req_id]['component_type'] = [component_type]
                        
                        # Add specs as separate fields
                        for i, spec in enumerate(part_info[1:], 1):
                            spec = spec.strip()
                            requirements[req_id][f'spec_{i}'] = [spec]
            else:
                # Process line by line for more complex formats
                for line in content.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    
                    # New requirement starts with an ID pattern like "REQ-001:"
                    if re.match(r'^[A-Za-z0-9\-_]+:', line):
                        # Save previous requirement if exists
                        if current_req_id and current_req:
                            requirements[current_req_id] = current_req
                        
                        parts = line.split(':', 1)
                        current_req_id = parts[0].strip()
                        current_req = {}
                        
                        # Add description if available
                        if len(parts) > 1 and parts[1].strip():
                            current_req['description'] = [parts[1].strip()]
                    
                    # Parse specification lines (e.g., "Type: Capacitor", "Value: 10uF")
                    elif current_req_id and ":" in line:
                        key, value = [s.strip() for s in line.split(":", 1)]
                        key = key.lower().replace(" ", "_")
                        
                        if value:
                            if key in current_req:
                                if isinstance(current_req[key], list):
                                    current_req[key].append(value)
                                else:
                                    current_req[key] = [current_req[key], value]
                            else:
                                current_req[key] = [value]
                    
                    # Add non-specification lines to description
                    elif current_req_id and line:
                        if 'description' in current_req:
                            current_req['description'].append(line)
                        else:
                            current_req['description'] = [line]
                
                # Save the last requirement
                if current_req_id and current_req:
                    requirements[current_req_id] = current_req
        
        except Exception as e:
            logger.error(f"Error extracting requirements from text file: {e}")
        
        logger.info(f"Extracted {len(requirements)} requirements from {self.file_path}")
        return requirements
    
    def _extract_from_csv(self) -> Dict[str, Dict[str, Any]]:
        """Extract requirements from a CSV file."""
        requirements = {}
        
        try:
            df = pd.read_csv(self.file_path)
            
            # Identify the ID column
            id_column = None
            for col in df.columns:
                if 'id' in col.lower() or 'req' in col.lower() or 'part' in col.lower():
                    id_column = col
                    break
            
            if id_column is None and not df.empty:
                # Use the first column as ID if no obvious ID column
                id_column = df.columns[0]
            
            if id_column:
                for _, row in df.iterrows():
                    req_id = str(row[id_column])
                    req_data = {}
                    
                    for col in df.columns:
                        if col != id_column and not pd.isna(row[col]):
                            key = col.lower().replace(" ", "_")
                            value = str(row[col])
                            req_data[key] = [value]
                    
                    if req_data:
                        requirements[req_id] = req_data
        
        except Exception as e:
            logger.error(f"Error extracting requirements from CSV file: {e}")
        
        logger.info(f"Extracted {len(requirements)} requirements from {self.file_path}")
        return requirements
    
    def _extract_from_json(self) -> Dict[str, Dict[str, Any]]:
        """Extract requirements from a JSON file."""
        requirements = {}
        
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                # If the JSON is already in the format we need
                if all(isinstance(v, dict) for v in data.values()):
                    # Convert values to lists for consistency
                    requirements = {
                        k: {
                            sub_k: [sub_v] if not isinstance(sub_v, list) else sub_v
                            for sub_k, sub_v in v.items()
                        }
                        for k, v in data.items()
                    }
                # If the JSON has items under a key
                elif 'requirements' in data and isinstance(data['requirements'], dict):
                    requirements = {
                        k: {
                            sub_k: [sub_v] if not isinstance(sub_v, list) else sub_v
                            for sub_k, sub_v in v.items()
                        }
                        for k, v in data['requirements'].items()
                    }
                # If each key is a property, not a requirement ID
                else:
                    requirements['REQ-001'] = {
                        k: [v] if not isinstance(v, list) else v
                        for k, v in data.items()
                    }
            
            # If the JSON is a list of objects
            elif isinstance(data, list):
                for i, item in enumerate(data):
                    if isinstance(item, dict):
                        # Try to find an ID field, or use index as ID
                        req_id = None
                        for key in item:
                            if 'id' in key.lower() or 'req' in key.lower() or 'part' in key.lower():
                                req_id = str(item[key])
                                break
                        
                        if req_id is None:
                            req_id = f"REQ-{i+1:03d}"
                        
                        requirements[req_id] = {
                            k: [v] if not isinstance(v, list) else v
                            for k, v in item.items() if k.lower() != 'id'
                        }
        
        except Exception as e:
            logger.error(f"Error extracting requirements from JSON file: {e}")
        
        logger.info(f"Extracted {len(requirements)} requirements from {self.file_path}")
        return requirements


class MouserScraper:
    """Search for parts on Mouser.com based on requirements."""
    
    BASE_URL = "https://www.mouser.com"
    # Mouser API endpoints
    API_BASE_URL = "https://api.mouser.com/api/v1"
    SEARCH_API_URL = f"{API_BASE_URL}/search"
    PART_API_URL = f"{API_BASE_URL}/search/partnumber"
    
    def __init__(self, requirements: Dict[str, Any], api_key: str = None):
        """
        Initialize with part requirements.
        
        Args:
            requirements (Dict[str, Any]): Dictionary of part requirements
            api_key (str, optional): Mouser API key for making API requests
        """
        self.requirements = requirements
        self.api_key = api_key
        
        # For non-API (web scraping) requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://www.mouser.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        self.session = requests.Session()
    
    def build_search_query(self) -> str:
        """
        Convert requirements to a search query.
        
        Returns:
            str: Search query string
        """
        query_parts = []
        
        # Check if description field exists (common for text-based requirements)
        if 'description' in self.requirements and self.requirements['description']:
            desc = self.requirements['description'][0]
            # Just use the full description as the query
            query_parts.append(desc)
            
        # Add part number if available
        elif 'part_number' in self.requirements and self.requirements['part_number']:
            query_parts.append(self.requirements['part_number'][0])
            
        # Add component type if available
        elif 'component_type' in self.requirements and self.requirements['component_type']:
            query_parts.append(self.requirements['component_type'][0])
            
        # Add specifications if available and no specific part number
        elif not query_parts:
            for spec_type in ['resistance', 'capacitance', 'voltage', 'current']:
                if spec_type in self.requirements and self.requirements[spec_type]:
                    query_parts.append(self.requirements[spec_type][0])
        
        # If no structured fields found, try to use any available field
        if not query_parts:
            for key, value in self.requirements.items():
                if key != 'id' and value and isinstance(value, list) and value[0]:
                    query_parts.append(str(value[0]))
                    break
        
        query = ' '.join(query_parts)
        logger.info(f"Built search query: {query}")
        
        if not query.strip():
            logger.error("Could not build a search query from requirements")
            return ""
            
        return query

    def search_via_api(self) -> List[Dict[str, str]]:
        """
        Search for parts on Mouser.com using the official API.
        
        Returns:
            List[Dict[str, str]]: List of parts with names and links
        """
        if not self.api_key:
            logger.error("API key is required for API search. Set it with --mouser-api-key argument.")
            return []
        
        parts = []
        query = self.build_search_query()
        
        if not query:
            logger.error("Could not build a search query from requirements")
            return parts
        
        try:
            # Prepare API request payload
            search_payload = {
                "SearchByKeywordRequest": {
                    "keyword": query,
                    "records": 50,
                    "startingRecord": 0,
                    "searchOptions": "InStock",
                    "searchWithYourSignUpLanguage": "false"
                }
            }
            
            # API request headers
            api_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            logger.info(f"Searching Mouser API with query: {query}")
            response = requests.post(
                self.SEARCH_API_URL, 
                headers=api_headers, 
                json=search_payload
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to search Mouser API. Status code: {response.status_code}")
                logger.error(f"API Response: {response.text}")
                return parts
            
            # Parse JSON response
            data = response.json()
            search_results = data.get('SearchResults', {}).get('Parts', [])
            
            for result in search_results:
                try:
                    part = {
                        'name': result.get('Description', ''),
                        'part_number': result.get('MouserPartNumber', ''),
                        'manufacturer': result.get('Manufacturer', ''),
                        'link': f"{self.BASE_URL}/ProductDetail/{result.get('MouserPartNumber', '')}",
                        'price': result.get('PriceBreaks', [{}])[0].get('Price', '') if result.get('PriceBreaks') else '',
                        'stock': result.get('AvailabilityInStock', '0'),
                        'min_order': result.get('Min', '1')
                    }
                    
                    # Check if part data includes country of origin
                    if 'CountryOfOrigin' in result:
                        part['country_of_origin'] = result.get('CountryOfOrigin', '')
                    
                    parts.append(part)
                except Exception as e:
                    logger.error(f"Error parsing API search result: {e}")
            
            logger.info(f"Found {len(parts)} parts via API search")
            
        except Exception as e:
            logger.error(f"Error searching Mouser API: {e}")
        
        return parts
    
    def search_part_number_via_api(self, part_number: str) -> Dict[str, Any]:
        """
        Search for a specific part number on Mouser.com using the official API.
        
        Args:
            part_number (str): Part number to search for
            
        Returns:
            Dict[str, Any]: Part details if found, empty dict otherwise
        """
        if not self.api_key:
            logger.error("API key is required for API search")
            return {}
        
        try:
            # Prepare API request payload
            search_payload = {
                "SearchByPartRequest": {
                    "mouserPartNumber": part_number,
                }
            }
            
            # API request headers
            api_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': f'Bearer {self.api_key}'
            }
            
            logger.info(f"Searching Mouser API for part number: {part_number}")
            response = requests.post(
                self.PART_API_URL, 
                headers=api_headers, 
                json=search_payload
            )
            
            if response.status_code != 200:
                logger.error(f"Failed to search part number on Mouser API. Status code: {response.status_code}")
                return {}
            
            # Parse JSON response
            data = response.json()
            part_data = data.get('SearchResults', {}).get('Parts', [])
            
            if part_data and len(part_data) > 0:
                part = part_data[0]
                return {
                    'name': part.get('Description', ''),
                    'part_number': part.get('MouserPartNumber', ''),
                    'manufacturer': part.get('Manufacturer', ''),
                    'link': f"{self.BASE_URL}/ProductDetail/{part.get('MouserPartNumber', '')}",
                    'price': part.get('PriceBreaks', [{}])[0].get('Price', '') if part.get('PriceBreaks') else '',
                    'stock': part.get('AvailabilityInStock', '0'),
                    'country_of_origin': part.get('CountryOfOrigin', ''),
                    'min_order': part.get('Min', '1')
                }
            
        except Exception as e:
            logger.error(f"Error searching part number on Mouser API: {e}")
        
        return {}
        
    def search(self) -> List[Dict[str, str]]:
        """
        Search for parts on Mouser.com.
        
        Returns:
            List[Dict[str, str]]: List of parts with names and links
        """
        # If API key is available, use the API search method
        if self.api_key:
            logger.info("Using Mouser API for search")
            return self.search_via_api()
        
        # Otherwise, use the web scraping method (fallback)
        logger.warning("API key not provided, falling back to web scraping (may be unreliable)")
        query = self.build_search_query()
        
        if not query:
            logger.error("Could not build a search query from requirements")
            return []
        
        try:
            # Use a simple GET request to the main search URL
            search_url = f"{self.BASE_URL}/c/?q={urllib.parse.quote(query)}"
            
            logger.info(f"Searching Mouser with query: {query}")
            response = self.session.get(search_url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to search Mouser. Status code: {response.status_code}")
                return []
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Modern Mouser.com uses a different structure for search results
            # Look for product rows in the search results
            results = soup.select('.product-row')
            
            if not results:
                # Try alternative selectors if the first one didn't work
                results = soup.select('.mfr-part-number-table-row')
            
            if not results:
                # As a fallback, create simulated results for testing
                for i in range(1, 4):
                    part = {
                        'name': f"Simulated {query.split(',')[0]} #{i}",
                        'part_number': f"SIM{i}",
                        'link': f"{self.BASE_URL}/ProductDetail/SimulatedPart{i}",
                    }
                    parts.append(part)
                logger.warning("Using simulated parts for testing purposes only")
                return parts
            
            parts = []
            for result in results:
                try:
                    # Try to find elements using modern Mouser selectors
                    part_name_elem = result.select_one('.product-name, .product-description')
                    part_num_elem = result.select_one('.part-number, .mfr-part-number')
                    link_elem = result.select_one('a.text-nowrap, a.part-details')
                    
                    if part_name_elem and part_num_elem and link_elem:
                        part_name = part_name_elem.text.strip()
                        part_number = part_num_elem.text.strip()
                        link = self.BASE_URL + link_elem['href'] if link_elem['href'].startswith('/') else link_elem['href']
                        
                        # Create part dictionary
                        part = {
                            'name': part_name,
                            'part_number': part_number,
                            'link': link
                        }
                        
                        parts.append(part)
                except Exception as e:
                    logger.error(f"Error parsing search result: {e}")
            
        except Exception as e:
            logger.error(f"Error searching Mouser: {e}")
        
        return parts


class TAAComplianceChecker:
    """Check if parts are TAA compliant."""
    
    def __init__(self):
        """Initialize the TAA compliance checker."""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
    
    def check_compliance(self, part_url: str, part_data: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Check if a part is TAA compliant.
        
        Args:
            part_url (str): URL to the part detail page
            part_data (Dict[str, Any], optional): Part data that may contain compliance info
            
        Returns:
            Tuple[bool, str]: Whether the part is compliant and evidence text
        """
        # First check if compliance data is already available in the part data
        if part_data and 'is_taa_compliant' in part_data:
            is_compliant = bool(part_data['is_taa_compliant'])
            evidence = part_data.get('compliance_evidence', 'Compliance data from sample')
            return is_compliant, evidence
        
        # Otherwise, try to check compliance by scraping the product page
        try:
            logger.info(f"Checking TAA compliance for part at {part_url}")
            response = self.session.get(part_url, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to get part details. Status code: {response.status_code}")
                return False, f"Error: Status code {response.status_code}"
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for TAA compliance indicators in the page
            # This is highly dependent on how Mouser structures their pages
            taa_indicators = [
                "TAA Compliant",
                "Trade Agreement Act",
                "Complies with TAA",
                "Country of Origin: USA",
                "Made in USA",
                "Made in America"
            ]
            
            # Try to find the product details or specifications section
            product_text = ""
            details_section = soup.select_one('.product-details, .product-specs, .compliance-section')
            
            if details_section:
                product_text = details_section.text
            else:
                # If we can't find a specific section, just use the whole page
                product_text = soup.text
            
            # Check for TAA compliance indicators
            found_indicators = []
            for indicator in taa_indicators:
                if indicator.lower() in product_text.lower():
                    found_indicators.append(indicator)
            
            if found_indicators:
                evidence = "Found indicators: " + ", ".join(found_indicators)
                return True, evidence
            
            # Additional check for country of origin from TAA compliant countries
            taa_countries = [
                "United States", "USA", "Australia", "Austria", "Belgium", 
                "Bulgaria", "Canada", "Croatia", "Cyprus", "Czech Republic", 
                "Denmark", "Estonia", "Finland", "France", "Germany", 
                "Greece", "Hungary", "Ireland", "Israel", "Italy", 
                "Japan", "Latvia", "Lithuania", "Luxembourg", "Malta", 
                "Netherlands", "Norway", "Poland", "Portugal", "Romania", 
                "Singapore", "Slovakia", "Slovenia", "South Korea", "Spain", 
                "Sweden", "Switzerland", "Taiwan", "Ukraine", "United Kingdom",
                "Mexico", "Thailand"
            ]
            
            for country in taa_countries:
                if f"Country of Origin: {country}" in product_text or f"Country: {country}" in product_text:
                    return True, f"Country of Origin: {country} - TAA Compliant Country"
            
            # If we get here, no compliance indicators were found
            return False, "No TAA compliance indicators found"
            
        except Exception as e:
            logger.error(f"Error checking TAA compliance: {e}")
            return False, f"Error: {str(e)}"


def print_parts_table(parts, title, include_compliance=False):
    """Print a table of parts to the console."""
    print("\n" + "="*80)
    print(f"{title} ({len(parts)} found)")
    print("="*80)
    
    if not parts:
        print("No parts found.")
        return
    
    # Determine column widths
    name_width = max(len("Part Name"), max(len(p.get('name', '')) for p in parts))
    part_num_width = max(len("Part Number"), max(len(p.get('part_number', '')) for p in parts))
    link_width = min(50, max(len("Link"), max(len(p.get('link', '')) for p in parts)))
    
    # Print header
    if include_compliance:
        print(f"{'Part Name':<{name_width}} | {'Part Number':<{part_num_width}} | {'Link':<{link_width}} | TAA Status")
        print(f"{'-'*name_width} | {'-'*part_num_width} | {'-'*link_width} | {'-'*20}")
    else:
        print(f"{'Part Name':<{name_width}} | {'Part Number':<{part_num_width}} | {'Link':<{link_width}}")
        print(f"{'-'*name_width} | {'-'*part_num_width} | {'-'*link_width}")
    
    # Print rows
    for part in parts:
        name = part.get('name', '')[:name_width]
        part_number = part.get('part_number', '')
        link = part.get('link', '')[:link_width]
        
        if include_compliance:
            taa_status = f"{' Compliant' if part.get('taa_compliant', False) else ' Non-compliant'}"
            print(f"{name:<{name_width}} | {part_number:<{part_num_width}} | {link:<{link_width}} | {taa_status}")
        else:
            print(f"{name:<{name_width}} | {part_number:<{part_num_width}} | {link:<{link_width}}")
    
    print("="*80 + "\n")


def save_parts_to_csv(parts, filename):
    """Save parts to a CSV file."""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        
        # Get all field names from all parts
        fieldnames = set()
        for part in parts:
            fieldnames.update(part.keys())
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted(fieldnames))
            writer.writeheader()
            writer.writerows(parts)
            
        logger.info(f"Saved {len(parts)} parts to {filename}")
        return True
    
    except Exception as e:
        logger.error(f"Error saving parts to CSV {filename}: {e}")
        return False


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description="Tapa Tool - Extract requirements, search parts, and check TAA compliance")
    parser.add_argument("--input-file", required=True, help="Path to input requirements document")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "OUTPUT_FILES"), 
                        help="Directory for output files (defaults to Tapa_tool/OUTPUT_FILES)")
    parser.add_argument("--check-taa", action="store_true", help="Check TAA compliance of found parts")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--use-sample-data", action="store_true", help="Use sample data for testing instead of searching Mouser")
    parser.add_argument("--mouser-api-key", help="Mouser API key for making API requests")
    
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Configure file logging
    file_handler = logging.FileHandler(os.path.join(args.output_dir, 'tapa_tool.log'))
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(file_handler)
    
    # Extract requirements from input file
    print(f"Extracting requirements from {args.input_file}")
    extractor = RequirementsExtractor(args.input_file)
    requirements = extractor.extract()
    
    # Save requirements to JSON file
    requirements_file = os.path.join(args.output_dir, 'requirements.json')
    with open(requirements_file, 'w') as f:
        json.dump(requirements, f, indent=2)
    
    if requirements:
        print(f"Found {len(requirements)} requirements")
        print(f"Saved requirements to {requirements_file}")
        
        # Check if we should use sample data from the JSON file
        all_parts = []
        
        # See if this is a JSON file that already contains parts data for testing
        try:
            if args.input_file.endswith('.json') and args.use_sample_data:
                with open(args.input_file, 'r') as f:
                    data = json.load(f)
                    if 'parts' in data and isinstance(data['parts'], list):
                        all_parts = data['parts']
                        print(f"Using {len(all_parts)} sample parts from JSON file for testing")
        except Exception as e:
            logger.error(f"Error loading sample parts data: {e}")
            
        # If no sample data loaded, search for parts for each requirement
        if not all_parts:
            all_parts = []
            for req_id, req_data in requirements.items():
                print(f"Searching for parts matching requirement {req_id}")
                
                scraper = MouserScraper(req_data, api_key=args.mouser_api_key)
                parts = scraper.search()
                
                # Add requirement ID to each part
                for part in parts:
                    part['req_id'] = req_id
                
                all_parts.extend(parts)
                
                if parts:
                    print(f"Found {len(parts)} parts for requirement {req_id}")
                else:
                    print(f"No parts found for requirement {req_id}")
        
        # Print and save all parts
        print_parts_table(all_parts, "All Parts Matching Requirements")
        all_parts_file = os.path.join(args.output_dir, "all_parts.csv")
        save_parts_to_csv(all_parts, all_parts_file)
        
        # Check TAA compliance if requested
        if args.check_taa:
            print("\nChecking TAA compliance for all parts...")
            
            checker = TAAComplianceChecker()
            compliant_parts = []
            
            for part in all_parts:
                # If we're using sample data, pass the part data to use any included compliance info
                if args.use_sample_data:
                    is_compliant, evidence = checker.check_compliance(part.get('link', ''), part_data=part)
                else:
                    is_compliant, evidence = checker.check_compliance(part.get('link', ''))
                
                part['taa_compliant'] = is_compliant
                part['taa_evidence'] = evidence
                
                if is_compliant:
                    compliant_parts.append(part)
            
            # Save all parts with compliance info
            compliance_file = os.path.join(args.output_dir, "parts_with_compliance.csv")
            save_parts_to_csv(all_parts, compliance_file)
            
            # Print and save compliant parts
            if compliant_parts:
                print_parts_table(compliant_parts, "TAA Compliant Parts", include_compliance=True)
                compliant_file = os.path.join(args.output_dir, "taa_compliant_parts.csv")
                save_parts_to_csv(compliant_parts, compliant_file)
                print(f"Found {len(compliant_parts)} TAA compliant parts out of {len(all_parts)} total parts")
            else:
                print("No TAA compliant parts found.")
    
    print(f"\nResults saved to {args.output_dir}")
    return 0


if __name__ == "__main__":
    exit_code = main()
    exit(exit_code)
