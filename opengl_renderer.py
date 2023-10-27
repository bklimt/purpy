
from random import randint
import typing

import pygame

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader


class OpenGLRenderer:
    program: typing.Any
    logical_rect: pygame.Rect
    destination_rect: pygame.Rect
    window_rect: pygame.Rect

    def __init__(self,
                 logical: pygame.Rect,
                 destination: pygame.Rect,
                 window: pygame.Rect) -> None:
        self.logical_rect = logical
        self.destination_rect = destination
        self.window_rect = window

        pygame.display.set_mode(
            window.size,
            pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)

        print('initializing opengl')
        glViewport(0, 0, window.w, window.h)
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_VERTEX_ARRAY)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.init_static()
        self.init_shader()

    def init_static(self):
        print('initializing static')
        self.static = pygame.Surface(self.logical_rect.size)
        for x in range(self.logical_rect.w):
            for y in range(self.logical_rect.h):
                r = randint(0, 255)
                g = randint(0, 255)
                b = randint(0, 255)
                color = pygame.Color(r, g, b)
                self.static.set_at((x, y), color)

        texture_data = pygame.image.tobytes(self.static, 'RGBA', True)
        texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     self.logical_rect.w,
                     self.logical_rect.h,
                     0, GL_RGBA, GL_UNSIGNED_BYTE,
                     texture_data)

    def init_shader(self):
        print('initializing shader')
        frag_src = open('./shader.frag')
        frag_shader = compileShader(frag_src, GL_FRAGMENT_SHADER)

        vert_src = open('./shader.vert')
        vert_shader = compileShader(vert_src, GL_VERTEX_SHADER)

        program = glCreateProgram()
        self.program = program
        glAttachShader(program, frag_shader)
        glAttachShader(program, vert_shader)
        glLinkProgram(program)
        glUseProgram(program)

        res = glGetUniformLocation(program, 'iResolution')
        glUniform2f(res, self.destination_rect.w, self.destination_rect.h)

        offset = glGetUniformLocation(program, 'iOffset')
        glUniform2f(offset,
                    (self.window_rect.w - self.destination_rect.w) / 2.0,
                    (self.window_rect.h - self.destination_rect.h) / 2.0)

        static_loc = glGetUniformLocation(program, 'iStatic')
        glUniform1i(static_loc, 1)

        vertices = [
            -1.0, 1.0,
            -1.0, -1.0,
            1.0, -1.0,
            1.0, 1.0,
        ]
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, vertices)

    def render(self, surface: pygame.Surface):
        glClearColor(0, 0, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        time_loc = glGetUniformLocation(self.program, 'iTime')
        glUniform1f(time_loc, pygame.time.get_ticks() / 1000.0)

        texture_data = pygame.image.tobytes(surface, 'RGBA', True)
        texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     self.logical_rect.w,
                     self.logical_rect.h,
                     0, GL_RGBA, GL_UNSIGNED_BYTE,
                     texture_data)

        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glDrawArrays(GL_QUADS, 0, 4)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)
        glDeleteTextures(1, [texture_id])

        pygame.display.flip()
