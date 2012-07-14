import json
import os.path
from OpenGL.GL import *
from vbo import VBO
from image import Image
from shader import Shader, Matrix
from item import *
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

        self.grid = np.array(data['layers'][0]['data'], np.uint32)

        # load objects
        self.obj1 = list(self.twiddle(data['layers'][1]['objects']))
        self.obj2 = list(self.twiddle(data['layers'][2]['objects']))
        self.obj3 = list(self.twiddle(data['layers'][3]['objects']))

        self.pickups = []

    @staticmethod
    def twiddle(src):
        for obj in src:
            t = obj['type']
            if t == 'food': item = Food(**obj)
            elif t == 'kebab': item = Schebab(**obj)
            elif t == 'key': item = QuestItem(**obj)
            else: raise ValueError, 'unknown type %s' % t
            yield item

    def draw(self, *args, **kwargs):
        Shader.upload_model(Matrix.identity())
        self.texture.texture_bind()
        self.vbo.draw(*args, **kwargs)

    def tile_at(self, pos):
        x = int(pos.x)
        y = -int(pos.y)
        if x < 0 or y < 0: return -1
        i = y * self.width + x
        try:
            return self.grid[i]
        except IndexError:
            return -1

    def update(self):
        self.pickups = [x for x in self.pickups if not x.killed]
