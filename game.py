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
from image import Image

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

        self.size = size
        pygame.display.set_mode(size.xy, flags)
        pygame.display.set_caption('nox II gamedev entry')

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

        self.projection = Matrix.perspective(75, size, 0.1, 100)
        self.ortho = Matrix.ortho(size)

        v = np.array([
                0,0,0, 0,0,
                1,0,0, 1,0,
                1,1,0, 1,1,
                0,1,0, 0,1,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.quad = VBO(GL_QUADS, v, i)

        # parallax
        self.parallax_rep = 5
        v = np.array([
                0,0,0, 0,1,
                1,0,0, self.parallax_rep, 1,
                1,1,0, self.parallax_rep,0,
                0,1,0, 0,0,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.repquad = VBO(GL_QUADS, v, i)
        self.parallax = Image('texture/sky.png', wrap=GL_REPEAT)

        self.fbo = FBO(self.size, format=GL_RGB8, depth=True)

        self.shader = Shader('derp')
        self.passthru = Shader('passtru')

        self.map = Map('map.json')
        self.player = Player(Vector2f(55,-9))
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
            self.player.pos.x, self.player.pos.y+7, 15,
            self.player.pos.x, self.player.pos.y+7, 0,
            0,1,0)

        with self.fbo as frame:
            frame.clear(0,0,1,1)

            Shader.upload_projection_view(self.projection, view)
            Shader.upload_player(self.player)
            self.shader.bind()

            # parallax background
            pm1 = Matrix.identity()
            pm1[3,0] = self.player.pos.x * 0.5 - 20
            pm1[3,1] = self.player.pos.y * 0.5 - 20
            pm1[0,0] = 42.0 * self.parallax_rep
            pm1[1,1] = 42.0
            self.parallax.texture_bind()
            Shader.upload_model(pm1)
            self.repquad.draw()

            Shader.upload_projection_view(self.projection, view)

            self.map.draw()
            self.player.draw()

        mat = Matrix.identity()
        mat[0,0] = self.size.x
        mat[1,1] = self.size.y
        Shader.upload_projection_view(self.ortho, Matrix.identity())
        Shader.upload_model(mat)

        self.fbo.bind_texture()
        self.passthru.bind()
        self.quad.draw()

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
