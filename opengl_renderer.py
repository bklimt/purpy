# pyright: reportWildcardImportFromLibrary=false

from random import randint
import typing

import pygame

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader

from rendercontext import RenderContext


class Texture:
    constant: Constant
    unit: int
    name: int

    def __init__(self, constant: Constant, unit: int) -> None:
        self.constant = constant
        self.unit = unit
        self.name = glGenTextures(1)

    def free(self):
        glDeleteTextures([self.name])


class OpenGLRenderer:
    program: typing.Any
    logical_rect: pygame.Rect
    destination_rect: pygame.Rect
    window_rect: pygame.Rect

    static_texture: Texture

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
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.static_texture = Texture(GL_TEXTURE1, 1)

        self.init_static()
        self.init_shader()

    def set_texture_data(self, texture: Texture, surface: pygame.Surface):
        texture_data = pygame.image.tobytes(surface, 'RGBA', True)
        glActiveTexture(texture.constant)
        glBindTexture(GL_TEXTURE_2D, texture.name)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     self.logical_rect.w,
                     self.logical_rect.h,
                     0, GL_RGBA, GL_UNSIGNED_BYTE,
                     texture_data)

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

        self.set_texture_data(self.static_texture, self.static)

    def set_constant_inputs(self):
        res = glGetUniformLocation(self.program, 'iResolution')
        glUniform2f(res, self.destination_rect.w, self.destination_rect.h)

        offset = glGetUniformLocation(self.program, 'iOffset')
        glUniform2f(offset,
                    (self.window_rect.w - self.destination_rect.w) / 2.0,
                    (self.window_rect.h - self.destination_rect.h) / 2.0)

        glUniform1i(glGetUniformLocation(self.program, 'iStaticTexture'),
                    self.static_texture.unit)

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

        self.set_constant_inputs()

        vertices = [
            -1.0, 1.0,
            -1.0, -1.0,
            1.0, -1.0,
            1.0, 1.0,
        ]
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, vertices)

    def set_shader_inputs(self, context: RenderContext):
        glUniform1f(glGetUniformLocation(self.program, 'iTime'),
                    pygame.time.get_ticks() / 1000.0)
        glUniform2f(glGetUniformLocation(self.program, 'iTextureSize'),
                    context.logical_size[0], context.logical_size[1])
        glUniform1i(glGetUniformLocation(self.program, 'iDark'),
                    context.dark)

        ls = context.lights
        if len(ls) > 20:
            ls = ls[:20]

        glUniform1i(glGetUniformLocation(
            self.program, 'iSpotlightCount'), len(ls))

        glUniform2fv(glGetUniformLocation(self.program, 'iSpotlightPosition'),
                     len(ls),
                     [l.position for l in ls])

        glUniform1fv(glGetUniformLocation(self.program, 'iSpotlightRadius'),
                     len(ls),
                     [l.radius for l in ls])

    def render(self, context: RenderContext):
        surface = context.player_surface

        glClearColor(0, 0, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        self.set_shader_inputs(context)

        hud_texture = Texture(GL_TEXTURE2, 2)
        self.set_texture_data(hud_texture, context.hud_surface)
        glUniform1i(glGetUniformLocation(self.program, 'iHudTexture'),
                    hud_texture.unit)

        player_texture = Texture(GL_TEXTURE0, 0)
        self.set_texture_data(player_texture, context.player_surface)
        glUniform1i(glGetUniformLocation(self.program, 'iPlayerTexture'),
                    player_texture.unit)

        glEnableClientState(GL_TEXTURE_COORD_ARRAY)
        glDrawArrays(GL_QUADS, 0, 4)
        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        hud_texture.free()
        player_texture.free()

        pygame.display.flip()
