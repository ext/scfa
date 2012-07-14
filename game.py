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
from hud import HUD, ALIGN_CENTER
import math

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
        pygame.display.set_caption('Super Chainsaw Food Adventure')

        i = pygame.display.Info()
        self.size = Vector2i(i.current_w, i.current_h)

        glMatrixMode(GL_MODELVIEW)
        glEnable(GL_TEXTURE_2D)
        glDisable(GL_CULL_FACE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)

        self.stage = 1
        self.projection = Matrix.perspective(75, self.size, 0.1, 100)
        self.ortho = Matrix.ortho(self.size)

        v = np.array([
                0,0,0, 0,0,
                1,0,0, 1,0,
                1,1,0, 1,1,
                0,1,0, 0,1,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.quad = VBO(GL_QUADS, v, i)

        # parallax
        self.parallax_rep = 25
        v = np.array([
                0,0,0, 0,1,
                1,0,0, self.parallax_rep, 1,
                1,1,0, self.parallax_rep,0,
                0,1,0, 0,0,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.repquad = VBO(GL_QUADS, v, i)
        self.parallax = Image('texture/sky.png', wrap=GL_REPEAT)
        self.parallax2 = Image('texture/sky2.png', wrap=GL_REPEAT)

        self.fbo = FBO(self.size, format=GL_RGB8, depth=True)

        self.shader = Shader('derp')
        self.passthru = Shader('passtru')
        self.herp = Shader('herp')

        self.map = Map('map.json')
        self.player = Player(Vector2f(55,-9))
        self.clock = pygame.time.Clock()
        self.hud = HUD(Vector2i(500,100))
        self.hpmeter = HUD(Vector2i(20, 500))
        self.font = self.hud.create_font(size=16)
        self.font2 = self.hud.create_font(size=12)

        self.land = pygame.mixer.Sound('data/sound/land.wav')
        self.ding = pygame.mixer.Sound('data/sound/ding.wav')
        self.eat = pygame.mixer.Sound('data/sound/eat.wav')
        self.wind = pygame.mixer.Sound('data/sound/wind.wav')

        self.wind.play(loops=-1)

        self.set_stage(1)
        self.killfade = None
        self.killfade2 = 1.0 # fade amount
        self.textbuf = []
        self.texttime = -10.0
        self.message('<b>Welcome adventurer!</b>\nYou can start exploring the world but beware of wandering away too far.')
        self.message('When outside of lights your <i>HP</i> will drain and you will get lost in the woods.')
        self.message('Eat food to temporary increase your <i>HP</i>.')
        self.message('Quest started: "Find the chainsaw".')
        self.message('Quest started: "Frobnicate something".')

        with self.hud:
            self.hud.clear((0,1,1,1))

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
        if self.killfade is not None:
            t = pygame.time.get_ticks() / 1000.0
            s = (t - self.killfade) / 2.5
            self.killfade2 = 1.0 - s

            if s > 1.0:
                self.quit()

            # so player keeps falling
            dt = 1.0 / self.clock.tick(60)
            self.player.vel.y = 0
            self.player.update(dt, self.map)

            return

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
        self.player.frobnicate(self.map.pickups)
        self.map.update()

    def render(self):
        glClearColor(1,0,1,1)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        with self.hpmeter as hud:
            hud.clear((0.3,0,0,1))
            hud.cr.identity_matrix()

            hud.rectangle(0,0, hud.width, hud.height * self.player.hp_ratio, (0,0.3,0,1))

            hud.cr.translate(18,0)
            hud.cr.rotate(math.pi*0.5)
            hud.text(' Energy: %d / %d' % (int(math.ceil(self.player.hp/10)) * 10, Player.max_hp), self.font2, color=(1,0.8,0,1))

        with self.hud:
            self.hud.clear((0,0,0,0))
            self.hud.cr.identity_matrix()

            t = pygame.time.get_ticks() / 1000.0
            s = (t - self.texttime) / 4.0

            if s > 1.0:
                if len(self.textbuf) > 0:
                    self.texttime = pygame.time.get_ticks() / 1000.0
                    self.text = self.textbuf.pop(0)
            else:
                a = min(1.0-s, 0.2) * 5
                self.hud.cr.translate(0,25)
                self.hud.text(self.text, self.font, color=(1,0.8,0,a), width=self.hud.width, alignment=ALIGN_CENTER)

        view = Matrix.lookat(
            self.player.pos.x, self.player.pos.y+7, 15,
            self.player.pos.x, self.player.pos.y+7, 0,
            0,1,0)

        with self.fbo as frame:
            frame.clear(0,0.03,0.15,1)

            Shader.upload_projection_view(self.projection, view)
            Shader.upload_player(self.player)
            self.shader.bind()

            # parallax background
            pm1 = Matrix.identity()
            pm1[3,0] = self.player.pos.x * 0.35 - 20
            pm1[3,1] = self.player.pos.y * 0.5 - 20
            pm1[0,0] = 42.0 * self.parallax_rep
            pm1[1,1] = 42.0
            self.parallax.texture_bind()
            Shader.upload_model(pm1)
            self.repquad.draw()

            Shader.upload_projection_view(self.projection, view)

            self.map.draw()

            # entities
            for obj in self.map.pickups:
                obj.draw(self.quad)
            self.player.draw()

            # parallax 2
            pm1 = Matrix.identity()
            pm1[3,0] = self.player.pos.x * -2.0 + 100
            pm1[3,1] = self.player.pos.y * 0.5 - 45 * 3 + 10
            pm1[0,0] = 45.0 * self.parallax_rep * 3
            pm1[1,1] = 45 * 3
            self.parallax2.texture_bind()
            Shader.upload_model(pm1)
            self.repquad.draw()

        mat = Matrix.identity()
        mat[0,0] = self.size.x
        mat[1,1] = self.size.y
        Shader.upload_projection_view(self.ortho, Matrix.identity())
        Shader.upload_model(mat)

        self.fbo.bind_texture()
        self.herp.bind()
        self.quad.draw()

        # messagebox
        mat = Matrix.identity()
        mat[3,0] = self.size.x / 2 - self.hud.width / 2
        mat[3,1] = self.size.y - self.hud.height
        Shader.upload_model(mat)
        self.hud.draw()

        # hpmeter
        mat = Matrix.identity()
        mat[3,1] = self.size.y / 2 - self.hpmeter.height / 2
        Shader.upload_model(mat)
        self.hpmeter.draw()

        Shader.unbind()

        pygame.display.flip()

    def run(self):
        self._running = True
        while self.running():
            self.poll()
            self.update()
            self.render()

    def message(self, text):
        self.textbuf.append(text)

    def set_stage(self, n):
        if n == 1:
            self.map.pickups.extend(self.map.obj1)
        elif n == 2:
            self.map.pickups.extend(self.map.obj2)
        elif n == 3:
            self.map.pickups.extend(self.map.obj3)

    def over(self):
        self.killfade = pygame.time.get_ticks() / 1000.0

def run():
    pygame.display.init()
    pygame.mixer.init(channels=3, buffer=1024)
    pygame.mouse.set_visible(False)

    game = Game()

    # superglobals for quick access
    __builtins__['game'] = game

    game.init(Vector2i(0,0), fullscreen=True)
    game.run()

    # force deallocation
    del __builtins__['game']
    del game
