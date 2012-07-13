from image import Image
from vbo import VBO
from shader import Shader, Matrix
from vector import Vector2f
import numpy as np
from OpenGL.GL import *
import math

def walkable(id):
    return id <= 1 or id > 100

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

        # handle vertical
        self.in_air = True
        t1 = map.tile_at(self.pos + Vector2f(0, self.vel.y))
        t2 = map.tile_at(self.pos + Vector2f(0.999, self.vel.y))
        if walkable(t1) and walkable (t2):
            self.pos.y += self.vel.y
        else:
            self.in_air = False
            self.vel.y = 0
            self.pos.y = math.floor(self.pos.y)

        # handle horizontal
        t1 = map.tile_at(self.pos + Vector2f(self.vel.x, 0.01))
        t2 = map.tile_at(self.pos + Vector2f(self.vel.x + 1.0, 0.01))
        if walkable(t1) and walkable(t2):
            self.pos.x += self.vel.x
        elif self.vel.x < 0:
            self.pos.x = math.floor(self.pos.x)
        elif self.vel.x > 0:
            self.pos.x = math.ceil(self.pos.x)

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


