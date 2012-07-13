from vector import Vector2f
from shader import Shader, Matrix
from OpenGL.GL import *
import image

class Food(object):
    def __init__(self, name, x, y, **kwargs):
        self.name = name
        self.pos = Vector2f(x,-y) * (1.0 / 8)

        self.texture = image.load('texture/apple.png')

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
