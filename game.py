import pygame
import os, sys
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from vbo import VBO
from vector import Vector2i

event_table = {}
def event(type):
    def wrapper(func):
        event_table[type] = func
        return func
    return wrapper

class Game(object):
    def __init__(self):
        self._running = False

    def init(self, size, fullscreen=False):
        flags = OPENGL|DOUBLEBUF
        if fullscreen:
            flags |= FULLSCREEN

        pygame.display.set_mode(size.xy, flags)
        pygame.display.set_caption('nox II gamedev entry')

        glClearColor(1,0,1,1)

        glEnableClientState(GL_VERTEX_ARRAY)

        # temp
        v = np.array([
                0,0,0,
                1,0,0,
                1,1,0,
                0,1,0,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.test = VBO(GL_QUADS, v, i)

    def running(self):
        return self._running

    @event(pygame.QUIT)
    def quit(self, event=None):
        self._running = False

    @event(pygame.KEYDOWN)
    def on_keypress(self, event):
        if event.key == 113 and event.mod & KMOD_CTRL: # ctrl+q
            return self.quit()
        if event.key == 27: # esc
            return self.quit()

    def poll(self):
        global event_table
        for event in pygame.event.get():
            func = event_table.get(event.type, None)
            if func is None:
                continue
            func(self, event)

    def update(self):
        pass

    def render(self):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        glColor4f(1,1,0,1)
        self.test.draw()

        pygame.display.flip()

    def run(self):
        self._running = True
        while self.running():
            self.poll()
            self.update()
            self.render()

def run():
    pygame.display.init()

    game = Game()

    # superglobals for quick access
    __builtins__['game'] = game

    game.init(Vector2i(800,600))
    game.run()

    # force deallocation
    del __builtins__['game']
    del game
