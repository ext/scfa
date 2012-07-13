from image import Image
from vbo import VBO
from shader import Shader, Matrix
import numpy as np
from OpenGL.GL import *

class Player(object):
    def __init__(self, pos):
        self.pos = pos
        self.texture = Image('texture/player.png', filter=GL_NEAREST)

        v = np.array([
                0,0,0, 0,1,
                1,0,0, 1,1,
                1,2,0, 1,0,
                0,2,0, 0,0,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.vbo = VBO(GL_QUADS, v, i)


    def draw(self):
        model = Matrix.identity()

        # translate
        model[3,0] = self.pos.x
        model[3,1] = self.pos.y

        Shader.upload_model(model)
        self.texture.texture_bind()
        self.vbo.draw()
