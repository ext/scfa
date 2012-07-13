import json
import os.path
from OpenGL.GL import *
from vbo import VBO
from image import Image
import numpy as np

class Map(object):
    def __init__(self, filename):
        self.filename = os.path.join('data', filename)

        with open(self.filename) as fp:
            data = json.load(fp)

        self.width  = data['width']
        self.height = data['height']

        self.tile_width  = data['tilewidth']
        self.tile_height = data['tileheight']

        # hardcoded
        dx = self.tile_width  / 128.0
        dy = self.tile_height / 128.0
        tile_div = 128 / self.tile_width

        # load tilemap
        self.texture = Image(data['tilesets'][0]['image'], filter=GL_NEAREST)

        n = len(data['layers'][0]['data'])
        ver = np.zeros((n*4, 5), np.float32)
        for i, tile in enumerate(data['layers'][0]['data']):
            x = i % self.width
            y = -(i / self.width)

            tile -= 1 # start with 0 index
            tx = tile % tile_div
            ty = tile / tile_div

            ver[i*4+0] = (x  , y  , 0, tx*dx,    ty*dy+dy)
            ver[i*4+1] = (x+1, y  , 0, tx*dx+dx, ty*dy+dy)
            ver[i*4+2] = (x+1, y+1, 0, tx*dx+dx, ty*dy)
            ver[i*4+3] = (x  , y+1, 0, tx*dx,    ty*dy)

        ver = ver.flatten()
        ind = np.array(range(n*4), np.uint32)
        self.vbo = VBO(GL_QUADS, ver, ind)

    def draw(self, *args, **kwargs):
        self.texture.texture_bind()
        self.vbo.draw(*args, **kwargs)
