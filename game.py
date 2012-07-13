import pygame
import os, sys
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

from vbo import VBO
from fbo import FBO
from shader import Shader, Matrix
from vector import Vector2i, Vector2f
from map import Map
from player import Player

event_table = {}
def event(type):
    def wrapper(func):
        event_table[type] = func
        return func
    return wrapper

class Game(object):
    def __init__(self):
        self._running = False
        self.camera = Vector2f(0,5)

    def init(self, size, fullscreen=False):
        flags = OPENGL|DOUBLEBUF
        if fullscreen:
            flags |= FULLSCREEN

        pygame.display.set_mode(size.xy, flags)
        pygame.display.set_caption('nox II gamedev entry')

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

        self.projection = Matrix.perspective(75, size, 0.1, 100)

        # temp
        v = np.array([
                0,0,0, 0,0,
                1,0,0, 1,0,
                1,1,0, 1,1,
                0,1,0, 0,1,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.test = VBO(GL_QUADS, v, i)

        self.fbo = FBO(Vector2i(100,100))

        self.shader = Shader('derp')
        self.map = Map('map.json')
        self.player = Player(Vector2f(0,0))
        self.clock = pygame.time.Clock()

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

        if event.key == 119:
            self.player.jump()

    @event(pygame.KEYUP)
    def on_keyrelease(self, event):
        if event.key == 119:
            self.player.unjump()

    def poll(self):
        global event_table
        for event in pygame.event.get():
            func = event_table.get(event.type, None)
            if func is None:
                continue
            func(self, event)

    def update(self):
        key = pygame.key.get_pressed()

        self.player.vel.x = 0
        if key[97 ]: self.player.vel.x = -0.15
        if key[100]: self.player.vel.x =  0.15

        if key[260]: self.camera.x -= 0.1
        if key[262]: self.camera.x += 0.1
        if key[258]: self.camera.y -= 0.1
        if key[264]: self.camera.y += 0.1

        dt = 1.0 / self.clock.tick(60)
        self.player.update(dt, self.map)

    def render(self):
        glClearColor(1,0,1,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        view = Matrix.lookat(
            self.player.pos.x, self.player.pos.y, 15,
            self.player.pos.x, self.player.pos.y, 0,
            0,1,0)
        model = Matrix.identity()

        Shader.upload_projection_view(self.projection, view)
        Shader.upload_model(model)

        with self.fbo as frame:
            frame.clear(0,1,1,1)

        glColor4f(1,1,1,1)
        self.fbo.bind_texture()
        self.shader.bind()
        self.map.draw()
        self.player.draw()
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

    game.init(Vector2i(1024,768))
    game.run()

    # force deallocation
    del __builtins__['game']
    del game
