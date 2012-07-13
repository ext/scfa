from vector import Vector2f
from shader import Shader, Matrix
from OpenGL.GL import *
import image

class Food(object):
    def __init__(self, name, x, y, **kwargs):
        self.name = name
        self.pos = Vector2f(x,y)

        self.texture = image.load('texture/apple.png')

        mat = Matrix.identity()
        mat[3,0] = self.pos.x / 8
        mat[3,1] = -self.pos.y / 8
        mat[0,0] = 1
        mat[1,1] = 1
        self.mat = mat

    def draw(self, q):
        Shader.upload_model(self.mat)
        self.texture.texture_bind()
        q.draw()
