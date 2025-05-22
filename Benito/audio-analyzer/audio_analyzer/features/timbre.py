"""
Timbre analysis module.

This module extracts and analyzes timbral characteristics of audio segments,
including spectral features and harmonic content.
"""
import numpy as np
import librosa
import essentia
import essentia.standard as es


class TimbreAnalyzer:
    """Class for analyzing timbral features of audio segments."""
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the timbre analyzer.
        
        Args:
            sample_rate (int): Sample rate of the audio signal.
        """
        self.sample_rate = sample_rate
        
        # Initialize Essentia algorithms
        self.spectral_peaks = es.SpectralPeaks(
            sampleRate=sample_rate,
            orderBy='magnitude',
            magnitudeThreshold=0.001
        )
        self.harmonic_peaks = es.HarmonicPeaks()
        self.inharmonicity = es.Inharmonicity()
        self.dissonance = es.Dissonance()
        self.tristimulus = es.Tristimulus()
    
    def analyze(self, audio_segment):
        """
        Analyze timbral features of an audio segment.
        
        Args:
            audio_segment (np.ndarray): Audio segment data.
            
        Returns:
            dict: Timbre analysis results including spectral features,
                  harmonic content, and perceptual characteristics.
        """
        # Convert to Essentia array format if needed
        if not isinstance(audio_segment, essentia.array):
            audio_segment_es = essentia.array(audio_segment.astype(np.float32))
        else:
            audio_segment_es = audio_segment
        
        # Compute basic spectral features using librosa
        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio_segment, sr=self.sample_rate
        ).mean()
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(
            y=audio_segment, sr=self.sample_rate
        ).mean()
        
        spectral_contrast = librosa.feature.spectral_contrast(
            y=audio_segment, sr=self.sample_rate
        ).mean()
        
        spectral_flatness = librosa.feature.spectral_flatness(
            y=audio_segment
        ).mean()
        
        spectral_rolloff = librosa.feature.spectral_rolloff(
            y=audio_segment, sr=self.sample_rate
        ).mean()
        
        # Compute harmonic features using Essentia
        spectrum = es.Spectrum()(audio_segment_es)
        frequencies, magnitudes = self.spectral_peaks(spectrum)
        
        # Check if we have peaks before proceeding
        if len(frequencies) > 0:
            # Get fundamental frequency from the strongest peak
            f0 = float(frequencies[0])
            
            # Compute harmonic peaks
            harmonic_frequencies, harmonic_magnitudes = self.harmonic_peaks(
                frequencies, magnitudes, f0
            )
            
            # Compute inharmonicity
            if len(harmonic_frequencies) > 1:
                inharmonicity_value = self.inharmonicity(harmonic_frequencies, harmonic_magnitudes)
                
                # Compute dissonance
                dissonance_value = self.dissonance(frequencies, magnitudes)
                
                # Compute tristimulus (balance of harmonics)
                tristimulus = self.tristimulus(harmonic_frequencies, harmonic_magnitudes)
                
                # Calculate harmonic-to-noise ratio
                total_energy = np.sum(magnitudes**2)
                harmonic_energy = np.sum(harmonic_magnitudes**2)
                harmonic_ratio = harmonic_energy / total_energy if total_energy > 0 else 0
            else:
                inharmonicity_value = 0
                dissonance_value = 0
                tristimulus = [0, 0, 0]
                harmonic_ratio = 0
        else:
            inharmonicity_value = 0
            dissonance_value = 0
            tristimulus = [0, 0, 0]
            harmonic_ratio = 0
        
        # Calculate perceptual metrics
        # Brightness: higher spectral centroid = brighter sound
        perceived_brightness = self._normalize_brightness(spectral_centroid)
        
        # Warmth: combination of low-frequency content and harmonic richness
        perceived_warmth = self._calculate_warmth(
            audio_segment, 
            spectral_centroid, 
            harmonic_ratio, 
            inharmonicity_value
        )
        
        # Calculate noisiness (opposite of harmonic content)
        noisiness = 1.0 - harmonic_ratio
        
        # Calculate roughness (related to dissonance)
        roughness = dissonance_value
        
        # Compile results
        results = {
            'spectral_centroid': float(spectral_centroid),
            'spectral_bandwidth': float(spectral_bandwidth),
            'spectral_contrast': float(np.mean(spectral_contrast)),
            'spectral_flatness': float(spectral_flatness),
            'spectral_rolloff': float(spectral_rolloff),
            'inharmonicity': float(inharmonicity_value),
            'dissonance': float(dissonance_value),
            'tristimulus': [float(t) for t in tristimulus],
            'harmonic_ratio': float(harmonic_ratio),
            'noisiness': float(noisiness),
            'roughness': float(roughness),
            'perceived_brightness': float(perceived_brightness),
            'perceived_warmth': float(perceived_warmth)
        }
        
        return results
    
    def _normalize_brightness(self, centroid):
        """
        Normalize spectral centroid to a 0-1 brightness scale.
        
        Args:
            centroid (float): Spectral centroid in Hz.
            
        Returns:
            float: Normalized brightness value (0-1).
        """
        # Map typical centroid range (500-5000 Hz) to 0-1 scale
        min_centroid = 500
        max_centroid = 5000
        normalized = (centroid - min_centroid) / (max_centroid - min_centroid)
        return max(0, min(normalized, 1))
    
    def _calculate_warmth(self, audio, centroid, harmonic_ratio, inharmonicity):
        """
        Calculate a warmth metric based on multiple factors.
        
        Args:
            audio (np.ndarray): Audio data.
            centroid (float): Spectral centroid.
            harmonic_ratio (float): Harmonic to noise ratio.
            inharmonicity (float): Inharmonicity value.
            
        Returns:
            float: Warmth metric (0-1).
        """
        # Calculate low-frequency energy ratio
        spec = np.abs(librosa.stft(audio))
        freqs = librosa.fft_frequencies(sr=self.sample_rate)
        low_mask = freqs < 500  # Consider frequencies below 500 Hz as "low"
        low_energy = np.sum(spec[low_mask, :])
        total_energy = np.sum(spec)
        low_energy_ratio = low_energy / total_energy if total_energy > 0 else 0
        
        # Combine factors:
        # - Higher low-frequency content increases warmth
        # - Lower spectral centroid increases warmth
        # - Higher harmonic ratio increases warmth
        # - Lower inharmonicity increases warmth
        
        # Normalize centroid contribution (invert it since lower centroid = warmer)
        centroid_factor = 1.0 - self._normalize_brightness(centroid)
        
        # Combine all factors with weights
        warmth = (
            0.4 * low_energy_ratio + 
            0.3 * centroid_factor + 
            0.2 * harmonic_ratio + 
            0.1 * (1.0 - min(inharmonicity, 1.0))
        )
        
        return max(0, min(warmth, 1))
