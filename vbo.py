from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

class VBO(object):
    stride = 4*3

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

        glVertexPointer(3, GL_FLOAT, self.stride, None)
        #glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, vertex.itemsize, 0)
        #glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, sizeof(vertex_t), (const GLvoid*) (sizeof(glm::vec3)))
        #glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, sizeof(vertex_t), (const GLvoid*) (sizeof(glm::vec3)+sizeof(glm::vec2)))
        #glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, sizeof(vertex_t), (const GLvoid*) (2*sizeof(glm::vec3)+sizeof(glm::vec2)))
        #glVertexAttribPointer(4, 3, GL_FLOAT, GL_FALSE, sizeof(vertex_t), (const GLvoid*) (3*sizeof(glm::vec3)+sizeof(glm::vec2)))

        glDrawElements(self.what, 4, GL_UNSIGNED_INT, None)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
