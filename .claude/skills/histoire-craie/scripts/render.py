#!/usr/bin/env python3
"""
Moteur « HISTOIRE À LA CRAIE » : courts-métrages verticaux (TikTok / Reels / Shorts)
façon craie blanche sur tableau noir. Personnages en bâtons articulés, décors
hachurés, caméra (zoom / travelling / cut), texte qui s'écrit à la main, lueurs
(téléphone, lampadaire), pluie, poussière de craie, fondus.

Tout est décrit dans un fichier JSON (voir SKILL.md et examples/).

Usage :
    python3 render.py histoire.json -o video.mp4
    python3 render.py histoire.json -o apercu.png --preview 2 8.5 20

Dépendances : Python 3.9+, numpy, Pillow, ffmpeg.
"""
import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import zlib

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_PATH = os.path.join(HERE, "..", "assets", "fonts", "PatrickHandSC-Regular.ttf")
sys.path.insert(0, HERE)
import audio as audiogen  # noqa: E402

W, H = 1080, 1920
CHALK_RGB = np.array([238, 241, 245], np.float32) / 255.0
GLOW_COLORS = {"warm": (1.0, 0.78, 0.45), "cool": (0.62, 0.78, 1.0), "white": (1, 1, 1)}
_RT = np.random.default_rng(12345).random(1 << 16).astype(np.float32)


def rnd(seed, i):
    return float(_RT[(seed * 7919 + i * 104729 + 17) & 0xFFFF])


def sid(s):
    return zlib.crc32(str(s).encode()) & 0xFFFFF


def ease(u, kind="inout"):
    u = min(max(u, 0.0), 1.0)
    if kind == "linear":
        return u
    if kind == "in":
        return u * u
    if kind == "out":
        return 1 - (1 - u) ** 2
    return u * u * (3 - 2 * u)


def vec(angle, length, d=1):
    """angle en degrés : 0 = vers le bas, 90 = devant (dans le sens du regard), 180 = vers le haut."""
    a = math.radians(angle)
    return math.sin(a) * length * d, math.cos(a) * length


def rot(p, deg):
    a = math.radians(deg)
    return p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a)


# --------------------------------------------------------------------------
# Pistes d'images clés
# --------------------------------------------------------------------------
class Track:
    def __init__(self, keys):
        self.keys = sorted(keys or [{"t": 0}], key=lambda k: k["t"])

    def num(self, name, t, default=0.0):
        prev = nxt = None
        for k in self.keys:
            if name in k:
                if k["t"] <= t:
                    prev = k
                elif nxt is None:
                    nxt = k
        if prev is None and nxt is None:
            return default
        if prev is None:
            return nxt[name]
        if nxt is None or nxt.get("cut"):
            return prev[name]
        u = (t - prev["t"]) / max(1e-6, nxt["t"] - prev["t"])
        return prev[name] + (nxt[name] - prev[name]) * ease(u, nxt.get("ease", "inout"))

    def disc(self, name, t, default=None):
        v = default
        for k in self.keys:
            if k["t"] <= t and name in k:
                v = k[name]
        return v

    def blend(self, name, t, trans_default=0.35):
        """(valeur précédente, valeur suivante, u) pour les paramètres non numériques (poses)."""
        prev = nxt = None
        for k in self.keys:
            if name in k:
                if k["t"] <= t:
                    prev = k
                elif nxt is None:
                    nxt = k
        if prev is None:
            return (nxt[name] if nxt else None), None, 0.0
        if nxt is None or nxt.get("cut"):
            return prev[name], None, 0.0
        tr = nxt.get("trans", trans_default)
        t0 = max(prev["t"], nxt["t"] - tr)
        u = 0.0 if t < t0 else (t - t0) / max(1e-6, nxt["t"] - t0)
        return prev[name], nxt[name], ease(u)


