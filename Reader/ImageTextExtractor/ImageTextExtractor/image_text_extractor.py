"""
Image Text Extractor Module
--------------------------
This module extracts text from images using OCR (Optical Character Recognition).
"""

import os
import argparse
import pytesseract
import cv2
import numpy as np
from PIL import Image
from typing import List, Optional


class ImageTextExtractor:
    """
    A class to extract text from images using OCR.
    """
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize the ImageTextExtractor with optional tesseract executable path.
        
        Args:
            tesseract_path: Path to the tesseract executable (optional)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def preprocess_image(self, image_path: str):
        """
        Preprocess the image to improve OCR accuracy.
        
        Args:
            image_path: Path to the input image
            
        Returns:
            Preprocessed image
        """
        # Read the image using OpenCV
        img = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get image with only black and white pixels
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(binary, None, 10, 7, 21)
        
        return denoised
    
    def extract_text(self, image_path: str, preprocess: bool = True) -> str:
        """
        Extract text from an image file.
        
        Args:
            image_path: Path to the input image
            preprocess: Whether to preprocess the image for better OCR results
            
        Returns:
            Extracted text as a string
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        if preprocess:
            # Use preprocessing for better results
            img = self.preprocess_image(image_path)
            # Convert the OpenCV image to PIL format
            img_pil = Image.fromarray(img)
            text = pytesseract.image_to_string(img_pil)
        else:
            # Use Pillow to open the image directly
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
        
        return text
    
    def extract_text_as_list(self, image_path: str, preprocess: bool = True) -> List[str]:
        """
        Extract text from an image and return it as a list of lines.
        
        Args:
            image_path: Path to the input image
            preprocess: Whether to preprocess the image for better OCR results
            
        Returns:
            List of extracted text lines
        """
        text = self.extract_text(image_path, preprocess)
        
        # Split the text by newlines and remove empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        return lines


def main():
    """
    Main function to run the image text extractor from command line.
    """
    parser = argparse.ArgumentParser(description='Extract text from images')
    parser.add_argument('image_path', help='Path to the input image')
    parser.add_argument('--tesseract-path', help='Path to the tesseract executable')
    parser.add_argument('--no-preprocess', action='store_true', help='Skip image preprocessing')
    
    args = parser.parse_args()
    
    extractor = ImageTextExtractor(args.tesseract_path)
    
    try:
        text_list = extractor.extract_text_as_list(args.image_path, not args.no_preprocess)
        
        print("\nExtracted Text:")
        print("--------------")
        for i, line in enumerate(text_list, 1):
            print(f"{i}. {line}")
            
        print(f"\nTotal lines extracted: {len(text_list)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
