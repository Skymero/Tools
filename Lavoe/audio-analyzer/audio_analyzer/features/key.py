"""
Key analysis module.

Determines the musical key (tonic + mode) for a given audio segment via
chroma feature aggregation and template matching against Krumhansl key
profiles.
"""
from typing import Dict, Tuple

import librosa
import numpy as np

_MAJOR_PROFILE = np.array([
    6.35, 2.23, 3.48, 2.33, 4.38, 4.09,
    2.52, 5.19, 2.39, 3.66, 2.29, 2.88
], dtype=np.float32)
_MINOR_PROFILE = np.array([
    6.33, 2.68, 3.52, 5.38, 2.60, 3.53,
    2.54, 4.75, 3.98, 2.69, 3.34, 3.17
], dtype=np.float32)
_NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
               'F#', 'G', 'G#', 'A', 'A#', 'B']


class KeyAnalyzer:
    """Infer the musical key for an audio segment."""

    def __init__(self, sample_rate: int = 44100):
        self.sample_rate = sample_rate

    def analyze(self, audio_segment: np.ndarray) -> Dict[str, object]:
        """Analyze key characteristics for a segment.

        Args:
            audio_segment: Audio samples for the segment.

        Returns:
            Dictionary describing the estimated key, mode, tonic and
            confidence along with supporting chroma statistics.
        """
        if audio_segment is None or len(audio_segment) == 0:
            return self._empty_result()

        audio = np.asarray(audio_segment, dtype=np.float32)
        if not np.any(audio):
            return self._empty_result()

        chroma = librosa.feature.chroma_cqt(y=audio, sr=self.sample_rate)
        if chroma.size == 0:
            return self._empty_result()

        chroma_vector = np.mean(chroma, axis=1)
        chroma_norm = self._normalize_vector(chroma_vector)

        major_scores = self._match_profile(chroma_norm, _MAJOR_PROFILE)
        minor_scores = self._match_profile(chroma_norm, _MINOR_PROFILE)

        best_mode, tonic_index, confidence = self._select_key(major_scores, minor_scores)

        key_label = f"{_NOTE_NAMES[tonic_index]} {best_mode}"

        return {
            'key': key_label,
            'tonic': _NOTE_NAMES[tonic_index],
            'mode': best_mode,
            'confidence': confidence,
            'chroma': chroma_norm.tolist(),
            'major_scores': major_scores.tolist(),
            'minor_scores': minor_scores.tolist()
        }

    def _match_profile(self, chroma: np.ndarray, profile: np.ndarray) -> np.ndarray:
        scores = []
        profile_norm = profile / np.linalg.norm(profile)
        for shift in range(12):
            rotated = np.roll(profile_norm, shift)
            score = np.dot(chroma, rotated)
            scores.append(score)
        return np.array(scores, dtype=np.float32)

    def _select_key(
        self,
        major_scores: np.ndarray,
        minor_scores: np.ndarray
    ) -> Tuple[str, int, float]:
        combined = []
        for idx, score in enumerate(major_scores):
            combined.append(('major', idx, float(score)))
        for idx, score in enumerate(minor_scores):
            combined.append(('minor', idx, float(score)))

        combined.sort(key=lambda item: item[2], reverse=True)
        best_mode, tonic_idx, best_score = combined[0]
        second_score = combined[1][2] if len(combined) > 1 else best_score
        confidence = self._confidence(best_score, second_score)
        return best_mode, tonic_idx, confidence

    @staticmethod
    def _confidence(best: float, second: float) -> float:
        if best <= 0:
            return 0.0
        margin = best - second
        ratio = best / (second + 1e-6)
        confidence = np.tanh(margin * ratio)
        return float(np.clip(confidence, 0.0, 1.0))

    @staticmethod
    def _normalize_vector(vector: np.ndarray) -> np.ndarray:
        total = np.sum(vector)
        if total <= 0:
            return np.zeros_like(vector)
        return vector / total

    @staticmethod
    def _empty_result() -> Dict[str, object]:
        return {
            'key': 'unknown',
            'tonic': None,
            'mode': None,
            'confidence': 0.0,
            'chroma': [0.0] * 12,
            'major_scores': [0.0] * 12,
            'minor_scores': [0.0] * 12
        }
