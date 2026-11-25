#!/usr/bin/env python3
"""Génère les 10 histoires « femmes à l'honneur » (jauges / compteurs au-dessus des têtes).

    python3 generate.py      -> écrit 01-....json à 10-....json dans ce dossier
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
G = 1300  # sol


def K(t, **kw):
    d = {"t": t}
    d.update(kw)
    return d


def hook(lines, t1=2.6):
    return {"lines": [{"text": l, "size": s} for l, s in lines], "y": 200, "t0": 0, "write": 0.6, "t1": t1,
            "fade": 0.15}


def tag(text, t0, t1, y=440, size=84):
    return {"text": text, "size": size, "y": y, "t0": t0, "write": 0.15, "t1": t1, "fade": 0.05, "color": "green"}


def moral(l1, l2, t0, y=230):
    return {"lines": [{"text": l1, "size": 88}, {"text": l2, "size": 108}], "y": y, "t0": t0, "write": 1.5}


def bubble(name, who, text, t0, t1, tail=1, font=38, dy=-20, dx=0):
    return name, {"type": "bubble", "text": text, "font": font, "tail": tail,
                  "keys": [K(0, visible=False, attach=f"{who}.head", dy=dy, dx=dx), K(t0, visible=True), K(t1, visible=False)]}


def story(name, dur, turn, **kw):
    d = {"duration": dur, "music": {"mood": "sad", "bpm": 80, "turn": turn, "volume": 0.55},
         "fade": [{"t": 0, "b": 1}], "set": [{"type": "ground", "y": G}], "actors": {}, "props": {},
         "camera": [], "texts": [], "sfx": []}
    d.update(kw)
    return name, d


def props(*items):
    return dict(items)


S = []

# --------------------------------------------------------------------------- 1
S.append(story(
    "01-la-charge-invisible", 19.6, 13.6,
    _legende="Sa batterie ne tombe jamais à 0 %. Tag celle qui recharge tout le monde 🔋 #maman #stickman #animation #femme",
    set=[{"type": "ground", "y": G}, {"type": "desk", "x": 780, "w": 240},
         {"type": "bench", "x": 300, "w": 250}],
    actors={
        "maman": {"hair": "ponytail", "extras": ["skirt"],
                  "hud": [{"type": "gauge", "label": "ÉNERGIE", "fmt": "pct", "warn": 15,
                           "keys": [K(0, v=100), K(2.0, v=100), K(2.5, v=82), K(4.6, v=82), K(5.1, v=61),
                                    K(7.2, v=61), K(7.7, v=38), K(9.9, v=38), K(10.4, v=14), K(11.6, v=3),
                                    K(13.9, v=3), K(15.2, v=100, ease="in"), K(14.0, glow=None), K(14.2, glow="warm"),
                                    K(16.0, glow=None)]}],
                  "keys": [K(0, x=520, ground=G, dir=1, pose="hold", face="smile"),
                           K(1.6, pose="reach"), K(2.3, pose="stand", face="neutral"),
                           K(2.9, x=700, pose="hold", face="neutral", cut=True), K(3.0, pose="hold"),
                           K(5.6, x=200, pose="carry", face="worried", cut=True), K(7.0, x=560, ease="out"),
                           K(8.3, x=620, pose="point", face="sad", cut=True),
                           K(11.0, x=300, pose="sit_sad", face="sad", cut=True),
                           K(12.6, face="closed"),
                           K(13.8, pose="sit_look_up", face="surprised"), K(14.4, pose="sit_umbrella", face="happy"),
                           K(15.3, face="closed")]},
        "fille": {"hair": "bow",
                  "hud": [{"type": "gauge", "label": "JOIE", "fmt": "pct", "size": 0.65, "t1": 2.8,
                           "keys": [K(0, v=40), K(2.0, v=40), K(2.4, v=90)]}],
                  "keys": [K(0, x=720, ground=G, dir=-1, pose="stand", face="neutral", scale=0.6),
                           K(2.2, face="happy"), K(2.8, visible=False),
                           K(12.2, visible=True, x=-80, dir=1, pose="hold", face="smile", cut=True),
                           K(13.6, x=230, ease="out"), K(13.9, pose="reach"),
                           K(14.6, x=230, ground=G), K(14.9, x=240, ground=G - 25, pose="sit_bench", face="closed")]},
        "fils": {"hair": "cowlick",
                 "hud": [{"type": "gauge", "label": "JOIE", "fmt": "pct", "size": 0.65, "t0": 5.5, "t1": 10.8,
                          "keys": [K(0, v=20), K(7.4, v=20), K(7.8, v=95), K(9.4, v=95), K(9.9, v=100)]}],
                 "keys": [K(0, visible=False, x=760, ground=G, dir=-1, scale=0.55, pose="stand", face="neutral"),
                          K(5.6, visible=True), K(7.6, face="happy", pose="cheer"),
                          K(8.3, pose="sit_type", face="worried", cut=True, x=700, ground=G - 20),
                          K(9.8, face="happy", pose="cheer", ground=G), K(10.8, visible=False)]}},
    props=props(
        ("bol", {"type": "cup", "size": 0.7, "keys": [K(0, attach="maman.hand_r", dy=30), K(1.9, attach="fille.hand_r"),
                                                     K(2.8, visible=False)]}),
        ("ordi", {"type": "laptop", "keys": [K(0, visible=False, x=790, y=G - 105, glow=True), K(2.9, visible=True),
                                             K(5.6, visible=False)]}),
        ("courses", {"type": "box", "size": 0.75, "keys": [K(0, visible=False, attach="maman.hands", dy=55),
                                                           K(5.6, visible=True), K(8.3, visible=False)]}),
        ("cahier", {"type": "book", "keys": [K(0, visible=False, x=760, y=G - 105), K(8.3, visible=True),
                                            K(10.9, visible=False)]}),
        ("tasse", {"type": "cup", "size": 0.6, "shine": True,
                   "keys": [K(0, visible=False, attach="fille.hand_r", dy=22, shine=True), K(12.2, visible=True),
                            K(14.2, attach="maman.hand_r")]})),
    camera=[K(0, cx=620, cy=1060, zoom=1.25), K(2.85, cx=620, cy=1060, zoom=1.25),
            K(2.9, cx=730, cy=1080, zoom=1.35, cut=True), K(5.55, cx=730, cy=1080, zoom=1.35),
            K(5.6, cx=520, cy=1060, zoom=1.2, cut=True), K(8.25, cx=520, cy=1060, zoom=1.2),
            K(8.3, cx=680, cy=1090, zoom=1.4, cut=True), K(10.95, cx=680, cy=1090, zoom=1.4),
            K(11.0, cx=340, cy=1100, zoom=1.55, cut=True), K(12.2, cx=330, cy=1100, zoom=1.6),
            K(13.6, cx=330, cy=1080, zoom=1.3), K(15.8, cx=380, cy=1030, zoom=1.15)],
    texts=[hook([("SA BATTERIE NE TOMBE", 84), ("JAMAIS À 0 %...", 96)]),
           tag("7H00", 0.05, 2.85), tag("9H00", 2.9, 5.55), tag("18H00", 5.6, 8.25), tag("21H00", 8.3, 10.95),
           tag("23H30", 11.0, 13.4),
           moral("ELLE RECHARGE TOUT LE MONDE.", "QUI LA RECHARGE ?", 16.1)],
    sfx=[K(2.5, type="tick", volume=0.3), K(5.1, type="tick", volume=0.3), K(7.7, type="tick", volume=0.3),
         K(10.4, type="tick", volume=0.3), K(14.2, type="heart", volume=0.6)]))

# --------------------------------------------------------------------------- 2
doors = [("BANQUE", 0, 2.6), ("INVESTISSEURS", 2.6, 4.9), ("BANQUE", 4.9, 7.2), ("FONDS PRIVÉ", 7.2, 9.5),
         ("PORTE 100", 9.5, 12.8)]
S.append(story(
    "02-1-sur-100", 19.4, 10.6,
    _legende="99 « non ». 1 « oui ». Et maintenant c'est elle qui ouvre la porte 🚪✨ #entrepreneuse #femme #stickman #motivation",
    set=[{"type": "ground", "y": G}] +
        [{"type": "house", "x": 820, "w": 280, "h": 260, "label": n, "label_size": 34, "t0": a, "t1": b - 0.01}
         for n, a, b in doors] +
        [{"type": "house", "x": 820, "w": 300, "h": 270, "label": "SA BOÎTE", "light": True, "t0": 13.6},
         {"type": "burst", "x": 560, "y": 880, "t0": 10.6}, {"type": "burst", "x": 560, "y": 900, "t0": 15.6}],
    actors={
        "elle": {"hair": "long", "extras": ["skirt"],
                 "hud": [{"type": "counter", "prefix": "NON × ", "t1": 10.5,
                          "t0": 1.45, "keys": [K(0, v=1), K(2.65, v=12, cut=True),
                                   K(5.0, v=47, cut=True), K(7.3, v=99, cut=True)]},
                         {"type": "counter", "prefix": "OUI !", "fmt": "none", "t0": 10.6, "t1": 12.8, "size": 1.3,
                          "keys": [K(0, v=0, glow="warm")]}],
                 "keys": [K(0, x=380, ground=G, dir=1, pose="hold", face="smile"), K(0.9, x=580, ease="out"),
                          K(1.0, pose="present"), K(2.1, face="sad", pose="hold"),
                          K(2.65, x=580, pose="present", face="neutral", cut=True), K(3.8, face="sad", pose="hold"),
                          K(4.95, x=580, pose="present", face="worried", cut=True), K(6.1, pose="sad", face="sad"),
                          K(7.25, x=580, pose="sad", face="cry", cut=True), K(8.6, face="cry"),
                          K(9.55, x=580, pose="present", face="worried", cut=True),
                          K(10.6, face="surprised"), K(11.0, face="laugh", pose="cheer"), K(12.8, visible=False),
                          K(13.6, visible=True, x=760, dir=-1, pose="stand", face="neutral", cut=True),
                          K(15.4, pose="present", face="smile"), K(16.0, face="happy")]},
        "banquier": {"hair": "none", "extras": ["tie", "glasses"],
                     "keys": [K(0, x=800, ground=G, dir=-1, pose="stand", face="neutral"),
                              K(1.4, face="angry"), K(2.4, face="laugh"), K(4.0, face="angry"),
                              K(6.2, face="laugh"), K(8.0, face="angry"), K(9.5, visible=False)]},
        "mamie": {"hair": "curly", "extras": ["glasses", "skirt"],
                  "keys": [K(0, visible=False, x=800, ground=G, dir=-1, pose="old", face="smile"),
                           K(10.0, visible=True), K(10.6, face="happy"), K(12.8, visible=False)]},
        "petite": {"hair": "ponytail", "extras": ["skirt"],
                   "hud": [{"type": "counter", "prefix": "NON × ", "t1": 15.5, "size": 0.8,
                            "keys": [K(0, v=37)]},
                           {"type": "counter", "prefix": "OUI !", "fmt": "none", "t0": 15.6, "size": 1.1,
                            "keys": [K(0, v=0, glow="warm")]}],
                   "keys": [K(0, visible=False, x=240, ground=G, dir=1, pose="hold", face="worried", scale=0.85),
                            K(13.6, visible=True), K(14.6, x=560, ease="out"), K(14.8, pose="knock"),
                            K(15.4, pose="present", face="surprised"), K(15.9, face="laugh", pose="cheer")]}},
    props=props(
        ("dossier", {"type": "letter", "keys": [K(0, attach="elle.hands", dy=6), K(12.8, visible=False)]}),
        ("dossier2", {"type": "letter", "size": 0.8,
                      "keys": [K(0, visible=False, attach="petite.hand_l", dy=6), K(13.6, visible=True)]}),
        bubble("b1", "banquier", "NON.", 1.4, 2.5, tail=-1),
        bubble("b2", "banquier", "NON. NEXT.", 3.5, 4.8, tail=-1),
        bubble("b3", "banquier", "HAHA... NON.", 5.6, 7.1, tail=-1),
        bubble("b4", "banquier", "NON.", 8.0, 9.4, tail=-1),
        bubble("b5", "mamie", "OUI.", 10.4, 12.7, tail=-1, font=54),
        bubble("b6", "elle", "OUI.", 15.5, 17.4, tail=-1, font=54)),
    camera=[K(0, cx=640, cy=1040, zoom=1.25), K(9.4, cx=660, cy=1060, zoom=1.35),
            K(10.4, cx=680, cy=1080, zoom=1.45), K(12.8, cx=660, cy=1050, zoom=1.25),
            K(13.6, cx=600, cy=1040, zoom=1.2, cut=True), K(16.0, cx=640, cy=1050, zoom=1.3)],
    texts=[hook([("ON LUI A DIT NON", 92), ("99 FOIS.", 120)]),
           {"text": "10 ANS PLUS TARD", "size": 84, "y": 470, "t0": 12.85, "write": 0.4, "t1": 14.6, "fade": 0.2},
           moral("IL SUFFIT D'UN OUI.", "DEVIENS-LE.", 17.2)],
    sfx=[K(10.6, type="pop", volume=0.4), K(15.6, type="pop", volume=0.4)] +
        [K(t, type="wood", volume=0.5) for t in (0.95, 1.15, 14.85, 15.05)]))

# --------------------------------------------------------------------------- 3
S.append(story(
    "03-le-volume", 17.8, 10.4,
    _legende="Elle a eu l'idée. Il a eu les applaudissements. Jusqu'à ce qu'une collègue monte le son 🔊 #femmes #travail #stickman",
    set=[{"type": "ground", "y": G}, {"type": "desk", "x": 560, "w": 560, "h": 110},
         {"type": "burst", "x": 400, "y": 860, "t0": 11.5}],
    actors={
        "elle": {"hair": "long", "extras": ["skirt"],
                 "hud": [{"type": "bars", "label": "SA VOIX", "warn": 1.5,
                          "keys": [K(0, v=5), K(2.5, v=5), K(2.7, v=4), K(5.0, v=4), K(5.2, v=3), K(7.3, v=3),
                                   K(7.5, v=2), K(8.2, v=1), K(11.4, v=1), K(12.0, v=5),
                                   K(11.6, glow="warm"), K(13.5, glow=None)]}],
                 "keys": [K(0, x=400, ground=G, dir=1, pose="stand", face="smile"), K(1.0, pose="wave"),
                          K(2.3, pose="stand", face="sad"), K(3.9, pose="present", face="smile"),
                          K(5.0, pose="stand", face="sad"), K(7.6, pose="sad", face="sad"), K(9.0, face="cry"),
                          K(11.3, pose="look_up", face="surprised"), K(12.0, pose="stand", face="happy")]},
        "chef": {"hair": "none", "extras": ["tie"],
                 "keys": [K(0, x=720, ground=G, dir=-1, pose="stand", face="neutral"), K(2.0, pose="point", face="angry"),
                          K(3.0, pose="stand"), K(6.3, pose="present", face="happy"), K(8.4, pose="cheer", face="laugh"),
                          K(10.0, pose="stand"), K(11.1, face="surprised"), K(12.4, face="worried", pose="sad")]},
        "collegue": {"hair": "cap", "extras": ["tie"],
                     "keys": [K(0, x=860, ground=G, dir=-1, pose="stand", face="neutral"), K(4.6, pose="point", face="angry"),
                              K(5.6, pose="stand"), K(7.4, pose="cheer", face="laugh"), K(9.6, pose="stand"),
                              K(11.2, face="surprised")]},
        "allie": {"hair": "curly", "extras": ["skirt", "glasses"],
                  "hud": [{"type": "bars", "label": "", "t0": 11.4, "keys": [K(0, v=5)]}],
                  "keys": [K(0, x=225, ground=G, dir=1, pose="stand", face="neutral"), K(9.2, face="angry"),
                           K(10.4, pose="point", face="angry"), K(12.2, pose="stand", face="happy")]}},
    props=props(
        bubble("b1", "elle", "J'AI UNE IDÉE...", 1.0, 2.2, dy=-185),
        bubble("b2", "chef", "ATTENDS.", 2.0, 3.1, tail=-1),
        bubble("b3", "elle", "ET SI ON...", 3.9, 4.8, dy=-185),
        bubble("b4", "collegue", "PAS MAINTENANT.", 4.6, 5.7, tail=-1),
        bubble("b5", "chef", "J'AI UNE IDÉE GÉNIALE !", 6.3, 7.8, tail=-1),
        bubble("b6", "collegue", "BRAVO CHEF !", 7.5, 8.8, tail=-1),
        bubble("b7", "allie", "C'ÉTAIT SON IDÉE.", 10.4, 12.6, font=36, dy=-60)),
    camera=[K(0, cx=620, cy=1040, zoom=1.35), K(7.8, cx=620, cy=1040, zoom=1.35),
            K(9.6, cx=420, cy=1080, zoom=1.9), K(10.1, cx=420, cy=1080, zoom=1.9),
            K(10.6, cx=520, cy=1050, zoom=1.15, ease="out"), K(13.2, cx=520, cy=1030, zoom=1.15)],
    texts=[hook([("À CHAQUE RÉUNION,", 88), ("SA VOIX BAISSE D'UN CRAN.", 84)], t1=2.4),
           moral("QUAND UNE FEMME PARLE,", "MONTE LE SON.", 14.0)],
    sfx=[K(10.5, type="whoosh", volume=0.4), K(11.5, type="pop", volume=0.4)]))

# --------------------------------------------------------------------------- 4
trees = [{"type": "tree", "x": x, "h": 330} for x in range(-300, 5200, 1150)]
S.append(story(
    "04-le-chrono", 19.2, 12.4,
    _legende="Ils se moquaient de mamie. Regarde qui est arrivée en premier 🏃‍♀️ #mamie #motivation #stickman #running",
    set=[{"type": "ground", "y": G, "x0": -3000, "x1": 9000}] + trees +
        [{"type": "sign", "x": 4200, "h": 360, "w": 330, "text": "ARRIVÉE", "tape": True},
         {"type": "burst", "x": 4200, "y": 980, "t0": 13.6, "r": 220}],
    actors={
        "mamie": {"hair": "headband", "extras": ["glasses", "skirt"],
                  "hud": [{"type": "counter", "fmt": "time", "label": "SEMAINE 1", "t1": 8.95,
                           "keys": [K(0, v=1440), K(3.3, label="SEMAINE 8", v=1170, cut=True),
                                    K(6.6, label="SEMAINE 20", v=910, cut=True)]},
                          {"type": "counter", "label": "MARATHON", "suffix": " KM", "t0": 9.0,
                           "keys": [K(9.0, v=37), K(13.6, v=42, ease="linear"), K(13.6, glow="warm")]}],
                  "keys": [K(0, x=200, ground=G, dir=1, pose="run", face="worried"), K(3.25, x=560, ease="linear"),
                           K(3.3, x=900, face="neutral", cut=True), K(4.9, x=1150, ease="linear"),
                           K(5.05, pose="kneel", face="cry", x=1170, ease="out"), K(5.9, face="angry"),
                           K(6.3, pose="run", x=1170), K(6.55, x=1240, ease="in"),
                           K(6.6, x=1800, face="angry", cut=True), K(8.95, x=2450, ease="linear"),
                           K(9.0, x=3000, face="neutral", cut=True), K(13.6, x=4300, ease="linear"),
                           K(13.8, pose="cheer", face="laugh"), K(14.0, x=4340, ease="out")]},
        "jeune1": {"hair": "cap",
                   "keys": [K(0, x=-100, ground=G, dir=1, pose="run", face="laugh"), K(2.6, x=1100, ease="linear"),
                            K(3.3, x=600, cut=True, pose="run"), K(4.6, x=1500, ease="linear"),
                            K(9.0, x=3350, pose="sad", face="sad", cut=True), K(12.0, x=3900, ease="linear"),
                            K(12.5, x=3950), K(14.2, x=4080, pose="cheer", face="happy")]},
        "jeune2": {"hair": "beanie",
                   "keys": [K(0, x=-250, ground=G, dir=1, pose="run", face="laugh"), K(2.8, x=1000, ease="linear"),
                            K(3.3, x=480, cut=True, pose="run"), K(4.8, x=1450, ease="linear"),
                            K(9.0, x=3250, pose="sad", face="worried", cut=True), K(12.0, x=3800, ease="linear"),
                            K(12.5, x=3840), K(14.2, x=3960, pose="cheer", face="happy")]}},
    props=props(
        bubble("b1", "jeune1", "ALLEZ MAMIE ! HAHA", 1.1, 2.4, tail=-1),
        bubble("b2", "jeune2", "T'ES TROP LENTE !", 3.6, 4.7, tail=-1)),
    camera=[K(0, cx=380, cy=1060, zoom=1.15), K(3.25, cx=640, cy=1060, zoom=1.15, ease="linear"),
            K(3.3, cx=1000, cy=1060, zoom=1.15, cut=True), K(5.0, cx=1180, cy=1080, zoom=1.3),
            K(6.55, cx=1240, cy=1080, zoom=1.3),
            K(6.6, cx=1900, cy=1060, zoom=1.15, cut=True), K(8.95, cx=2500, cy=1060, zoom=1.15, ease="linear"),
            K(9.0, cx=3150, cy=1060, zoom=1.15, cut=True), K(13.6, cx=4150, cy=1040, zoom=1.05, ease="linear"),
            K(14.6, cx=4180, cy=1020, zoom=1.0)],
    texts=[hook([("ELLE A COMMENCÉ À COURIR", 84), ("À 64 ANS.", 116)]),
           moral("IL N'EST JAMAIS TROP TARD", "POUR COMMENCER.", 15.3)],
    sfx=[K(5.05, type="thud", volume=0.6), K(13.6, type="pop", volume=0.5)]))

# --------------------------------------------------------------------------- 5
S.append(story(
    "05-la-peur", 17.6, 11.4,
    _legende="Sa peur était à 100 %. Elle a sauté quand même 💥 #courage #ado #stickman #animation",
    set=[{"type": "ground", "y": G, "x0": -1500, "x1": 300},
         {"type": "tower", "x": 250, "top": 720, "w": 80, "board": 170, "side": 1},
         {"type": "burst", "x": 395, "y": 430, "t0": 11.35, "r": 160},
         {"type": "burst", "x": 520, "y": 1320, "t0": 11.95, "r": 180, "glow": False}],
    actors={
        "ado": {"hair": "ponytail",
                "hud": [{"type": "gauge", "label": "PEUR", "fmt": "pct", "t1": 11.3,
                         "keys": [K(0, v=100), K(2.85, v=100), K(2.9, v=90, cut=True), K(5.3, v=70, cut=True),
                                  K(7.7, v=40, cut=True), K(10.2, v=12), K(0.01, glow=None)]}],
                "keys": [K(0, x=380, ground=720, dir=1, pose="shiver", face="worried"),
                         K(1.8, face="cry"), K(2.2, dir=-1, pose="sad"), K(2.85, x=300, ease="out"),
                         K(2.9, x=330, dir=1, pose="shiver", face="worried", cut=True), K(4.2, x=375, ease="inout"),
                         K(4.7, dir=-1, pose="sad"),
                         K(5.3, x=360, dir=1, pose="shiver", face="worried", cut=True), K(6.5, x=395, ease="inout"),
                         K(7.1, dir=-1),
                         K(7.7, x=395, dir=1, pose="stand", face="worried", cut=True), K(9.6, face="closed"),
                         K(10.6, pose="cheer", face="closed"), K(11.2, pose="dive", face="closed"),
                         K(11.25, x=395, ground=720), K(11.9, x=520, ground=1500, ease="in"),
                         K(12.4, x=520, ground=1440, pose="cheer", face="laugh", cut=True)]},
        "amie1": {"hair": "curly", "keys": [K(0, x=700, ground=1440, dir=-1, pose="stand", face="smile"),
                                            K(7.8, pose="wave", face="happy"), K(12.3, pose="cheer", face="laugh")]},
        "amie2": {"hair": "bow", "keys": [K(0, x=880, ground=1440, dir=-1, pose="stand", face="neutral"),
                                          K(8.6, pose="wave", face="happy"), K(12.3, pose="cheer", face="laugh")]}},
    props=props(
        ("eau", {"type": "water", "w": 1900, "keys": [K(0, x=900, y=1320)]}),
        bubble("b1", "amie1", "VAS-Y !", 8.0, 9.6, tail=-1),
        bubble("b2", "amie2", "ON EST LÀ !", 8.8, 10.4, tail=-1)),
    camera=[K(0, cx=470, cy=640, zoom=1.2), K(2.85, cx=470, cy=640, zoom=1.2),
            K(2.9, cx=460, cy=650, zoom=1.15, cut=True), K(5.25, cx=460, cy=650, zoom=1.15),
            K(5.3, cx=470, cy=630, zoom=1.3, cut=True), K(7.65, cx=470, cy=630, zoom=1.3),
            K(7.7, cx=560, cy=1000, zoom=0.95, cut=True), K(9.4, cx=560, cy=1000, zoom=0.95),
            K(10.6, cx=420, cy=780, zoom=1.9), K(11.2, cx=420, cy=780, zoom=1.9),
            K(11.9, cx=600, cy=1050, zoom=1.0, ease="out"), K(13.0, cx=680, cy=1020, zoom=1.2)],
    texts=[hook([("SA PEUR ÉTAIT À 100 %.", 90), ("REGARDE CE QU'ELLE A FAIT.", 76)], t1=2.4),
           tag("ESSAI 1", 0.05, 2.85, y=470), tag("ESSAI 5", 2.9, 5.25), tag("ESSAI 9", 5.3, 7.65),
           tag("ESSAI 12", 7.7, 10.4),
           moral("LE COURAGE, CE N'EST PAS", "DE NE PAS AVOIR PEUR.", 13.4)],
    sfx=[K(11.35, type="pop", volume=0.5), K(11.3, type="whoosh", volume=0.5), K(11.9, type="drop", volume=0.6)]))

# --------------------------------------------------------------------------- 6
S.append(story(
    "06-les-credits", 19.8, 13.0,
    _legende="4 000 vies sauvées. 0 merci. Jusqu'à ce soir-là 🤍 #infirmière #soignante #stickman #merci",
    set=[{"type": "ground", "y": G, "x0": -1500, "x1": 4000}, {"type": "bed", "x": 680, "w": 330},
         {"type": "window", "x": 930, "y": 860, "w": 180, "h": 170, "moon": True},
         {"type": "bench", "x": 1500, "w": 240}, {"type": "lamp", "x": 2250, "h": 470, "side": 1},
         {"type": "house", "x": 2900, "w": 300, "h": 260, "label": "CHEZ ELLE", "light": True},
         {"type": "burst", "x": 2620, "y": 820, "t0": 13.0, "r": 180}],
    rain={"t0": 8.4, "t1": 12.5, "density": 0.9, "volume": 0.14},
    actors={
        "inf": {"hair": "nurse", "extras": ["skirt"],
                "hud": [{"type": "counter", "label": "VIES SAUVÉES", "dy": 75,
                         "keys": [K(0, v=1), K(2.9, v=1), K(3.0, v=120, cut=True), K(5.5, v=900),
                                  K(5.6, v=2300, cut=True), K(8.3, v=4000), K(14, v=4000)]},
                        {"type": "counter", "label": "MERCI", "dy": 200, "warn": 0.5,
                         "keys": [K(0, v=0), K(13.0, v=0), K(15.0, v=9999, ease="in"), K(13.0, glow="warm")]}],
                "keys": [K(0, x=470, ground=G, dir=1, pose="reach", face="worried"), K(1.8, pose="stand", face="smile"),
                         K(3.0, x=-150, pose="run", face="worried", cut=True), K(5.5, x=1150, ease="linear"),
                         K(5.6, x=1540, pose="sit_sad", face="sad", cut=True), K(7.4, face="closed"),
                         K(8.4, x=1900, pose="sad", face="sad", cut=True), K(12.0, x=2560, ease="linear"),
                         K(12.4, face="surprised", pose="stand"), K(13.1, face="cry"), K(14.0, face="happy")]},
        "patient": {"hair": "cap", "keys": [K(0, x=715, ground=G - 70, dir=1, pose="lie", face="closed"),
                                            K(2.9, visible=False),
                                            K(11.0, visible=True, x=2760, ground=G, dir=-1, pose="stand", face="smile",
                                              cut=True), K(12.8, pose="present", face="happy")]},
        "epouse": {"hair": "long", "extras": ["skirt"],
                   "keys": [K(0, visible=False, x=2900, ground=G, dir=-1, pose="hold", face="happy"),
                            K(11.0, visible=True), K(13.4, pose="cheer")]},
        "gamin": {"hair": "cowlick",
                  "keys": [K(0, visible=False, x=2840, ground=G, dir=-1, pose="stand", face="happy", scale=0.55),
                           K(11.0, visible=True), K(13.2, pose="cheer", face="laugh")]}},
    props=props(
        ("trousse", {"type": "box", "size": 0.55, "keys": [K(0, visible=False, attach="inf.hand_r", dy=40),
                                                           K(3.0, visible=True), K(5.6, visible=False)]}),
        ("fleur", {"type": "flower", "shine": True, "keys": [K(0, visible=False, attach="epouse.hands", shine=True),
                                                             K(11.0, visible=True)]}),
        ("c1", {"type": "heart", "size": 0.8, "keys": [K(0, visible=False, x=2600, y=900), K(13.2, visible=True),
                                                       K(15.2, y=500)]}),
        ("c2", {"type": "heart", "size": 0.6, "keys": [K(0, visible=False, x=2720, y=950), K(13.5, visible=True),
                                                       K(15.5, y=560)]}),
        bubble("b1", "patient", "MERCI.", 12.8, 14.8, tail=-1, font=52)),
    camera=[K(0, cx=560, cy=1060, zoom=1.35), K(2.95, cx=560, cy=1060, zoom=1.35),
            K(3.0, cx=300, cy=1040, zoom=1.1, cut=True), K(5.5, cx=900, cy=1040, zoom=1.1, ease="linear"),
            K(5.6, cx=1520, cy=1080, zoom=1.45, cut=True), K(8.35, cx=1520, cy=1080, zoom=1.55),
            K(8.4, cx=2000, cy=1040, zoom=1.1, cut=True), K(11.0, cx=2500, cy=1050, zoom=1.1, ease="linear"),
            K(12.6, cx=2700, cy=1060, zoom=1.2), K(14.5, cx=2700, cy=1020, zoom=1.05)],
    texts=[hook([("ELLE A SAUVÉ 4 000 VIES.", 86), ("PERSONNE NE CONNAÎT SON NOM.", 72)]),
           moral("ELLES SAUVENT DES VIES EN SILENCE.", "DIS-LEUR MERCI.", 15.6)],
    sfx=[K(12.8, type="heart", volume=0.6), K(13.0, type="pop", volume=0.4)]))

# --------------------------------------------------------------------------- 7
S.append(story(
    "07-la-taille", 18.4, 9.6,
    _legende="Chaque remarque la faisait rapetisser. Jusqu'au jour où elle a décidé de sa taille 🎧 #confiance #ado #stickman #harcèlement",
    set=[{"type": "ground", "y": G, "x0": -1500, "x1": 5000},
         {"type": "house", "x": 960, "w": 300, "h": 280, "label": "COLLÈGE"},
         {"type": "window", "x": 2380, "y": 820, "w": 200, "h": 190, "moon": True},
         {"type": "burst", "x": 2540, "y": 1100, "t0": 9.6, "r": 120}],
    actors={
        "elle": {"hair": "bow", "extras": ["skirt"],
                 "hud": [{"type": "gauge", "label": "CONFIANCE", "fmt": "pct", "warn": 12,
                          "keys": [K(0, v=100), K(1.9, v=100), K(2.3, v=62), K(4.2, v=62), K(4.6, v=31), K(6.4, v=31),
                                   K(6.8, v=7), K(9.6, v=7), K(13.4, v=100, ease="in"), K(10.0, glow="warm")]}],
                 "keys": [K(0, x=220, ground=G, dir=1, pose="stand", face="smile", scale=1.0),
                          K(1.4, x=470, ease="out"), K(1.9, face="surprised"),
                          K(2.4, scale=0.72, face="sad", ease="out"), K(4.6, scale=0.48, ease="out", pose="sad"),
                          K(6.8, scale=0.27, ease="out", face="cry"), K(7.4, dir=-1), K(8.0, x=200, ease="in"),
                          K(8.1, x=2520, dir=1, pose="hug_knees", face="sad", cut=True),
                          K(9.4, pose="stand", face="surprised"), K(9.9, pose="dance", face="closed"),
                          K(10.5, scale=0.3), K(13.6, scale=4.2, ease="in"), K(12.2, face="laugh")]},
        "moq1": {"hair": "cap",
                 "keys": [K(0, x=700, ground=G, dir=-1, pose="stand", face="laugh"), K(1.2, pose="point"),
                          K(2.6, pose="stand"), K(6.2, pose="point"), K(7.4, pose="stand"), K(8.1, visible=False)]},
        "moq2": {"hair": "beanie",
                 "keys": [K(0, x=840, ground=G, dir=-1, pose="stand", face="laugh"), K(3.4, pose="point"),
                          K(4.8, pose="cheer"), K(8.1, visible=False)]}},
    props=props(
        bubble("b1", "moq1", "TROP GROSSE.", 1.2, 2.6, tail=-1),
        bubble("b2", "moq2", "T'ES BIZARRE.", 3.4, 4.9, tail=-1),
        bubble("b3", "moq1", "PERSONNE T'AIME.", 5.8, 7.4, tail=-1),
        ("casque", {"type": "headphones", "keys": [K(0, visible=False, x=2600, y=G - 10, rot=0),
                                                   K(8.1, visible=True), K(9.5, attach="elle.head", dy=0)]})),
    camera=[K(0, cx=560, cy=1060, zoom=1.2), K(6.0, cx=500, cy=1100, zoom=1.35), K(8.05, cx=480, cy=1140, zoom=1.6),
            K(8.1, cx=2530, cy=1200, zoom=2.4, cut=True), K(9.6, cx=2530, cy=1200, zoom=2.3),
            K(12.4, cx=2540, cy=1000, zoom=1.0), K(13.7, cx=2540, cy=900, zoom=0.9),
            K(14.6, cx=2560, cy=380, zoom=0.42, ease="out")],
    texts=[hook([("À CHAQUE REMARQUE,", 92), ("ELLE RAPETISSE.", 110)], t1=2.2),
           moral("TA TAILLE,", "C'EST TOI QUI LA DÉCIDES.", 14.6)],
    sfx=[K(2.3, type="drop", volume=0.3), K(4.6, type="drop", volume=0.3), K(6.8, type="drop", volume=0.3),
         K(9.6, type="pop", volume=0.4)]))

# --------------------------------------------------------------------------- 8
S.append(story(
    "08-le-salaire", 18.6, 12.0,
    _legende="Même travail. Pas le même chiffre. Alors elle est allée le demander 💼 #salaire #égalité #femme #stickman",
    set=[{"type": "ground", "y": G, "x0": -1500, "x1": 4000},
         {"type": "desk", "x": 420, "w": 200}, {"type": "bench", "x": 300, "w": 110},
         {"type": "desk", "x": 760, "w": 200}, {"type": "bench", "x": 640, "w": 110},
         {"type": "house", "x": 1700, "w": 300, "h": 270, "label": "DIRECTION"},
         {"type": "burst", "x": 1560, "y": 860, "t0": 11.9, "r": 170}],
    actors={
        "elle": {"hair": "long", "extras": ["skirt"],
                 "hud": [{"type": "counter", "fmt": "euro",
                          "keys": [K(0, v=2000), K(2.8, v=2000), K(3.4, v=2100), K(5.6, v=2100), K(6.2, v=2150),
                                   K(11.9, v=2150), K(12.6, v=2750, ease="out"), K(11.9, glow="warm"),
                                   K(14.5, glow=None)]}],
                 "keys": [K(0, x=300, ground=G, dir=1, pose="sit_type", face="neutral"),
                          K(7.0, face="surprised", pose="sit_look_up"), K(7.9, face="angry"),
                          K(8.6, x=300, pose="stand", face="angry"), K(10.6, x=1530, ease="inout"),
                          K(10.8, pose="present"), K(11.9, face="happy", pose="cheer"),
                          K(13.0, x=300, pose="sit_type", face="smile", cut=True)]},
        "lui": {"hair": "none", "extras": ["tie"],
                "hud": [{"type": "counter", "fmt": "euro",
                         "keys": [K(0, v=2000), K(2.8, v=2000), K(3.4, v=2300), K(5.6, v=2300), K(6.2, v=2600)]}],
                "keys": [K(0, x=640, ground=G, dir=1, pose="sit_type", face="neutral"), K(6.4, face="smile"),
                         K(13.4, pose="sit_look_up", face="surprised")]},
        "boss": {"hair": "curly", "extras": ["glasses", "skirt"],
                 "keys": [K(0, visible=False, x=1680, ground=G, dir=-1, pose="stand", face="neutral"),
                          K(10.0, visible=True), K(11.0, pose="hold", face="surprised"), K(11.7, face="smile"),
                          K(12.9, visible=False)]}},
    props=props(
        ("ordi1", {"type": "laptop", "keys": [K(0, x=430, y=G - 105, glow=True)]}),
        ("ordi2", {"type": "laptop", "keys": [K(0, x=770, y=G - 105, glow=True)]}),
        ("dossier", {"type": "letter", "keys": [K(0, visible=False, attach="elle.hands", dy=4), K(8.6, visible=True),
                                                K(11.1, attach="boss.hands"), K(12.9, visible=False)]}),
        bubble("b1", "elle", "MES RÉSULTATS.", 10.8, 12.0)),
    camera=[K(0, cx=540, cy=1040, zoom=1.25), K(6.6, cx=540, cy=1040, zoom=1.25), K(7.6, cx=520, cy=1000, zoom=1.5),
            K(8.4, cx=520, cy=1000, zoom=1.5), K(9.4, cx=1000, cy=1040, zoom=1.1),
            K(10.6, cx=1600, cy=1060, zoom=1.35), K(12.95, cx=1600, cy=1060, zoom=1.35),
            K(13.0, cx=540, cy=1040, zoom=1.25, cut=True)],
    texts=[hook([("MÊME BUREAU. MÊME TRAVAIL.", 82), ("REGARDE LES CHIFFRES.", 96)]),
           tag("MOIS 1", 0.05, 2.8, y=470), tag("MOIS 6", 2.85, 5.6), tag("MOIS 12", 5.65, 8.6),
           moral("ÇA NE S'OFFRE PAS.", "ÇA SE DEMANDE.", 14.6)],
    sfx=[K(11.9, type="pop", volume=0.5)]))

# --------------------------------------------------------------------------- 9
liste = ["VOIR LA MER", "ÉCRIRE UN LIVRE", "DANSER SOUS LA PLUIE", "ÊTRE FIÈRE DE MOI"]
S.append(story(
    "09-les-annees", 21.4, 10.6,
    _legende="Elle a écrit sa liste à 20 ans. Elle l'a finie à 80 📜 #rêves #mamie #stickman #inspiration",
    set=[{"type": "ground", "y": G, "x0": -1500, "x1": 3000},
         {"type": "desk", "x": 520, "w": 220}, {"type": "bench", "x": 380, "w": 110},
         {"type": "bench", "x": 1500, "w": 240},
         {"type": "burst", "x": 2380, "y": 820, "t0": 12.6}, {"type": "burst", "x": 640, "y": 780, "t0": 14.6},
         {"type": "burst", "x": 1180, "y": 800, "t0": 16.7}, {"type": "burst", "x": 1640, "y": 760, "t0": 18.3, "r": 200}],
    rain={"t0": 15.2, "t1": 17.1, "density": 0.9, "volume": 0.12},
    actors={
        "jeune": {"hair": "long", "extras": ["skirt"],
                  "hud": [{"type": "counter", "label": "ÂGE", "keys": [K(0, v=20), K(2.7, v=32, cut=True),
                                                                      K(5.0, v=50, cut=True)]}],
                  "keys": [K(0, x=380, ground=G, dir=1, pose="sit_type", face="happy"),
                           K(2.7, x=300, pose="walk", face="smile", cut=True), K(4.9, x=640, ease="linear"),
                           K(5.0, x=380, pose="sit_type", face="sad", cut=True), K(7.3, visible=False)]},
        "petit": {"hair": "cowlick",
                  "keys": [K(0, visible=False, x=380, ground=G, dir=1, pose="reach", face="happy", scale=0.5),
                           K(2.7, visible=True, cut=True), K(4.9, x=720, ease="linear"), K(5.0, visible=False)]},
        "vieille": {"hair": "long", "extras": ["skirt", "glasses"],
                    "hud": [{"type": "counter", "label": "ÂGE",
                             "keys": [K(7.3, v=70), K(9.4, v=78, cut=True), K(17.5, v=78), K(17.6, v=80, cut=True),
                                      K(17.6, glow="warm")]}],
                    "keys": [K(0, visible=False, x=1520, ground=G, dir=1, pose="sit_sad", face="sad"),
                             K(7.3, visible=True), K(9.4, pose="sit_look_up", face="surprised", cut=True),
                             K(10.4, pose="sit_bench", face="happy"),
                             K(11.0, x=2200, pose="old", face="happy", cut=True), K(12.4, x=2300, ease="out"),
                             K(12.6, pose="cheer", face="laugh"),
                             K(13.4, x=520, pose="sit_type", face="closed", cut=True),
                             K(15.2, x=1100, pose="dance", face="laugh", cut=True),
                             K(17.2, x=1520, pose="sit_bench", face="closed", cut=True), K(18.3, face="happy")]}},
    props=props(
        ("liste", {"type": "list", "items": liste, "title": "MA LISTE", "size": 0.8,
                   "keys": [K(0, x=700, y=1070, done=0), K(2.7, visible=False),
                            K(9.4, visible=True, x=1700, y=1080, cut=True),
                            K(11.0, x=2480, y=1090, cut=True), K(12.6, done=1, cut=True),
                            K(13.4, x=760, y=1050, cut=True), K(14.6, done=2, cut=True),
                            K(15.2, x=1300, y=1040, cut=True), K(16.7, done=3, cut=True),
                            K(17.2, x=1720, y=1080, cut=True), K(18.3, done=4, cut=True)]}),
        ("ordi", {"type": "laptop", "keys": [K(0, visible=False, x=540, y=G - 105, glow=True), K(5.0, visible=True),
                                             K(7.3, visible=False)]}),
        ("boite", {"type": "box", "size": 0.6, "keys": [K(0, visible=False, x=1690, y=G), K(7.3, visible=True),
                                                        K(9.4, visible=False)]}),
        ("mer", {"type": "water", "w": 1200, "keys": [K(0, visible=False, x=2900, y=G + 2), K(11.0, visible=True),
                                                      K(13.4, visible=False)]}),
        ("livre", {"type": "book", "keys": [K(0, visible=False, x=540, y=G - 105), K(13.4, visible=True),
                                            K(15.2, visible=False)]})),
    camera=[K(0, cx=540, cy=1040, zoom=1.3), K(2.65, cx=540, cy=1040, zoom=1.3),
            K(2.7, cx=480, cy=1060, zoom=1.2, cut=True), K(4.95, cx=560, cy=1060, zoom=1.2),
            K(5.0, cx=480, cy=1060, zoom=1.35, cut=True), K(7.25, cx=480, cy=1060, zoom=1.35),
            K(7.3, cx=1560, cy=1080, zoom=1.4, cut=True), K(10.95, cx=1600, cy=1070, zoom=1.45),
            K(11.0, cx=2400, cy=1060, zoom=1.2, cut=True), K(13.35, cx=2400, cy=1060, zoom=1.2),
            K(13.4, cx=620, cy=1040, zoom=1.3, cut=True), K(15.15, cx=620, cy=1040, zoom=1.3),
            K(15.2, cx=1180, cy=1040, zoom=1.25, cut=True), K(17.15, cx=1180, cy=1040, zoom=1.25),
            K(17.2, cx=1600, cy=1060, zoom=1.35, cut=True), K(18.6, cx=1600, cy=1020, zoom=1.15)],
    texts=[hook([("À 80 ANS, ELLE A RAYÉ", 88), ("LE DERNIER RÊVE DE SA LISTE.", 76)]),
           moral("TES RÊVES N'ONT PAS", "DE DATE LIMITE.", 18.8)],
    sfx=[K(12.6, type="pop", volume=0.35), K(14.6, type="pop", volume=0.35), K(16.7, type="pop", volume=0.35),
         K(18.3, type="heart", volume=0.6)]))

# --------------------------------------------------------------------------- 10
cercle = {}
import math as _m
for i in range(10):
    a = i / 10 * 2 * _m.pi
    hairs = ["long", "curly", "ponytail", "bow", "beanie", "cap", "long", "curly", "ponytail", "headband"]
    back = _m.sin(a) < 0
    cercle[f"f{i}"] = {"hair": hairs[i], "extras": ["skirt"] + (["glasses"] if i % 3 == 0 else []),
                       "keys": [K(0, visible=False, x=540 + 390 * _m.cos(a), ground=G - (60 if back else 0) + 40 * _m.sin(a),
                                  dir=1 if _m.cos(a) < 0 else -1, pose="reach", face="happy",
                                  scale=0.82 if back else 0.95), K(12.3, visible=True), K(13.8, pose="cheer", face="laugh")]}
S.append(story(
    "10-le-cercle", 19.4, 12.3,
    _legende="Une femme en a aidé une autre. Compte jusqu'à la fin ⭕ #femmes #sororité #stickman #entraide",
    set=[{"type": "ground", "y": G, "x0": -1500, "x1": 9000},
         {"type": "bench", "x": 600, "w": 250}, {"type": "lamp", "x": 2900, "h": 470},
         {"type": "burst", "x": 540, "y": 900, "t0": 12.3, "r": 260}],
    rain={"t0": 4.95, "t1": 7.4, "density": 0.9, "volume": 0.12},
    actors=dict(**{
        "m1": {"hair": "ponytail", "extras": ["skirt"],
               "hud": [{"type": "counter", "label": "FEMMES", "size": 1.1,
                        "keys": [K(0, v=1), K(12.3, v=6), K(14.6, v=1000000, ease="in"), K(12.3, glow="warm")]}],
               "keys": [K(0, x=260, ground=G, dir=1, pose="walk", face="smile"), K(1.2, x=520, ease="out"),
                        K(1.4, pose="reach"), K(2.5, visible=False),
                        K(12.3, visible=True, x=540, pose="cheer", face="laugh", cut=True)]},
        "etu": {"hair": "long", "extras": ["glasses", "skirt"],
                "hud": [{"type": "counter", "label": "FEMMES", "size": 1.0, "t0": 2.5, "t1": 4.9,
                         "keys": [K(0, v=2)]}],
                "keys": [K(0, x=660, ground=G, dir=-1, pose="sit_sad", face="cry"), K(1.6, face="surprised"),
                         K(2.1, face="happy", pose="sit_look_up"),
                         K(2.5, x=1500, dir=1, pose="carry", face="smile", cut=True), K(4.8, x=1950, ease="linear"),
                         K(4.9, visible=False)]},
        "vieille": {"hair": "curly", "extras": ["glasses", "skirt"],
                    "hud": [{"type": "counter", "label": "FEMMES", "size": 1.0, "t0": 4.95, "t1": 7.35,
                             "keys": [K(0, v=3)]}],
                    "keys": [K(0, x=1640, ground=G, dir=1, pose="old", face="smile"), K(4.8, x=2100, ease="linear"),
                             K(4.95, x=2700, dir=1, pose="umbrella", face="smile", cut=True), K(7.35, visible=False)]},
        "ado": {"hair": "bow", "extras": ["skirt"],
                "hud": [{"type": "counter", "label": "FEMMES", "size": 1.0, "t0": 7.4, "t1": 9.8, "keys": [K(0, v=4)]}],
                "keys": [K(0, x=2870, ground=G, dir=-1, pose="sad", face="sad", scale=0.85), K(6.2, face="happy",
                                                                                              pose="look_up"),
                         K(7.4, x=4500, dir=1, pose="hold", face="smile", cut=True), K(9.8, visible=False)]},
        "maman2": {"hair": "long", "extras": ["skirt"],
                   "hud": [{"type": "counter", "label": "FEMMES", "size": 1.0, "t0": 9.85, "t1": 12.25,
                            "keys": [K(0, v=5)]}],
                   "keys": [K(0, x=4680, ground=G, dir=-1, pose="sit_sad", face="sad"), K(8.6, face="surprised"),
                            K(9.1, face="happy"),
                            K(9.85, x=6200, dir=1, pose="kneel", face="smile", cut=True), K(10.6, pose="reach"),
                            K(12.25, visible=False)]},
        "fillette": {"hair": "ponytail",
                     "keys": [K(0, x=6380, ground=G, dir=-1, pose="hug_knees", face="cry", scale=0.55),
                              K(10.8, pose="stand", face="happy"), K(12.25, visible=False)]}}, **cercle),
    props=props(
        ("carton", {"type": "box", "size": 0.8, "keys": [K(0, visible=False, attach="etu.hands", dy=50),
                                                         K(2.5, visible=True), K(4.9, visible=False)]}),
        ("parapluie", {"type": "umbrella", "keys": [K(0, attach="vieille.hand_r", rot=0, visible=False),
                                                    K(4.95, visible=True), K(5.6, rot=0), K(6.2, rot=26),
                                                    K(7.35, visible=False)]}),
        ("bebe", {"type": "ball", "keys": [K(0, visible=False, attach="ado.hands", dy=30), K(7.4, visible=True),
                                           K(9.8, visible=False)]})),
    camera=[K(0, cx=520, cy=1060, zoom=1.35), K(2.45, cx=560, cy=1060, zoom=1.35),
            K(2.5, cx=1640, cy=1060, zoom=1.25, cut=True), K(4.9, cx=1880, cy=1060, zoom=1.25, ease="linear"),
            K(4.95, cx=2800, cy=1060, zoom=1.3, cut=True), K(7.35, cx=2800, cy=1060, zoom=1.3),
            K(7.4, cx=4600, cy=1060, zoom=1.35, cut=True), K(9.8, cx=4600, cy=1060, zoom=1.35),
            K(9.85, cx=6300, cy=1080, zoom=1.45, cut=True), K(12.25, cx=6300, cy=1080, zoom=1.45),
            K(12.3, cx=540, cy=1150, zoom=2.2, cut=True), K(13.6, cx=540, cy=1080, zoom=0.95, ease="out")],
    texts=[hook([("UNE FEMME EN A AIDÉ UNE AUTRE.", 74), ("COMPTE JUSQU'À LA FIN.", 92)], t1=2.4),
           moral("SEULE, ELLE AVANCE.", "ENSEMBLE, ELLES CHANGENT TOUT.", 15.0)],
    sfx=[K(t, type="pop", volume=0.3) for t in (2.5, 4.95, 7.4, 9.85)] + [K(12.3, type="heart", volume=0.6)]))

# ---- extras sur ado (scène 4 : elle garde le bébé de maman2) : rien d'autre
for name, d in S:
    with open(os.path.join(HERE, name + ".json"), "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print("écrit", name)
