# Design notes — Mosaic Star Raiders

## Intention

Créer un shoot'em up arcade pour navigateur, inspiré de la culture rétro, mais sans reproduire fidèlement Space Invaders. L'esthétique centrale est celle d'une mosaïque pixel-art vivante : des créatures carrelées, des tirs lumineux, des explosions en petits carreaux.

## Boucle de jeu

1. Une vague descend ou se déplace dans l'espace.
2. Le joueur détruit les ennemis et évite les tirs.
3. Des power-ups tombent.
4. Les armes évoluent temporairement.
5. Un boss monumental apparaît après plusieurs vagues.
6. Le joueur avance jusqu'au Grand Mur final.

## Ennemis

- `tile` : ennemi simple et lisible.
- `diver` : plonge vers le joueur.
- `splitter` : se fragmente en petits ennemis.
- `mirror` : ennemi plus résistant, visuellement protégé.
- `builder` : répare les ennemis proches.
- `elite` : ennemi lourd qui tire en éventail.

## Power-ups

- `spread` : tir en éventail.
- `laser` : tir rapide et perforant.
- `drone` : satellite de tir automatique.
- `shield` : bouclier temporaire.
- `bomb` : bombe qui détruit les tirs et blesse tout l'écran.
- `repair` : vie supplémentaire.

## Boss

- Médecin cosmique : boss portrait, tirs ECG et tir visé.
- Duo stellaire : deux masses visuelles dans une même mosaïque, patterns bilatéraux.
- Grand Mur : boss final large, pluie de projectiles.

## Priorités pour v0.2

1. Ajouter sons et musique.
2. Équilibrer difficulté vague par vague.
3. Ajouter un high score.
4. Ajouter options : volume, difficulté, plein écran.
5. Ajouter des boss plus modulaires avec tuiles destructibles individuellement.
