"""
Pitch analysis module.

This module handles pitch detection, frequency estimation, and related
characteristics for audio segments.
"""
import numpy as np
import librosa
import crepe
from scipy.stats import hmean


class PitchAnalyzer:
    """Class for analyzing pitch-related features of audio segments."""
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the pitch analyzer.
        
        Args:
            sample_rate (int): Sample rate of the audio signal.
        """
        self.sample_rate = sample_rate
    
    def analyze(self, audio_segment):
        """
        Analyze pitch-related features of an audio segment.
        
        Args:
            audio_segment (np.ndarray): Audio segment data.
            
        Returns:
            dict: Pitch analysis results including fundamental frequency,
                  confidence, stability, and other pitch-related metrics.
        """
        # Check if segment is long enough for analysis
        if len(audio_segment) < 512:
            # Return default values for very short segments
            return {
                'fundamental_frequency': 0.0,
                'confidence': 0.0,
                'stability': 0.0,
                'pitch_trajectory': np.array([]),
                'confidence_trajectory': np.array([]),
                'is_stable': False
            }
        
        # Use CREPE for high-quality pitch detection
        time, frequency, confidence, activation = crepe.predict(
            audio_segment, 
            self.sample_rate, 
            viterbi=True,
            model_capacity='full'
        )
        
        # Filter out low-confidence estimates
        confidence_threshold = 0.5
        valid_indices = confidence > confidence_threshold
        
        if np.sum(valid_indices) > 0:
            valid_frequencies = frequency[valid_indices]
            valid_confidences = confidence[valid_indices]
            
            # Calculate weighted average for fundamental frequency
            weighted_freq = np.sum(valid_frequencies * valid_confidences) / np.sum(valid_confidences)
            
            # Pitch stability (lower value = more stable)
            if len(valid_frequencies) > 1:
                pitch_stability = np.std(valid_frequencies) / weighted_freq if weighted_freq > 0 else 1.0
                is_stable = pitch_stability < 0.05  # Threshold for stability
            else:
                pitch_stability = 0.0
                is_stable = True
            
            # Mean confidence
            mean_confidence = np.mean(valid_confidences)
        else:
            # Fallback to YIN algorithm if CREPE has no confident estimates
            yin_pitch = librosa.yin(
                audio_segment, 
                fmin=librosa.note_to_hz('C2'),
                fmax=librosa.note_to_hz('C7'),
                sr=self.sample_rate
            )
            
            # Filter out infinite values
            valid_yin = yin_pitch[np.isfinite(yin_pitch)]
            
            if len(valid_yin) > 0:
                weighted_freq = hmean(valid_yin[valid_yin > 0]) if np.any(valid_yin > 0) else 0
                pitch_stability = np.std(valid_yin) / weighted_freq if weighted_freq > 0 else 1.0
                is_stable = pitch_stability < 0.1
                mean_confidence = 0.3  # Lower confidence for YIN algorithm
            else:
                weighted_freq = 0.0
                pitch_stability = 1.0
                is_stable = False
                mean_confidence = 0.0
        
        # Compile results
        results = {
            'fundamental_frequency': float(weighted_freq),
            'confidence': float(mean_confidence),
            'stability': float(1.0 - min(pitch_stability, 1.0)),  # Convert to 0-1 scale where 1 is stable
            'pitch_trajectory': frequency,
            'confidence_trajectory': confidence,
            'is_stable': is_stable
        }
        
        return results
    
    def detect_vibrato(self, pitch_trajectory, time_points, min_rate=4, max_rate=8):
        """
        Detect vibrato in a pitch trajectory.
        
        Args:
            pitch_trajectory (np.ndarray): Array of pitch values over time.
            time_points (np.ndarray): Corresponding time points.
            min_rate (float): Minimum vibrato rate in Hz.
            max_rate (float): Maximum vibrato rate in Hz.
            
        Returns:
            dict: Vibrato analysis results including rate, depth, and extent.
        """
        # Need sufficient data for vibrato detection
        if len(pitch_trajectory) < 10:
            return {'present': False, 'rate': 0, 'depth': 0, 'extent': 0}
        
        # Normalize and detrend the pitch trajectory
        if np.std(pitch_trajectory) > 0:
            normalized = (pitch_trajectory - np.mean(pitch_trajectory)) / np.std(pitch_trajectory)
        else:
            normalized = np.zeros_like(pitch_trajectory)
            
        # Compute FFT to find oscillation rate
        if len(normalized) > 1:
            sample_rate = 1.0 / np.mean(np.diff(time_points))
            fft = np.abs(np.fft.rfft(normalized))
            freqs = np.fft.rfftfreq(len(normalized), 1.0/sample_rate)
            
            # Look for peaks in the vibrato frequency range (typically 4-8 Hz)
            valid_indices = (freqs >= min_rate) & (freqs <= max_rate)
            
            if np.any(valid_indices):
                peak_idx = np.argmax(fft[valid_indices]) + np.where(valid_indices)[0][0]
                vibrato_rate = freqs[peak_idx]
                vibrato_amplitude = fft[peak_idx] / (len(normalized) / 2)
                
                # Calculate vibrato depth in semitones
                # Convert normalized values back to Hz variation and then to semitones
                std_dev = np.std(pitch_trajectory)
                avg_pitch = np.mean(pitch_trajectory)
                vibrato_depth = 12 * np.log2(1 + vibrato_amplitude * std_dev / avg_pitch) if avg_pitch > 0 else 0
                
                # Calculate vibrato extent (percentage of the note with vibrato)
                # Simple method: count zero-crossings
                zero_crossings = np.sum(np.diff(normalized > 0))
                vibrato_extent = min(zero_crossings / len(normalized), 1.0)
                
                return {
                    'present': vibrato_amplitude > 0.1,  # Threshold for vibrato presence
                    'rate': float(vibrato_rate),
                    'depth': float(vibrato_depth),
                    'extent': float(vibrato_extent)
                }
        
        # Default: no vibrato detected
        return {'present': False, 'rate': 0, 'depth': 0, 'extent': 0}
