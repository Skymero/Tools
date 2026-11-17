import cv2
import pytesseract
import numpy as np
from PIL import Image
import re
import csv
import os

# purpose of this script is to extract the set number, serial number, and rarity from a Yu-Gi-Oh! card image and appends the data to a csv file that updated not overwritten
# to execute: python yugioh_card_extractor.py <image_path> i.e.: python yugioh_set_extractor.py cards/20250530_163700.jpg
# Optional: Set path to Tesseract executable if not in PATH
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def preprocess_image(image_path):
    """
    Preprocess the image to improve OCR accuracy.

    Args:
        image_path: Path to the input image

    Returns:
        Preprocessed image
    """
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def extract_text(image):
    """
    Extract text from an image using OCR (Optical Character Recognition).

    Args:
        image: Image to extract text from

    Returns:
        Extracted text as a string
    """
    custom_config = r'--oem 3 --psm 6'
    return pytesseract.image_to_string(image, config=custom_config)

def parse_card_info(text):
    """
    Parse the extracted text from a Yu-Gi-Oh! card image and extract the relevant information.

    Args:
        text: Extracted text from the card image

    Returns:
        dict: A dictionary containing the extracted information, such as the card title, set number, serial number, and rarity.
    """
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]
    
    title = lines[0] if lines else ""
    
    set_number = ""
    serial_number = ""
    rarity = ""

    for line in lines:
        # Set Number: Format often like "LOB-001"
        match_set = re.search(r'\b[A-Z]{2,}-[A-Z]{0,3}\d{2,}\b', line)
        if match_set:
            set_number = match_set.group()

        # Serial Number: 8-digit number often at bottom-right
        match_serial = re.search(r'\b\d{8}\b', line)
        if match_serial:
            serial_number = match_serial.group()

        # Rarity may be abbreviated: UR, SR, R, N, etc.
        match_rarity = re.search(r'\b(UR|SR|R|N|Secret Rare|Ultra Rare|Super Rare|Common)\b', line, re.IGNORECASE)
        if match_rarity:
            rarity = match_rarity.group()

    return {
        'Title': title,
        'Set Number': set_number,
        'Serial Number': serial_number,
        'Rarity': rarity
    }

def append_to_csv(data, csv_path='yugioh_cards.csv'):
    """
    Append a dictionary of card information to a CSV file.

    Args:
        data (dict): A dictionary containing the extracted information, such as the card title, set number, serial number, and rarity.
        csv_path (str): The path to the CSV file to append to. Defaults to 'yugioh_cards.csv'.
    """
    file_exists = os.path.isfile(csv_path)
    with open(csv_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Title', 'Set Number', 'Serial Number', 'Rarity'])
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def extract_card_details(image_path):
    """
    Extracts relevant information from a Yu-Gi-Oh! card image and appends it to a CSV file.

    Args:
        image_path (str): Path to the image of the Yu-Gi-Oh! card

    Returns:
        dict: A dictionary containing the extracted information, such as the card title, set number, serial number, and rarity
    """
    processed_image = preprocess_image(image_path)
    text = extract_text(processed_image)
    info = parse_card_info(text)
    append_to_csv(info)
    return info

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Yu-Gi-Oh! Card Info Extractor")
    parser.add_argument("image_path", help="Path to the image of the Yu-Gi-Oh! card")
    args = parser.parse_args()

    details = extract_card_details(args.image_path)
    print("Extracted Card Info:")
    for key, value in details.items():
        print(f"{key}: {value}")
