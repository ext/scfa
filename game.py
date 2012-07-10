import pygame
import os, sys
from vector import Vector2i
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

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
