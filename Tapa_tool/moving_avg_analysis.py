#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Moving Average Analysis Tool for TapaTool

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
import sys
from bs4 import BeautifulSoup
from typing import Dict, List, Tuple, Any, Optional
import logging
from datetime import datetime, timedelta
import random
import time

# Add new_benner directory to path to import StockData
new_benner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'new_benner')
sys.path.append(new_benner_path)
analysis_tools_path = os.path.join(new_benner_path, 'Analysis Tools')
sys.path.append(analysis_tools_path)

# Import StockData from pe_analyzer
try:
    from pe_analyzer import StockData
    HAS_STOCK_DATA = True
    print("✅ Successfully imported StockData from Benner Cycle project")
except ImportError as e:
    HAS_STOCK_DATA = False
    print(f"⚠️ Could not import StockData from Benner Cycle project: {e}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tapa_tool.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("moving_avg_analysis")

class MarketDataCollector:
    """Collect market data using StockData from Benner Cycle project"""
    
    def __init__(self, symbol=None, years=5):
        """
        Initialize with stock symbol and analysis period.
        
        Args:
            symbol (str, optional): Stock symbol to analyze
            years (int): Number of years of historical data to retrieve
        """
        self.symbol = symbol
        self.years = years
        self.stock_data = None
        self.data_available = False
        
    def collect_data(self, symbol=None, years=None):
        """
        Collect market data using StockData from Benner Cycle project.
        
        Args:
            symbol (str, optional): Stock symbol to override the instance symbol
            years (int, optional): Years of data to override the instance years
            
        Returns:
            bool: True if data collection successful, False otherwise
        """
        if not HAS_STOCK_DATA:
            logger.error("StockData from Benner Cycle project not available")
            return False
            
        # Use provided values or instance values
        symbol = symbol or self.symbol
        years = years or self.years
        
        if not symbol:
            logger.error("No symbol provided for data collection")
            return False
            
        try:
            logger.info(f"Collecting market data for {symbol} over {years} years")
            self.stock_data = StockData(symbol, years)
            success = self.stock_data.download_data()
            
            if success and self.stock_data.valid:
                self.data_available = True
                logger.info(f"Successfully collected data for {symbol}")
                return True
            else:
                logger.warning(f"Failed to collect data for {symbol}")
                return False
                
        except Exception as e:
            logger.error(f"Error collecting market data: {e}")
            return False
            
    def get_price_data(self):
        """Get the price data DataFrame"""
        if not self.data_available or not self.stock_data or not hasattr(self.stock_data, 'price_data'):
            return None
        return self.stock_data.price_data
        
    def get_earnings_data(self):
        """Get the earnings data DataFrame"""
        if not self.data_available or not self.stock_data or not hasattr(self.stock_data, 'earnings_data'):
            return None
        return self.stock_data.earnings_data
        
    def get_info(self):
        """Get company/asset information"""
        if not self.data_available or not self.stock_data or not hasattr(self.stock_data, 'info'):
            return {}
        return self.stock_data.info
        
    def save_data(self, output_path):
        """
        Save the collected data to CSV.
        
        Args:
            output_path (str): Path to save the CSV file
        """
        if not self.data_available or self.stock_data is None:
            logger.warning("No data available to save")
            return False
            
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            
            # Save price data
            if hasattr(self.stock_data, 'price_data') and self.stock_data.price_data is not None:
                self.stock_data.price_data.to_csv(output_path)
                logger.info(f"Saved price data to {output_path}")
                return True
            else:
                logger.warning("No price data available to save")
                return False
                
        except Exception as e:
            logger.error(f"Error saving data: {e}")
            return False

class RequirementsExtractor:
    """Extract parts requirements from specification documents."""
    
    def __init__(self, file_path: str):
        """
        Initialize with the path to the requirements document.
        
        Args:
            file_path (str): Path to the requirements document
        """
        self.file_path = file_path
        self.requirements = {}
        
    def extract_from_txt(self) -> Dict[str, Any]:
        """Extract requirements from a text file."""
        requirements = {}
        
        try:
            with open(self.file_path, 'r') as file:
                content = file.read()
                
                # Look for part numbers
                part_numbers = re.findall(r'Part\s*(?:Number|No|#)?\s*:\s*([A-Za-z0-9\-]+)', content, re.IGNORECASE)
                if part_numbers:
                    requirements['part_number'] = part_numbers
                
                # Look for component types
                component_types = re.findall(r'Component\s*Type\s*:\s*([A-Za-z0-9\-\s]+)', content, re.IGNORECASE)
                if component_types:
                    requirements['component_type'] = [ct.strip() for ct in component_types]
                
                # Look for specifications
                specs = {
                    'resistance': re.findall(r'(\d+(?:\.\d+)?\s*(?:ohm|Ω|kΩ|MΩ))', content, re.IGNORECASE),
                    'capacitance': re.findall(r'(\d+(?:\.\d+)?\s*(?:pF|nF|µF|uF|F))', content, re.IGNORECASE),
                    'voltage': re.findall(r'(\d+(?:\.\d+)?\s*(?:V|kV|mV))', content, re.IGNORECASE),
                    'current': re.findall(r'(\d+(?:\.\d+)?\s*(?:A|mA|µA|uA))', content, re.IGNORECASE),
                    'tolerance': re.findall(r'(\d+(?:\.\d+)?\s*%)', content),
                    'temperature': re.findall(r'(\-?\d+(?:\.\d+)?\s*(?:°C|C))', content),
                }
                
                # Add non-empty specs to requirements
                requirements.update({k: v for k, v in specs.items() if v})
                
                logger.info(f"Extracted requirements: {requirements}")
                return requirements
                
        except Exception as e:
            logger.error(f"Error extracting requirements from {self.file_path}: {e}")
            return {}
            
    def extract_from_csv(self) -> Dict[str, Any]:
        """Extract requirements from a CSV file."""
        try:
            df = pd.read_csv(self.file_path)
            requirements = df.to_dict(orient='list')
            logger.info(f"Extracted requirements from CSV: {requirements}")
            return requirements
        except Exception as e:
            logger.error(f"Error extracting requirements from CSV {self.file_path}: {e}")
            return {}
    
    def extract(self) -> Dict[str, Any]:
        """
        Extract requirements based on file type.
        
        Returns:
            Dict[str, Any]: Dictionary of requirements
        """
        if self.file_path.endswith('.txt'):
            self.requirements = self.extract_from_txt()
        elif self.file_path.endswith('.csv'):
            self.requirements = self.extract_from_csv()
        else:
            logger.error(f"Unsupported file type: {self.file_path}")
            self.requirements = {}
            
        return self.requirements


class MouserScraper:
    """Search for parts on Mouser.com based on requirements."""
    
    BASE_URL = "https://www.mouser.com"
    SEARCH_URL = f"{BASE_URL}/ProductSearch/Refine"
    
    def __init__(self, requirements: Dict[str, Any]):
        """
        Initialize with part requirements.
        
        Args:
            requirements (Dict[str, Any]): Dictionary of part requirements
        """
        self.requirements = requirements
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.mouser.com/',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        
        # Create MarketDataCollector for component stock data if available
        self.market_data = MarketDataCollector() if HAS_STOCK_DATA else None
        
    def build_search_query(self) -> str:
        """
        Convert requirements to a search query.
        
        Returns:
            str: Search query string
        """
        query_parts = []
        
        # Add part number if available
        if 'part_number' in self.requirements and self.requirements['part_number']:
            query_parts.append(self.requirements['part_number'][0])
            
        # Add component type if available
        elif 'component_type' in self.requirements and self.requirements['component_type']:
            query_parts.append(self.requirements['component_type'][0])
            
        # Add specifications if available and no specific part number
        if not query_parts:
            for spec_type in ['resistance', 'capacitance', 'voltage', 'current']:
                if spec_type in self.requirements and self.requirements[spec_type]:
                    query_parts.append(self.requirements[spec_type][0])
        
        query = ' '.join(query_parts)
        logger.info(f"Built search query: {query}")
        return query

    def search(self) -> List[Dict[str, str]]:
        """
        Search for parts on Mouser.com.
        
        Returns:
            List[Dict[str, str]]: List of parts with names and links
        """
        parts = []
        query = self.build_search_query()
        
        if not query:
            logger.error("Could not build a search query from requirements")
            return parts
        
        try:
            search_params = {
                'keyword': query,
                'recordsPerPage': 50
            }
            
            logger.info(f"Searching Mouser with query: {query}")
            response = self.session.get(self.SEARCH_URL, params=search_params, headers=self.headers)
            
            if response.status_code != 200:
                logger.error(f"Failed to search Mouser. Status code: {response.status_code}")
                return parts
                
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.select('.product-detail')
            
            for result in results:
                try:
                    part_name_elem = result.select_one('.product-description')
                    part_num_elem = result.select_one('.part-num')
                    link_elem = result.select_one('a.product-details-link')
                    
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
                        
                        # Try to get manufacturer information
                        mfr_elem = result.select_one('.mfr-part-num')
                        if mfr_elem:
                            part['manufacturer'] = mfr_elem.text.strip()
                            
                            # If we have StockData available, try to get stock data for the manufacturer
                            if self.market_data and part.get('manufacturer'):
                                # Extract ticker symbol from manufacturer name (if publicly traded)
                                mfr_tickers = self._get_manufacturer_ticker(part['manufacturer'])
                                if mfr_tickers:
                                    part['manufacturer_ticker'] = mfr_tickers[0]
                                    # Collect market data in background (don't wait for it)
                                    # This helps enrich the data but doesn't block the search
                                    self._enrich_with_market_data(part)
                        
                        parts.append(part)
                except Exception as e:
                    logger.error(f"Error parsing search result: {e}")
            
            logger.info(f"Found {len(parts)} parts matching the search criteria")
            return parts
            
        except Exception as e:
            logger.error(f"Error searching Mouser: {e}")
            return parts
            
    def _get_manufacturer_ticker(self, manufacturer_name: str) -> List[str]:
        """
        Get potential stock ticker symbols for a manufacturer.
        
        Args:
            manufacturer_name (str): Name of the manufacturer
            
        Returns:
            List[str]: List of potential ticker symbols
        """
        # This is a simplified mapping - in a real application, you'd use
        # a more comprehensive database or API for company name to ticker mapping
        manufacturer_tickers = {
            'texas instruments': ['TXN'],
            'ti': ['TXN'],
            'intel': ['INTC'],
            'amd': ['AMD'],
            'nvidia': ['NVDA'],
            'qualcomm': ['QCOM'],
            'broadcom': ['AVGO'],
            'analog devices': ['ADI'],
            'micron': ['MU'],
            'microchip': ['MCHP'],
            'maxim integrated': ['MXIM'],
            'on semiconductor': ['ON'],
            'skyworks': ['SWKS'],
            'nxp': ['NXPI'],
            'stmicroelectronics': ['STM'],
            'infineon': ['IFNNY'],
            'renesas': ['RNECY'],
            'cypress': ['CY'],
            'vishay': ['VSH'],
            'diodes': ['DIOD'],
            'onsemi': ['ON'],
        }
        
        # Normalize manufacturer name and check against the mapping
        normalized_name = manufacturer_name.lower()
        
        # Direct match
        if normalized_name in manufacturer_tickers:
            return manufacturer_tickers[normalized_name]
            
        # Partial match
        for key, tickers in manufacturer_tickers.items():
            if key in normalized_name or normalized_name in key:
                return tickers
                
        return []
        
    def _enrich_with_market_data(self, part: Dict[str, str]) -> None:
        """
        Enrich part information with market data for the manufacturer.
        
        Args:
            part (Dict[str, str]): Part dictionary to enrich
        """
        if not self.market_data or 'manufacturer_ticker' not in part:
            return
            
        ticker = part['manufacturer_ticker']
        
        try:
            # Collect data for the manufacturer's stock
            if self.market_data.collect_data(ticker, years=1):
                # Add some basic market info to the part
                info = self.market_data.get_info() or {}
                price_data = self.market_data.get_price_data()
                
                if price_data is not None and not price_data.empty:
                    # Get latest price
                    latest_price = price_data['Close'].iloc[-1] if 'Close' in price_data else None
                    if latest_price is not None:
                        part['manufacturer_stock_price'] = f"${latest_price:.2f}"
                        
                    # Calculate 50-day moving average if we have enough data
                    if len(price_data) >= 50:
                        ma_50 = price_data['Close'].rolling(window=50).mean().iloc[-1]
                        part['manufacturer_50day_ma'] = f"${ma_50:.2f}"
                        
                # Add sector and industry if available
                if info:
                    part['manufacturer_sector'] = info.get('sector', 'Unknown')
                    part['manufacturer_industry'] = info.get('industry', 'Unknown')
                    
        except Exception as e:
            logger.error(f"Error enriching part with market data: {e}")


class TAAComplianceChecker:
    """Check if parts are TAA compliant."""
    
    def __init__(self, parts: List[Dict[str, str]]):
        """
        Initialize with a list of parts.
        
        Args:
            parts (List[Dict[str, str]]): List of parts with links
        """
        self.parts = parts
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session = requests.Session()
        
    def check_compliance(self) -> List[Dict[str, Any]]:
        """
        Check if parts are TAA compliant.
        
        Returns:
            List[Dict[str, Any]]: List of TAA compliant parts
        """
        compliant_parts = []
        
        for part in self.parts:
            try:
                logger.info(f"Checking TAA compliance for part: {part['part_number']}")
                response = self.session.get(part['link'], headers=self.headers)
                
                if response.status_code != 200:
                    logger.error(f"Failed to get part details. Status code: {response.status_code}")
                    continue
                    
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for TAA compliance in the part details
                taa_indicators = [
                    'TAA Compliant',
                    'Trade Agreements Act',
                    'Country of Origin: USA',
                    'Country of Origin: Taiwan',
                    'Country of Origin: Korea',
                    'Country of Origin: Japan',

                    # Add more TAA compliant countries as needed
                ]
                
                # Check for country of origin indicators
                country_elem = soup.find(text=re.compile(r'Country\s+of\s+Origin', re.IGNORECASE))
                origin_country = None
                
                if country_elem:
                    # Try to find the country value
                    origin_text = country_elem.parent.text if hasattr(country_elem, 'parent') else country_elem
                    country_match = re.search(r'Country\s+of\s+Origin[:\s]+([A-Za-z\s]+)', origin_text, re.IGNORECASE)
                    
                    if country_match:
                        origin_country = country_match.group(1).strip()
                
                # Check the page content for TAA compliance indicators
                page_text = soup.get_text()
                taa_compliant = False
                taa_evidence = None
                
                for indicator in taa_indicators:
                    if indicator.lower() in page_text.lower():
                        taa_compliant = True
                        taa_evidence = indicator
                        break
                
                # If we found a country of origin, check if it's TAA compliant
                if origin_country and not taa_compliant:
                    taa_countries = [
                        'USA', 'United States', 'Taiwan', 'South Korea', 'Korea', 
                        'Japan', 'Israel', 'Australia', 'Canada', 'Mexico',
                        # Add more TAA compliant countries as needed
                    ]
                    
                    for country in taa_countries:
                        if country.lower() in origin_country.lower():
                            taa_compliant = True
                            taa_evidence = f"Country of Origin: {origin_country}"
                            break
                
                if taa_compliant:
                    logger.info(f"Part {part['part_number']} is TAA compliant: {taa_evidence}")
                    compliant_part = part.copy()
                    compliant_part['taa_evidence'] = taa_evidence
                    compliant_parts.append(compliant_part)
                else:
                    logger.info(f"Part {part['part_number']} is not confirmed TAA compliant")
                    
            except Exception as e:
                logger.error(f"Error checking TAA compliance for part {part['part_number']}: {e}")
        
        logger.info(f"Found {len(compliant_parts)} TAA compliant parts")
        return compliant_parts


class PartAnalyzer:
    """Analyze and report on parts that meet requirements and TAA compliance."""
    
    def __init__(self, requirements_file: str, output_dir: str = None):
        """
        Initialize with path to requirements file and output directory.
        
        Args:
            requirements_file (str): Path to requirements file
            output_dir (str, optional): Directory for output files
        """
        self.requirements_file = requirements_file
        self.output_dir = output_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), 'OUTPUT')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
    def run_analysis(self) -> Tuple[List[Dict[str, str]], List[Dict[str, Any]]]:
        """
        Run the complete analysis workflow.
        
        Returns:
            Tuple[List[Dict[str, str]], List[Dict[str, Any]]]: 
                A tuple containing (all matching parts, TAA compliant parts)
        """
        # Extract requirements
        extractor = RequirementsExtractor(self.requirements_file)
        requirements = extractor.extract()
        
        if not requirements:
            logger.error("Failed to extract requirements. Exiting analysis.")
            return [], []
        
        # Save extracted requirements to JSON file
        requirements_file = os.path.join(self.output_dir, "requirements.json")
        with open(requirements_file, "w") as f:
            json.dump(requirements, f, indent=4)
        
        print(f"Found {len(requirements)} requirements. Saved to {requirements_file}")
        
        # Search for parts
        print("Searching for parts on Mouser.com...")
        all_parts = []
        
        for req_id, req_data in requirements.items():
            print(f"Searching for parts matching requirement {req_id}...")
            scraper = MouserScraper(req_data)
            parts = scraper.search()
            
            if parts:
                print(f"Found {len(parts)} parts matching requirement {req_id}")
                
                # Add requirement ID to parts
                for part in parts:
                    part['requirement_id'] = req_id
                
                all_parts.extend(parts)
            else:
                print(f"No parts found for requirement {req_id}")
        
        # Check TAA compliance if requested
        if all_parts:
            print("Checking TAA compliance of parts...")
            
            taa_checker = TAAComplianceChecker(all_parts)
            
            for part in all_parts:
                is_compliant, details = taa_checker.check_compliance(part['link'])
                part['taa_compliant'] = is_compliant
                part['taa_details'] = details
    
        # Save all parts to CSV file
        if all_parts:
            output_file = os.path.join(self.output_dir, "parts.csv")
            
            # Determine all fields across all parts
            all_fields = set()
            for part in all_parts:
                all_fields.update(part.keys())
            
            # Write parts data to CSV
            with open(output_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(all_fields))
                writer.writeheader()
                writer.writerows(all_parts)
            
            print(f"Saved {len(all_parts)} parts to {output_file}")
        
        if all_parts:
            print(f"Results saved to the output directory.")
        
        # Collect market data for manufacturers if requested
        if all_parts:
            print("Collecting market data for manufacturers...")
            
            # Create a MarketDataCollector
            market_data = MarketDataCollector()
            
            # Get unique manufacturer tickers from all parts
            manufacturer_tickers = set()
            for part in all_parts:
                if 'manufacturer_ticker' in part:
                    manufacturer_tickers.add(part['manufacturer_ticker'])
            
            # Collect data for each manufacturer ticker
            manufacturer_data = {}
            for ticker in manufacturer_tickers:
                print(f"Collecting market data for {ticker}...")
                
                # Collect data for 2 years to get enough for moving averages
                if market_data.collect_data(ticker, years=2):
                    # Save the data to CSV
                    ticker_file = os.path.join(self.output_dir, f"market_data_{ticker}.csv")
                    market_data.save_data(ticker_file)
                    print(f"Saved market data for {ticker} to {ticker_file}")
                    
                    # Store price data for analysis
                    manufacturer_data[ticker] = market_data.get_price_data()
            
            # Calculate and save moving averages for each manufacturer
            if manufacturer_data:
                # Create a directory for charts
                charts_dir = os.path.join(self.output_dir, "charts")
                os.makedirs(charts_dir, exist_ok=True)
                
                # Calculate moving averages and create charts
                try:
                    import matplotlib.pyplot as plt
                    import matplotlib.dates as mdates
                    
                    for ticker, price_data in manufacturer_data.items():
                        if price_data is None or price_data.empty:
                            continue
                        
                        # Ensure index is datetime for plotting
                        if not isinstance(price_data.index, pd.DatetimeIndex):
                            continue
                        
                        # Calculate moving averages
                        price_data['MA20'] = price_data['Close'].rolling(window=20).mean()
                        price_data['MA50'] = price_data['Close'].rolling(window=50).mean()
                        price_data['MA200'] = price_data['Close'].rolling(window=200).mean()
                        
                        # Create a new figure
                        plt.figure(figsize=(12, 6))
                        
                        # Plot price and moving averages
                        plt.plot(price_data.index, price_data['Close'], label='Price', color='black', alpha=0.75)
                        plt.plot(price_data.index, price_data['MA20'], label='20-day MA', color='blue')
                        plt.plot(price_data.index, price_data['MA50'], label='50-day MA', color='orange')
                        plt.plot(price_data.index, price_data['MA200'], label='200-day MA', color='red')
                        
                        # Format the plot
                        plt.title(f'Moving Averages for {ticker}')
                        plt.xlabel('Date')
                        plt.ylabel('Price ($)')
                        plt.grid(True, alpha=0.3)
                        plt.legend()
                        
                        # Format x-axis dates
                        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                        plt.xticks(rotation=45)
                        
                        # Save the plot
                        chart_file = os.path.join(charts_dir, f"moving_averages_{ticker}.png")
                        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                        plt.close()
                        
                        print(f"Created moving average chart for {ticker}")
                        
                        # Save the data with moving averages
                        ma_file = os.path.join(self.output_dir, f"moving_averages_{ticker}.csv")
                        price_data.to_csv(ma_file)
                        print(f"Saved moving average data for {ticker} to {ma_file}")
                        
                except ImportError:
                    print("Matplotlib not installed. Charts could not be created.")
                except Exception as e:
                    print(f"Error creating charts: {e}")


