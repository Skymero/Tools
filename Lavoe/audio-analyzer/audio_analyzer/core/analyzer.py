"""
Main audio analyzer module.

This module orchestrates the complete audio analysis process, integrating
note detection and all feature extraction components.
"""
import os
import json
import csv
import numpy as np
import pandas as pd
import librosa

from ..core.audio_loader import AudioLoader
from ..core.note_detector import NoteDetector
from ..features.pitch import PitchAnalyzer
from ..features.timbre import TimbreAnalyzer
from ..features.envelope import EnvelopeAnalyzer
from ..features.instrument import InstrumentClassifier
from ..features.effects import EffectsAnalyzer
from ..features.dynamics import DynamicsAnalyzer
from ..features.articulation import ArticulationAnalyzer
from ..features.texture import TextureAnalyzer
from ..features.spatial import SpatialAnalyzer
from ..features.emotion import EmotionAnalyzer
from ..features.key import KeyAnalyzer
from ..utils.conversions import hz_to_note


class AudioAnalyzer:
    """Main class for comprehensive audio analysis."""
    
    def __init__(self, sample_rate=44100):
        """
        Initialize the audio analyzer with all required components.
        
        Args:
            sample_rate (int): Sample rate for audio processing.
        """
        self.sample_rate = sample_rate
        
        # Initialize components
        self.audio_loader = AudioLoader(sample_rate=sample_rate)
        self.note_detector = NoteDetector(sample_rate=sample_rate)
        
        # Initialize feature analyzers
        self.pitch_analyzer = PitchAnalyzer(sample_rate=sample_rate)
        self.timbre_analyzer = TimbreAnalyzer(sample_rate=sample_rate)
        self.envelope_analyzer = EnvelopeAnalyzer(sample_rate=sample_rate)
        self.instrument_classifier = InstrumentClassifier(sample_rate=sample_rate)
        self.effects_analyzer = EffectsAnalyzer(sample_rate=sample_rate)
        self.dynamics_analyzer = DynamicsAnalyzer(sample_rate=sample_rate)
        self.articulation_analyzer = ArticulationAnalyzer(sample_rate=sample_rate)
        self.texture_analyzer = TextureAnalyzer(sample_rate=sample_rate)
        self.spatial_analyzer = SpatialAnalyzer(sample_rate=sample_rate)
        self.emotion_analyzer = EmotionAnalyzer(sample_rate=sample_rate)
        self.key_analyzer = KeyAnalyzer(sample_rate=sample_rate)
    
    def analyze_file(self, file_path, start_time=None, end_time=None, monophonic=None):
        """
        Analyze an audio file and extract all features.
        
        Args:
            file_path (str): Path to the audio file.
            start_time (float, optional): Start time in seconds for analysis.
            end_time (float, optional): End time in seconds for analysis.
            monophonic (bool, optional): Whether the audio is monophonic. If None, it will be detected.
            
        Returns:
            dict: Analysis results containing all extracted features.
        """
        # Load audio file
        audio_data, sample_rate, duration = self.audio_loader.load_file(
            file_path, start_time, end_time
        )
        
        # Preprocess audio
        processed_audio = self.audio_loader.preprocess(audio_data, normalize=True)
        
        # Auto-detect if monophonic if not specified
        if monophonic is None:
            # Simple heuristic: compute spectral flatness and use a threshold
            spec_flat = np.mean(librosa.feature.spectral_flatness(y=processed_audio))
            monophonic = spec_flat > 0.1  # Higher flatness often indicates monophonic content
        
        # Detect notes
        note_segments = self.note_detector.detect_notes(
            processed_audio, monophonic=monophonic
        )
        
        # Refine note boundaries
        refined_segments = self.note_detector.refine_note_boundaries(
            note_segments, processed_audio
        )
        
        # Analyze each note
        notes_analysis = []
        for i, (start_time, end_time, segment) in enumerate(refined_segments):
            note_analysis = self._analyze_note(segment, start_time, end_time, i)
            notes_analysis.append(note_analysis)
        
        # Compile full analysis
        results = {
            'file_path': os.path.basename(file_path),
            'duration': duration,
            'sample_rate': sample_rate,
            'number_of_notes': len(notes_analysis),
            'is_monophonic': monophonic,
            'notes': notes_analysis
        }
        
        return results
    
    def _analyze_note(self, segment, start_time, end_time, note_index):
        """
        Analyze a single note segment and extract all features.
        
        Args:
            segment (np.ndarray): Audio data for the note.
            start_time (float): Start time of the note in seconds.
            end_time (float): End time of the note in seconds.
            note_index (int): Index of the note in the sequence.
            
        Returns:
            dict: Analysis results for the note.
        """
        duration = end_time - start_time
        
        # Extract all features
        # 1. Pitch and Musical Note
        pitch_data = self.pitch_analyzer.analyze(segment)
        fundamental_hz = pitch_data['fundamental_frequency']
        note_name = hz_to_note(fundamental_hz)
        
        # 2. Instrument Identification
        instrument_data = self.instrument_classifier.classify(segment)
        
        # 3. Timbre and Harmonic Content
        timbre_data = self.timbre_analyzer.analyze(segment)
        
        # 4. Envelope (ADSR)
        envelope_data = self.envelope_analyzer.analyze(segment)
        
        # 5-8. Effects (Vibrato, Reverb, Distortion, Filtering)
        effects_data = self.effects_analyzer.analyze(segment)
        
        # 9. Dynamics
        dynamics_data = self.dynamics_analyzer.analyze(segment)
        
        # 10. Articulation
        articulation_data = self.articulation_analyzer.analyze(segment)
        
        # 11. Texture
        texture_data = self.texture_analyzer.analyze(segment)
        
        # 12. Space and Positioning
        spatial_data = self.spatial_analyzer.analyze(segment)
        
        # 13. Emotion
        emotion_data = self.emotion_analyzer.analyze(segment)
        
        # 18. Key
        key_data = self.key_analyzer.analyze(segment)

        # Combine all analysis into a single result
        note_analysis = {
            'note_index': note_index,
            'start_time': start_time,
            'end_time': end_time,
            'duration': duration,
            
            # Pitch and Note
            'pitch_hz': fundamental_hz,
            'note_name': note_name,
            'pitch_confidence': pitch_data['confidence'],
            'pitch_stability': pitch_data['stability'],
            
            # Instrument
            'instrument': instrument_data['instrument'],
            'instrument_confidence': instrument_data['confidence'],
            'instrument_family': instrument_data['family'],
            
            # Timbre
            'spectral_centroid': timbre_data['spectral_centroid'],
            'spectral_bandwidth': timbre_data['spectral_bandwidth'],
            'spectral_contrast': timbre_data['spectral_contrast'],
            'harmonic_ratio': timbre_data['harmonic_ratio'],
            'perceived_brightness': timbre_data['perceived_brightness'],
            'perceived_warmth': timbre_data['perceived_warmth'],
            
            # Envelope
            'attack_time': envelope_data['attack_time'],
            'decay_time': envelope_data['decay_time'],
            'sustain_level': envelope_data['sustain_level'],
            'release_time': envelope_data['release_time'],
            'envelope_shape': envelope_data['shape'],
            
            # Effects
            'vibrato_rate': effects_data['vibrato']['rate'],
            'vibrato_depth': effects_data['vibrato']['depth'],
            'vibrato_extent': effects_data['vibrato']['extent'],
            'reverb_rt60': effects_data['reverb']['rt60'],
            'reverb_drr': effects_data['reverb']['drr'],
            'distortion_amount': effects_data['distortion']['amount'],
            'distortion_type': effects_data['distortion']['type'],
            'filter_type': effects_data['filter']['type'],
            'filter_cutoff': effects_data['filter']['cutoff'],
            'filter_resonance': effects_data['filter']['resonance'],
            
            # Dynamics
            'loudness_lufs': dynamics_data['loudness_lufs'],
            'dynamic_range': dynamics_data['dynamic_range'],
            'crest_factor': dynamics_data['crest_factor'],
            'compression_detected': dynamics_data['compression_detected'],
            
            # Articulation
            'articulation_type': articulation_data['type'],
            'articulation_confidence': articulation_data['confidence'],
            
            # Texture
            'polyphony_degree': texture_data['polyphony_degree'],
            'density': texture_data['density'],
            
            # Spatial
            'stereo_position': spatial_data['position'],
            'stereo_width': spatial_data['width'],
            
            # Emotion
            'emotional_content': emotion_data['emotions'],
            'emotional_intensity': emotion_data['intensity'],

            # Key
            'estimated_key': key_data['key'],
            'key_confidence': key_data['confidence'],
            'key_mode': key_data['mode'],
            'key_tonic': key_data['tonic']
        }
        
        return note_analysis
    
    def export_results(self, results, output_path, format='json'):
        """
        Export analysis results to a file.
        
        Args:
            results (dict): Analysis results.
            output_path (str): Path to save the results.
            format (str): Output format ('json' or 'csv').
            
        Returns:
            str: Path to the saved file.
        """
        if format.lower() == 'json':
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            return output_path
        
        elif format.lower() == 'csv':
            # Flatten the notes for CSV output
            notes = results['notes']
            df = pd.DataFrame(notes)
            
            # Add file information as columns
            df['file_path'] = results['file_path']
            df['total_duration'] = results['duration']
            df['is_monophonic'] = results['is_monophonic']
            
            df.to_csv(output_path, index=False)
            return output_path
        
        else:
            raise ValueError(f"Unsupported export format: {format}. Use 'json' or 'csv'.")
