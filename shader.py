import re
from OpenGL.GL import *
from OpenGL.GLU import *
from os.path import exists, join

file_counter = 1
file_lut = {}
re_inc = re.compile(r'#\s*include\s+[<"](.*)[<"]')
re_log = re.compile("([0-9]+)[(]([0-9]+)[)] \\: ([a-zA-Z]+) ([a-zA-Z0-9]+)\\: (.+)")

def file_id(filename):
    global file_lut, file_counter
    if filename not in file_lut:
        file_lut[filename] = file_counter
        file_counter += 1
    return file_lut[filename]

def file_reverse(id):
    # hack
    global file_lut
    id = int(id)
    for k,v in file_lut.iteritems():
        if v == id: return k
    raise KeyError, 'No file with id %d' % id

def preprocess(source, parent_id):
    global re_inc, file_lut

    for i, line in enumerate(source.splitlines()):
        line = line.strip()

        # hack to put a #line marker after #version so errors is marked correctly
        if i == 0 and line[:8] == '#version':
            yield line
            yield '#line %d %s' % (2, parent_id)
            continue

        match = re_inc.match(line)
        if match:
            filename = join('data/shader', match.group(1))
            id = file_id(filename)
            with open(filename) as fp:
                yield '#line %d %s' % (1, id)
                for x in preprocess(fp.read(), id):
                    yield x
                yield '#line %d %d' % (i+2, parent_id)
        else:
            yield line

class Shader(object):
    def __init__(self, name):
        self.initialize()

        self.sp = glCreateProgram()
        self.add_shader(name, '.vs', GL_VERTEX_SHADER)
        self.add_shader(name, '.fs', GL_FRAGMENT_SHADER)
        glLinkProgram(self.sp)

        self.bind()

        self.m = glGetUniformLocation(self.sp, 'm')
        self.p = glGetUniformLocation(self.sp, 'p')
        self.pv = glGetUniformLocation(self.sp, 'pv')

        self.unbind()

    def add_shader(self, filename, ext, type):
        shader = glCreateShader(type)

        fullpath = join('data/shader', filename) + ext
        if not exists(fullpath):
            assert filename != 'default'
            return self.add_shader('default', ext, type)

        with open(fullpath) as fp:
            id = file_id(fullpath)
            source = '\n'.join(preprocess(fp.read(), id))

        glShaderSource(shader, source)
        glCompileShader(shader)
        glAttachShader(self.sp, shader)

        self.print_log(shader)

    def print_log(self, obj):
        global re_log
        if glIsShader(obj):
            raw = glGetShaderInfoLog(obj)
        else:
            raw = glGetProgramInfoLog(obj)
        for line in raw.splitlines():
            match = re_log.match(line)
            if match:
                file_id, line_num, severity, reference, message = match.groups()
                try:
                    filename = file_reverse(file_id)
                except KeyError:
                    filename = '<unknown>'
                print '%s:%s: %s: %s [%s]' % (filename, line_num, severity, message, reference)
            else:
                print line

    def bind(self):
        glUseProgram(self.sp)

    @staticmethod
    def unbind():
        glUseProgram(0)

    def upload(self, p):
        glUniformMatrix4fv(self.p, 1, False, p)

    @staticmethod
    def initialize():
        for i in range(1):
            glEnableVertexAttribArray(i)

class Matrix:
    @staticmethod
    def perspective(fov, size, near, far):
        glLoadIdentity()
        gluPerspective(fov, size.ratio(), near, far)
        return glGetFloatv(GL_MODELVIEW_MATRIX)

    @staticmethod
    def lookat(ex, ey, ez, cx, cy, cz, ux, uy, uz):
        glLoadIdentity()
        gluLookAt(ex, ey, ez, cx, cy, cz, ux, uy, uz)
        return glGetFloatv(GL_MODELVIEW_MATRIX)

    @staticmethod
    def identity():
        glLoadIdentity()
        return glGetFloatv(GL_MODELVIEW_MATRIX)
