# Project Overview
- Name: TapaTool
- Framework: What framework is it using, if known
- UI components: What UI libaries are being used

## Description

- The TapaTool, is used to scrape websites for TAA compliant parts given certain requirements 

## Features

- extract requirements from documents
- search for parts that match the requirements
- display results in a user-friendly interface
- search for manufacturing information of the part and check if it meets TAA compliance criteria

# React Native Expo Project Layout

```

📁 venv                 #  Python virtual environment

📁 DOCS            # Project documentation

📁 OUTPUT            # Main tab navigation screens

📄 tapa_tool.py       # main tool to find parts that meet TAA requirements

📄 requirements_extraction.py       # Saved events screen

📄 compliance_taa.py      # Create event screen

📄 parts.py      # resulting parts that meet requirements

```
## Process

- extract requirements from documents
- search for parts that match the requirements in requirements document
- Check for TAA compliance
    - search for manufacturing information of the part and check if it meets TAA compliance criteria
- display results as a link to the part if it meets TAA requirements

# Websties to scrape

1. Mouser Electronics - Comprehensive selection of components from many manufacturers
2. Digi-Key - Huge inventory with fast shipping and excellent search capabilities
3. Arrow Electronics - Wide range of electronic components and development tools
4. Newark/Farnell - Good selection with international shipping options
5. SparkFun - Great for hobbyist components and development boards
6. Adafruit - Excellent for makers, with good tutorials and specialized components
7. LCSC - Often more affordable, especially for bulk orders
8. Jameco Electronics - Good for hobbyists and professionals alike
9. RS Components - Extensive catalog with global shipping options
10. Amazon - Convenient for many common components, though specifications may be less detailed

# TAA compliance

TAA compliance refers to parts that meet the requirements of the Trade Agreements Act (TAA) of 1979. Here's what makes a part TAA compliant:

The part must be made or "substantially transformed" in either:
- The United States
- A TAA designated country that has a trade agreement with the US

"Substantially transformed" means the component underwent a fundamental change in form, function, or character in a designated country, creating a new article with a different name, character, or use from its constituent parts.

TAA compliance is particularly important for:
- Government contracts and purchases
- Projects funded by federal money
- Companies that sell to the US government

TAA designated countries include most major US trading partners like Canada, Mexico, European nations, Japan, Australia, and others, but notably exclude China and some other countries.

When purchasing electronic components, TAA compliance is often indicated in the product specifications or can be filtered for in search results on sites like Digi-Key or Mouser. These parts typically cost more than non-compliant alternatives.

# GUI

The GUI will be a React Native Expo webpage with the following screens:

1. Home Screen
    - Upload requirements document (json, csv, txt, or md)
2. Results Screen
    - Display results in a table
    - each row will have the name, image of the part, if TAA compliant, each specification of the part, and a link to the part's website
    - add a sorting button to sort by name, TAA compliance, or specification
