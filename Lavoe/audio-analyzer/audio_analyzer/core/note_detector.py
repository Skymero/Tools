"""
Note detection module.

This module handles the detection of individual notes within an audio signal,
identifying note boundaries and preparing segments for detailed analysis.
"""
import numpy as np
import librosa
import crepe
from scipy.signal import find_peaks


class NoteDetector:
    """Class for detecting individual notes in audio signals."""
    
    def __init__(self, sample_rate=44100, min_note_duration=0.1):
        """
        Initialize the note detector.
        
        Args:
            sample_rate (int): Sample rate of the audio signal.
            min_note_duration (float): Minimum duration of a note in seconds.
        """
        self.sample_rate = sample_rate
        self.min_note_duration = min_note_duration
        self.min_note_samples = int(min_note_duration * sample_rate)
    
    def detect_notes(self, audio_data, onset_method='energy', monophonic=True):
        """
        Detect individual notes in the audio data.
        
        Args:
            audio_data (np.ndarray): Audio signal data.
            onset_method (str): Method for onset detection ('energy', 'hfc', 'complex', etc.).
            monophonic (bool): Whether the audio is monophonic (single notes only).
            
        Returns:
            list: List of note segments as (start_time, end_time, audio_segment) tuples.
        """
        if monophonic:
            return self._detect_monophonic_notes(audio_data, onset_method)
        else:
            return self._detect_polyphonic_notes(audio_data)
    
    def _detect_monophonic_notes(self, audio_data, onset_method):
        """
        Detect notes in monophonic audio.
        
        Args:
            audio_data (np.ndarray): Audio signal data.
            onset_method (str): Method for onset detection.
            
        Returns:
            list: List of note segments.
        """
        # Detect onsets
        onset_frames = librosa.onset.onset_detect(
            y=audio_data, 
            sr=self.sample_rate,
            units='frames',
            hop_length=512,
            backtrack=True,
            energy=onset_method=='energy'
        )
        
        # Convert onset frames to time
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate, hop_length=512)
        
        # Add the end of the audio as the final offset
        offset_times = np.append(onset_times[1:], len(audio_data) / self.sample_rate)
        
        # Create note segments
        note_segments = []
        for i in range(len(onset_times)):
            start_time = onset_times[i]
            end_time = offset_times[i]
            
            # Skip notes that are too short
            if end_time - start_time < self.min_note_duration:
                continue
            
            # Get audio segment
            start_sample = int(start_time * self.sample_rate)
            end_sample = int(end_time * self.sample_rate)
            segment = audio_data[start_sample:end_sample]
            
            note_segments.append((start_time, end_time, segment))
        
        return note_segments
    
    def _detect_polyphonic_notes(self, audio_data):
        """
        Detect notes in polyphonic audio using harmonic-percussive source separation
        and chroma features.
        
        Args:
            audio_data (np.ndarray): Audio signal data.
            
        Returns:
            list: List of note segments.
        """
        # Separate harmonic and percussive components
        harmonic, percussive = librosa.effects.hpss(audio_data)
        
        # Detect onsets primarily from percussive component for timing accuracy
        onset_frames = librosa.onset.onset_detect(
            y=percussive, 
            sr=self.sample_rate,
            units='frames',
            hop_length=512,
            backtrack=True
        )
        
        # Convert onset frames to time
        onset_times = librosa.frames_to_time(onset_frames, sr=self.sample_rate, hop_length=512)
        
        # Add the end of the audio as the final offset
        offset_times = np.append(onset_times[1:], len(audio_data) / self.sample_rate)
        
        # Create note segments
        note_segments = []
        for i in range(len(onset_times)):
            start_time = onset_times[i]
            end_time = offset_times[i]
            
            # Skip notes that are too short
            if end_time - start_time < self.min_note_duration:
                continue
            
            # Get audio segment (from original audio, not just harmonic part)
            start_sample = int(start_time * self.sample_rate)
            end_sample = int(end_time * self.sample_rate)
            segment = audio_data[start_sample:end_sample]
            
            note_segments.append((start_time, end_time, segment))
        
        return note_segments
    
    def estimate_polyphony(self, audio_segment):
        """
        Estimate the degree of polyphony in an audio segment.
        
        Args:
            audio_segment (np.ndarray): Audio segment.
            
        Returns:
            int: Estimated number of simultaneous notes.
        """
        # Compute chroma features
        chroma = librosa.feature.chroma_cqt(y=audio_segment, sr=self.sample_rate)
        
        # Sum across time to get a histogram of pitch class activity
        chroma_sum = np.sum(chroma, axis=1)
        
        # Count significant pitch classes
        threshold = 0.1 * np.max(chroma_sum)  # Threshold at 10% of max
        significant_pitches = np.sum(chroma_sum > threshold)
        
        return max(1, int(significant_pitches))
    
    def refine_note_boundaries(self, note_segments, audio_data):
        """
        Refine note boundaries using amplitude envelope.
        
        Args:
            note_segments (list): List of (start_time, end_time, segment) tuples.
            audio_data (np.ndarray): Original audio data.
            
        Returns:
            list: Refined note segments.
        """
        refined_segments = []
        
        for start_time, end_time, segment in note_segments:
            # Calculate the amplitude envelope
            envelope = np.abs(librosa.hilbert(segment))
            
            # Find when the envelope falls below a threshold at the end
            threshold = 0.1 * np.max(envelope)
            below_threshold = np.where(envelope < threshold)[0]
            
            # Adjust end time if needed
            if len(below_threshold) > 0 and below_threshold[-1] > 0.8 * len(envelope):
                # Only adjust if the drop is in the latter portion of the note
                new_end_sample = below_threshold[0]
                new_end_time = start_time + new_end_sample / self.sample_rate
                
                # Don't make notes too short
                if new_end_time - start_time >= self.min_note_duration:
                    end_time = new_end_time
                    segment = segment[:new_end_sample]
            
            refined_segments.append((start_time, end_time, segment))
        
        return refined_segments
