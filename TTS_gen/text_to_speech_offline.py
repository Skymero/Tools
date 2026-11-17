"""
Text to Speech Converter using pyttsx3 (Offline)
This script reads a text file and converts it to an MP3 audio file using system TTS engines.
Works offline without requiring an internet connection.
"""

import os
import sys
import pyttsx3


def text_to_speech_offline(input_file, output_file, voice_index=None, rate=None, volume=None):
    """
    Convert a text file to an MP3 audio file using pyttsx3 (system TTS).
    
    Args:
        input_file (str): Path to the input text file
        output_file (str): Path to the output MP3 file
        voice_index (int): Index of the voice to use (optional, uses default if not specified)
        rate (int): Speech rate in words per minute (optional, uses default if not specified)
        volume (float): Volume level between 0.0 and 1.0 (optional, uses default if not specified)
    
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
        
        # Initialize the TTS engine
        print("Initializing TTS engine...")
        engine = pyttsx3.init()
        
        # Set voice if specified
        if voice_index is not None:
            voices = engine.getProperty('voices')
            if 0 <= voice_index < len(voices):
                engine.setProperty('voice', voices[voice_index].id)
                print(f"Using voice: {voices[voice_index].name}")
            else:
                print(f"Warning: Voice index {voice_index} out of range. Using default voice.")
        
        # Set speech rate if specified
        if rate is not None:
            engine.setProperty('rate', rate)
            print(f"Speech rate: {rate} words per minute")
        
        # Set volume if specified
        if volume is not None:
            engine.setProperty('volume', volume)
            print(f"Volume: {volume}")
        
        # Save to file
        print(f"Converting text to speech (offline)...")
        engine.save_to_file(text, output_file)
        
        # Run the engine to process the conversion
        engine.runAndWait()
        
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


def list_available_voices():
    """
    List all available system voices for TTS.
    
    Returns:
        list: List of voice information dictionaries
    """
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print("\nAvailable voices:")
        for i, voice in enumerate(voices):
            print(f"{i}: {voice.name} ({voice.id})")
            print(f"   Languages: {voice.languages}")
            print(f"   Gender: {voice.gender}")
            print()
        
        return voices
    except Exception as e:
        print(f"Error listing voices: {e}")
        return []


def main():
    """
    Main function to handle command line arguments and execute conversion.
    """
    # Check if correct number of arguments provided
    if len(sys.argv) < 2:
        print("Usage: python text_to_speech_offline.py <input_file> [output_file] [voice_index] [rate] [volume]")
        print("Example: python text_to_speech_offline.py input.txt output.mp3")
        print("Example: python text_to_speech_offline.py input.txt output.mp3 0 150 0.9")
        print("Options:")
        print("  --list-voices    List all available system voices")
        sys.exit(1)
    
    # Handle --list-voices flag
    if sys.argv[1] == '--list-voices':
        list_available_voices()
        sys.exit(0)
    
    # Parse arguments
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.rsplit('.', 1)[0] + '.mp3'
    voice_index = int(sys.argv[3]) if len(sys.argv) > 3 else None
    rate = int(sys.argv[4]) if len(sys.argv) > 4 else None
    volume = float(sys.argv[5]) if len(sys.argv) > 5 else None
    
    # Execute conversion
    success = text_to_speech_offline(input_file, output_file, voice_index, rate, volume)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
