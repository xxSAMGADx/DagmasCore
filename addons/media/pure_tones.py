#!/usr/bin/env python3
"""
DAGMAS Brain Vault - Pure Tones & Local Music Engine
Synthesizes pure Solfeggio frequencies (432Hz, 528Hz, 741Hz), binaural beats
(Alpha, Theta, Delta), and ambient harmonic soundscapes completely on-device.
"""

import math
import wave
import struct
from pathlib import Path
from typing import Dict, Any, List

# Standard Solfeggio & Brainwave Frequencies
SOLFEGGIO_FREQUENCIES = {
    "174": "174 Hz - Foundation & Natural Pain Relief",
    "285": "285 Hz - Cellular Restoration & Energy Field",
    "396": "396 Hz - Liberating Guilt & Grounding",
    "417": "417 Hz - Facilitating Change & Clearing Negativity",
    "432": "432 Hz - Harmonic Natural Resonance & Calm",
    "528": "528 Hz - Transformation, DNA Repair & Healing",
    "639": "639 Hz - Harmonious Relationships & Connection",
    "741": "741 Hz - Intuition & Emotional Detoxification",
    "852": "852 Hz - Awakening Higher Consciousness",
    "963": "963 Hz - Pure Transcendent Awareness"
}

BRAINWAVE_BINAURAL = {
    "delta": {"carrier": 200, "beat": 2.5, "desc": "0.5 - 4 Hz: Deep Sleep & Restoration"},
    "theta": {"carrier": 220, "beat": 6.0, "desc": "4 - 8 Hz: Deep Meditation & REM Dream"},
    "alpha": {"carrier": 250, "beat": 10.0, "desc": "8 - 13 Hz: Calm Focus, Flow State & Relaxation"},
    "beta":  {"carrier": 300, "beat": 18.0, "desc": "13 - 30 Hz: Alert Problem Solving"}
}

class PureTonesEngine:
    """Generates clean mathematical pure tone frequencies and binaural audio files."""

    def __init__(self, output_dir: Path = None):
        self.output_dir = output_dir or Path("~/.brain-vault/memory/audio_vault").expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_solfeggio_wave(self, freq_hz: float, duration_seconds: int = 10,
                                sample_rate: int = 44100, amplitude: float = 0.5) -> Path:
        """Synthesizes a pure sine wave audio file with gentle fade in/out envelopes."""
        output_path = self.output_dir / f"tone_{int(freq_hz)}hz_{duration_seconds}s.wav"
        total_samples = sample_rate * duration_seconds

        with wave.open(str(output_path), "wb") as wav:
            wav.setnchannels(1)  # Mono
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)

            for i in range(total_samples):
                t = float(i) / sample_rate
                # 0.5s fade in / fade out envelope
                fade = min(1.0, float(i) / (sample_rate * 0.5), float(total_samples - i) / (sample_rate * 0.5))
                sample_val = amplitude * fade * math.sin(2.0 * math.pi * freq_hz * t)
                packed = struct.pack("<h", int(sample_val * 32767.0))
                wav.writeframes(packed)

        return output_path

    def generate_binaural_wave(self, wave_type: str = "alpha", duration_seconds: int = 10,
                               sample_rate: int = 44100, amplitude: float = 0.5) -> Path:
        """Synthesizes a binaural stereo wave (left ear carrier, right ear carrier + beat)."""
        preset = BRAINWAVE_BINAURAL.get(wave_type.lower(), BRAINWAVE_BINAURAL["alpha"])
        carrier = preset["carrier"]
        beat = preset["beat"]
        output_path = self.output_dir / f"binaural_{wave_type}_{int(carrier)}hz_{duration_seconds}s.wav"
        total_samples = sample_rate * duration_seconds

        freq_left = carrier - (beat / 2.0)
        freq_right = carrier + (beat / 2.0)

        with wave.open(str(output_path), "wb") as wav:
            wav.setnchannels(2)  # Stereo
            wav.setsampwidth(2)  # 16-bit
            wav.setframerate(sample_rate)

            for i in range(total_samples):
                t = float(i) / sample_rate
                fade = min(1.0, float(i) / (sample_rate * 0.5), float(total_samples - i) / (sample_rate * 0.5))
                sample_l = amplitude * fade * math.sin(2.0 * math.pi * freq_left * t)
                sample_r = amplitude * fade * math.sin(2.0 * math.pi * freq_right * t)
                packed = struct.pack("<hh", int(sample_l * 32767.0), int(sample_r * 32767.0))
                wav.writeframes(packed)

        return output_path


if __name__ == "__main__":
    pte = PureTonesEngine()
    print("Available Solfeggio Frequencies:")
    for k, v in SOLFEGGIO_FREQUENCIES.items():
        print(f"  {k}Hz -> {v}")
    tone = pte.generate_solfeggio_wave(528, duration_seconds=2)
    print("Generated 528Hz Pure Healing Tone:", tone)
