"""
Text to Speech Converter using gTTS
This script reads a text file and converts it to an MP3 audio file.
"""

import os
import sys
from gtts import gTTS


def text_to_speech(input_file, output_file, language='en'):
    """
    Convert a text file to an MP3 audio file using Google Text-to-Speech.
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to the output MP3 file
        language (str): Language code for TTS (default: 'en' for English)
    
    Returns:
        bool: True if conversion successful, False otherwise
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        Exception: For other conversion errors
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file '{input_file}' not found")
        
        # Read the text from the file
        with open(input_file, 'r', encoding='utf-8') as file:
            text = file.read().strip()
        
        # Validate that file is not empty
        if not text:
            raise ValueError("Input file is empty")
        
        print(f"Reading text from: {input_file}")
        print(f"Text length: {len(text)} characters")
        
        # Create gTTS object
        print(f"Converting text to speech (language: {language})...")
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Save the audio file
        tts.save(output_file)
        
        print(f"Successfully created audio file: {output_file}")
        return True
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False
    except ValueError as e:
        print(f"Error: {e}")
        return False
    except Exception as e:
        print(f"An error occurred during conversion: {e}")
        return False


def main():
    """
    Main function to handle command line arguments and execute conversion.
    """
    # Check if correct number of arguments provided
    if len(sys.argv) < 2:
        print("Usage: python text_to_speech.py <input_file> [output_file] [language]")
        print("Example: python text_to_speech.py input.txt output.mp3")
        print("Example: python text_to_speech.py input.txt output.mp3 en")
        sys.exit(1)
    
    # Parse arguments
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.rsplit('.', 1)[0] + '.mp3'
    language = sys.argv[3] if len(sys.argv) > 3 else 'en'
    
    # Execute conversion
    success = text_to_speech(input_file, output_file, language)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
