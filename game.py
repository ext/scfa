import pygame
import os, sys
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from vbo import VBO
from fbo import FBO
from shader import Shader, Matrix
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

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)

        self.projection = Matrix.perspective(75, size, 0.1, 100)
        self.view = Matrix.lookat(1,3,5, 0,0,0, 0,1,0)
        self.model = Matrix.identity()

        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(self.projection)

        glMatrixMode(GL_MODELVIEW)
        glLoadMatrixf(self.view)

        # temp
        v = np.array([
                0,0,0,
                1,0,0,
                1,1,0,
                0,1,0,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.test = VBO(GL_QUADS, v, i)

        self.fbo = FBO(Vector2i(100,100))

        self.shader = Shader('derp')

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
        glClearColor(1,0,1,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        with self.fbo as frame:
            frame.clear(0,1,1,1)

        glColor4f(1,1,1,1)
        self.fbo.bind_texture()
        self.shader.bind()
        self.shader.upload(self.projection, self.view)
        self.test.draw()
        Shader.unbind()

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
