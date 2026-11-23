#!/usr/bin/env python3
"""Estime le BPM et les premiers temps d'une instru (pour `bpm` et `audio_offset`).

Usage : python3 detect_beat.py instru.mp3      (nécessite : pip install librosa)
"""
import sys

try:
    import librosa
    import numpy as np
except ImportError:
    sys.exit("Installer librosa :  pip install librosa")

if len(sys.argv) < 2:
    sys.exit(__doc__)
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True)
tempo, frames = librosa.beat.beat_track(y=y, sr=sr)
times = librosa.frames_to_time(frames, sr=sr)
tempo = float(np.atleast_1d(tempo)[0])
print(f"BPM estimé : {tempo:.1f}  (si l'instru semble 2x trop lente/rapide : {tempo / 2:.1f} ou {tempo * 2:.1f})")
print("Premiers temps détectés (s) :", " ".join(f"{t:.3f}" for t in times[:16]))
print("-> audio_offset = un de ces instants, idéalement un temps 1 (début de mesure, souvent sur le kick).")
