---
name: rap-en-rythme
description: Créer une vidéo verticale TikTok/Reels/Shorts « RAP EN RYTHME ! » rendue en code — grille de 4 cases par mesure, balle orange qui rebondit sur chaque temps, mots qui riment (même couleur) à placer sur le 4e temps, compte à rebours néon, instru libre de droits générée et calée au temps près. À utiliser quand on demande une vidéo de défi rap, « rappe en rythme », « rappe comme [artiste] », freestyle avec mots imposés, ou une nouvelle vidéo dans ce style.
---

# Rap en rythme — vidéo défi « freestyle sur mots imposés »

Le spectateur rappe par-dessus la vidéo : chaque ligne = 1 mesure de 4 temps.
Les 3 premières cases sont vides (il improvise), la 4e affiche le mot qu'il doit
placer **pile sur le 4e temps**. Les mots arrivent par familles de rimes
(même couleur), donc il enchaîne naturellement des rimes plates (AABB).
La balle donne le tempo ; la grille défile d'une ligne par mesure.

Analyse complète des 3 vidéos sources (timings mesurés, couleurs, mise en page) :
`references/analyse.md`.

## Pourquoi ça marche (à garder en tête pour chaque vidéo)

1. **Participation** : ce n'est pas une vidéo à regarder, c'est un jeu à faire.
   Les gens se filment en duo/stitch → contenu généré par la communauté.
2. **Zéro barrière** : mots simples du quotidien, tempo lent (≈ 89 BPM), compte
   à rebours 3-2-1 → tout le monde peut essayer.
3. **Rétention** : on veut voir le mot suivant ; on rejoue pour « réussir ».
4. **Série** : même titre, même charte, seuls les mots/l'instru changent →
   déclinable à l'infini (thèmes, difficulté, « rappe comme [artiste] »).

## Flux de travail