def main():
    """
    Main function to run the Moving Average Analysis Tool.
    """
    import argparse
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Moving Average Analysis Tool for TapaTool")
    parser.add_argument("--input-file", type=str, required=True, help="Path to input requirements document")
    parser.add_argument("--output-dir", type=str, default="output", help="Path to output directory")
    parser.add_argument("--check-taa", action="store_true", help="Check TAA compliance of parts")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--market-data", action="store_true", help="Collect market data for manufacturers")
    args = parser.parse_args()
    
    # Set logging level based on verbosity
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Extract requirements from document
    print(f"Extracting requirements from {args.input_file}...")
    extractor = RequirementsExtractor(args.input_file)
    requirements = extractor.extract()
    
    if not requirements:
        print("No requirements found in the document.")
        return
    
    # Save extracted requirements to JSON file
    requirements_file = os.path.join(args.output_dir, "requirements.json")
    with open(requirements_file, "w") as f:
        json.dump(requirements, f, indent=4)
    
    print(f"Found {len(requirements)} requirements. Saved to {requirements_file}")
    
    # Search for parts on Mouser.com
    print("Searching for parts on Mouser.com...")
    all_parts = []
    
    for req_id, req_data in requirements.items():
        print(f"Searching for parts matching requirement {req_id}...")
        scraper = MouserScraper(req_data)
        parts = scraper.search()
        
        if parts:
            print(f"Found {len(parts)} parts matching requirement {req_id}")
            
            # Add requirement ID to parts
            for part in parts:
                part['requirement_id'] = req_id
            
            all_parts.extend(parts)
        else:
            print(f"No parts found for requirement {req_id}")
    
    # Check TAA compliance if requested
    if args.check_taa and all_parts:
        print("Checking TAA compliance of parts...")
        
        taa_checker = TAAComplianceChecker(all_parts)
        
        for part in all_parts:
            is_compliant, details = taa_checker.check_compliance(part['link'])
            part['taa_compliant'] = is_compliant
            part['taa_details'] = details
    
    # Save all parts to CSV file
    if all_parts:
        output_file = os.path.join(args.output_dir, "parts.csv")
        
        # Determine all fields across all parts
        all_fields = set()
        for part in all_parts:
            all_fields.update(part.keys())
        
        # Write parts data to CSV
        with open(output_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(all_fields))
            writer.writeheader()
            writer.writerows(all_parts)
        
        print(f"Saved {len(all_parts)} parts to {output_file}")
    
    if all_parts:
        print(f"Results saved to the output directory.")
    
    # Collect market data for manufacturers if requested
    if args.market_data and HAS_STOCK_DATA:
        print("Collecting market data for manufacturers...")
        
        # Create a MarketDataCollector
        market_data = MarketDataCollector()
        
        # Get unique manufacturer tickers from all parts
        manufacturer_tickers = set()
        for part in all_parts:
            if 'manufacturer_ticker' in part:
                manufacturer_tickers.add(part['manufacturer_ticker'])
        
        # Collect data for each manufacturer ticker
        manufacturer_data = {}
        for ticker in manufacturer_tickers:
            print(f"Collecting market data for {ticker}...")
            
            # Collect data for 2 years to get enough for moving averages
            if market_data.collect_data(ticker, years=2):
                # Save the data to CSV
                ticker_file = os.path.join(args.output_dir, f"market_data_{ticker}.csv")
                market_data.save_data(ticker_file)
                print(f"Saved market data for {ticker} to {ticker_file}")
                
                # Store price data for analysis
                manufacturer_data[ticker] = market_data.get_price_data()
        
        # Calculate and save moving averages for each manufacturer
        if manufacturer_data:
            # Create a directory for charts
            charts_dir = os.path.join(args.output_dir, "charts")
            os.makedirs(charts_dir, exist_ok=True)
            
            # Calculate moving averages and create charts
            try:
                import matplotlib.pyplot as plt
                import matplotlib.dates as mdates
                
                for ticker, price_data in manufacturer_data.items():
                    if price_data is None or price_data.empty:
                        continue
                    
                    # Ensure index is datetime for plotting
                    if not isinstance(price_data.index, pd.DatetimeIndex):
                        continue
                    
                    # Calculate moving averages
                    price_data['MA20'] = price_data['Close'].rolling(window=20).mean()
                    price_data['MA50'] = price_data['Close'].rolling(window=50).mean()
                    price_data['MA200'] = price_data['Close'].rolling(window=200).mean()
                    
                    # Create a new figure
                    plt.figure(figsize=(12, 6))
                    
                    # Plot price and moving averages
                    plt.plot(price_data.index, price_data['Close'], label='Price', color='black', alpha=0.75)
                    plt.plot(price_data.index, price_data['MA20'], label='20-day MA', color='blue')
                    plt.plot(price_data.index, price_data['MA50'], label='50-day MA', color='orange')
                    plt.plot(price_data.index, price_data['MA200'], label='200-day MA', color='red')
                    
                    # Format the plot
                    plt.title(f'Moving Averages for {ticker}')
                    plt.xlabel('Date')
                    plt.ylabel('Price ($)')
                    plt.grid(True, alpha=0.3)
                    plt.legend()
                    
                    # Format x-axis dates
                    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))
                    plt.xticks(rotation=45)
                    
                    # Save the plot
                    chart_file = os.path.join(charts_dir, f"moving_averages_{ticker}.png")
                    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                    plt.close()
                    
                    print(f"Created moving average chart for {ticker}")
                    
                    # Save the data with moving averages
                    ma_file = os.path.join(args.output_dir, f"moving_averages_{ticker}.csv")
                    price_data.to_csv(ma_file)
                    print(f"Saved moving average data for {ticker} to {ma_file}")
                    
            except ImportError:
                print("Matplotlib not installed. Charts could not be created.")
            except Exception as e:
                print(f"Error creating charts: {e}")


if __name__ == "__main__":
    main()