# --------------------------------------------------------------------------
# Toile « craie » avec caméra
# --------------------------------------------------------------------------
class Canvas:
    def __init__(self, cam):
        self.cx, self.cy, self.z = cam
        self.img = Image.new("L", (W, H), 0)
        self.d = ImageDraw.Draw(self.img)
        self.glow = {k: Image.new("L", (W // 4, H // 4), 0) for k in GLOW_COLORS}
        self.gd = {k: ImageDraw.Draw(v) for k, v in self.glow.items()}

    def S(self, p):
        return ((p[0] - self.cx) * self.z + W / 2, (p[1] - self.cy) * self.z + H / 2)

    def poly(self, pts, w=6.0, seed=1, val=255, closed=False, jit=1.0):
        if len(pts) < 2:
            return
        sp = [self.S(p) for p in pts]
        if closed:
            sp.append(sp[0])
        out = []
        k = 0
        for a, b in zip(sp, sp[1:]):
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy)
            n = max(1, int(L / 16))
            nx, ny = (-dy / L, dx / L) if L > 1e-6 else (0, 0)
            for i in range(n):
                u = i / n
                j = (rnd(seed, k) - 0.5) * 2.6 * jit * min(1.6, self.z)
                out.append((a[0] + dx * u + nx * j, a[1] + dy * u + ny * j))
                k += 1
        last = sp[-1]
        out.append((last[0] + (rnd(seed, k) - 0.5) * 2 * jit, last[1]))
        ww = max(1, int(round(w * self.z)))
        self.d.line(out, fill=int(val), width=ww, joint="curve")
        if ww >= 3:
            off = [(x + 0.9, y + 0.7) for x, y in out]
            self.d.line(off, fill=int(val * 0.55), width=max(1, ww // 2))

    def line(self, a, b, w=6.0, seed=1, val=255, jit=1.0):
        self.poly([a, b], w, seed, val, jit=jit)

    def circle(self, c, r, w=6.0, seed=1, val=255, a0=0, a1=360, n=None):
        n = n or max(10, int(r * self.z / 3))
        pts = []
        for i in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * i / n)
            rr = r * (1 + (rnd(seed, i + 900) - 0.5) * 0.06)
            pts.append((c[0] + math.cos(a) * rr, c[1] + math.sin(a) * rr))
        self.poly(pts, w, seed, val)

    def dot(self, c, r, val=255):
        x, y = self.S(c)
        rr = max(1, r * self.z)
        self.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=int(val))

    def fill_poly(self, pts, val=0):
        """bouche le fond (pour qu'un objet masque ce qui est derrière)."""
        self.d.polygon([self.S(p) for p in pts], fill=int(val))

    def add_glow(self, c, r, kind="warm", val=255):
        x, y = self.S(c)
        rr = r * self.z / 4
        self.gd[kind].ellipse([x / 4 - rr, y / 4 - rr, x / 4 + rr, y / 4 + rr], fill=int(val))

    def add_glow_poly(self, pts, kind="warm", val=120):
        self.gd[kind].polygon([(x / 4, y / 4) for x, y in (self.S(p) for p in pts)], fill=int(val))


# --------------------------------------------------------------------------
# Personnages
# --------------------------------------------------------------------------
P0 = dict(lean=0, tilt=0, sl=6, el=4, sr=-6, er=4, hl=4, kl=0, hr=-4, kr=0, dy=0)
POSES = {
    "stand": {}, "walk": {},
    "sad": dict(lean=10, tilt=22, sl=3, sr=-3),
    "old": dict(lean=16, tilt=10, sl=20, el=10, sr=12, er=10, kl=-8, kr=-6),
    "look_up": dict(tilt=-24),
    "look_down": dict(tilt=22),
    "hold": dict(sl=35, el=55, sr=40, er=50),
    "carry": dict(lean=-4, sl=30, el=70, sr=34, er=66),
    "reach": dict(lean=6, sl=80, el=6, sr=86, er=4),
    "point": dict(sr=90, er=0),
    "wave": dict(sr=160, er=10, anim="wave"),
    "cheer": dict(sl=165, el=5, sr=170, er=5, anim="bounce"),
    "phone": dict(tilt=18, sl=8, sr=40, er=105),
    "umbrella": dict(sr=60, er=100),
    "umbrella_look": dict(tilt=18, sr=60, er=100),
    "umbrella_look_up": dict(tilt=-20, sr=60, er=100),
    "hug": dict(sl=80, el=70, sr=85, er=65),
    "think": dict(tilt=-8, sr=30, er=140),
    "facepalm": dict(tilt=20, sr=45, er=135),
    "cry": dict(lean=12, tilt=25, sl=40, el=120, sr=45, er=115),
    "shiver": dict(lean=8, tilt=15, sl=45, el=95, sr=50, er=90, anim="shiver"),
    "kneel": dict(lean=15, hl=88, kl=-88, hr=-12, kr=-78, sl=60, el=15, sr=50, er=20),
    "crouch": dict(lean=42, tilt=10, hl=105, kl=-150, hr=80, kr=-120, sl=70, el=10, sr=60, er=15),
    "sit_bench": dict(lean=4, hl=90, kl=-90, hr=86, kr=-86, sl=30, el=45, sr=34, er=40),
    "sit_sad": dict(lean=20, tilt=26, hl=90, kl=-90, hr=86, kr=-86, sl=40, el=50, sr=44, er=46),
    "sit_look_up": dict(lean=4, tilt=-14, hl=90, kl=-90, hr=86, kr=-86, sl=30, el=45, sr=34, er=40),
    "sit_umbrella": dict(lean=4, hl=90, kl=-90, hr=86, kr=-86, sl=30, el=45, sr=60, er=100),
    "sit_phone": dict(lean=8, tilt=20, hl=90, kl=-90, hr=86, kr=-86, sl=30, el=50, sr=40, er=105),
    "sit_ground": dict(lean=-6, hl=90, kl=0, hr=86, kr=-4, sl=-30, el=0, sr=-34, er=0),
    "hug_knees": dict(lean=28, tilt=18, hl=135, kl=-150, hr=130, kr=-146, sl=100, el=-35, sr=104, er=-38),
    "lie": dict(lean=-90, tilt=0, hl=88, kl=0, hr=92, kr=0, sl=180, el=0, sr=175, er=0, dy=0),
    "jump": dict(sl=150, el=10, sr=155, er=10, hl=40, kl=-70, hr=20, kr=-60, dy=-60),
}
ARMS_FREE = {"stand", "walk", "sad", "old", "look_up", "look_down"}
BODY = dict(T=105, NECK=8, R=34, UA=55, FA=50, TH=62, SH=62)


def pose_params(name):
    p = dict(P0)
    p.update(POSES.get(name, {}))
    return p


class Actor:
    def __init__(self, name, spec):
        self.name = name
        self.tr = Track(spec.get("keys", []))
        self.hair = spec.get("hair", "none")
        self.extras = set(spec.get("extras", []))   # glasses, mustache, beard, skirt, scarf, bow, tie
        self.seed = sid(name)
        self.joints = {}

    def state(self, t):
        tr = self.tr
        p0, p1, u = tr.blend("pose", t)
        pa, pb = pose_params(p0 or "stand"), pose_params(p1 or p0 or "stand")
        P = {k: pa[k] + (pb[k] - pa[k]) * u for k in P0}
        anim = (pb if u > 0.5 else pa).get("anim")
        x = tr.num("x", t, 540)
        v = (tr.num("x", t + 0.04, 540) - tr.num("x", t - 0.04, 540)) / 0.08
        s = tr.num("scale", t, 1.0)
        amp = min(1.0, abs(v) / (110 * s))
        name_now = p0 if u < 0.5 else p1
        if amp > 0.02:
            ph = x / (58 * s) * math.pi * 0.5
            sw = math.sin(ph)
            P["hl"] += 24 * amp * sw
            P["hr"] -= 24 * amp * sw
            P["kl"] -= 34 * amp * max(0.0, -math.sin(ph + 0.9))
            P["kr"] -= 34 * amp * max(0.0, math.sin(ph + 0.9))
            if (name_now or "stand") in ARMS_FREE:
                P["sl"] -= 22 * amp * sw
                P["sr"] += 22 * amp * sw
                P["el"] += 12 * amp
                P["er"] += 12 * amp
            P["dy"] -= 5 * amp * abs(math.cos(ph))
        if anim == "wave":
            P["er"] += 22 * math.sin(t * 9)
        elif anim == "bounce":
            P["dy"] -= 18 * abs(math.sin(t * 6))
        elif anim == "shiver":
            P["lean"] += 1.5 * math.sin(t * 55)
        P["dy"] += tr.num("lift", t, 0.0)
        return dict(P=P, x=x, ground=tr.num("ground", t, 1300), s=s, d=tr.disc("dir", t, 1),
                    face=tr.disc("face", t, "neutral"), vis=tr.disc("visible", t, True))

    def solve(self, st):
        P, s, d = st["P"], st["s"], st["d"]
        B = {k: v * s for k, v in BODY.items()}
        R = B["R"] * (1.22 if s < 0.8 else 1.0)       # enfants : tête plus grosse
        hip = (0.0, 0.0)
        neck = tuple(np.add(hip, vec(180 - P["lean"], B["T"], d)))
        sho = tuple(np.add(hip, vec(180 - P["lean"], B["T"] * 0.9, d)))
        head = tuple(np.add(neck, vec(180 - P["lean"] - P["tilt"] * 0.5, B["NECK"] + R, d)))
        el_l = tuple(np.add(sho, vec(P["sl"], B["UA"], d)))
        ha_l = tuple(np.add(el_l, vec(P["sl"] + P["el"], B["FA"], d)))
        el_r = tuple(np.add(sho, vec(P["sr"], B["UA"], d)))
        ha_r = tuple(np.add(el_r, vec(P["sr"] + P["er"], B["FA"], d)))
        kn_l = tuple(np.add(hip, vec(P["hl"], B["TH"], d)))
        ft_l = tuple(np.add(kn_l, vec(P["hl"] + P["kl"], B["SH"], d)))
        kn_r = tuple(np.add(hip, vec(P["hr"], B["TH"], d)))
        ft_r = tuple(np.add(kn_r, vec(P["hr"] + P["kr"], B["SH"], d)))
        pts = dict(hip=hip, neck=neck, sho=sho, head=head, elbow_l=el_l, hand_l=ha_l, elbow_r=el_r,
                   hand_r=ha_r, knee_l=kn_l, foot_l=ft_l, knee_r=kn_r, foot_r=ft_r)
        low = max(ft_l[1], ft_r[1], kn_l[1], kn_r[1], 4 * s)
        ox, oy = st["x"], st["ground"] - low + P["dy"]
        J = {k: (v[0] + ox, v[1] + oy) for k, v in pts.items()}
        J["hands"] = ((J["hand_l"][0] + J["hand_r"][0]) / 2, (J["hand_l"][1] + J["hand_r"][1]) / 2)
        J["R"] = R
        self.joints = J
        return J

    def draw(self, cv, t):
        st = self.state(t)
        J = self.solve(st)
        if not st["vis"]:
            return
        s, d, sd = st["s"], st["d"], self.seed
        w = 6.5 * max(s, 0.75)
        P = st["P"]
        cv.poly([J["hip"], J["neck"]], w, sd + 1)
        if "skirt" in self.extras:
            a = J["hip"]
            top = (a[0] + (J["neck"][0] - a[0]) * 0.45, a[1] + (J["neck"][1] - a[1]) * 0.45)
            cv.poly([top, (a[0] - 34 * s, a[1] + 26 * s), (a[0] + 34 * s, a[1] + 26 * s), top], w * 0.8, sd + 2)
        for side, k in (("l", 3), ("r", 5)):
            cv.poly([J["sho"], J["elbow_" + side], J["hand_" + side]], w, sd + k)
            cv.poly([J["hip"], J["knee_" + side], J["foot_" + side]], w, sd + k + 1)
            f = J["foot_" + side]
            cv.line(f, (f[0] + 13 * s * d, f[1]), w, sd + k + 7)
        if "scarf" in self.extras:
            n = J["neck"]
            cv.poly([(n[0] - 16 * s, n[1] + 2), (n[0] + 16 * s, n[1] + 2)], w * 1.2, sd + 30)
            cv.poly([(n[0] - 8 * s * d, n[1] + 2), (n[0] - 22 * s * d, n[1] + 34 * s)], w, sd + 31)
        if "tie" in self.extras:
            n = J["neck"]
            cv.poly([n, (n[0] + 6 * s * d, n[1] + 36 * s)], w * 0.8, sd + 32)
        self.draw_head(cv, J, st, P, t)

    def draw_head(self, cv, J, st, P, t):
        c, R, s, d, sd = J["head"], J["R"], st["s"], st["d"], self.seed
        w = 6.0 * max(s, 0.75)
        cv.fill_poly([(c[0] + math.cos(a) * R, c[1] + math.sin(a) * R) for a in np.linspace(0, 6.28, 24)], 0)
        cv.circle(c, R, w, sd + 40)
        look = P["tilt"] / 90.0
        ex = c[0] + 0.30 * R * d
        ey = c[1] - 0.10 * R + look * 0.35 * R
        face = st["face"]
        blink = (t + (sd % 7) * 0.53) % 4.1 < 0.12
        er = 0.16 * R
        for k, dx in enumerate((-0.30 * R, 0.30 * R)):
            e = (ex + dx, ey)
            if face in ("closed", "laugh") or blink:
                cv.circle((e[0], e[1] + er * 0.4), er, w * 0.7, sd + 50 + k, a0=200, a1=340, n=8)
            elif face == "angry":
                cv.dot(e, er * 0.6)
                cv.line((e[0] - er * 1.3, e[1] - er * (2.2 if k == 0 else 1.2)),
                        (e[0] + er * 1.3, e[1] - er * (1.2 if k == 0 else 2.2)), w * 0.6, sd + 60 + k)
            else:
                rr = er * (1.35 if face == "surprised" else 1.0)
                cv.circle(e, rr, w * 0.6, sd + 50 + k, n=10)
                cv.dot((e[0] + 0.35 * rr * d, e[1] + look * 0.4 * rr), rr * 0.45)
                if face in ("sad", "worried", "cry"):
                    cv.line((e[0] - rr * 1.2, e[1] - rr * (1.6 if (k == 0) == (d > 0) else 2.4)),
                            (e[0] + rr * 1.2, e[1] - rr * (2.4 if (k == 0) == (d > 0) else 1.6)),
                            w * 0.55, sd + 62 + k)
        mx, my = ex, c[1] + 0.42 * R + look * 0.2 * R
        mw = 0.36 * R
        if face in ("happy", "laugh", "closed", "smile", "love"):
            big = face in ("happy", "laugh")
            cv.circle((mx, my - mw * 0.55), mw, w * 0.7, sd + 70, a0=30, a1=150, n=10)
            if big:
                cv.line((mx - mw * 0.85, my - mw * 0.05), (mx + mw * 0.85, my - mw * 0.05), w * 0.5, sd + 71)
        elif face in ("sad", "cry"):
            cv.circle((mx, my + mw * 0.75), mw, w * 0.7, sd + 72, a0=210, a1=330, n=10)
        elif face == "surprised":
            cv.circle((mx, my), mw * 0.42, w * 0.6, sd + 73, n=10)
        elif face == "worried":
            cv.poly([(mx - mw, my), (mx - mw * 0.4, my - 3 * s), (mx + mw * 0.2, my + 2 * s), (mx + mw, my - 2 * s)],
                    w * 0.6, sd + 74)
        else:
            cv.line((mx - mw * 0.7, my), (mx + mw * 0.7, my), w * 0.6, sd + 75)
        if face == "cry":
            ph = (t * 1.3) % 1.0
            cv.dot((ex - 0.30 * R + 0.1 * R * d, ey + er * 2 + ph * R * 0.9), er * 0.45)
        if face == "love":
            for k, dx in enumerate((-0.30 * R, 0.30 * R)):
                heart(cv, (ex + dx, ey), er * 1.3, w * 0.5, sd + 80 + k)
        # accessoires du visage
        if "glasses" in self.extras:
            for k, dx in enumerate((-0.30 * R, 0.30 * R)):
                cv.circle((ex + dx, ey), er * 1.9, w * 0.5, sd + 90 + k, n=12)
            cv.line((ex - 0.30 * R + er * 1.9, ey), (ex + 0.30 * R - er * 1.9, ey), w * 0.5, sd + 92)
        if "mustache" in self.extras:
            for k, sg in enumerate((-1, 1)):
                cv.circle((mx + sg * mw * 0.55, my - mw * 0.75), mw * 0.6, w * 0.7, sd + 93 + k, a0=200, a1=340, n=8)
        if "beard" in self.extras:
            cv.circle(c, R * 1.02, w * 0.9, sd + 95, a0=20, a1=160, n=16)
        self.draw_hair(cv, c, R, s, d, w, sd, P)

    def draw_hair(self, cv, c, R, s, d, w, sd, P):
        h = self.hair
        top = (c[0], c[1] - R)
        if h == "cowlick":
            pts = []
            for i in range(14):
                a = i / 13 * 4.6
                rr = R * 0.30 * (1 - i / 16)
                pts.append((top[0] - 4 * s * d + math.cos(a + 1.6) * rr * d, top[1] - R * 0.28 + math.sin(a + 1.6) * rr))
            cv.poly([top] + pts, w * 0.7, sd + 100)
        elif h == "long":
            for k, sg in enumerate((-1, 1)):
                a = (c[0] + sg * R * 0.9, c[1] - R * 0.4)
                cv.poly([(c[0] + sg * R * 0.2, top[1] + 2), a, (c[0] + sg * R * 1.05, c[1] + R * 1.5)], w * 0.8, sd + 101 + k)
        elif h == "ponytail":
            b = (c[0] - R * 1.0 * d, c[1] - R * 0.5)
            cv.poly([b, (b[0] - R * 0.5 * d, b[1] + R * 0.6), (b[0] - R * 0.35 * d, b[1] + R * 1.3)], w * 0.8, sd + 103)
            cv.circle(b, R * 0.16, w * 0.6, sd + 104, n=8)
        elif h == "beanie":
            cv.circle((c[0], c[1] - R * 0.15), R * 1.02, w * 0.9, sd + 105, a0=195, a1=345, n=14)
            cv.line((c[0] - R, c[1] - R * 0.38), (c[0] + R, c[1] - R * 0.38), w * 0.9, sd + 106)
            cv.circle((c[0], c[1] - R * 1.32), R * 0.2, w * 0.6, sd + 107, n=8)
        elif h == "cap":
            cv.circle((c[0], c[1] - R * 0.2), R * 1.0, w * 0.9, sd + 108, a0=190, a1=350, n=14)
            cv.line((c[0] + R * 0.3 * d, c[1] - R * 0.45), (c[0] + R * 1.6 * d, c[1] - R * 0.4), w * 0.9, sd + 109)
        elif h == "curly":
            for i in range(6):
                a = math.radians(200 + i * 28)
                cc = (c[0] + math.cos(a) * R, c[1] + math.sin(a) * R)
                cv.circle(cc, R * 0.24, w * 0.55, sd + 110 + i, n=8)
        elif h == "bow":
            b = (c[0] + R * 0.5 * d, c[1] - R * 0.95)
            cv.poly([b, (b[0] - 14 * s, b[1] - 10 * s), (b[0] - 14 * s, b[1] + 10 * s), b,
                     (b[0] + 14 * s, b[1] - 10 * s), (b[0] + 14 * s, b[1] + 10 * s), b], w * 0.6, sd + 116)


def heart(cv, c, r, w, seed):
    pts = []
    for i in range(25):
        a = i / 24 * 2 * math.pi
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((c[0] + x / 16 * r, c[1] + y / 16 * r))
    cv.poly(pts, w, seed)


# --------------------------------------------------------------------------
# Objets (props)
# --------------------------------------------------------------------------
class Prop:
    def __init__(self, name, spec):
        self.name = name
        self.kind = spec.get("type", "box")
        self.tr = Track(spec.get("keys", []))
        self.size = spec.get("size", 1.0)
        self.seed = sid(name)
        self.shelter = None

    def pos(self, t, actors):
        att = self.tr.disc("attach", t, None)
        rt = self.tr.num("rot", t, 0.0)
        if att:
            who, joint = att.split(".")
            a = actors[who]
            J = a.joints
            d = a.state(t)["d"]
            p = J.get(joint, J["hands"])
            return (p[0] + self.tr.num("dx", t, 0.0) * d, p[1] + self.tr.num("dy", t, 0.0)), rt * d
        return (self.tr.num("x", t, 540), self.tr.num("y", t, 1300)), rt

    def draw(self, cv, t, actors):
        self.shelter = None
        if not self.tr.disc("visible", t, True):
            return
        (x, y), r = self.pos(t, actors)
        k, s, sd = self.kind, self.size, self.seed
        w = 5.5

        def P(px, py):
            q = rot((px * s, py * s), r)
            return (x + q[0], y + q[1])

        if k == "plank":
            box = [P(-75, -9), P(75, -9), P(75, 9), P(-75, 9)]
            cv.fill_poly(box, 0)
            cv.poly(box, w, sd, closed=True)
            cv.line(P(-55, 0), P(40, 0), 2.5, sd + 1, val=170)
            cv.dot(P(-64, 0), 2.8)
            cv.dot(P(64, 0), 2.8)
        elif k == "umbrella":
            op = self.tr.disc("open", t, True)
            top = P(0, -180)
            cv.line(P(0, 0), top, w, sd)
            cv.circle(P(-9, 0), 9 * s, w * 0.8, sd + 1, a0=0, a1=180, n=8)
            if op:
                c, rr = P(0, -170), 125 * s
                pts = [P(math.cos(a) * 125, -170 - math.sin(a) * 105) for a in np.linspace(0, math.pi, 22)]
                scal = []
                for i in range(4):
                    x0 = -125 + i * 62.5
                    for a in np.linspace(math.pi, 0, 6):
                        scal.append(P(x0 + 31.25 + math.cos(a) * 31.25, -170 + math.sin(a) * -10 + 6))
                cv.fill_poly(pts + scal, 0)
                cv.poly(pts, w, sd + 2)
                cv.poly(scal, w * 0.8, sd + 3)
                for i, xx in enumerate((-62, 0, 62)):
                    cv.line(P(0, -275), P(xx, -168), 2.5, sd + 4 + i, val=150)
                self.shelter = (c[0] - rr, c[0] + rr, c[1])
            else:
                cv.poly([P(0, -40), P(-16, -150), P(0, -185), P(16, -150), P(0, -40)], w * 0.8, sd + 2)
        elif k == "phone":
            box = [P(-10, -18), P(10, -18), P(10, 18), P(-10, 18)]
            cv.fill_poly(box, 60)
            cv.poly(box, 4, sd, closed=True)
            if self.tr.disc("glow", t, True):
                cv.add_glow(P(0, 0), 70 * s, "cool", 255)
        elif k == "cane":
            cv.line(P(0, 0), P(0, -150), w, sd)
            cv.circle(P(14, -150), 14 * s, w, sd + 1, a0=180, a1=360, n=8)
        elif k == "balloon":
            c = P(0, -170)
            cv.circle(c, 42 * s, w, sd, n=20)
            cv.poly([P(0, -128), P(-8, -90), P(6, -50), P(0, 0)], 2.5, sd + 1, val=200)
        elif k == "heart":
            heart(cv, (x, y), 40 * s, w, sd)
        elif k == "gift":
            box = [P(-40, -60), P(40, -60), P(40, 0), P(-40, 0)]
            cv.fill_poly(box, 0)
            cv.poly(box, w, sd, closed=True)
            cv.line(P(0, -60), P(0, 0), 3.5, sd + 1)
            cv.circle(P(-12, -68), 12 * s, 3.5, sd + 2, n=8)
            cv.circle(P(12, -68), 12 * s, 3.5, sd + 3, n=8)
        elif k == "box":
            box = [P(-50, -70), P(50, -70), P(50, 0), P(-50, 0)]
            cv.fill_poly(box, 0)
            cv.poly(box, w, sd, closed=True)
            cv.line(P(-50, -70), P(-30, -88), w, sd + 1)
            cv.line(P(50, -70), P(30, -88), w, sd + 2)
        elif k == "letter":
            box = [P(-34, -22), P(34, -22), P(34, 22), P(-34, 22)]
            cv.fill_poly(box, 0)
            cv.poly(box, 4, sd, closed=True)
            cv.poly([P(-34, -22), P(0, 4), P(34, -22)], 3.5, sd + 1)
        elif k == "flower":
            cv.line(P(0, 0), P(0, -90), 4, sd)
            for i in range(6):
                a = i * 60
                cv.circle(P(math.cos(math.radians(a)) * 14, -100 + math.sin(math.radians(a)) * 14), 10 * s, 3.5,
                          sd + 2 + i, n=8)
        elif k == "ball":
            cv.circle((x, y - 26 * s), 26 * s, w, sd, n=16)
            cv.circle((x, y - 26 * s), 26 * s, 3, sd + 1, a0=-40, a1=60, n=6)
        elif k == "candle":
            cv.poly([P(-10, 0), P(-10, -60), P(10, -60), P(10, 0)], 4.5, sd)
            cv.poly([P(0, -64), P(-6, -76), P(0, -92), P(6, -76), P(0, -64)], 3, sd + 1)
            if self.tr.disc("glow", t, True):
                cv.add_glow(P(0, -78), 90 * s, "warm", 230)
        elif k == "text":
            pass


# --------------------------------------------------------------------------
# Décors
# --------------------------------------------------------------------------
class Scenery:
    def __init__(self, spec, idx):
        self.s = spec
        self.k = spec["type"]
        self.seed = sid(f"{self.k}{idx}")
        self.hatch = []
        rng = np.random.default_rng(self.seed)
        if self.k in ("cliff", "ground"):
            x0, x1 = spec.get("x0", -1500), spec.get("x1", 2600)
            top = spec.get("y", spec.get("top", 1300))
            bot = spec.get("bottom", top + 1400)
            depth = spec.get("depth", 700) if self.k == "ground" else (bot - top)
            n = int((x1 - x0) * depth / (1700 if self.k == "cliff" else 2000))
            for _ in range(n):
                px = rng.uniform(x0 + 6, x1 - 6)
                py = top + 10 + (rng.random() ** (1.3 if self.k == "ground" else 1.0)) * depth
                L = rng.uniform(25, 90)
                a = math.radians(rng.uniform(32, 56))
                sgn = -1 if rng.random() < 0.8 else 1          # 80 % « / », 20 % qui croisent
                qx, qy = px + sgn * math.cos(a) * L, py + math.sin(a) * L
                qx = min(max(qx, x0 + 4), x1 - 4)
                fade = 1 - (py - top) / depth if self.k == "ground" else 1
                self.hatch.append(((px, py), (qx, qy), rng.uniform(90, 175) * (0.4 + 0.6 * fade)))
            self.grass = [(rng.uniform(x0 + 15, x1 - 15), rng.integers(3, 6)) for _ in range(int((x1 - x0) / 140))]

    def draw(self, cv, t):
        s, k, sd = self.s, self.k, self.seed
        if not (s.get("t0", -1e9) <= t <= s.get("t1", 1e9)):
            return
        if k in ("cliff", "ground"):
            x0, x1 = s.get("x0", -1500), s.get("x1", 2600)
            top = s.get("y", s.get("top", 1300))
            bot = s.get("bottom", top + 1400)
            cv.poly([(x0, top), (x1, top)], 6, sd)
            if k == "cliff":
                if s.get("edge_left", True):
                    cv.poly([(x0, top), (x0 + 6, (top + bot) / 2), (x0 - 4, bot)], 6, sd + 1)
                if s.get("edge_right", True):
                    cv.poly([(x1, top), (x1 - 6, (top + bot) / 2), (x1 + 4, bot)], 6, sd + 2)
            for i, (a, b, v) in enumerate(self.hatch):
                cv.line(a, b, 2.2, sd + 10 + i, val=v, jit=0.5)
            for i, (gx, n) in enumerate(self.grass):
                for j in range(n):
                    a = -40 + 80 * j / max(1, n - 1)
                    L = 14 + 10 * rnd(sd, i * 7 + j)
                    cv.line((gx + j * 3, top - 1), (gx + j * 3 + math.sin(math.radians(a)) * L,
                                                    top - math.cos(math.radians(a)) * L), 2.5, sd + 500 + i * 7 + j)
        elif k == "bench":
            x, y, w2 = s["x"], s.get("y", 1300), s.get("w", 260) / 2
            seat = y - 62
            cv.poly([(x - w2, seat), (x + w2, seat)], 7, sd)
            cv.poly([(x - w2 + 6, seat - 50), (x + w2 - 6, seat - 50)], 6, sd + 1)
            cv.poly([(x - w2 + 6, seat - 88), (x + w2 - 6, seat - 88)], 6, sd + 2)
            for i, xx in enumerate((x - w2 + 20, x + w2 - 20)):
                cv.line((xx, seat), (xx, y), 6, sd + 3 + i)
                cv.line((xx, seat), (xx, seat - 92), 5, sd + 5 + i)
        elif k == "lamp":
            x, y, h = s["x"], s.get("y", 1300), s.get("h", 520)
            side = s.get("side", -1)
            cv.line((x, y), (x, y - h), 7, sd)
            cv.poly([(x, y - h), (x + side * 40, y - h - 30), (x + side * 90, y - h - 22)], 6, sd + 1)
            hx, hy = x + side * 95, y - h - 8
            cv.poly([(hx - 26, hy + 14), (hx - 16, hy - 16), (hx + 16, hy - 16), (hx + 26, hy + 14), (hx - 26, hy + 14)],
                    5, sd + 2)
            on = s.get("on", True)
            if on:
                cv.add_glow((hx, hy), 80, "warm", 255)
                cv.add_glow_poly([(hx - 22, hy + 14), (hx + 22, hy + 14), (hx + 190, y), (hx - 190, y)], "warm", 70)
        elif k == "tree":
            x, y, h = s["x"], s.get("y", 1300), s.get("h", 420)
            cv.poly([(x - 14, y), (x - 8, y - h * 0.55), (x - 30, y - h * 0.75)], 6, sd)
            cv.poly([(x + 14, y), (x + 9, y - h * 0.55), (x + 34, y - h * 0.72)], 6, sd + 1)
            for i in range(9):
                a = i / 9 * 2 * math.pi
                cv.circle((x + math.cos(a) * h * 0.22, y - h * 0.8 + math.sin(a) * h * 0.16), h * 0.14, 5, sd + 2 + i,
                          a0=150, a1=420, n=12)
        elif k == "moon":
            c, r = (s["x"], s["y"]), s.get("r", 55)
            cv.circle(c, r, 4, sd, n=30)
            cv.circle((c[0] + r * 0.35, c[1] - r * 0.1), r * 0.8, 3.5, sd + 1, a0=100, a1=260, n=16)
        elif k == "cloud":
            c, r = (s["x"], s["y"]), s.get("r", 70)
            for i, (dx, dy, rr) in enumerate(((-1.2, 0.1, 0.7), (-0.4, -0.35, 0.9), (0.5, -0.2, 0.8), (1.2, 0.15, 0.6))):
                cv.circle((c[0] + dx * r, c[1] + dy * r), rr * r, 4.5, sd + i, a0=150, a1=390, n=14)
            cv.line((c[0] - 1.8 * r, c[1] + 0.55 * r), (c[0] + 1.75 * r, c[1] + 0.55 * r), 4.5, sd + 9)
        elif k == "house":
            x, y, w2, h = s["x"], s.get("y", 1300), s.get("w", 300) / 2, s.get("h", 260)
            cv.poly([(x - w2, y), (x - w2, y - h), (x, y - h - w2 * 0.8), (x + w2, y - h), (x + w2, y)], 6, sd)
            cv.poly([(x - 30, y), (x - 30, y - 90), (x + 30, y - 90), (x + 30, y)], 5, sd + 1)
            wx = x + w2 * 0.5
            cv.poly([(wx - 30, y - h + 40), (wx + 30, y - h + 40), (wx + 30, y - h + 100), (wx - 30, y - h + 100)],
                    4.5, sd + 2, closed=True)
            if s.get("light", False):
                cv.add_glow((wx, y - h + 70), 70, "warm", 200)
        elif k == "line":
            cv.poly([tuple(p) for p in s["points"]], s.get("w", 6), sd)


# --------------------------------------------------------------------------
# Textes écrits à la craie
# --------------------------------------------------------------------------
class ChalkText:
    _cache = {}

    def __init__(self, spec):
        self.s = spec
        lines = spec.get("lines") or [{"text": spec["text"], "size": spec.get("size", 96)}]
        self.lines = [ln if isinstance(ln, dict) else {"text": ln, "size": spec.get("size", 96)} for ln in lines]
        self.imgs = [self._img(ln["text"], ln.get("size", spec.get("size", 96))) for ln in self.lines]

    @classmethod
    def _img(cls, txt, size):
        key = (txt, size)
        if key not in cls._cache:
            f = ImageFont.truetype(FONT_PATH, int(size))
            while f.getlength(txt) > W - 120 and size > 30:
                size -= 4
                f = ImageFont.truetype(FONT_PATH, int(size))
            wd = int(f.getlength(txt)) + 40
            im = Image.new("L", (wd, int(size * 1.35)), 0)
            dr = ImageDraw.Draw(im)
            for k, (ox, oy, v) in enumerate(((0, 0, 255), (1.4, 0.8, 150), (-0.8, 1.2, 110))):
                dr.text((20 + ox, size * 0.12 + oy), txt, font=f, fill=v, stroke_width=2 if k == 0 else 0,
                        stroke_fill=v)
            cls._cache[key] = im
        return cls._cache[key]

    def draw(self, layer, t):
        s = self.s
        t0, t1 = s.get("t0", 0), s.get("t1", 1e9)
        if t < t0 or t > t1 + s.get("fade", 0.5):
            return
        alpha = 1.0 if t <= t1 else 1 - (t - t1) / s.get("fade", 0.5)
        total = sum(len(ln["text"]) for ln in self.lines)
        write = s.get("write", 0.06 * total)
        done = (t - t0) / max(1e-6, write) * total if write > 0 else total
        y = s.get("y", 400)
        gap = s.get("gap", 1.05)
        for ln, im in zip(self.lines, self.imgs):
            n = len(ln["text"])
            frac = min(1.0, max(0.0, done / n)) if n else 1
            done -= n
            if frac <= 0:
                break
            x = int(s.get("x", W / 2) - im.width / 2)
            cut = int(20 + (im.width - 40) * frac)
            part = im.crop((0, 0, cut, im.height))
            if alpha < 1:
                part = part.point(lambda v: int(v * alpha))
            layer.paste(ImageChops.lighter(layer.crop((x, int(y), x + part.width, int(y) + part.height)), part),
                        (x, int(y)))
            y += im.height * gap


# --------------------------------------------------------------------------
# Scène complète
# --------------------------------------------------------------------------
class Scene:
    def __init__(self, cfg):
        self.cfg = cfg
        self.dur = float(cfg["duration"])
        self.scenery = [Scenery(s, i) for i, s in enumerate(cfg.get("set", []))]
        self.actors = {n: Actor(n, a) for n, a in cfg.get("actors", {}).items()}
        self.props = {n: Prop(n, p) for n, p in cfg.get("props", {}).items()}
        self.front = [n for n, p in cfg.get("props", {}).items() if p.get("layer", "front") == "front"]
        self.cam = Track(cfg.get("camera", [{"t": 0, "cx": 540, "cy": 960, "zoom": 1}]))
        self.fade = Track(cfg.get("fade", [{"t": 0, "b": 1}]))
        self.texts = [ChalkText(s) for s in cfg.get("texts", [])]
        self.rain = cfg.get("rain")
        rng = np.random.default_rng(7)
        self.drops = rng.random((420, 3))
        self.dust = rng.random((70, 4))
        self.bg = self._background()
        g = rng.random((H, W)).astype(np.float32)
        g2 = np.asarray(Image.fromarray((g * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)),
                        np.float32) / 255
        self.grain = [np.clip(0.30 + 0.95 * (0.65 * gi + 0.35 * g2) ** 0.8, 0, 1.05)
                      for gi in (g, np.roll(g, 3, axis=1))]

    def _background(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
        base = 0.115 - 0.07 * np.clip(r * 1.6, 0, 1)
        rng = np.random.default_rng(3)
        sm = rng.random((H // 64 + 2, W // 64 + 2)).astype(np.float32)
        sm = np.asarray(Image.fromarray((sm * 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
        base = base + (sm - 0.5) * 0.025
        tone = np.array([0.95, 1.0, 1.06], np.float32)
        return np.clip(base[..., None] * tone, 0, 1)

    def frame(self, t, fps=30):
        cam = (self.cam.num("cx", t, 540), self.cam.num("cy", t, 960), self.cam.num("zoom", t, 1.0))
        cv = Canvas(cam)
        for a in self.actors.values():          # positions d'abord (objets tenus en main)
            a.solve(a.state(t))
        for sc in self.scenery:
            sc.draw(cv, t)
        for n, p in self.props.items():
            if n not in self.front:
                p.draw(cv, t, self.actors)
        for a in self.actors.values():
            a.draw(cv, t)
        for n in self.front:
            self.props[n].draw(cv, t, self.actors)
        shelters = [p.shelter for p in self.props.values() if p.shelter]
        shelters += [(sc.s.get("x0", -1e5), sc.s.get("x1", 1e5), sc.s.get("y", sc.s.get("top", 1300)))
                     for sc in self.scenery if sc.k in ("ground", "cliff")]
        if self.rain and self.rain.get("t0", 0) <= t <= self.rain.get("t1", 1e9):
            self._rain(cv, t, shelters)
        self._dust(cv, t)
        chalk = np.asarray(cv.img, np.float32) / 255
        chalk = chalk * self.grain[int(t * 8) % 2]
        soft = np.asarray(cv.img.filter(ImageFilter.GaussianBlur(5)), np.float32) / 255
        img = self.bg + chalk[..., None] * CHALK_RGB + soft[..., None] * 0.16
        for k, g in cv.glow.items():
            if g.getbbox():
                ga = np.asarray(g.filter(ImageFilter.GaussianBlur(9)).resize((W, H), Image.BILINEAR), np.float32) / 255
                img = img + ga[..., None] * np.array(GLOW_COLORS[k], np.float32) * 0.85
        b = self.fade.num("b", t, 1.0)
        img = img * b
        tl = Image.new("L", (W, H), 0)
        top = Image.new("L", (W, H), 0)
        for tx in self.texts:
            tx.draw(top if tx.s.get("over_fade") else tl, t)
        if tl.getbbox():
            ta = np.asarray(tl, np.float32) / 255 * (0.45 + 0.6 * self.grain[0])
            img = img + ta[..., None] * CHALK_RGB * b
        if top.getbbox():
            ta = np.asarray(top, np.float32) / 255 * (0.45 + 0.6 * self.grain[0])
            img = img + ta[..., None] * CHALK_RGB
        return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8), "RGB")

    def _rain(self, cv, t, shelters):
        r = self.rain
        dens = r.get("density", 1.0)
        n = int(len(self.drops) * min(1.0, dens))
        ang = math.radians(r.get("angle", 12))
        sp = r.get("speed", 1500)
        span = H + 400
        for i in range(n):
            fx, ph, ln = self.drops[i]
            y = (ph * span + t * sp * (0.8 + 0.4 * ln)) % span - 200
            x = fx * (W + 400) - 200 - y * math.tan(ang)
            wx, wy = (x - W / 2) / cv.z + cv.cx, (y - H / 2) / cv.z + cv.cy
            if any(a <= wx <= b and wy > cy for a, b, cy in shelters):
                continue
            L = 26 + 26 * ln
            cv.d.line([(x, y), (x + math.sin(ang) * L, y + math.cos(ang) * L)], fill=110, width=2)

    def _dust(self, cv, t):
        for i, (fx, fy, sp, ph) in enumerate(self.dust):
            x = (fx * W + math.sin(t * 0.3 + ph * 6) * 30) % W
            y = (fy * H - t * (8 + 14 * sp)) % H
            v = 60 + 90 * (0.5 + 0.5 * math.sin(t * (1 + sp) + ph * 9))
            rr = 1.2 + 1.6 * sp
            cv.d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=int(v))


# --------------------------------------------------------------------------
def render(cfg_path, out, fps=30, preview=None, crf=19):
    with open(cfg_path, encoding="utf-8") as f:
        cfg = json.load(f)
    sc = Scene(cfg)
    if preview:
        for t in preview:
            p = os.path.splitext(out)[0] + f"_{t:05.2f}s.png"
            sc.frame(t).save(p)
            print("aperçu :", p)
        return
    tmp = tempfile.mkdtemp(prefix="craie_")
    wav = os.path.join(tmp, "audio.wav")
    audiogen.build(cfg, sc.dur, wav, os.path.dirname(os.path.abspath(cfg_path)))
    n = int(math.ceil(sc.dur * fps))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "medium", "-crf", str(crf), "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        proc.stdin.write(sc.frame(i / fps, fps).tobytes())
        if i % (fps * 5) == 0:
            print(f"  {i / fps:5.1f}s / {sc.dur:.1f}s", flush=True)
    proc.stdin.close()
    proc.wait()
    if proc.returncode:
        raise SystemExit("ffmpeg a échoué")
    print(f"OK -> {out} ({sc.dur:.1f}s)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("-o", "--out", default="histoire.mp4")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--preview", type=float, nargs="+")
    a = ap.parse_args()
    render(a.config, a.out, a.fps, a.preview)


if __name__ == "__main__":
    main()
