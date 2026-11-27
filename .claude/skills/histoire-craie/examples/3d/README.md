# « La porte » en 3D (Blender)

Version 3D de `../la-porte.json`, même découpage (18,2 s).

```bash
apt-get install -y blender xvfb          # Blender 4.0
blender -b -P porte3d.py -- $PWD/frames  # construit la scène -> frames/porte3d.blend
xvfb-run -a blender -b frames/porte3d.blend -s 1 -e 546 -j 2 -a   # rendu Eevee 15 i/s (~10 s/image sur CPU)
python3 compose.py /usr/share/fonts/opentype/inter/Inter-ExtraBold.otf la_porte_3d.mp4  # textes + son
```

- Personnages « jouet » faits de primitives : pivots aux épaules, hanches et cou, poses dans `POSES`, expressions via la bouche et les sourcils.
- Caméra : liste `SHOTS` (temps, position, cible, coupe franche).
- Le Blender d'Ubuntu n'a pas OpenImageDenoise : Cycles demande ~40 s/image sans débruitage, d'où Eevee.
