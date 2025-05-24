"""
Envelope analysis module.

This module extracts ADSR (Attack, Decay, Sustain, Release) envelope characteristics
from audio segments.
"""
import numpy as np
import librosa
from scipy.signal import find_peaks


class EnvelopeAnalyzer:
    """Class for analyzing ADSR envelope of audio segments."""
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the envelope analyzer.
        
        Args:
            sample_rate (int): Sample rate of the audio signal.
        """
        self.sample_rate = sample_rate
    
    def analyze(self, audio_segment):
        """
        Analyze the ADSR envelope of an audio segment.
        
        Args:
            audio_segment (np.ndarray): Audio segment data.
            
        Returns:
            dict: Envelope analysis results including attack, decay, sustain, and release times.
        """
        # Compute amplitude envelope
        envelope = self._extract_envelope(audio_segment)
        
        # Normalize envelope
        if np.max(envelope) > 0:
            envelope_norm = envelope / np.max(envelope)
        else:
            envelope_norm = envelope
        
        # Get ADSR parameters
        attack_time, decay_time, sustain_level, release_time = self._compute_adsr(envelope_norm)
        
        # Determine envelope shape
        shape = self._classify_envelope_shape(envelope_norm)
        
        # Compile results
        results = {
            'attack_time': float(attack_time),
            'decay_time': float(decay_time),
            'sustain_level': float(sustain_level),
            'release_time': float(release_time),
            'shape': shape,
            'envelope': envelope_norm.tolist()  # Full envelope for visualization
        }
        
        return results
    
    def _extract_envelope(self, audio_segment):
        """
        Extract the amplitude envelope from an audio segment.
        
        Args:
            audio_segment (np.ndarray): Audio segment data.
            
        Returns:
            np.ndarray: Amplitude envelope.
        """
        # Use Hilbert transform for accurate envelope detection
        analytic_signal = librosa.feature.rms(
            y=audio_segment,
            frame_length=512,
            hop_length=128
        )
        
        # Convert 2D array to 1D
        envelope = analytic_signal.flatten()
        
        # Apply smoothing
        if len(envelope) > 3:
            envelope = np.convolve(envelope, np.ones(3)/3, mode='same')
        
        return envelope
    
    def _compute_adsr(self, envelope):
        """
        Compute ADSR parameters from an amplitude envelope.
        
        Args:
            envelope (np.ndarray): Normalized amplitude envelope.
            
        Returns:
            tuple: (attack_time, decay_time, sustain_level, release_time)
        """
        # Handle edge case of very short envelopes
        if len(envelope) < 4:
            return 0.0, 0.0, 0.0, 0.0
        
        # Find peak (end of attack)
        peak_idx = np.argmax(envelope)
        
        # Determine attack time (time to reach 90% of peak)
        attack_threshold = 0.1  # 10% of peak
        attack_points = np.where(envelope[:peak_idx+1] >= attack_threshold)[0]
        if len(attack_points) > 0:
            attack_start = attack_points[0]
            attack_time = (peak_idx - attack_start) / (len(envelope) * 128 / self.sample_rate)
        else:
            attack_time = 0.0
        
        # Find sustain region (look for relatively stable portion after decay)
        # First, determine if there's enough samples after peak for decay/sustain
        if peak_idx >= len(envelope) - 3:
            # Not enough samples for proper decay/sustain/release
            return attack_time, 0.0, 0.0, 0.0
        
        # Compute first derivative to find where envelope stabilizes
        derivative = np.diff(envelope)
        
        # Find potential sustain region (where derivative is close to zero)
        # Look only at region after peak
        post_peak_derivative = derivative[peak_idx:]
        stable_threshold = 0.01  # Threshold for "stable" envelope
        stable_points = np.where(np.abs(post_peak_derivative) < stable_threshold)[0]
        
        # Determine decay and sustain parameters
        if len(stable_points) > 0:
            # Find first stable point after peak (end of decay)
            decay_end = stable_points[0] + peak_idx
            decay_time = (decay_end - peak_idx) / (len(envelope) * 128 / self.sample_rate)
            
            # Sustain level is average of stable region
            sustain_region = envelope[decay_end:int(decay_end + len(envelope)/4)]
            sustain_level = np.mean(sustain_region) if len(sustain_region) > 0 else envelope[decay_end]
        else:
            # No clear sustain region
            decay_time = (len(envelope) - peak_idx) / (len(envelope) * 128 / self.sample_rate)
            sustain_level = envelope[-1]
        
        # Determine release time (from 90% of sustain level to 10%)
        release_start = int(0.8 * len(envelope))  # Assume release starts at 80% of note duration
        release_end = len(envelope) - 1
        
        if release_start < release_end:
            release_segment = envelope[release_start:release_end+1]
            if len(release_segment) > 0 and np.max(release_segment) > 0:
                release_time = (release_end - release_start) / (len(envelope) * 128 / self.sample_rate)
            else:
                release_time = 0.0
        else:
            release_time = 0.0
        
        return attack_time, decay_time, sustain_level, release_time
    
    def _classify_envelope_shape(self, envelope):
        """
        Classify the shape of an envelope into common categories.
        
        Args:
            envelope (np.ndarray): Normalized amplitude envelope.
            
        Returns:
            str: Envelope shape classification.
        """
        # Calculate envelope features
        if len(envelope) < 3:
            return "unknown"
        
        # Find peak position (relative to total length)
        peak_idx = np.argmax(envelope)
        peak_position = peak_idx / len(envelope)
        
        # Calculate area under envelope
        area = np.sum(envelope) / len(envelope)
        
        # Calculate centroid
        times = np.arange(len(envelope))
        centroid = np.sum(times * envelope) / np.sum(envelope) if np.sum(envelope) > 0 else 0
        centroid_position = centroid / len(envelope)
        
        # Decision tree for classification
        if peak_position < 0.1:
            # Peak occurs very early
            if area < 0.3:
                return "percussive"  # Sharp attack, quick decay
            else:
                return "pluck"  # Sharp attack, moderate sustain
        elif peak_position < 0.3:
            # Peak occurs in first third
            if area > 0.6:
                return "pad"  # Moderate attack, high sustain
            else:
                return "plucked_string"  # Moderate attack, moderate decay
        else:
            # Peak occurs later
            if area > 0.7:
                return "swell"  # Slow attack, high sustain
            elif centroid_position > 0.6:
                return "reverse"  # Energy concentrated toward end
            else:
                return "complex"  # Other complex shapes
