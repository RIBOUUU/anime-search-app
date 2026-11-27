#!/usr/bin/env python3
"""Assemble les images 3D (15 i/s rendues) + textes + bande-son -> MP4 1080x1920 30 i/s."""
import glob, json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
SK = "/home/user/anime-search-app/.claude/skills/histoire-craie"
sys.path.insert(0, SK + "/scripts")
import audio as A  # noqa

FONT = sys.argv[1]
OUT = sys.argv[2]
W, H, FPS, DUR = 1080, 1920, 30, 18.2
WHITE, GREEN = (255, 255, 255), (150, 240, 70)

frames = sorted(glob.glob(D + "/frames/f_*.png"), key=lambda p: int(p[-8:-4]))
byf = {int(p[-8:-4]): p for p in frames}
keys = sorted(byf)

TEXTS = [  # (t0, t1, [(texte, taille)], y, couleur)
    (0.0, 2.5, [("IL FRAPPE À CETTE PORTE", 64), ("DEPUIS 100 JOURS.", 84)], 210, WHITE),
    (0.0, 2.65, [("JOUR 1", 96)], 470, GREEN),
    (2.7, 4.45, [("JOUR 12", 96)], 470, GREEN),
    (4.5, 6.25, [("JOUR 47", 96)], 470, GREEN),
    (6.3, 8.35, [("JOUR 99", 96)], 470, GREEN),
    (8.4, 11.0, [("JOUR 100", 110)], 230, GREEN),
    (15.2, 99, [("PARFOIS, IL SUFFIT", 76), ("DE FAIRE LE TOUR.", 96)], 230, WHITE),
]
fonts = {}


def font(sz):
    if sz not in fonts:
        fonts[sz] = ImageFont.truetype(FONT, sz)
    return fonts[sz]


def draw_texts(im, t):
    d = ImageDraw.Draw(im)
    for t0, t1, lines, y, colr in TEXTS:
        if not (t0 <= t < t1):
            continue
        # écriture progressive en 0,5 s (effet de frappe)
        total = sum(len(l) for l, _ in lines)
        shown = int(total * min(1.0, (t - t0) / 0.5)) if t0 > 0 or colr == WHITE else total
        yy = y
        for l, sz in lines:
            part = l[:max(0, shown)]
            shown -= len(l)
            f = font(sz)
            if part:
                d.text((W / 2, yy), part, font=f, fill=colr, anchor="ma", stroke_width=8, stroke_fill=(0, 0, 0))
            yy += int(sz * 1.25)


wav = D + "/audio.wav"
cfg = json.load(open(SK + "/examples/la-porte.json"))
A.build(cfg, DUR, wav)
n = int(DUR * FPS)
cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
       "-i", "-", "-i", wav, "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
cache = {}
for i in range(n):
    fr = i + 1
    src = max(k for k in keys if k <= fr) if any(k <= fr for k in keys) else keys[0]
    if src not in cache:
        cache.clear()
        cache[src] = Image.open(byf[src]).convert("RGB").resize((W, H), Image.LANCZOS)
    im = cache[src].copy()
    draw_texts(im, i / FPS)
    p.stdin.write(im.tobytes())
p.stdin.close()
p.wait()
print("OK", OUT)
