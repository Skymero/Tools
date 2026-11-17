"""
Text File Translator
This script reads a text file and translates it to Spanish and Portuguese.
"""

import os
import sys
from deep_translator import GoogleTranslator


def translate_text(input_text, target_language):
    """
    Translate text to the specified target language using Google Translate.
    
    Args:
        input_text (str): Text to be translated
        target_language (str): Target language code ('es' for Spanish, 'pt' for Portuguese)
    
    Returns:
        str: Translated text
    
    Raises:
        Exception: For translation errors
    """
    try:
        translator = GoogleTranslator(source='auto', target=target_language)
        translated_text = translator.translate(input_text)
        return translated_text
    except Exception as e:
        raise Exception(f"Translation error for language {target_language}: {e}")


def translate_file(input_file, output_file_es=None, output_file_pt=None):
    """
    Read a text file and translate it to Spanish and Portuguese.
    
    Args:
        input_file (str): Path to the input text file
        output_file_es (str): Path to the Spanish translation output file (optional)
        output_file_pt (str): Path to the Portuguese translation output file (optional)
    
    Returns:
        dict: Dictionary with keys 'spanish' and 'portuguese' containing translation status
    
    Raises:
        FileNotFoundError: If input file doesn't exist
        ValueError: If input file is empty
    """
    results = {'spanish': False, 'portuguese': False}
    
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
        
        # Generate output filenames if not provided
        base_name = input_file.rsplit('.', 1)[0]
        if output_file_es is None:
            output_file_es = f"{base_name}_spanish.txt"
        if output_file_pt is None:
            output_file_pt = f"{base_name}_portuguese.txt"
        
        # Translate to Spanish
        print("Translating to Spanish...")
        spanish_text = translate_text(text, 'es')
        with open(output_file_es, 'w', encoding='utf-8') as file:
            file.write(spanish_text)
        print(f"Spanish translation saved to: {output_file_es}")
        results['spanish'] = True
        
        # Translate to Portuguese
        print("Translating to Portuguese...")
        portuguese_text = translate_text(text, 'pt')
        with open(output_file_pt, 'w', encoding='utf-8') as file:
            file.write(portuguese_text)
        print(f"Portuguese translation saved to: {output_file_pt}")
        results['portuguese'] = True
        
        print("\nTranslation completed successfully!")
        return results
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return results
    except ValueError as e:
        print(f"Error: {e}")
        return results
    except Exception as e:
        print(f"An error occurred during translation: {e}")
        return results


def main():
    """
    Main function to handle command line arguments and execute translation.
    """
    # Check if correct number of arguments provided
    if len(sys.argv) < 2:
        print("Usage: python translate_text.py <input_file> [output_spanish] [output_portuguese]")
        print("Example: python translate_text.py input.txt")
        print("Example: python translate_text.py input.txt spanish_output.txt portuguese_output.txt")
        sys.exit(1)
    
    # Parse arguments
    input_file = sys.argv[1]
    output_file_es = sys.argv[2] if len(sys.argv) > 2 else None
    output_file_pt = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Execute translation
    results = translate_file(input_file, output_file_es, output_file_pt)
    
    # Exit with appropriate code
    success = all(results.values())
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
