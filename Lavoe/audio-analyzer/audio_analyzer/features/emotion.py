"""
Emotion analysis module.

Provides heuristic estimation of emotional content for monophonic
or polyphonic audio segments using acoustic descriptors related to
arousal (energy, tempo, brightness) and valence (harmonic content,
spectral smoothness).
"""
import math
from typing import Dict, List

import librosa
import numpy as np


class EmotionAnalyzer:
    """Estimate emotional characteristics from an audio segment."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def analyze(self, audio_segment: np.ndarray) -> Dict[str, object]:
        """Analyze emotional content for a segment.

        Args:
            audio_segment: Audio samples for the segment.

        Returns:
            Dictionary with emotion labels, arousal/valence, and auxiliary
            acoustic descriptors useful for further inspection.
        """
        if audio_segment is None or len(audio_segment) == 0:
            return self._empty_result()

        audio = np.asarray(audio_segment, dtype=np.float32)
        if not np.any(audio):
            return self._empty_result()

        features = self._extract_features(audio)
        valence = self._estimate_valence(features)
        arousal = self._estimate_arousal(features)
        intensity = float(np.clip((arousal + 1.0) / 2.0, 0.0, 1.0))
        emotions = self._map_to_emotions(valence, arousal)

        return {
            'emotions': emotions,
            'intensity': intensity,
            'valence': float(valence),
            'arousal': float(arousal),
            'features': features
        }

    def _empty_result(self) -> Dict[str, object]:
        return {
            'emotions': [{'label': 'neutral', 'score': 0.0}],
            'intensity': 0.0,
            'valence': 0.0,
            'arousal': 0.0,
            'features': {}
        }

    def _extract_features(self, audio: np.ndarray) -> Dict[str, float]:
        rms = librosa.feature.rms(y=audio)[0]
        rms_mean = float(np.mean(rms))
        rms_std = float(np.std(rms))

        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=audio)))

        spectral_centroid = librosa.feature.spectral_centroid(
            y=audio,
            sr=self.sample_rate
        )[0]
        centroid_mean = float(np.mean(spectral_centroid))
        centroid_norm = self._normalize(centroid_mean, 500.0, 5000.0)

        spectral_flatness = float(
            np.mean(librosa.feature.spectral_flatness(y=audio))
        )

        onset_env = librosa.onset.onset_strength(y=audio, sr=self.sample_rate)
        tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=self.sample_rate)
        tempo_bpm = float(tempo[0]) if tempo.size else 0.0
        tempo_norm = self._normalize(tempo_bpm, 40.0, 200.0)

        spec = np.abs(librosa.stft(audio))
        flux = librosa.onset.onset_strength(S=spec, sr=self.sample_rate)
        spectral_flux = float(np.mean(flux)) if flux.size else 0.0
        spectral_flux_norm = self._normalize(spectral_flux, 0.0, 5.0)

        harmonic, percussive = librosa.effects.hpss(audio)
        harmonic_energy = float(np.mean(harmonic**2))
        percussive_energy = float(np.mean(percussive**2))
        total_energy = harmonic_energy + percussive_energy + 1e-9
        harmonic_ratio = harmonic_energy / total_energy
        percussive_ratio = percussive_energy / total_energy

        mfcc = librosa.feature.mfcc(y=audio, sr=self.sample_rate, n_mfcc=5)
        mfcc1 = float(np.mean(mfcc[0])) if mfcc.shape[0] else 0.0
        mfcc2 = float(np.mean(mfcc[1])) if mfcc.shape[0] > 1 else 0.0

        return {
            'rms_mean': rms_mean,
            'rms_std': rms_std,
            'zcr_mean': zcr,
            'spectral_centroid': centroid_mean,
            'brightness': centroid_norm,
            'spectral_flatness': spectral_flatness,
            'tempo_bpm': tempo_bpm,
            'tempo_norm': tempo_norm,
            'spectral_flux': spectral_flux,
            'spectral_flux_norm': spectral_flux_norm,
            'harmonic_ratio': harmonic_ratio,
            'percussive_ratio': percussive_ratio,
            'mfcc1': mfcc1,
            'mfcc2': mfcc2
        }

    def _estimate_valence(self, features: Dict[str, float]) -> float:
        harmonic_component = 0.6 * features['harmonic_ratio']
        brightness_component = 0.25 * (1.0 - features['brightness'])
        smoothness_component = 0.15 * (1.0 - features['spectral_flatness'])
        valence = harmonic_component + brightness_component + smoothness_component
        valence = (valence * 2.0) - 1.0
        return float(np.clip(valence, -1.0, 1.0))

    def _estimate_arousal(self, features: Dict[str, float]) -> float:
        energy_norm = self._normalize(features['rms_mean'], 0.0, 0.4)
        energy_var_norm = self._normalize(features['rms_std'], 0.0, 0.2)
        tempo_norm = features['tempo_norm']
        brightness = features['brightness']
        percussive = features['percussive_ratio']
        flux = features['spectral_flux_norm']

        arousal = (
            0.35 * energy_norm +
            0.20 * tempo_norm +
            0.15 * brightness +
            0.15 * percussive +
            0.10 * flux +
            0.05 * energy_var_norm
        )
        arousal = (arousal * 2.0) - 1.0
        return float(np.clip(arousal, -1.0, 1.0))

    def _map_to_emotions(self, valence: float, arousal: float) -> List[Dict[str, float]]:
        val_norm = (valence + 1.0) / 2.0
        aro_norm = (arousal + 1.0) / 2.0

        prototypes = {
            'joyful': (0.85, 0.85),
            'energetic': (0.65, 0.95),
            'peaceful': (0.75, 0.35),
            'content': (0.65, 0.45),
            'tense': (0.35, 0.85),
            'aggressive': (0.20, 0.90),
            'melancholic': (0.30, 0.30),
            'sad': (0.25, 0.20),
            'neutral': (0.50, 0.50)
        }

        emotions: List[Dict[str, float]] = []
        for label, (p_val, p_aro) in prototypes.items():
            dist = math.sqrt((val_norm - p_val) ** 2 + (aro_norm - p_aro) ** 2)
            score = max(0.0, 1.0 - dist * 1.5)
            if score > 0.05:
                emotions.append({'label': label, 'score': float(score)})

        if not emotions:
            return [{'label': 'neutral', 'score': 1.0}]

        emotions.sort(key=lambda item: item['score'], reverse=True)
        top_score = emotions[0]['score'] or 1.0
        normalized = [
            {'label': item['label'], 'score': float(np.clip(item['score'] / top_score, 0.0, 1.0))}
            for item in emotions
        ]
        return normalized[:4]

    @staticmethod
    def _normalize(value: float, minimum: float, maximum: float) -> float:
        if maximum <= minimum:
            return 0.0
        norm = (value - minimum) / (maximum - minimum)
        return float(np.clip(norm, 0.0, 1.0))
