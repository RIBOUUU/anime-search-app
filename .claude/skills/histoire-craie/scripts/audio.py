#!/usr/bin/env python3
"""
Bande-son des histoires à la craie : piano doux généré (libre de droits), ambiance
pluie, petits bruitages. Ou une musique fournie (config "audio").

Config :
  "music": {"mood": "sad" | "tender" | "hope", "bpm": 66, "volume": 0.6,
            "turn": 21.0}      # instant où la musique passe en majeur (le retournement)
  "audio": "musique.mp3", "audio_start": 12.0, "audio_volume": 1.0
  "sfx":   [{"t": 3.2, "type": "thud" | "wood" | "whoosh" | "pop" | "drop" | "heart" | "tick"}]
  "rain":  {"t0": 0, "t1": 30}   -> ajoute le bruit de pluie
"""
import math
import os
import subprocess
import wave

import numpy as np

SR = 44100
PROGS = {
    # (accords en demi-tons depuis la tonique MIDI, tonique)
    "sad": ([[0, 3, 7], [-4, 0, 3], [-9, -5, -2], [-5, -2, 2]], 57),      # Am F C G
    "tender": ([[0, 4, 7], [-5, -1, 2], [-3, 0, 4], [-7, -3, 0]], 60),    # C G Am F
    "hope": ([[-7, -3, 0], [0, 4, 7], [-5, -1, 2], [-3, 0, 4]], 60),      # F C G Am
}


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def piano_note(f, dur, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for h, a in ((1, 1.0), (2, 0.42), (3, 0.18), (4, 0.09), (5, 0.04)):
        x += a * np.sin(2 * np.pi * f * h * t * (1 + 0.0004 * h)) * np.exp(-t * (1.1 + 0.9 * h))
    att = np.clip(t / 0.004, 0, 1)
    return x * att * vel * 0.35


def add(buf, x, at, g=1.0):
    i = int(at * SR)
    if i >= len(buf) or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    j = min(len(buf), i + len(x))
    buf[i:j] += g * x[: j - i]


def reverb(x, mix=0.32):
    y = np.zeros_like(x)
    for d_ms, g in ((29.7, 0.78), (37.1, 0.76), (41.1, 0.74), (43.7, 0.72)):
        D = int(SR * d_ms / 1000)
        c = x.copy()
        for k in range(D, len(c), D):
            c[k:k + D] += g * c[k - D:k][: len(c[k:k + D])]
        y += c
    y /= 4
    return (1 - mix) * x + mix * y


def music(dur, mood="sad", bpm=66, turn=None, seed=4):
    rng = np.random.default_rng(seed)
    buf = np.zeros(int((dur + 3) * SR))
    spb = 60 / bpm
    bar = 4 * spb
    t = 0.6
    b = 0
    while t < dur:
        m = mood if (turn is None or t < turn) else ("hope" if mood == "sad" else mood)
        prog, root = PROGS.get(m, PROGS["sad"])
        ch = prog[b % len(prog)]
        bass = midi(root - 12 + ch[0])
        add(buf, piano_note(bass, bar * 1.4, 0.9), t)
        add(buf, piano_note(bass * 2, bar * 1.2, 0.35), t)
        notes = [root + c for c in ch] + [root + 12 + ch[0]]
        patt = [0, 1, 2, 3, 2, 1, 2, 3]
        for i, p in enumerate(patt):
            add(buf, piano_note(midi(notes[p]), spb * 2.2, 0.45 + 0.1 * rng.random()), t + i * spb / 2)
        if b % 2 == 1:   # petite mélodie aiguë, une note par demi-mesure
            for i in range(2):
                n = root + 12 + ch[rng.integers(0, len(ch))]
                add(buf, piano_note(midi(n), spb * 3, 0.5), t + i * bar / 2 + spb * 0.02)
        t += bar
        b += 1
    return reverb(buf[: int(dur * SR)])


def rain_noise(n, rng):
    x = rng.normal(0, 1, n)
    k = np.ones(6) / 6
    x = np.convolve(x, k, "same") - 0.6 * np.convolve(x, np.ones(60) / 60, "same")
    drops = np.zeros(n)
    for i in rng.integers(0, n, n // 300):
        L = min(n - i, 300)
        drops[i:i + L] += rng.normal(0, 1, L) * np.exp(-np.arange(L) / 40) * rng.uniform(0.3, 1.2)
    return 0.6 * x + 0.25 * drops


def sfx(kind, rng):
    if kind in ("thud", "wood"):
        n = int(0.25 * SR)
        t = np.arange(n) / SR
        f = 170 if kind == "wood" else 90
        return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.05) + 0.4 * rng.normal(0, 1, n) * np.exp(-t / 0.015)) * 0.9
    if kind == "whoosh":
        n = int(0.7 * SR)
        t = np.arange(n) / SR
        x = np.convolve(rng.normal(0, 1, n), np.ones(12) / 12, "same")
        return x * np.sin(np.pi * t / t[-1]) ** 2 * 0.8
    if kind == "drop":
        n = int(0.9 * SR)
        t = np.arange(n) / SR
        f = 500 * np.exp(-t * 2.2) + 60
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.5) * 0.4
    if kind == "pop":
        n = int(0.12 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * 900 * t * (1 - t * 3)) * np.exp(-t / 0.03) * 0.6
    if kind == "heart":
        out = np.zeros(int(0.8 * SR))
        for off in (0, 0.22):
            n = int(0.18 * SR)
            t = np.arange(n) / SR
            add(out, np.sin(2 * np.pi * 55 * t) * np.exp(-t / 0.06), off)
        return out
    if kind == "tick":
        n = int(0.04 * SR)
        t = np.arange(n) / SR
        return np.sin(2 * np.pi * 2200 * t) * np.exp(-t / 0.006) * 0.5
    return np.zeros(10)


