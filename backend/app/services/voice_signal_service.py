"""
Voice signal analysis service.
Phase 2 MVP: heuristic audio-risk scoring from uploaded audio bytes.
"""
from __future__ import annotations

import io
import wave
from typing import Dict


class VoiceSignalService:
    """Lightweight audio analyzer for early multimodal MVP."""

    def analyze(self, audio_bytes: bytes) -> Dict[str, float]:
        if not audio_bytes:
            return {
                "voice_risk_score": 0.0,
                "confidence": 0.0,
                "method": "empty_audio",
                "details": {"samples": 0.0},
            }

        # Default fallback for non-WAV input: use payload-size heuristic.
        score = min(1.0, max(0.0, len(audio_bytes) / 400000.0))
        confidence = 0.35
        details = {
            "payload_bytes": float(len(audio_bytes)),
            "rms_norm": 0.0,
            "peak_norm": 0.0,
            "zero_crossing_rate": 0.0,
        }
        method = "payload_heuristic"

        try:
            with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
                n_frames = wav_file.getnframes()
                sampwidth = wav_file.getsampwidth()
                n_channels = wav_file.getnchannels()
                frame_rate = wav_file.getframerate()
                raw = wav_file.readframes(n_frames)

            if sampwidth != 2 or n_frames <= 0:
                return {
                    "voice_risk_score": score,
                    "confidence": confidence,
                    "method": method,
                    "details": details,
                }

            import array

            samples = array.array("h")
            samples.frombytes(raw)
            if n_channels > 1:
                # Downmix by selecting first channel values.
                samples = array.array("h", samples[::n_channels])

            abs_vals = [abs(s) for s in samples]
            max_amp = 32768.0
            peak_norm = (max(abs_vals) / max_amp) if abs_vals else 0.0
            rms = (sum(v * v for v in abs_vals) / max(1, len(abs_vals))) ** 0.5
            rms_norm = rms / max_amp

            zc = 0
            prev = samples[0] if samples else 0
            for cur in samples[1:]:
                if (prev < 0 <= cur) or (prev >= 0 > cur):
                    zc += 1
                prev = cur
            zcr = zc / max(1, len(samples) - 1)

            # Heuristic stress score:
            # high RMS/peak and high zero crossing can indicate strained/shaky speech.
            score = min(1.0, max(0.0, (0.50 * rms_norm) + (0.30 * peak_norm) + (0.20 * (zcr * 10.0))))
            confidence = 0.70 if frame_rate >= 8000 else 0.55
            method = "wav_rms_peak_zcr"
            details = {
                "payload_bytes": float(len(audio_bytes)),
                "rms_norm": float(rms_norm),
                "peak_norm": float(peak_norm),
                "zero_crossing_rate": float(zcr),
                "sample_rate_hz": float(frame_rate),
                "samples": float(len(samples)),
            }
        except Exception:
            # Keep fallback score and method.
            pass

        return {
            "voice_risk_score": float(score),
            "confidence": float(confidence),
            "method": method,
            "details": details,
        }

