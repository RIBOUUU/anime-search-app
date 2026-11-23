#!/usr/bin/env python3
"""
Générateur d'instru libre de droits (synthèse procédurale numpy), calé au temps près
sur la grille de la vidéo.

Styles :
  boombap : 80-100 BPM, kick/snare sur 2 et 4, charleston swingué, accords Rhodes mineurs
  trap    : 120-150 BPM, demi-tempo (clap sur le 3), charleston en doubles croches + rolls, 808 long
  drill   : 135-145 BPM, snare décalée (temps 2 « et » + 4), 808 glissés, ambiance sombre

L'intro (compte à rebours) ne contient que les accords + charleston filtrés, puis la
rythmique complète « drop » au moment où la 1re ligne de mots commence.
"""
import math
import wave

import numpy as np

A4 = 440.0


def midi(n):
    return A4 * 2 ** ((n - 69) / 12)


def env(n, sr, attack=0.002, decay=0.3):
    t = np.arange(n) / sr
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / decay)


def kick(sr, punch=1.0):
    n = int(0.45 * sr)
    t = np.arange(n) / sr
    f = 45 + 95 * np.exp(-t / 0.045)
    ph = 2 * np.pi * np.cumsum(f) / sr
    x = np.sin(ph) * np.exp(-t / 0.28)
    x[: int(0.004 * sr)] += np.random.default_rng(1).normal(0, 0.4, int(0.004 * sr))
    return np.tanh(x * 1.6 * punch)


def snare(sr, rng):
    n = int(0.3 * sr)
    t = np.arange(n) / sr
    noise = rng.normal(0, 1, n)
    noise = np.diff(noise, prepend=0)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.06)
    return 0.55 * noise * np.exp(-t / 0.11) + 0.6 * body


def clap(sr, rng):
    n = int(0.3 * sr)
    t = np.arange(n) / sr
    noise = np.diff(rng.normal(0, 1, n), prepend=0)
    e = np.zeros(n)
    for d in (0, 0.011, 0.022):
        e += np.where(t >= d, np.exp(-(t - d) / 0.012), 0)
    e += np.exp(-t / 0.13) * 0.6
    return 0.5 * noise * e


def hat(sr, rng, open_=False):
    n = int((0.25 if open_ else 0.06) * sr)
    t = np.arange(n) / sr
    x = rng.normal(0, 1, n)
    x = np.diff(np.diff(x, prepend=0), prepend=0)
    return 0.22 * x * np.exp(-t / (0.09 if open_ else 0.018))


def keys(freqs, dur, sr, bright=1.0):
    n = int(dur * sr)
    t = np.arange(n) / sr
    x = np.zeros(n)
    for f in freqs:
        for h, a in ((1, 1.0), (2, 0.35 * bright), (3, 0.12 * bright), (4, 0.05 * bright)):
            x += a * np.sin(2 * np.pi * f * h * t + 0.3 * np.sin(2 * np.pi * 5 * t))
    e = np.clip(t / 0.01, 0, 1) * np.exp(-t / (dur * 0.7))
    return x * e / max(1, len(freqs))


def sub(f0, dur, sr, glide_from=None):
    n = int(dur * sr)
    t = np.arange(n) / sr
    f = np.full(n, f0)
    if glide_from:
        f = f0 + (glide_from - f0) * np.exp(-t / 0.06)
    ph = 2 * np.pi * np.cumsum(f) / sr
    x = np.sin(ph) + 0.15 * np.sin(2 * ph)
    e = np.clip(t / 0.005, 0, 1) * np.exp(-t / max(dur * 0.6, 0.05))
    return np.tanh(1.5 * x * e)


def add(buf, x, at, sr, gain=1.0):
    i = int(round(at * sr))
    if i >= len(buf):
        return
    j = min(len(buf), i + len(x))
    buf[i:j] += gain * x[: j - i]


def lowpass(x, alpha):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # 1 pôle ; appelé seulement sur l'intro (courte)
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


PROGRESSIONS = {
    # degrés en demi-tons depuis la tonique (la mineur = 57) : i - VI - iv - v
    "boombap": [[0, 3, 7, 10], [-4, 0, 3, 7], [-7, -4, 0, 3], [-5, -2, 2, 5]],
    "trap": [[0, 3, 7], [-4, 0, 3], [-2, 2, 5], [-5, -1, 2]],
    "drill": [[0, 3, 7], [1, 5, 8], [-4, 0, 3], [-5, -1, 2]],
}


