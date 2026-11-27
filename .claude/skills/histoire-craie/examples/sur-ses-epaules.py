#!/usr/bin/env python3
"""« SUR SES ÉPAULES » — histoire longue (34 s) : quelqu'un au-dessus de quelqu'un.
Elle le porte à bout de bras pour qu'il touche les étoiles ; il devient « grand », l'oublie
et saute vers une autre. Sans elle tout s'écroule : c'est elle qui finit lumineuse, avec les étoiles.

    python3 sur-ses-epaules.py   -> écrit sur-ses-epaules.json
"""
import json
import os

G = 1300
UP, KN = 975, 1038          # hauteur des mains : elle debout bras levés / à genoux écrasée
XU, XK = 551, 578           # x des mains
STARS = [(430, 620), (560, 560), (690, 630)]


def K(t, **kw):
    d = {"t": t}
    d.update(kw)
    return d


crowd = {}
for i, (x, h) in enumerate([(110, "cap"), (185, "curly"), (255, "beanie"), (1040, "bow"), (1115, "cap"), (1190, "long")]):
    crowd[f"fan{i}"] = {"hair": h, "keys": [
        K(0, visible=False, x=x, ground=G, dir=1 if x < 540 else -1, pose="cheer", face="laugh", scale=0.55),
        K(5.5, visible=True), K(19.8, dir=1 if x < 900 else -1), K(23.0, visible=False)]}

actors = {
    "elle": {"hair": "ponytail", "extras": ["skirt"],
             "hud": [{"type": "gauge", "label": "FORCE", "fmt": "pct", "warn": 20, "dx": -230, "dy": -10, "size": 1.0,
                      "keys": [K(0, v=100), K(5.0, v=100), K(9.0, v=60), K(12.0, v=60), K(16.0, v=18),
                               K(19.2, v=2), K(25.4, v=2), K(26.8, v=100, ease="in")]}],
             "keys": [K(0, x=-120, ground=G, dir=1, pose="walk", face="smile", glow=0.0),
                      K(2.4, x=540, ease="out"), K(2.6, pose="lift_kneel", face="smile"),
                      K(3.8, pose="lift_kneel"), K(4.6, pose="lift", face="happy"),
                      K(8.0, face="worried"), K(10.4, face="cry"),
                      K(12.0, pose="lift_kneel", face="cry", cut=True),
                      K(19.2, pose="hug_knees", face="cry"),
                      K(24.4, pose="sit_look_up", face="surprised"),
                      K(25.6, pose="stand", face="happy", glow=0.0), K(26.6, glow=1.0, flicker=True),
                      K(27.4, flicker=False, pose="cheer", face="laugh"), K(29.0, pose="stand", face="closed")]},
    "lui": {"hair": "cap",
            "hud": [{"type": "gauge", "label": "SUCCÈS", "fmt": "pct", "dx": 230, "dy": -10, "size": 1.0,
                     "keys": [K(0, v=0), K(4.8, v=0), K(5.3, v=30), K(6.6, v=60), K(7.6, v=85), K(13, v=95),
                              K(22.6, v=95), K(23.8, v=0, ease="in")]}],
            "keys": [K(0, x=560, ground=G, dir=1, pose="look_up", face="worried", lift=0, glow=0.0),
                     K(5.6, glow=0.0),
                     K(0.6, pose="jump"), K(0.9, pose="look_up"), K(1.4, pose="jump"), K(1.7, pose="look_up"),
                     K(2.6, x=560), K(3.3, x=XK, ground=KN, ease="out", pose="stand", face="smile"),
                     K(3.8, x=XK, ground=KN), K(4.6, x=XU, ground=UP, pose="cheer", face="happy"),
                     K(6.0, pose="wave", face="laugh", glow=0.35),
                     K(12.0, x=XK, ground=KN, pose="wave", cut=True),
                     K(14.6, pose="stand", face="smile"), K(15.6, face="love", dir=1),
                     K(18.4, x=XK, ground=KN, pose="stand", lift=0), K(18.9, pose="jump", lift=-140, x=720, ground=990),
                     K(19.5, x=870, ground=958, lift=0, pose="cheer", face="laugh", ease="out"),
                     K(22.6, x=870, ground=958, face="surprised", pose="stand"),
                     K(23.6, x=930, ground=G, ease="in", pose="lie", face="surprised", glow=0.0),
                     K(25.0, face="cry"), K(27.6, face="sad")]},
    "autre": {"hair": "curly", "extras": ["skirt"],
              "keys": [K(0, visible=False, x=930, ground=958, dir=-1, pose="wave", face="happy"),
                       K(14.8, visible=True), K(19.6, pose="cheer", face="laugh"),
                       K(22.6, face="surprised", pose="stand"), K(22.9, visible=False)]},
}
actors.update(crowd)

