# pyright: reportWildcardImportFromLibrary=false

import numpy
import pygame
from random import randint
import sys
import typing

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader

from imagemanager import ImageManager
from inputmanager import InputManager
from level import Level
from levelselect import LevelSelect
from scene import Scene
from soundmanager import SoundManager

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
LOGICAL_WIDTH = 320
LOGICAL_HEIGHT = 180
FRAME_RATE = 60


class Game:
    clock = pygame.time.Clock()
    back_buffer: pygame.Surface
    game_window: pygame.Surface
    static: pygame.Surface
    program: typing.Any

    images: ImageManager
    inputs: InputManager
    sounds: SoundManager

    scene: Scene | None

    def __init__(self):
        pygame.init()

        self.back_buffer = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        self.game_window = pygame.display.set_mode(
            (WINDOW_WIDTH, WINDOW_HEIGHT),
            pygame.HWSURFACE | pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption('purpy')

        glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        glEnable(GL_BLEND)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_VERTEX_ARRAY)
        glEnable(GL_NORMAL_ARRAY)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        self.init_static()
        self.init_shader()

        self.images = ImageManager()
        self.inputs = InputManager()
        self.sounds = SoundManager()

        if len(sys.argv) > 1:
            self.scene = Level(None, sys.argv[1])
        else:
            self.scene = LevelSelect(None, 'assets/levels')

    def init_static(self):
        self.static = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))
        for x in range(LOGICAL_WIDTH):
            for y in range(LOGICAL_HEIGHT):
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
                     LOGICAL_WIDTH,
                     LOGICAL_HEIGHT,
                     0, GL_RGBA, GL_UNSIGNED_BYTE,
                     texture_data)

    def init_shader(self):
        src = open('./shader.frag')
        shader = compileShader(src, GL_FRAGMENT_SHADER)

        program = glCreateProgram()
        self.program = program
        glAttachShader(program, shader)
        glLinkProgram(program)
        glUseProgram(program)

        dest = self.compute_scaled_buffer_dest()
        res = glGetUniformLocation(program, 'iResolution')
        glUniform2f(res, dest.w, dest.h)

        offset = glGetUniformLocation(program, 'iOffset')
        glUniform2f(offset,
                    (WINDOW_WIDTH - dest.w) / 2.0,
                    (WINDOW_HEIGHT - dest.h) / 2.0)

        static_loc = glGetUniformLocation(program, 'iStatic')
        glUniform1i(static_loc, 1)

    def compute_scaled_buffer_dest(self) -> pygame.Rect:
        target_aspect_ratio = LOGICAL_WIDTH / LOGICAL_HEIGHT
        needed_width = target_aspect_ratio * WINDOW_HEIGHT
        if needed_width <= WINDOW_WIDTH:
            # The window is wider than needed.
            return pygame.Rect((WINDOW_WIDTH - needed_width)//2, 0, needed_width, WINDOW_HEIGHT)
        else:
            # The window is taller than needed.
            needed_height = WINDOW_WIDTH / target_aspect_ratio
            return pygame.Rect(0, (WINDOW_HEIGHT - needed_height)//2, WINDOW_WIDTH, needed_height)

    def update(self) -> bool:
        """ Returns True if the game should keep running. """
        if self.scene is None:
            return False

        # Update the actual game logic.
        self.scene = self.scene.update(self.inputs, self.sounds)
        if self.scene is None:
            return False

        self.inputs.update()

        # Clear the back buffer with solid black.
        back_buffer_src = pygame.Rect(0, 0, LOGICAL_WIDTH, LOGICAL_HEIGHT)
        self.back_buffer.fill((0, 0, 0), back_buffer_src)
        # Draw the scene.
        self.scene.draw(self.back_buffer, back_buffer_src, self.images)

        glClearColor(1, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # type: ignore

        time_loc = glGetUniformLocation(self.program, 'iTime')
        glUniform1f(time_loc, pygame.time.get_ticks() / 1000.0)

        texture_data = pygame.image.tobytes(self.back_buffer, 'RGBA', True)
        texture_id = glGenTextures(1)
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA,
                     LOGICAL_WIDTH,
                     LOGICAL_HEIGHT,
                     0, GL_RGBA, GL_UNSIGNED_BYTE,
                     texture_data)

        texture_coords = [
            0.0, 1.0,
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0,
        ]
        texture_coords_array = numpy.array(texture_coords, dtype=numpy.float32)

        vertices = [
            -1.0, 1.0,
            -1.0, -1.0,
            1.0, -1.0,
            1.0, 1.0,
        ]
        vertices_array = numpy.array(vertices, dtype=numpy.float32)

        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        if False:
            glVertexPointer(2, GL_FLOAT, 0, vertices_array)
            glTexCoordPointer(2, GL_FLOAT, 0, texture_coords_array)
            glDrawArrays(GL_QUADS, 0, 4)

        if False:
            glEnableVertexAttribArray(0)
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, vertices_array)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE,
                                  0, texture_coords_array)
            glDrawArrays(GL_QUADS, 0, 4)

        if True:
            glBegin(GL_QUADS)
            glColor3f(1, 0, 0)
            glVertex2f(-1, -1)
            glColor3f(0, 1, 0)
            glVertex2f(1, -1)
            glColor3f(0, 0, 1)
            glVertex2f(1, 1)
            glColor3f(1, 0, 1)
            glVertex2f(-1, 1)
            glEnd()

        glDisableClientState(GL_TEXTURE_COORD_ARRAY)

        glDeleteTextures(1, [texture_id])

        pygame.display.flip()

        return True

    def main(self):
        game_running = True
        while game_running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        game_running = False
                    case (pygame.KEYDOWN | pygame.KEYUP |
                          pygame.JOYBUTTONDOWN | pygame.JOYBUTTONUP |
                          pygame.JOYAXISMOTION | pygame.JOYHATMOTION |
                          pygame.JOYDEVICEADDED | pygame.JOYDEVICEREMOVED):
                        self.inputs.handle_event(event)

            if not self.update():
                game_running = False

            self.clock.tick(FRAME_RATE)
        pygame.quit()


game = Game()
game.main()
