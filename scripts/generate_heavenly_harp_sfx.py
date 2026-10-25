"""
Generate Heavenly Harp Glissando & Shimmering Bell Chime SFX
============================================================
Synthesizes a clean, non-noise acoustic harp glissando (Major 9th arpeggio)
layered with celestial bell harmonics for the comedy heavenly punchline.
Complies with Dan's strict rule: NO white-noise or filtered-noise static!
"""

import numpy as np
from scipy.io import wavfile
from pathlib import Path

SAMPLE_RATE = 48000
DURATION = 5.0

def generate_harp_sfx(output_path: Path):
    total_samples = int(DURATION * SAMPLE_RATE)
    audio = np.zeros(total_samples, dtype=np.float32)

    # Ascending harp notes: C4, E4, G4, B4, D5, E5, G5, B5, D6, E6, G6
    notes_freq = [
        261.63, 329.63, 392.00, 493.88, 587.33, 659.25, 783.99, 987.77, 1174.66, 1318.51, 1567.98
    ]

    for idx, freq in enumerate(notes_freq):
        st_time = 0.08 * idx
        note_dur = DURATION - st_time
        st_idx = int(st_time * SAMPLE_RATE)
        n_samples = total_samples - st_idx
        if n_samples <= 0:
            continue
        t = np.linspace(0, note_dur, n_samples, endpoint=False)
        # Fundamental + sweet 2nd & 3rd string harmonics
        string = (np.sin(2 * np.pi * freq * t) * 0.60 +
                  np.sin(2 * np.pi * 2 * freq * t) * 0.25 +
                  np.sin(2 * np.pi * 3 * freq * t) * 0.10)
        envelope = np.exp(-2.2 * t)
        audio[st_idx:] += (string * envelope * 0.25).astype(np.float32)

    # Shimmering angelic bell chord at peak (G6 & E6)
    top_idx = int(0.9 * SAMPLE_RATE)
    t_bell = np.linspace(0, DURATION - 0.9, total_samples - top_idx, endpoint=False)
    bell = (np.sin(2 * np.pi * 1567.98 * t_bell) * 0.5 + np.sin(2 * np.pi * 2093.00 * t_bell) * 0.3) * np.exp(-1.5 * t_bell) * 0.2
    audio[top_idx:] += bell.astype(np.float32)

    # Normalize
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio / max_val * 0.85

    pcm = (audio * 32767).astype(np.int16)
    stereo = np.column_stack([pcm, pcm])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(str(output_path), SAMPLE_RATE, stereo)
    print(f"Generated clean acoustic harp SFX: {output_path} ({output_path.stat().st_size:,} bytes)")

if __name__ == "__main__":
    out_file = Path("sfx_heavenly_harp_chime.wav")
    generate_harp_sfx(out_file)
