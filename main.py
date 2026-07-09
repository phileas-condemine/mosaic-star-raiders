import asyncio
from src.game import Game

# Pygbag requires the game loop to be async-aware and to yield with
# await asyncio.sleep(0) once per frame. Do not put sys.exit() after asyncio.run().

async def main():
    game = Game()
    while game.state != "quit":
        game.tick()
        await asyncio.sleep(0)

asyncio.run(main())
