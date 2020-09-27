import sys
import pygame as pg

from gamestates import CoinTossScreen, ShootOut, DustSettling, PlayerSelect, Instructions, TitleScreen
from state_engine import Game

def run_game():
    print('initializing game')
    pg.init()
    screen = pg.display.set_mode((1024, 576))
    states = {
        "TITLESCREEN": TitleScreen(),
        "PLAYERSELECT": PlayerSelect(),
        "INSTRUCTIONS": Instructions(),
        "COINTOSS": CoinTossScreen(),
        "SHOOTOUT": ShootOut(),
        "DUSTSETTLING": DustSettling()
    }
    game = Game(screen, states, "TITLESCREEN")
    print('running game')
    game.run()
    pg.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()