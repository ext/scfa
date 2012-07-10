import pygame
import os, sys
from vector import Vector2i
from pygame.locals import *

class Game(object):
    def __init__(self):
        self._running = False

    def init(self, size, fullscreen=False):
        flags = OPENGL|DOUBLEBUF
        if fullscreen:
            flags |= FULLSCREEN

        pygame.display.set_mode(size.xy, flags)
        pygame.display.set_caption('nox II gamedev entry')

    def running(self):
        return self._running

    def quit(self):
        self._running = False

    def update(self):
        pass

    def render(self):
        pygame.display.flip()

    def run(self):
        self._running = True
        while self.running():
            self.update()
            self.render()

def run():
    pygame.display.init()

    game = Game()

    # superglobals for quick access
    __builtins__['game'] = game

    game.init(Vector2i(800,600))
    game.run()