props = {
    "plateau": {"type": "platform", "h": 342, "keys": [
        K(0, visible=False, x=930, y=958, rot=0), K(14.6, visible=True),
        K(22.6, x=930, y=958, rot=0), K(23.5, x=1010, y=1330, rot=38, ease="in"), K(24.2, visible=False)]},
}
for i, (sx, sy) in enumerate(STARS):
    t_take = [5.0, 6.6, 7.6][i]
    off = [-70, 0, 70][i]
    props[f"etoile{i}"] = {"type": "star", "size": 1.2, "keys": [
        K(0, x=sx, y=sy, shine=True),
        K(t_take - 0.4, x=sx, y=sy),
        K(t_take, attach="lui.head", dx=off, dy=-160),
        K(22.6, attach="lui.head", dx=off, dy=-160),
        K(22.7, attach=None, x=870 + off, y=640),
        K(23.9, x=930 + off * 1.4, y=G - 20, ease="in", shine=False, dim=True, rot=60),
        K(25.8, x=930 + off * 1.4, y=G - 20),
        K(27.2, attach="elle.head", dx=off, dy=-175, rot=0, dim=False, shine=True, ease="inout")]}

story = {
    "_histoire": __doc__.strip().split("\n")[1],
    "_legende": "Il était grand… parce qu'elle le portait ⭐ #couple #stickman #animation #amour #histoire",
    "duration": 34.0,
    "music": {"mood": "sad", "bpm": 70, "turn": 24.6, "volume": 0.6},
    "set": [{"type": "ground", "y": G, "x0": -3000, "x1": 6000},
            {"type": "moon", "x": 860, "y": 420, "r": 55},
            {"type": "burst", "x": 560, "y": 600, "t0": 5.0, "r": 120},
            {"type": "burst", "x": 930, "y": 1000, "t0": 22.7, "r": 200, "glow": False},
            {"type": "burst", "x": 540, "y": 800, "t0": 27.2, "r": 220}],
    "actors": actors,
    "props": props,
    "camera": [
        K(0, cx=560, cy=900, zoom=1.15), K(2.2, cx=560, cy=900, zoom=1.15),
        K(3.6, cx=560, cy=880, zoom=1.0), K(5.4, cx=560, cy=860, zoom=1.0),
        K(6.6, cx=600, cy=900, zoom=0.92), K(9.4, cx=600, cy=900, zoom=0.92),
        K(10.3, cx=545, cy=1060, zoom=2.0), K(11.9, cx=545, cy=1060, zoom=2.0),
        K(12.0, cx=640, cy=930, zoom=1.0, cut=True), K(15.2, cx=700, cy=880, zoom=1.35),
        K(18.2, cx=700, cy=920, zoom=1.0), K(22.4, cx=720, cy=940, zoom=1.0),
        K(24.0, cx=700, cy=980, zoom=1.0), K(24.6, cx=560, cy=1060, zoom=1.6),
        K(26.6, cx=600, cy=920, zoom=1.1), K(29.0, cx=640, cy=900, zoom=1.0)],
    "fade": [{"t": 0, "b": 1}],
    "texts": [
        {"lines": [{"text": "IL VOULAIT TOUCHER", "size": 96}, {"text": "LES ÉTOILES.", "size": 118}],
         "y": 200, "t0": 0, "write": 0.6, "t1": 2.6, "fade": 0.15},
        {"text": "AN 1", "size": 84, "y": 300, "t0": 2.7, "write": 0.15, "t1": 5.4, "fade": 0.05, "color": "green"},
        {"text": "AN 2", "size": 84, "y": 300, "t0": 5.5, "write": 0.15, "t1": 11.9, "fade": 0.05, "color": "green"},
        {"text": "AN 5", "size": 84, "y": 300, "t0": 12.0, "write": 0.15, "t1": 22.4, "fade": 0.05, "color": "green"},
        {"lines": [{"text": "IL ÉTAIT GRAND...", "size": 96}, {"text": "PARCE QU'ELLE LE PORTAIT.", "size": 84}],
         "y": 210, "t0": 29.0, "write": 1.6}],
    "sfx": [K(0.6, type="whoosh", volume=0.3), K(1.4, type="whoosh", volume=0.3),
            K(5.0, type="pop", volume=0.4), K(6.6, type="pop", volume=0.4), K(7.6, type="pop", volume=0.4),
            K(18.9, type="whoosh", volume=0.5), K(22.6, type="wood", volume=0.6), K(23.5, type="thud", volume=0.8),
            K(26.6, type="heart", volume=0.6), K(27.2, type="pop", volume=0.4)],
}
here = os.path.dirname(os.path.abspath(__file__))
json.dump(story, open(os.path.join(here, "sur-ses-epaules.json"), "w"), ensure_ascii=False, indent=1)
print("ok")
