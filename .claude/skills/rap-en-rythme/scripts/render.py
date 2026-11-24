#!/usr/bin/env python3
"""
Rendu d'une vidéo verticale « RAP EN RYTHME » (format TikTok / Reels / Shorts).

Grille de 4 cases par ligne (= 1 mesure de 4 temps) : 3 cases vides où le
spectateur rappe librement + 1 case « mot » qui doit tomber pile sur le 4e temps.
Une balle orange rebondit de case en case sur chaque temps, la grille défile
d'une ligne à chaque mesure, les mots qui riment partagent la même couleur.

Usage :
    python3 render.py config.json -o sortie.mp4 [--preview 12.5] [--fps 30]

Dépendances : Python 3.9+, numpy, Pillow, ffmpeg dans le PATH.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "..", "assets", "fonts")
sys.path.insert(0, HERE)
import beat as beatgen  # noqa: E402

# --------------------------------------------------------------------------
# Charte graphique (couleurs relevées pixel par pixel sur les vidéos sources)
# --------------------------------------------------------------------------
W, H = 1080, 1920
BG_TOP, BG_MID, BG_BOT = (0x54, 0x29, 0xEC), (0x46, 0x22, 0xC9), (0x3B, 0x1C, 0x9C)
CELL = (0x56, 0x34, 0xC2)
CELL_LINE = (0x66, 0x46, 0xD6)
CELL_DARK = (0x27, 0x14, 0x73)
CELL_DARK_LINE = (0x30, 0x1B, 0x88)
CELL_LIT = (0xEF, 0xEA, 0xFF)       # flash blanc au contact de la balle
ROWNUM = (0x70, 0x50, 0xE6)
PILL_HIT = (0xFE, 0xEA, 0xB4)       # pastille « mot » une fois jouée (crème)
PILL_HIT_EDGE = (0xE2, 0xC2, 0x86)
PILL_HIT_TEXT = (0xE6, 0xCF, 0x98)
# (remplissage, bord 3D, texte) — cycle orange, bleu, jaune, vert par famille de rimes
PALETTE = [
    ((0xED, 0x7A, 0x2E), (0xB3, 0x4C, 0x12), (0x44, 0x06, 0x00)),
    ((0x44, 0x9E, 0xE4), (0x1F, 0x68, 0xA8), (0x02, 0x1D, 0x35)),
    ((0xF9, 0xC0, 0x2A), (0xC0, 0x8A, 0x08), (0x36, 0x23, 0x00)),
    ((0x46, 0xC3, 0x79), (0x1D, 0x84, 0x49), (0x04, 0x30, 0x1A)),
]

# Géométrie (référence 1080x1920, déduite de la mise en page d'origine x1.875)
GRID_X0, CELL_W, GAP, CELL_H, PITCH = 94, 212, 15, 100, 124
RADIUS = 22
ROW0_Y = 620                     # haut de la ligne active (toujours la 1re visible)
VISIBLE_ROWS = 5
TITLE_Y = 310
BALL_R = 33
LAND_Y = ROW0_Y - BALL_R - 8     # centre de la balle au moment de l'impact
HOP_H, HOP_BACK_H = 135, 200     # hauteur des sauts (case suivante / retour à la ligne)
COUNT_Y = ROW0_Y + (VISIBLE_ROWS - 1) * PITCH + CELL_H + 190
WIN_TOP = ROW0_Y - 26
WIN_BOT = ROW0_Y + (VISIBLE_ROWS - 1) * PITCH + CELL_H + 26
CELL_X = [GRID_X0 + i * (CELL_W + GAP) for i in range(4)]
CELL_CX = [x + CELL_W / 2 for x in CELL_X]


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_rgb(c1, c2, t):
    return tuple(int(round(lerp(a, b, t))) for a, b in zip(c1, c2))


def ease_io(u):
    u = min(max(u, 0.0), 1.0)
    return u * u * (3 - 2 * u)


def font(name, size, axes):
    f = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    try:
        f.set_variation_by_axes(axes)
    except Exception:
        pass
    return f


def fredoka(size, weight=600):
    return font("Fredoka.ttf", size, [weight, 100])


def montserrat(size, weight=850):
    return font("Montserrat.ttf", size, [weight])


# --------------------------------------------------------------------------
# Sprites pré-calculés (supersampling x3 pour des arrondis propres)
# --------------------------------------------------------------------------
SS = 3


def rounded(w, h, r, fill, outline=None, width=0, edge=None, edge_h=0):
    im = Image.new("RGBA", (w * SS, (h + edge_h) * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if edge is not None and edge_h:
        d.rounded_rectangle([0, edge_h * SS, w * SS - 1, (h + edge_h) * SS - 1], r * SS, fill=edge)
    d.rounded_rectangle([0, 0, w * SS - 1, h * SS - 1], r * SS, fill=fill,
                        outline=outline, width=width * SS)
    return im.resize((w, h + edge_h), Image.LANCZOS)


def text_center(im, txt, fnt, fill, box_h=None, stroke=0, stroke_fill=None):
    d = ImageDraw.Draw(im)
    bh = box_h if box_h is not None else im.height
    d.text((im.width / 2, bh / 2), txt, font=fnt, fill=fill, anchor="mm",
           stroke_width=stroke, stroke_fill=stroke_fill)


class Sprites:
    def __init__(self, words, colors):
        self.cell = [rounded(CELL_W, CELL_H, RADIUS, lerp_rgb(CELL, CELL_LIT, k / 20) + (255,),
                             lerp_rgb(CELL_LINE, CELL_LIT, k / 20) + (255,), 3) for k in range(21)]
        self.dark = [rounded(CELL_W, CELL_H, RADIUS, lerp_rgb(CELL_DARK, CELL_LIT, k / 20) + (255,),
                             lerp_rgb(CELL_DARK_LINE, CELL_LIT, k / 20) + (255,), 3) for k in range(21)]
        edge_h = 9
        self.pill, self.pill_hit = [], []
        for w, ci in zip(words, colors):
            fill, edge, tcol = PALETTE[ci % len(PALETTE)]
            size = 50
            while size > 22:
                f = fredoka(size, 600)
                if f.getlength(w) <= CELL_W * 0.86:
                    break
                size -= 2
            a = rounded(CELL_W, CELL_H, RADIUS, fill + (255,), edge=edge + (255,), edge_h=edge_h)
            text_center(a, w, f, tcol + (255,), box_h=CELL_H + 2)
            b = rounded(CELL_W, CELL_H, RADIUS, PILL_HIT + (255,), edge=PILL_HIT_EDGE + (255,), edge_h=edge_h)
            text_center(b, w, f, PILL_HIT_TEXT + (255,), box_h=CELL_H + 2)
            self.pill.append(a)
            self.pill_hit.append(b)
        self.ball = self._ball(BALL_R)
        self.trail = []
        for k in range(1, 9):
            r = int(BALL_R * (1 - k * 0.075))
            s = Image.new("RGBA", (r * 2 + 8, r * 2 + 8), (0, 0, 0, 0))
            ImageDraw.Draw(s).ellipse([4, 4, 4 + 2 * r, 4 + 2 * r],
                                      fill=(185, 140, 255, int(95 * (1 - k / 9))))
            self.trail.append(s.filter(ImageFilter.GaussianBlur(3)))
        self.rownum = {}

    @staticmethod
    def _ball(r):
        n = (2 * r + 10) * SS
        yy, xx = np.mgrid[0:n, 0:n].astype(np.float32) / SS - (r + 5)
        dist = np.sqrt(xx ** 2 + yy ** 2)
        hx, hy = -r * 0.35, -r * 0.4
        hd = np.sqrt((xx - hx) ** 2 + (yy - hy) ** 2) / (r * 1.25)
        base = np.array([0xFF, 0xAC, 0x19], np.float32)
        light = np.array([0xFF, 0xDA, 0x7A], np.float32)
        dark = np.array([0xD8, 0x6A, 0x00], np.float32)
        t = np.clip(hd, 0, 1)[..., None]
        col = np.where(t < 0.5, lerp(light, base, t * 2), lerp(base, dark, (t - 0.5) * 2))
        alpha = np.clip((r - dist) * SS, 0, 1) * 255
        img = np.dstack([col, alpha]).astype(np.uint8)
        return Image.fromarray(img, "RGBA").resize((2 * r + 10, 2 * r + 10), Image.LANCZOS)

    def rownum_img(self, n):
        if n not in self.rownum:
            f = fredoka(30, 500)
            im = Image.new("RGBA", (70, 40), (0, 0, 0, 0))
            text_center(im, str(n), f, ROWNUM + (255,))
            self.rownum[n] = im
        return self.rownum[n]


def neon_digit(ch, size=240):
    f = fredoka(size, 700)
    pad = 70
    w = int(f.getlength(ch)) + pad * 2
    h = size + pad * 2
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(glow).text((w / 2, h / 2), ch, font=f, anchor="mm", fill=(255, 20, 30, 255),
                              stroke_width=16, stroke_fill=(255, 20, 30, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(22))
    out = Image.alpha_composite(glow, glow)
    core = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(core).text((w / 2, h / 2), ch, font=f, anchor="mm", fill=(0xFF, 0x16, 0x1B, 255),
                              stroke_width=9, stroke_fill=(0xFB, 0xF6, 0x8F, 255))
    out = Image.alpha_composite(out, core)
    return out


def title_sprite(text, color):
    size = 80
    while size > 40:
        f = montserrat(size, 850)
        if f.getlength(text) + 16 <= W - 100:
            break
        size -= 2
    im = Image.new("RGBA", (W, size + 60), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((W / 2, im.height / 2), text, font=f, anchor="mm", fill=color + (255,),
                            stroke_width=8, stroke_fill=(0, 0, 0, 255))
    return im


def gradient_bg():
    y = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    top, mid, bot = (np.array(c, np.float32) for c in (BG_TOP, BG_MID, BG_BOT))
    col = np.where(y < 0.5, lerp(top, mid, y * 2), lerp(mid, bot, (y - 0.5) * 2))
    arr = np.repeat(col[:, None, :], W, axis=1).reshape(H, W, 3)
    # légère vignette radiale pour la profondeur
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    v = 1 - 0.10 * (((xx - W / 2) / (W / 2)) ** 2)
    arr = arr * v[..., None]
    a = np.full((H, W, 1), 255, np.float32)
    return Image.fromarray(np.concatenate([arr, a], 2).clip(0, 255).astype(np.uint8), "RGBA")


# --------------------------------------------------------------------------
# Chronologie
# --------------------------------------------------------------------------
class Timeline:
    def __init__(self, cfg):
        self.bpm = float(cfg.get("bpm", 89))
        self.spb = 60.0 / self.bpm
        self.bar = 4 * self.spb
        # délai avant le 1er temps de l'intro (s). Par défaut 1 temps : la balle tombe dans la 1re case.
        # Utiliser 'start_before_drop' pour que la vidéo démarre N s avant le drop
        # (= 1re ligne de mots) : lead = N - intro_bars * mesure.
        self.intro = int(cfg.get("intro_bars", 2))
        self.lead = float(cfg.get("lead", self.spb))
        if cfg.get("start_before_drop") is not None:
            self.lead = float(cfg["start_before_drop"]) - self.intro * self.bar
            if self.lead < 0:
                raise SystemExit(f"start_before_drop trop court : l'intro de {self.intro} mesure(s) dure "
                                 f"{self.intro * self.bar:.2f}s ; réduire intro_bars")
        self.n_words = len(cfg["_words"])
        # lignes de 4 cases vides (sans mot) jouées juste après l'intro / le drop,
        # pour laisser au rappeur le temps de se caler avant le 1er mot
        self.blank = int(cfg.get("blank_rows", 0))
        self.rows = self.intro + self.blank + self.n_words
        self.last_beat = self.rows * 4 - 1
        self.outro = float(cfg.get("outro_bars", 1))
        self.duration = self.lead + (self.rows + self.outro) * self.bar

    def beat(self, t):
        return (t - self.lead) / self.spb

    def scroll(self, t):
        tb = (t - self.lead) / self.bar
        if tb < 0:
            return 0.0
        k = math.floor(tb)
        f = tb - k
        s0, s1 = 0.75 + 0.25 * 0.30, 0.75 + 0.25 * 0.95
        return k + ease_io((f - s0) / (s1 - s0))


# --------------------------------------------------------------------------
# Rendu d'une image
# --------------------------------------------------------------------------
class Renderer:
    def __init__(self, cfg):
        self.cfg = cfg
        self.tl = Timeline(cfg)
        self.sp = Sprites(cfg["_words"], cfg["_colors"])
        self.bg = gradient_bg()
        self.title = title_sprite(cfg.get("title", "RAP EN RYTHME !"),
                                  hexrgb(cfg.get("title_color", "#ffffff")))
        self.title_mode = cfg.get("title_mode", "always")
        self.digits = {d: neon_digit(d) for d in "321"}
        self.footer = None
        if cfg.get("footer"):
            im = Image.new("RGBA", (W, 70), (0, 0, 0, 0))
            text_center(im, cfg["footer"], fredoka(40, 500), (255, 255, 255, 150))
            self.footer = im
        self.outro_txt = None
        if cfg.get("outro_text"):
            im = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
            text_center(im, cfg["outro_text"], montserrat(70, 850), (255, 255, 255, 255),
                        stroke=7, stroke_fill=(0, 0, 0, 255))
            self.outro_txt = im

    # niveau d'éclairage d'une case (0 = repos, 1 = flash blanc)
    def cell_level(self, r, c, t):
        tl = self.tl
        h = 4 * r + c
        th = tl.lead + h * tl.spb
        b = tl.beat(t)
        if t < th:
            if math.floor(b) == h - 1:
                u = b - (h - 1)
                return 0.28 * u * u          # anticipation pendant l'approche de la balle
            return 0.0
        dt = t - th
        if dt < tl.spb:
            return 0.45 + 0.55 * math.exp(-dt / 0.09)
        return 0.45 * math.exp(-(dt - tl.spb) / 0.07)

    def ball_pos(self, t):
        tl = self.tl
        b = tl.beat(t)
        if b < 0:                             # chute d'entrée (dernier temps avant l'intro)
            u = b + 1
            if u <= 0:
                return CELL_CX[0], LAND_Y - 420, 0.0
            return CELL_CX[0], LAND_Y - 420 * (1 - u * u), min(1.0, u * 3)
        if b >= tl.last_beat:                 # sortie : la balle s'envole et disparaît
            u = min((b - tl.last_beat) / 2, 1.0)
            return CELL_CX[3] + 120 * u, LAND_Y - 320 * u * (2 - u), 1 - u
        i = math.floor(b)
        u = b - i
        c0, c1 = i % 4, (i + 1) % 4
        hh = HOP_BACK_H if c0 == 3 else HOP_H
        x = lerp(CELL_CX[c0], CELL_CX[c1], u)
        y = LAND_Y - hh * 4 * u * (1 - u)
        return x, y, 1.0

    def frame(self, t):
        tl, sp = self.tl, self.sp
        im = self.bg.copy()
        # ---- titre
        if self.title_mode == "always" or t < tl.lead + tl.intro * tl.bar:
            a = 1.0
            if self.title_mode != "always":
                a = min(1.0, (tl.lead + tl.intro * tl.bar - t) / 0.3)
            tsp = self.title if a >= 1 else _fade(self.title, a)
            im.alpha_composite(tsp, (0, int(TITLE_Y - tsp.height / 2)))
        # ---- grille (couche clipée à la fenêtre visible)
        grid = Image.new("RGBA", (W, WIN_BOT - WIN_TOP), (0, 0, 0, 0))
        pos = tl.scroll(t)
        first = max(0, int(math.floor(pos)) - 1)
        for r in range(first, min(tl.rows, first + VISIBLE_ROWS + 2)):
            y = ROW0_Y + (r - pos) * PITCH
            if y + CELL_H < WIN_TOP or y > WIN_BOT:
                continue
            alpha = 1.0
            if y < ROW0_Y:                   # ligne qui sort par le haut : fondu
                alpha = max(0.0, 1 - (ROW0_Y - y) / (PITCH * 0.55))
            if y > ROW0_Y + (VISIBLE_ROWS - 1) * PITCH:   # ligne qui entre par le bas
                alpha = max(0.0, 1 - (y - ROW0_Y - (VISIBLE_ROWS - 1) * PITCH) / (PITCH * 0.8))
            if alpha <= 0.01:
                continue
            row = Image.new("RGBA", (W, CELL_H + 12), (0, 0, 0, 0))
            intro_row = r < tl.intro
            blank_row = tl.intro <= r < tl.intro + tl.blank
            for c in range(4):
                lvl = self.cell_level(r, c, t)
                if c == 3 and not intro_row and not blank_row:
                    wi = r - tl.intro - tl.blank
                    th = tl.lead + (4 * r + 3) * tl.spb
                    if t < th:
                        s = sp.pill[wi]
                        if lvl > 0:
                            s = Image.blend(s, sp.pill_hit[wi], min(lvl, 0.25))
                    else:
                        k = min(1.0, (t - th) / 0.10)
                        s = Image.blend(sp.pill[wi], sp.pill_hit[wi], k)
                        pop = 1 + 0.07 * math.sin(math.pi * min(1, (t - th) / 0.18))
                        if pop > 1.001:
                            s = s.resize((int(s.width * pop), int(s.height * pop)), Image.BILINEAR)
                    row.alpha_composite(s, (int(CELL_CX[3] - s.width / 2), int((CELL_H + 9) / 2 - s.height / 2) + 1))
                else:
                    lib = sp.dark if intro_row else sp.cell
                    row.alpha_composite(lib[int(round(min(lvl, 1) * 20))], (CELL_X[c], 1))
            if not blank_row:
                n = r - tl.intro - tl.blank + 1 if not intro_row else r - tl.intro
                rn = sp.rownum_img(n)
                row.alpha_composite(rn, (int(GRID_X0 / 2 - 35 - 6), int(CELL_H / 2 - 20)))
                row.alpha_composite(rn, (int(W - GRID_X0 / 2 - 35 + 6), int(CELL_H / 2 - 20)))
            if alpha < 1:
                row = _fade(row, alpha)
            grid.alpha_composite(row, (0, int(round(y - WIN_TOP - 1))))
        im.alpha_composite(grid, (0, WIN_TOP))
        # ---- compte à rebours néon 3-2-1 pendant l'intro
        b = tl.beat(t)
        if tl.intro > 0 and 0 <= b < tl.intro * 4 * 0.75:
            step = tl.intro * 4 / 4
            idx = int(b // step)
            if idx < 3:
                d = self.digits["321"[idx]]
                dt = (b - idx * step) * tl.spb
                sc = 1 + 0.35 * math.exp(-dt / 0.07)
                rem = (step - (b - idx * step)) * tl.spb
                a = min(1.0, rem / 0.12)
                s = d.resize((int(d.width * sc), int(d.height * sc)), Image.BILINEAR) if sc > 1.005 else d
                if a < 1:
                    s = _fade(s, a)
                im.alpha_composite(s, (int(W / 2 - s.width / 2), int(COUNT_Y - s.height / 2)))
        # ---- balle + traînée
        x, y, a = self.ball_pos(t)
        if a > 0.01:
            for k, tr in enumerate(sp.trail, 1):
                px, py, pa = self.ball_pos(t - k * 0.016)
                im.alpha_composite(_fade(tr, a * pa) if a * pa < 1 else tr,
                                   (int(px - tr.width / 2), int(py - tr.height / 2)))
            ball = sp.ball if a >= 1 else _fade(sp.ball, a)
            im.alpha_composite(ball, (int(x - ball.width / 2), int(y - ball.height / 2)))
        # ---- textes de fin / signature
        end_t = tl.lead + tl.rows * tl.bar
        if self.outro_txt is not None and t > end_t:
            a = min(1.0, (t - end_t) / 0.35)
            s = _fade(self.outro_txt, a) if a < 1 else self.outro_txt
            im.alpha_composite(s, (0, int(ROW0_Y + 1.5 * PITCH)))
        if self.footer is not None:
            im.alpha_composite(self.footer, (0, COUNT_Y + 190))
        return im


def _fade(img, a):
    if a >= 1:
        return img
    r, g, b, al = img.split()
    al = al.point(lambda v: int(v * max(0.0, a)))
    return Image.merge("RGBA", (r, g, b, al))


# --------------------------------------------------------------------------
# Config, audio, encodage
# --------------------------------------------------------------------------
def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    words, colors = [], []
    groups = cfg.get("groups")
    if not groups:
        raise SystemExit("config: 'groups' (liste de familles de rimes) est obligatoire")
    for gi, g in enumerate(groups):
        for w in g:
            words.append(w)
            colors.append(gi)
    cfg["_words"], cfg["_colors"] = words, colors
    return cfg


def build_audio(cfg, tl, out_wav, cfg_dir):
    sr = 44100
    if cfg.get("audio"):
        src = cfg["audio"]
        if not os.path.isabs(src):
            src = os.path.join(cfg_dir, src)
        # audio_offset = instant (s) du 1er temps fort de l'intro dans le fichier
        start = float(cfg.get("audio_offset", 0.0)) - tl.lead
        filt = []
        args = ["ffmpeg", "-v", "error", "-y"]
        if start >= 0:
            args += ["-ss", f"{start:.3f}", "-i", src]
        else:
            args += ["-i", src]
            ms = int(-start * 1000)
            filt.append(f"adelay={ms}|{ms}")
        filt.append(f"afade=t=out:st={tl.duration - 0.6:.3f}:d=0.6")
        args += ["-t", f"{tl.duration:.3f}", "-af", ",".join(filt), "-ac", "2", "-ar", str(sr), out_wav]
        subprocess.run(args, check=True)
        if cfg.get("tick"):
            _mix_ticks(out_wav, tl, sr)
        return
    audio = beatgen.make_beat(bpm=tl.bpm, lead=tl.lead, intro_bars=tl.intro, main_bars=tl.blank + tl.n_words,
                              outro_bars=tl.outro, style=cfg.get("beat_style", "boombap"),
                              seed=int(cfg.get("seed", 7)), sr=sr, tick=bool(cfg.get("tick", False)))
    beatgen.write_wav(out_wav, audio, sr)


def _mix_ticks(path, tl, sr):
    with wave.open(path, "rb") as w:
        n = w.getnframes()
        data = np.frombuffer(w.readframes(n), np.int16).reshape(-1, 2).astype(np.float32) / 32768
    ticks = beatgen.ticks(tl.bpm, tl.lead, tl.last_beat + 1, len(data), sr)
    data = np.clip(data + ticks[:, None] * 0.5, -1, 1)
    beatgen.write_wav(path, data, sr)


def render(cfg_path, out, fps=30, preview=None, crf=18):
    cfg = load_config(cfg_path)
    r = Renderer(cfg)
    tl = r.tl
    if preview is not None:
        times = preview if isinstance(preview, list) else [preview]
        for t in times:
            p = os.path.splitext(out)[0] + f"_{t:05.2f}s.png"
            r.frame(t).convert("RGB").save(p)
            print("aperçu :", p)
        return
    tmp = tempfile.mkdtemp(prefix="rapenrythme_")
    wav = os.path.join(tmp, "audio.wav")
    build_audio(cfg, tl, wav, os.path.dirname(os.path.abspath(cfg_path)))
    n = int(math.ceil(tl.duration * fps))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium",
           "-crf", str(crf), "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        proc.stdin.write(r.frame(i / fps).convert("RGB").tobytes())
        if i % (fps * 5) == 0:
            print(f"  {i / fps:5.1f}s / {tl.duration:.1f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        raise SystemExit("ffmpeg a échoué")
    print(f"OK -> {out}  ({tl.duration:.1f}s, {tl.bpm:g} BPM, {tl.n_words} mots)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("-o", "--out", default="rap_en_rythme.mp4")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preview", type=float, nargs="+",
                    help="n'exporte que des images PNG aux instants donnés (secondes)")
    a = ap.parse_args()
    render(a.config, a.out, a.fps, a.preview, a.crf)


if __name__ == "__main__":
    main()
