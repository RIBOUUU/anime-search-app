# Analyse des 3 vidéos sources (format « Rap en rythme »)

Fichiers analysés : 3 vidéos TikTok téléchargées (576×1024, 30 i/s, letterbox noir :
la zone utile fait 576×677, l'original était probablement en 4:5 ou recadré).
Les filigranes TikTok et l'écran de fin « logo + @compte » sont ajoutés par
TikTok au téléchargement : ils ne font pas partie du montage.

## Vue d'ensemble

| | Vidéo 1 | Vidéo 2 | Vidéo 3 |
|---|---|---|---|
| Durée | 51,5 s | 52,2 s | 36,8 s |
| Titre | RAP EN RYTHME ! (blanc, contour noir) | RAPPE EN RYTHME ! | RAPPE COMME : [artiste] (orange) |
| Titre visible | toute la vidéo | intro seulement (0–4,3 s) | intro seulement |
| Tempo | 89 BPM (1 temps = 0,672 s) | 89 BPM | ≈ 134 BPM (0,448 s) |
| Mots | 16 = 8 paires | 16 = 8 paires | 16 = 4 groupes de 4 |
| Structure | 2 mesures d'intro + 16 lignes + fin | idem | idem |

Mots :
- V1 : flûte/chute · nature/aventure · nuit/lui · matin/Valentin · avion/Cendrillon ·
  pleurs/bonheur · égard/gare · banquet/coquet
- V2 : légende/bande · têtard/star · étape/rap · rumba/combat · grimace/place ·
  soupir/délire · chaîne/scène · micro/impro (fin sur le vocabulaire du rap)
- V3 : robot/corbeau/lavabo/flambeau · matin/satin/lutin/destin ·
  four/Singapour/retour/parcours · pot/peau/capot/dépôt

Couleur = famille de rime, cycle fixe orange → bleu → jaune → vert → orange…

## Mécanique (timings mesurés image par image, V1)

- Une ligne = une mesure = 4 temps. Cases 1-3 vides, case 4 = mot.
- Instants des impacts de la balle : 4,13 / 4,80 / 5,47 / 6,07 (mot) / 6,83 (ligne suivante)…
  → exactement un impact par temps, alignés sur le kick/les temps détectés dans l'audio.
- La balle (orange `#ffac19`, reflet `#ffc03b`, traînée lavande) décrit un arc
  au-dessus de la ligne active ; saut plus haut pour revenir de la case 4 à la case 1.
- Case touchée : flash blanc puis reste lavande claire jusqu'à l'impact suivant ;
  léger pré-éclairage de la case cible juste avant l'impact.
- Mot touché : la pastille passe en crème `#feeab4`, texte délavé (« mot joué »).
- Défilement : entre l'impact du mot et le temps 1 suivant (≈ derniers 70 % de
  l'intervalle), la grille monte d'une ligne avec easing ; la ligne jouée s'efface
  en haut, une nouvelle entre par le bas. 5 lignes visibles en permanence.
- Intro : 2 lignes sombres (`#271473`) numérotées −2 et −1, sur lesquelles la
  balle rebondit déjà ; compte à rebours néon (rouge `#ff161b`, liseré jaune
  `#fbf68f`, halo rouge) 3 → 2 → 1, un chiffre ≈ toutes les 2 temps, centré sous la grille.
- Numéros de ligne en petit (`#6e49e4`) des deux côtés de la grille.
- Fin : la dernière ligne est jouée puis la vidéo se termine (pas d'appel à l'action
  intégré — le CTA est dans la légende).

## Charte

- Fond : dégradé vertical `#5429ec` (haut) → `#4622c9` → `#3b1c9c` (bas).
- Cases vides : `#5836c4`, coins arrondis, liseré légèrement plus clair.
- Pastilles mots : relief 3D (bande plus foncée en bas), texte très foncé de la même teinte.
  Orange `#ed7a2e`/`#b34c12`, bleu `#449ee4`, jaune `#f9c02a`, vert `#46c379`/`#1d8449`.
- Polices : mots en arrondi gras type Fredoka SemiBold ; titre en sans-serif très
  gras capitales type Montserrat ExtraBold, contour noir épais.
- Mise en page (zone 576 px) : titre à 32 px du haut, grille de x=50 à 526,
  cases 113×48, pas de 60 px, balle Ø 36 px.

## Audio

Instru seule (pas de voix détectée de façon nette ; la transcription automatique
n'a pas pu être lancée dans l'environnement d'analyse). V1/V2 : boom-bap 89 BPM ;
V3 : instru rapide type trap/drill ≈ 134 BPM dans l'univers de l'artiste cité.
