#!/usr/bin/env python
# -*- coding: utf-8 -*-

import array, math
import cairo, pango, pangocairo
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from vbo import VBO

from pango import ALIGN_LEFT, ALIGN_CENTER, ALIGN_RIGHT

class HUD:
    def __init__(self, size):
        self.width, self.height = size.xy

        self.data = array.array('c', chr(0) * self.width * self.height * 4)

        stride = self.width * 4
        self.surface = cairo.ImageSurface.create_for_data(self.data, cairo.FORMAT_ARGB32, self.width, self.height, stride)
        self.texture = glGenTextures(1);

        self.cr = cairo.Context(self.surface)
        self.pango = pangocairo.CairoContext(self.cr)
        self.layout = self.pango.create_layout()

        # force subpixel rendering
        self.font_options = cairo.FontOptions()
        self.font_options.set_antialias(cairo.ANTIALIAS_SUBPIXEL)
        self.cr.set_font_options(self.font_options)

        glBindTexture(GL_TEXTURE_2D, self.texture);
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

        v = np.array([
                0,0,0, 0,1,
                size.x,0,0, 1,1,
                size.x,size.y,0, 1,0,
                0,size.y,0, 0,0,
                ], np.float32)
        i = np.array([0,1,2,3], np.uint32)
        self.vbo = VBO(GL_QUADS, v, i)

    def clear(self, color=(0,0,0,0)):
        self.cr.save()
        self.cr.set_source_rgba(color[0], color[1], color[2], color[3])
        self.cr.set_operator(cairo.OPERATOR_SOURCE)
        self.cr.paint()
        self.cr.restore()

    @classmethod
    def create_font(cls, font='Sans', size=12, raw=None):
        if raw is None:
            raw = '%s %f' % (font, size)
        return pango.FontDescription(raw)

    def text(self, text, font, color=(0,0,0,1), alignment=pango.ALIGN_LEFT, justify=False, width=None):
        cr = self.cr
        cr.set_source_rgba(*color)

        self.layout.context_changed()
        self.layout.set_font_description(font)

        if width:
            self.layout.set_width(int(width * pango.SCALE))

        self.layout.set_alignment(alignment)
        self.layout.set_justify(justify)
        self.layout.set_markup(text);
        self.pango.show_layout(self.layout)

        return self.layout.get_pixel_extents()

    def rectangle(self, x, y, w, h, color=(0,0,0,1)):
        self.cr.save()
        self.cr.set_source_rgba(color[0], color[1], color[2], color[3])
        self.cr.rectangle(x, y, w, h)
        self.cr.fill()
        self.cr.restore()

    def __enter__(self):
        self.cr.save()
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_BGRA, GL_UNSIGNED_BYTE, self.data.tostring())

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_BGRA, GL_UNSIGNED_BYTE, self.data.tostring())

        self.vbo.draw()