def make_beat(bpm=89, lead=0.67, intro_bars=2, main_bars=16, outro_bars=1, style="boombap",
              seed=7, sr=44100, tick=False):
    rng = np.random.default_rng(seed)
    spb = 60.0 / bpm
    bar = 4 * spb
    total = lead + (intro_bars + main_bars + outro_bars) * bar + 0.5
    L = int(total * sr)
    drums = np.zeros(L)
    music = np.zeros(L)
    bass = np.zeros(L)
    root = 57 if style == "boombap" else 53
    prog = PROGRESSIONS.get(style, PROGRESSIONS["boombap"])
    K, S, C = kick(sr), snare(sr, rng), clap(sr, rng)
    swing = 0.58 if style == "boombap" else 0.5
    n_bars = int(math.ceil(intro_bars + main_bars + outro_bars))

    def step_time(b, s16):
        beat_i, sub_i = divmod(s16, 4)
        pair, odd = divmod(sub_i, 2)
        off = (pair * 2 + (2 * swing if odd else 0)) * spb / 4
        return lead + b * bar + beat_i * spb + off

    for b in range(n_bars):
        chord = prog[b % len(prog)]
        t0 = lead + b * bar
        in_intro = b < intro_bars
        in_outro = b >= intro_bars + main_bars
        # accords
        add(music, keys([midi(root + d) for d in chord], bar * 0.98, sr,
                        bright=0.6 if style != "boombap" else 1.0), t0, sr, 0.55)
        if style != "boombap":  # nappe aiguë en blanche
            add(music, keys([midi(root + 12 + chord[0]), midi(root + 12 + chord[-1])], bar / 2, sr, 0.3),
                t0 + bar / 2, sr, 0.25)
        # charleston
        for s16 in range(16):
            if style == "boombap":
                if s16 % 2 == 0 or (s16 % 4 == 3 and rng.random() < 0.3):
                    add(drums, hat(sr, rng, open_=(s16 == 14 and b % 2)), step_time(b, s16), sr,
                        0.9 if s16 % 4 == 0 else 0.6)
            else:
                add(drums, hat(sr, rng), step_time(b, s16), sr, 0.75 if s16 % 2 == 0 else 0.45)
                if s16 in (6, 14) and rng.random() < 0.5:  # roll en triples croches
                    for r in range(1, 3):
                        add(drums, hat(sr, rng), step_time(b, s16) + r * spb / 6, sr, 0.35)
        if in_intro:
            continue
        if in_outro:
            add(drums, K, t0, sr, 1.0)
            add(bass, sub(midi(root - 24 + chord[0]), bar, sr), t0, sr, 0.8)
            continue
        if style == "boombap":
            for s16 in (0, 7, 10) if b % 2 == 0 else (0, 3, 10):
                add(drums, K, step_time(b, s16), sr, 1.0)
            for s16 in (4, 12):
                add(drums, S, step_time(b, s16), sr, 0.9)
            add(bass, sub(midi(root - 24 + chord[0]), spb * 1.6, sr), t0, sr, 0.7)
            add(bass, sub(midi(root - 24 + chord[0]), spb * 1.2, sr), step_time(b, 10), sr, 0.6)
        elif style == "trap":
            for s16 in (0, 10) if b % 2 == 0 else (0, 3, 11):
                add(drums, K, step_time(b, s16), sr, 0.9)
                add(bass, sub(midi(root - 24 + chord[0]), spb * 1.8, sr,
                              glide_from=midi(root - 12 + chord[0]) if s16 == 11 else None),
                    step_time(b, s16), sr, 0.85)
            add(drums, C, step_time(b, 8), sr, 1.0)
        else:  # drill
            for s16 in (0, 11) if b % 2 == 0 else (0, 6, 14):
                add(drums, K, step_time(b, s16), sr, 0.85)
            add(drums, S, step_time(b, 6), sr, 0.8)
            add(drums, S, step_time(b, 12), sr, 0.9)
            add(bass, sub(midi(root - 24 + chord[0]), spb * 2.5, sr,
                          glide_from=midi(root - 24 + chord[0] + 5)), t0, sr, 0.9)
            add(bass, sub(midi(root - 24 + chord[-1]), spb * 1.2, sr), step_time(b, 10), sr, 0.7)

    # intro filtrée (effet « radio ») puis drop
    i_end = int((lead + intro_bars * bar) * sr)
    if i_end > 0:
        music[:i_end] = lowpass(music[:i_end], 0.06) * 1.8
        drums[:i_end] = drums[:i_end] * 0.5
    mix = 0.9 * drums + 0.55 * music + 0.7 * bass
    if tick:
        mix += 0.35 * ticks(bpm, lead, (intro_bars + main_bars) * 4, L, sr)
    # fondu de fin
    fo = int(0.6 * sr)
    mix[-fo:] *= np.linspace(1, 0, fo)
    mix = np.tanh(mix * 1.2)
    mix /= max(1e-6, np.abs(mix).max()) / 0.89
    st = np.stack([mix, mix], 1)
    # léger élargissement stéréo sur la musique
    d = int(0.012 * sr)
    st[d:, 1] = 0.85 * st[d:, 1] + 0.15 * (0.55 * music[:-d] / max(1e-6, np.abs(music).max()))
    return st.astype(np.float32)


def ticks(bpm, lead, n_beats, L, sr):
    """Petit 'toc' de bois à chaque rebond de la balle (option tick)."""
    out = np.zeros(L)
    n = int(0.05 * sr)
    t = np.arange(n) / sr
    tk = np.sin(2 * np.pi * 1350 * t) * np.exp(-t / 0.012)
    for i in range(n_beats):
        add(out, tk, lead + i * 60.0 / bpm, sr, 1.0 if i % 4 == 3 else 0.6)
    return out


def write_wav(path, data, sr=44100):
    data = np.asarray(data, np.float32)
    if data.ndim == 1:
        data = np.stack([data, data], 1)
    pcm = (np.clip(data, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--bpm", type=float, default=89)
    ap.add_argument("--style", default="boombap", choices=["boombap", "trap", "drill"])
    ap.add_argument("--bars", type=int, default=16)
    ap.add_argument("-o", "--out", default="beat.wav")
    a = ap.parse_args()
    write_wav(a.out, make_beat(bpm=a.bpm, main_bars=a.bars, style=a.style))
    print("OK", a.out)
