"""
Image Text Extractor - Main Script
---------------------------------
This script demonstrates how to use the ImageTextExtractor class.
"""

import os
import sys
from ImageTextExtractor.image_text_extractor import ImageTextExtractor


def main():
    """
    Main function to demonstrate the use of ImageTextExtractor.
    """
    # Check if image path is provided
    if len(sys.argv) < 2:
        print("Usage: python main.py <image_path>")
        print("Example: python main.py sample_images/sample.jpg")
        return
    
    image_path = sys.argv[1]
    
    # Check if the provided file exists
    if not os.path.exists(image_path):
        print(f"Error: The image file '{image_path}' does not exist.")
        return
    
    # Create an instance of ImageTextExtractor
    # If you have Tesseract installed in a non-standard location, specify it here:
    # extractor = ImageTextExtractor(tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    extractor = ImageTextExtractor()
    
    try:
        # Extract text from the image and get it as a list
        text_list = extractor.extract_text_as_list(image_path)
        
        # Print the extracted text
        print("\nExtracted Text:")
        print("--------------")
        for i, line in enumerate(text_list, 1):
            print(f"{i}. {line}")
        
        print(f"\nTotal lines extracted: {len(text_list)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
