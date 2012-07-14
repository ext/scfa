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
    max_hp = 100

    def __init__(self, pos):
        self.pos = pos
        self.vel = Vector2f(0,0)
        self.texture = Image('texture/player.png', filter=GL_NEAREST)
        self.in_air = False
        self.jumping = 0
        self.hp = Player.max_hp
        self.hp_ratio = 0.8
        self.dir = 1
        self.cave_visited = False
        self.cave_quest = False
        self.have_ham = False
        self.have_cheese = False
        self.have_bread = False
        self.have_sandwich = False
        self.is_killed = False
        self.derp = False

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
            if self.vel.y < -0.4:
                game.land.play()
            self.in_air = False
            self.vel.y = 0
            self.pos.y = math.floor(self.pos.y)
            if not walkable(map.tile_at(self.pos+Vector2f(0,0.1))):
                self.pos.y += 1

        # handle horizontal
        t1 = map.tile_at(self.pos + Vector2f(self.vel.x, 0.01))
        t2 = map.tile_at(self.pos + Vector2f(self.vel.x + 1.0, 0.01))
        if walkable(t1) and walkable(t2):
            self.pos.x += self.vel.x
        elif self.vel.x < 0:
            self.pos.x = math.floor(self.pos.x)
        elif self.vel.x > 0:
            self.pos.x = math.ceil(self.pos.x)

        # flip direction
        if self.vel.x > 0:
            self.dir = 1
        elif self.vel.x < 0:
            self.dir = -1

        # kill players falling down the hole
        if not self.is_killed and self.pos.y < -30 and self.pos.x >= 130 and self.pos.x <= 135:
            game.message('Player was killed while jumping down a hole')
            game.over()
            self.is_killed = True

        if not self.is_killed and self.hp <= 0.0001:
            game.message('player got lost in the woods and died')
            game.over()
            self.is_killed = True

        # subtract health
        d = (self.pos - Vector2f(53,-8)).length()
        d2 = (self.pos - Vector2f(354,-18)).length()
        d3 = (self.pos - Vector2f(200,-48)).length()
        d4 = (self.pos - Vector2f(384,-87)).length()
        if d >= 14.0 and d2 >= 14.0 and d3 >= 17.0 and d4 >= 20.0:
            self.hp -= 1.7 * dt
        else:
            self.hp += (Player.max_hp / 100.0) * dt

        self.hp = min(max(self.hp, 0.0), Player.max_hp)
        self.hp_ratio = float(self.hp) / Player.max_hp

        # test if possible to make sandwhich (without sudo)
        if d < 2 and self.have_cheese and self.have_ham and self.have_bread and not self.have_sandwich:
            game.message('Sandwich made')
            self.have_sandwich = True

        # check cave
        dc = (self.pos - Vector2f(354,-18)).length()
        if dc < 2.0 and not self.derp:
            if not self.cave_visited:
                if self.have_sandwich:
                    game.message('Dward: om nom nom, thank you for the sandwich')
                    game.message('Quest finished: "Make me a sandwich".')
                    self.derp = True
                else:
                    game.message('Dwarf: Hey there, could you fetch me a sandwich?')
                    self.cave_visited = True
                    if not self.cave_quest:
                        game.message('Quest started: "Make me a sandwich".')
                        self.cave_quest = True
        elif dc > 30.0:
            self.cave_visited = False

    def draw(self):
        model = Matrix.identity()

        # translate
        model[3,0] = self.pos.x + (self.dir == -1 and 1.0 or 0.0)
        model[3,1] = self.pos.y
        model[0,0] = self.dir

        Shader.upload_model(model)
        self.texture.texture_bind()
        self.vbo.draw()

    def jump(self):
        if not self.in_air:
            self.vel.y += 18.0 / Player.weight
            self.jumping = 900.0

    def unjump(self):
        self.jumping = 0

    def frobnicate(self, stuff):
        min2 = self.pos + Vector2f(0.25,0)
        max = self.pos + Vector2f(0.75,2)
        for obj in stuff:
            omin = obj.pos
            omax = obj.pos + Vector2f(1,1)

            if max.x < omin.x or min2.x > omax.x: continue
            if max.y < omin.y or min2.y > omax.y: continue

            self.hp = min(self.hp + obj.hp, Player.max_hp)
            obj.kill()
