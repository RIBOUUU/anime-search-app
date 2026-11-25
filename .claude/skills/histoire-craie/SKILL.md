---
name: histoire-craie
description: Créer un court-métrage vertical TikTok/Reels/Shorts « histoire à la craie » rendu en code — personnages en bâtons dessinés à la craie blanche sur tableau noir, histoire muette autour d'un objet-métaphore (relation, famille, amitié, temps qui passe), gros plans, une seule lumière colorée, morale écrite à la main à la fin. À utiliser pour une vidéo émotionnelle en stickman, « style craie », « tableau noir », animation de bonhommes bâtons avec une leçon de vie.
---

# Histoire à la craie — court-métrage muet avec une morale

Format : 25 à 40 s, aucun dialogue, une petite histoire visuelle entre 2 ou 3
personnages en bâtons, construite autour d'**un objet-métaphore**, qui se termine
par une **morale écrite à la craie**. L'objectif n'est pas le like mais le
**partage** (« c'est nous », « je pense à toi »). Le reel de référence a autant de
partages que d'enregistrements, et ça représente 37 % de ses likes.

Analyse détaillée du reel de référence : `references/analyse.md`.

⚠️ On reprend le **format** (craie, bonhommes bâtons, métaphore, morale), jamais
l'histoire, le titre ni les personnages d'un autre créateur. Chaque vidéo doit
avoir sa propre idée.

## Écrire l'histoire (le plus important)

Remplir cette grille avant de toucher au JSON :

1. **Vérité universelle** (la morale), en une phrase courte :
   « l'amour se construit des deux côtés », « un jour ce sera ton tour de tenir le parapluie ».
2. **Objet-métaphore** qu'on peut *manipuler* : planche, parapluie, ballon,
   lettre, lampe, cadeau, fleur, échelle, corde, bougie.
3. **Déséquilibre visible dès la 1re seconde** : l'un donne, l'autre ne voit pas
   (téléphone, dos tourné, distraction). Il doit se voir sur l'image d'accroche.
4. **Escalade** (3 à 4 répétitions de l'effort) : le spectateur voit ce que le
   personnage distrait ne voit pas.
5. **Bascule** : l'effort s'arrête (l'objet tombe, s'envole, s'éteint).
6. **Retournement** : prise de conscience, **trop tard** (émotion triste) ou
   **juste à temps / inversion des rôles** (émotion tendre).
7. **Morale** en 2 ou 3 lignes manuscrites, dernier mot-clé plus gros.

Structure temporelle (≈ 30 s) : accroche + titre (0–3 s) → mise en place (3–8 s)
→ escalade avec gros plans (8–18 s) → bascule (18–22 s) → retournement (22–26 s)
→ morale qui s'écrit (26–32 s).

Idées de métaphores à décliner : le ballon qu'un parent tient pour l'enfant et que
l'enfant lâche ; la lampe qu'on garde allumée pour quelqu'un qui ne rentre pas ;
l'échelle qu'on tient pendant que l'autre monte ; les lettres jamais envoyées ;
la place gardée sur le banc ; le cadeau emballé chaque année.

## Grammaire visuelle (déjà intégrée au moteur)

- Tableau noir anthracite, vignettage, poussière de craie qui flotte, trait blanc granuleux.
- **Une seule couleur** et elle porte le sens : lueur `cool` (écran de téléphone,
  froid, distraction) ou `warm` (lampadaire, bougie, chaleur, foyer).
- Un signe distinctif par personnage (`hair`, `extras`) pour le reconnaître, même
  après une ellipse (« des années plus tard » : garder le même signe).
- Plan large pour la situation, **gros plan (zoom 1,5 à 1,7) sur les visages**
  aux moments d'émotion.
- Titre court en haut au début, morale à la fin, texte écrit lettre par lettre.

## Fichier d'histoire (JSON)

Partir de `examples/le-parapluie.json`, une histoire complète de 33 s.

```
duration      durée totale (s)
music         {"mood": "sad"|"tender"|"hope", "bpm": 60-72, "turn": t, "volume": 0.6}
              -> piano généré ; "turn" = instant où il passe en majeur (le retournement)
audio         musique perso (mp3/wav) + "audio_start", "audio_volume" (remplace music)
rain          {"t0","t1","density","angle"} : pluie (bloquée par le sol et les parapluies)
sfx           [{"t", "type": thud|wood|whoosh|drop|pop|heart|tick, "volume"}]
set           décor : ground{y,depth}, cliff{x0,x1,top}, bench{x,w}, lamp{x,h,side},
              tree{x,h}, moon{x,y,r}, cloud{x,y,r}, house{x,w,h,light}, line{points}
              (option t0/t1 pour n'apparaître qu'un temps)
actors        {"nom": {"hair", "extras", "keys": [...]}}
props         {"nom": {"type", "layer": front|back, "size", "keys": [...]}}
camera        [{"t","cx","cy","zoom","ease","cut"}]   (coordonnées monde, écran 1080×1920)
fade          [{"t","b"}]  luminosité 0..1 (fondus au noir, ellipses)
texts         [{"text" | "lines":[{"text","size"}], "y","size","t0","write","t1","fade","over_fade"}]
```

**Images clés** : chaque clé `{"t": ...}` ne contient que ce qui change. Les nombres
(`x`, `rot`, `zoom`…) s'interpolent depuis la clé précédente (`ease` : inout,
in, out, linear) ; `"cut": true` = changement instantané. Les poses se fondent
pendant `trans` s (0,35 s par défaut) avant leur clé.

**Personnages**
- Clés : `x`, `ground` (y du sol), `dir` (1 = regarde à droite, −1 = à gauche),
  `pose`, `face`, `scale` (enfant ≈ 0,6), `visible`, `lift` (décollage vertical).
- La marche est **automatique** dès que `x` change (jambes et bras animés).
- `hair` : none, cowlick (mèche en spirale), long, ponytail, beanie, cap, curly, bow.
- `extras` : glasses, mustache, beard, skirt, scarf, tie.
- `face` : neutral, smile, happy, laugh, closed (yeux fermés, apaisé), sad, cry
  (larme qui coule), worried, surprised, angry, love.
- `pose` : stand, walk, sad, old, look_up, look_down, hold, carry, reach, point,
  wave, cheer, phone, umbrella, umbrella_look, umbrella_look_up, hug, think,
  facepalm, cry, shiver, kneel, crouch, sit_bench, sit_sad, sit_look_up,
  sit_umbrella, sit_phone, sit_ground, hug_knees, lie, jump.
  Pour en ajouter, compléter le dictionnaire `POSES` de `render.py` (angles en
  degrés : 0 = vers le bas, 90 = devant, 180 = vers le haut).

**Objets** : plank, umbrella (`open`), phone (`glow`), cane, balloon, heart, gift,
box, letter, flower, ball, candle (`glow`).
Clés : soit `x`, `y`, `rot` (position libre, ex. une planche qui tombe avec
`"ease": "in"`), soit `"attach": "acteur.hand_r"` (+ `dx`, `dy`, `rot`). Points
d'attache possibles : hand_r, hand_l, hands, head, hip, foot_l, foot_r.

## Flux de travail

1. Écrire la grille de l'histoire (section ci-dessus) et la valider avec l'utilisateur.
2. Écrire le JSON : décor, puis personnages, puis objets, puis caméra, puis textes.
3. Vérifier sur des images fixes aux moments clés :
   `python3 scripts/render.py histoire.json -o apercu.png --preview 1 6 15 24 30`
   puis regarder les PNG (cadrage, lisibilité, chevauchements texte/décor).
4. Rendre : `python3 scripts/render.py histoire.json -o video.mp4`
   (≈ 1 min de calcul pour 30 s ; 1080×1920, 30 i/s).
5. Livrer la vidéo avec une légende : **paradoxe chiffré + morale + 3-5 hashtags**,
   ex. « Il a tenu le parapluie 10 ans. Il a suffi d'une fois pour comprendre ☔
   #animation #stickman #famille #émotion ».

Pièges : garder le texte du haut (y < 700 à l'écran) hors des décors hauts
(lampadaire, nuages) ; dézoomer légèrement (zoom ≈ 1,1) pendant la morale ;
à un gros plan sur un objet tenu en main, vérifier qu'il ne sort pas du cadre.
