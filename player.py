from image import Image
from vbo import VBO
from shader import Shader, Matrix
from vector import Vector2f
import numpy as np
from OpenGL.GL import *
import math

class Player(object):
    weight = 70.0

    def __init__(self, pos):
        self.pos = pos
        self.vel = Vector2f(0,0)
        self.texture = Image('texture/player.png', filter=GL_NEAREST)
        self.in_air = False
        self.jumping = 0

        v = np.array([
                0,1,0, 0,1,
                1,1,0, 1,1,
                1,3,0, 1,0,
                0,3,0, 0,0,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.vbo = VBO(GL_QUADS, v, i)

    def update(self, dt, map):
        acc = 0.0
        acc -= 9.8 * dt

        if self.jumping > 0:
            acc += self.jumping / Player.weight * dt
            self.jumping -= 25.0

        self.vel.y += acc * dt
        p = self.pos.copy()
        p += self.vel

        self.in_air = True
        if map.tile_at(p) <= 1:
            self.pos = p
        else:
            self.in_air = False
            self.vel.y = 0
            self.pos.y = math.floor(self.pos.y)

    def draw(self):
        model = Matrix.identity()

        # translate
        model[3,0] = self.pos.x
        model[3,1] = self.pos.y

        Shader.upload_model(model)
        self.texture.texture_bind()
        self.vbo.draw()

    def jump(self):
        if not self.in_air:
            self.vel.y += 18.0 / Player.weight
            self.jumping = 900.0

    def unjump(self):
        self.jumping = 0


