"""
Audio loading and preprocessing module.

This module handles loading various audio formats and preparing them
for analysis.
"""
import os
import numpy as np
import librosa
import soundfile as sf
from pydub import AudioSegment


class AudioLoader:
    """Class for loading and preprocessing audio files."""
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the audio loader.
        
        Args:
            sample_rate (int): Target sample rate for audio processing.
        """
        self.sample_rate = sample_rate
    
    def load_file(self, file_path, start_time=None, end_time=None):
        """
        Load an audio file and return the signal data.
        
        Args:
            file_path (str): Path to the audio file.
            start_time (float, optional): Start time in seconds for segment selection.
            end_time (float, optional): End time in seconds for segment selection.
            
        Returns:
            tuple: (audio_data, sample_rate, duration)
        
        Raises:
            ValueError: If the file format is not supported or the file doesn't exist.
        """
        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")
        
        # Get file extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # Check supported formats
        if ext not in ['.wav', '.mp3', '.flac']:
            raise ValueError(f"Unsupported audio format: {ext}. Supported formats: WAV, MP3, FLAC")
        
        # Load audio data
        try:
            # Use librosa for consistent handling of different formats
            audio_data, orig_sr = librosa.load(file_path, sr=self.sample_rate, mono=True)
            
            # Apply time selection if specified
            if start_time is not None or end_time is not None:
                start_sample = int(self.sample_rate * (start_time or 0))
                end_sample = int(self.sample_rate * (end_time or len(audio_data) / self.sample_rate))
                audio_data = audio_data[start_sample:end_sample]
            
            duration = len(audio_data) / self.sample_rate
            
            return audio_data, self.sample_rate, duration
            
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")
    
    def preprocess(self, audio_data, normalize=True, trim_silence=False):
        """
        Preprocess the audio signal.
        
        Args:
            audio_data (np.ndarray): Audio signal data.
            normalize (bool): Whether to normalize the audio.
            trim_silence (bool): Whether to trim leading and trailing silence.
            
        Returns:
            np.ndarray: Preprocessed audio data.
        """
        # Make a copy to avoid modifying the original
        processed_data = np.copy(audio_data)
        
        # Normalize if requested
        if normalize:
            processed_data = librosa.util.normalize(processed_data)
        
        # Trim silence if requested
        if trim_silence:
            processed_data, _ = librosa.effects.trim(processed_data)
        
        return processed_data
    
    def get_spectrogram(self, audio_data, n_fft=2048, hop_length=512):
        """
        Compute the spectrogram of the audio data.
        
        Args:
            audio_data (np.ndarray): Audio signal data.
            n_fft (int): FFT window size.
            hop_length (int): Hop length for the FFT windows.
            
        Returns:
            np.ndarray: Spectrogram (magnitude).
        """
        # Compute spectrogram
        spectrogram = np.abs(librosa.stft(audio_data, n_fft=n_fft, hop_length=hop_length))
        return spectrogram
    
    def get_mel_spectrogram(self, audio_data, n_mels=128, n_fft=2048, hop_length=512):
        """
        Compute the Mel spectrogram of the audio data.
        
        Args:
            audio_data (np.ndarray): Audio signal data.
            n_mels (int): Number of Mel bands.
            n_fft (int): FFT window size.
            hop_length (int): Hop length for the FFT windows.
            
        Returns:
            np.ndarray: Mel spectrogram.
        """
        # Compute Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio_data, 
            sr=self.sample_rate, 
            n_mels=n_mels,
            n_fft=n_fft, 
            hop_length=hop_length
        )
        return mel_spec