1. **Choisir la déclinaison** (voir tableau ci-dessous) : titre, BPM, style d'instru.
2. **Écrire les mots** en respectant les règles d'écriture (section suivante).
3. **Écrire le JSON** de config (partir d'un fichier de `examples/`).
4. **Vérifier des images fixes** avant le rendu complet :
   `python3 scripts/render.py config.json -o apercu.png --preview 1 6 15`
   puis regarder les PNG (mots lisibles ? aucun mot trop long ?).
5. **Rendre** : `python3 scripts/render.py config.json -o video.mp4`
   (≈ 35 s de calcul pour 50 s de vidéo ; 1080×1920, 30 i/s, H.264 + AAC).
6. Livrer la vidéo + proposer la légende et les hashtags (section « Publication »).

Dépendances : `python3`, `numpy`, `Pillow`, `ffmpeg`. Polices incluses (OFL).

## Déclinaisons observées

| Format | Titre | BPM | `beat_style` | Mots | Titre affiché |
|---|---|---|---|---|---|
| Classique | `RAP EN RYTHME !` | 89 | `boombap` | 8 paires (16 mots) | tout le long (`always`) |
| Classique v2 | `RAPPE EN RYTHME !` | 89 | `boombap` | 8 paires | pendant l'intro (`intro`) |
| Imitation | `RAPPE COMME : <ARTISTE>` (titre orange `#ffb21f`) | 130-140 | `drill` ou `trap` | 4 groupes de 4 | pendant l'intro |

Durée cible : 35-55 s (2 mesures d'intro + 16 lignes + 1 mesure de fin).
16 mots est le bon nombre ; au-delà la vidéo dépasse 1 min à 89 BPM.

## Règles d'écriture des mots

- **Familles de rimes** : chaque groupe de `groups` = une rime, une couleur
  (cycle orange → bleu → jaune → vert). Paires pour le format classique,
  groupes de 4 pour le format « rappe comme ».
- La rime porte sur **le son final** (pas l'orthographe) : *flûte/chute*,
  *nature/aventure*, *nuit/lui*, *égard/gare*, *pot/peau/capot/dépôt*.
- **Mots courts et concrets** (1 à 3 syllabes), faciles à placer sur un seul temps.
  Max ≈ 11 caractères (la police rétrécit automatiquement mais reste lisible).
- **Glisser des mots « fun »** qui font sourire ou forcent l'imagination :
  noms propres (*Valentin, Cendrillon, Singapour*), images (*têtard, lavabo, flambeau*).
- **Arc de difficulté** : commencer par des rimes évidentes, finir par des mots
  du thème rap (*micro/impro, scène/chaîne, rap/étape*) pour une fin satisfaisante.
- Varier les sons d'une paire à l'autre (ne pas enchaîner deux familles en *-on*).
- Pas de mots vulgaires, sensibles ou de marques.

Exemples de familles prêtes à l'emploi : *-o* (bateau, château, gâteau, cadeau),
*-in* (copain, demain, chemin, requin), *-é* (café, fusée, trophée, journée),
*-ou* (loup, bijou, genou, hibou), *-age* (nuage, voyage, plage, image),
*-ette* (planète, tempête, fête, conquête), *-oir* (miroir, histoire, victoire, couloir),
*-eur* (cœur, moteur, couleur, chanteur), *-ance* (danse, chance, France, silence).

## Config JSON

```json
{
  "title": "RAP EN RYTHME !",
  "title_color": "#ffffff",
  "title_mode": "always",
  "bpm": 89,
  "beat_style": "boombap",
  "intro_bars": 2,
  "outro_bars": 1,
  "groups": [["flûte", "chute"], ["nature", "aventure"]],
  "audio": null,
  "audio_offset": 0.0,
  "tick": false,
  "seed": 7,
  "footer": null,
  "outro_text": null
}
```

| Clé | Rôle |
|---|---|
| `groups` | **obligatoire** — liste de familles de rimes, dans l'ordre d'apparition |
| `bpm` | tempo ; toute l'animation est calculée dessus |
| `beat_style` | instru générée : `boombap` (80-100), `trap` (120-150), `drill` (135-145) |
| `seed` | change les variations de l'instru (charleston, rolls) |
| `audio` | chemin d'une instru perso (mp3/wav) au lieu de l'instru générée |
| `audio_offset` | instant (s) dans ce fichier du **1er temps fort** voulu pour la case 1 de l'intro |
| `tick` | ajoute un petit « toc » à chaque rebond (utile pour débuter) |
| `title_mode` | `always` ou `intro` (le titre disparaît quand les mots commencent) |
| `footer` | petit texte sous la grille (ex. `@toncompte`) |
| `outro_text` | texte de fin (ex. `À TOI ! Duo ⬇️`) |

### Utiliser sa propre instru

1. Trouver BPM et 1er temps : `python3 scripts/detect_beat.py instru.mp3`
   (nécessite `librosa`) — sinon les lire dans un logiciel audio.
2. Mettre `bpm` et `audio_offset` dans la config. Le 1er rebond de la balle
   (case 1 de la 1re ligne d'intro) tombera sur `audio_offset`.
3. Vérifier la synchro sur la vidéo rendue ; ajuster `audio_offset` de ±0,02 s.

⚠️ Une instru commerciale (type beat YouTube, son d'artiste) peut être
coupée par TikTok. Privilégier l'instru générée, une instru achetée avec
licence, ou ajouter le son directement dans TikTok (sons sous licence).

## Ce que fait le moteur (`scripts/render.py`)

- Fond dégradé violet `#5429ec → #3b1c9c`, grille 4 colonnes, 5 lignes visibles.
- Intro : 2 lignes sombres (numérotées −2, −1), compte à rebours néon rouge
  « 3 · 2 · 1 » (un chiffre tous les 2 temps), instru filtrée puis « drop ».
- Chaque temps : la balle atterrit sur la case → flash blanc puis lavande ;
  la case suivante s'éclaire légèrement à l'approche. Sur le 4e temps la
  pastille du mot « pop » et devient crème (= mot joué).
- Entre le 4e temps et le temps 1 suivant : défilement d'une ligne vers le
  haut (easing), la ligne jouée s'efface en fondu, la balle fait un grand saut
  de retour vers la case 1.
- Numéros de ligne discrets à gauche et à droite.
- Fin : la balle s'envole, la grille se vide, texte de fin optionnel.

Pour modifier le style, toutes les constantes (couleurs, géométrie, hauteur
des sauts) sont regroupées en tête de `render.py`.

## Publication (à proposer avec la vidéo)

- Légende : « Tu tiens le rythme jusqu'au bout ? 🎤 Fais-le en duo ! » /
  « Rappe ces 16 mots sans t'arrêter 🔥 » / « Niveau 1 ou niveau 10 ? »
- Hashtags : `#rap #freestyle #rapfr #defi #rapenrythme #duo #rime`
- Inviter au duo/stitch et aux commentaires (« donne-moi des mots pour la prochaine »)
  → nourrit la série suivante.
- Série : *niveau 1 → 10* (BPM qui monte : 80 → 100 → 120 → 140),
  thèmes (école, foot, amour, vacances, Noël), « rappe comme [artiste] ».
