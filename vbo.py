from OpenGL.GL import *
from OpenGL.GLU import *
from ctypes import c_void_p
import numpy as np

class VBO(object):
    stride = 4*5

    def __init__(self, what, vertices, indices):
        self.buffer = glGenBuffers(2)
        self.what = what
        self.num_vertices = len(vertices)
        self.num_indices = len(indices)

        glBindBuffer(GL_ARRAY_BUFFER, self.buffer[0])
        glBufferData(GL_ARRAY_BUFFER, 4 * len(vertices), vertices, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffer[1])
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(indices), indices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def __del__(self):
        glDeleteBuffers(2, self.buffer)

    def draw(self):
        glBindBuffer(GL_ARRAY_BUFFER, self.buffer[0])
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.buffer[1])

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, self.stride, c_void_p(0))
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, self.stride, c_void_p(4*3))

        glDrawElements(self.what, self.num_indices, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
