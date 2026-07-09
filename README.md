# Mosaic Star Raiders

MVP de shoot'em up rétro-moderne en Python/Pygame, conçu pour être jouable en local **et** dans le navigateur via **pygbag** + GitHub Pages.

Le jeu est volontairement original : il s'inspire du plaisir arcade des fixed shooters / vertical shooters, avec une esthétique de mosaïque pixel-art procédurale. Aucun asset externe n'est nécessaire : les vaisseaux, ennemis, boss, tirs, étoiles, particules et power-ups sont générés par le code.

## Fonctionnalités MVP

- Vaisseau jouable au clavier.
- Rendu pixel-perfect en résolution logique 320×240, upscalé en 4×.
- Fond spatial animé.
- Vagues successives d'ennemis mosaïques.
- Plusieurs familles d'ennemis : tile, diver, splitter, mirror, builder, elite.
- Splitters qui se fragmentent.
- Builders capables de réparer les ennemis proches.
- Trois boss de type “100 points” : Médecin cosmique, Duo stellaire, Grand Mur.
- Power-ups : spread shot, laser, drones, shield, bombes, réparation.
- Bombe déclenchable au clavier.
- Score, combo, vies, HUD, pause, game over, victoire.
- Compatible pygbag : boucle `async`, `await asyncio.sleep(0)` par frame.
- Workflow GitHub Actions prêt pour GitHub Pages.

## Contrôles

| Action | Touches |
|---|---|
| Déplacement | Flèches, WASD ou ZQSD |
| Tir | Espace, X ou J |
| Bombe | B |
| Pause | Échap |
| Redémarrer pendant la partie | R |
| Lancer / rejouer | Entrée ou Espace |

## Lancer en local avec Python

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

## Tester dans le navigateur avec pygbag

Depuis le dossier du projet :

```bash
python -m pygbag --ume_block 0 --width 1920 --height 1080 .
```

Puis ouvrir :

```text
http://localhost:8000
```

Build statique seul :

```bash
python -m pygbag --build --ume_block 0 --width 1920 --height 1080 --title "Mosaic Star Raiders" --app_name "Mosaic Star Raiders" .
```

Sur Windows PowerShell, tu peux aussi lancer :

```powershell
.\scripts\build_web.ps1
```

Les fichiers web sont générés dans :

```text
build/web/
```

## Déployer sur GitHub Pages

### 1. Créer un dépôt GitHub

Exemple : `mosaic-star-raiders`.

### 2. Initialiser git et pousser le projet

Windows PowerShell helper :

```powershell
.\scripts\git_first_push.ps1 -GitHubUser "<TON_USER>" -RepoName "<TON_REPO>"
```

Ou manuellement :

```bash
git init
git add .
git commit -m "Initial MVP"
git branch -M main
git remote add origin https://github.com/<TON_USER>/<TON_REPO>.git
git push -u origin main
```

### 3. Activer GitHub Pages avec Actions

Dans GitHub :

1. Aller dans **Settings → Pages**.
2. Dans **Build and deployment**, choisir **Source: GitHub Actions**.
3. Aller dans l'onglet **Actions**.
4. Lancer ou attendre le workflow **Build pygbag game and deploy to GitHub Pages**.
5. L'URL finale sera affichée dans le job `deploy`.

Le workflow est déjà inclus dans :

```text
.github/workflows/pages.yml
```

## Structure

```text
mosaic_shooter/
  main.py
  requirements.txt
  README.md
  .github/workflows/pages.yml
  scripts/
    build_web.ps1
    run_web.ps1
    git_first_push.ps1
    build_web.sh
  src/
    game.py
    entities.py
    waves.py
    sprites.py
    palette.py
    settings.py
```

## Notes de design

Le projet évite volontairement de copier un jeu ou des œuvres existantes. L'objectif est de garder :

- le plaisir d'un shoot arcade lisible ;
- une progression par vagues ;
- des super pouvoirs immédiatement satisfaisants ;
- des boss monumentaux ;
- une identité visuelle de mosaïque spatiale.

Les matrices de sprites sont faciles à modifier dans `src/sprites.py`. Les vagues sont définies dans `src/waves.py`. Les paramètres de résolution, vitesse et FPS sont dans `src/settings.py`.

## Prochaines extensions possibles

- Ajouter des sons procéduraux ou des petits fichiers `.wav` originaux.
- Ajouter un high score persistant côté navigateur.
- Ajouter une carte de campagne.
- Ajouter des boss supplémentaires.
- Ajouter un mode enfant plus facile.
- Ajouter des patterns de tirs plus variés.
- Ajouter une vraie page d'accueil HTML personnalisée pour pygbag.