def write_wav(path, x):
    x = np.asarray(x, np.float32)
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    pcm = (np.clip(st, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


def load_audio(path, start, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{start:.3f}", "-i", path, "-t", f"{dur:.3f}",
                          "-f", "s16le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    out = np.zeros(int(dur * SR), np.float32)
    out[: min(len(x), len(out))] = x[: len(out)]
    return out


def build(cfg, dur, out_wav, cfg_dir="."):
    rng = np.random.default_rng(cfg.get("seed", 5))
    n = int(dur * SR)
    mix = np.zeros(n)
    if cfg.get("audio"):
        p = cfg["audio"] if os.path.isabs(cfg["audio"]) else os.path.join(cfg_dir, cfg["audio"])
        mix += load_audio(p, float(cfg.get("audio_start", 0)), dur) * float(cfg.get("audio_volume", 1.0))
    else:
        m = cfg.get("music", {})
        if m is not None:
            mu = music(dur, m.get("mood", "sad"), m.get("bpm", 66), m.get("turn"))
            mu = mu / max(1e-6, np.abs(mu).max())
            mix[: len(mu)] += mu[:n] * m.get("volume", 0.6)
    r = cfg.get("rain")
    if r and r.get("sound", True):
        rn = rain_noise(n, rng)
        rn /= max(1e-6, np.abs(rn).max())
        tt = np.arange(n) / SR
        env = np.clip((tt - r.get("t0", 0)) / 1.0, 0, 1) * np.clip((r.get("t1", dur) - tt) / 1.0, 0, 1)
        mix += rn * env * r.get("volume", 0.16)
    for e in cfg.get("sfx", []):
        add(mix, sfx(e["type"], rng) * e.get("volume", 0.5), e["t"])
    # fondus selon la piste "fade" de la vidéo (le son suit l'image)
    fk = sorted(cfg.get("fade", []), key=lambda k: k["t"])
    if fk:
        tt = np.arange(n) / SR
        b = np.interp(tt, [k["t"] for k in fk], [k["b"] for k in fk])
        mix *= 0.25 + 0.75 * b
    fo = int(0.8 * SR)
    mix[-fo:] *= np.linspace(1, 0, fo)
    peak = np.abs(mix).max()
    if peak > 0:
        mix = np.tanh(mix / peak * 1.1) * 0.9
    write_wav(out_wav, mix)
