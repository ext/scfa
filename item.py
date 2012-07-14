from vector import Vector2f
from shader import Shader, Matrix
from OpenGL.GL import *
import image
from player import Player

class Item(object):
    def __init__(self, name, x, y, **kwargs):
        self.name = name
        self.pos = Vector2f(x,-y) * (1.0 / 8)

        mat = Matrix.identity()
        mat[3,0] = self.pos.x
        mat[3,1] = self.pos.y
        mat[0,0] = 1
        mat[1,1] = 1
        self.mat = mat
        self.killed = False

    def draw(self, q):
        Shader.upload_model(self.mat)
        self.texture.texture_bind()
        q.draw()

    def kill(self):
        self.killed = True

class Food(Item):
    def __init__(self, **kwargs):
        Item.__init__(self, **kwargs)
        self.hp = 35
        self.texture = image.load('texture/apple.png')

    def kill(self):
        Item.kill(self)
        game.eat.play()

class Schebab(Item):
    def __init__(self, **kwargs):
        Item.__init__(self, **kwargs)
        self.hp = 50
        self.texture = image.load('texture/kebab.png')

    def kill(self):
        Item.kill(self)
        game.eat.play()


class QuestItem(Item):
    def __init__(self, properties, **kwargs):
        Item.__init__(self, **kwargs)
        self.hp = 25
        self.texture = image.load(properties['texture'])

    def kill(self):
        Item.kill(self)
        game.ding.play()

        qn = len([x for x in [game.player.have_ham, game.player.have_bread, game.player.have_cheese] if x])

        if self.name == 'key':
            game.message('Picked up chainsaw key, hurry back home')
            game.set_stage(2)
        elif self.name == 'chainsaw':
            game.message('Picked up monster-ultra-food chainsaw 2000')
            game.message('Quest finished: "Find the chainsaw".')
            game.set_stage(3)
            Player.max_hp *= 2.0
            game.player.hp = Player.max_hp
        elif self.name == 'ham':
            game.message('Acquired questitem [%d/3]: Ham' % (qn+1))
            Player.max_hp *= 1.5
            game.player.hp = Player.max_hp
            game.player.have_ham = True
        elif self.name == 'bread':
            game.message('Acquired questitem [%d/3]: Bread' % (qn+1))
            Player.max_hp *= 1.5
            game.player.hp = Player.max_hp
            game.player.have_bread = True
        elif self.name == 'cheese':
            game.message('Acquired questitem [%d/3]: Cheese' % (qn+1))
            Player.max_hp *= 1.5
            game.player.hp = Player.max_hp
            game.player.have_cheese = True
        elif self.name == 'something':
            game.message('Something has been frobnicated')
            game.message('Quest finished: "Frobnicate something".')
        else:
            raise ValueError, 'unknown questitem %s' % self.name
