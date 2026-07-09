import asyncio
import sys
import pygame  # noqa: F401  (pygbag's dependency scanner only inspects main.py's top-level imports)
from src.game import Game

# Pygbag requires the game loop to be async-aware and to yield with
# await asyncio.sleep(0) once per frame. Do not put sys.exit() after asyncio.run().


async def _prime_web_canvas():
    # pygbag's template only grows the canvas to full size (gui_divider=1 +
    # window_resize()) after main.py *returns* -- which never happens for a
    # game with a persistent loop. Trigger that resize ourselves, then poke
    # set_mode((0, 0)) once so SDL picks up the new, larger canvas instead
    # of collapsing back to its small pre-resize default. The resize can
    # take a variable amount of time to settle on a real CDN (slower wasm
    # fetch/compile than a local dev server), so poll until the reported
    # size stops changing instead of a fixed short sleep.
    try:
        import platform
        platform.window.config.gui_divider = 1
        platform.window.window_resize()
    except Exception:
        return
    last = None
    for _ in range(80):  # up to ~4s
        await asyncio.sleep(0.05)
        try:
            info = pygame.display.Info()
            cur = (info.current_w, info.current_h)
        except Exception:
            continue
        if cur == last and cur[0] > 0 and cur[1] > 0:
            break
        last = cur
    try:
        pygame.display.set_mode((0, 0))
    except Exception:
        pass


async def main():
    if sys.platform == "emscripten":
        pygame.init()
        await _prime_web_canvas()
    game = Game()
    while game.state != "quit":
        game.tick()
        await asyncio.sleep(0)

asyncio.run(main())
