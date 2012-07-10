import pygame
import os, sys

class Game(object):
    def __init__(self):
        pass

def run():
    pygame.display.init()

    game = Game()

    # superglobals for quick access
    __builtins__['game'] = game
