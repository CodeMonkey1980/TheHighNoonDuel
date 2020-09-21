import sys
import pygame as pg

from gamestates import CoinTossScreen, ShootOut, DustSettling, PlayerSelect, Instructions
from state_engine import Game

if __name__ == "__main__":
    print('initializing game')
    pg.init()
    screen = pg.display.set_mode((1024, 576))
    states = {
        "PLAYERSELECT": PlayerSelect(),
        "INSTRUCTIONS": Instructions(),
        "COINTOSS": CoinTossScreen(),
        "SHOOTOUT": ShootOut(),
        "DUSTSETTLING": DustSettling()
    }
    game = Game(screen, states, "PLAYERSELECT")
    print('running game')
    game.run()
    pg.quit()
    sys.exit()
