
import pygame
import sys

from constants import *
from soundmanager import SoundManager
from scene import Scene
from levelselect import LevelSelect
from level import Level
from inputmanager import InputManager
from imagemanager import ImageManager
from render.renderer import Renderer
from render.rendercontext import RenderContext

if USE_OPENGL:
    from render.opengl_renderer import OpenGLRenderer
else:
    from render.pygame_renderer import PygameRenderer


class Game:
    clock = pygame.time.Clock()
    static: pygame.Surface
    renderer: Renderer
    render_context: RenderContext

    images: ImageManager
    inputs: InputManager
    sounds: SoundManager

    scene: Scene | None

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('purpy')

        destination = self.compute_scaled_buffer_dest()
        window = pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        print('initializing render context')
        render_area = pygame.Rect(0, 0, RENDER_WIDTH, RENDER_HEIGHT)
        self.render_context = RenderContext(render_area.size)
        print('initializing renderer')
        if USE_OPENGL:
            self.renderer = OpenGLRenderer(render_area, destination, window)
        else:
            self.renderer = PygameRenderer(render_area, destination, window)

        print('loading game content')
        self.images = ImageManager()
        self.inputs = InputManager()
        self.sounds = SoundManager()

        if len(sys.argv) > 1:
            self.scene = Level(None, sys.argv[1], self.images)
        else:
            self.scene = LevelSelect(None, 'assets/levels', self.images)

    def compute_scaled_buffer_dest(self) -> pygame.Rect:
        target_aspect_ratio = RENDER_WIDTH / RENDER_HEIGHT
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

        # Draw the scene.
        self.render_context.clear()
        self.scene.draw(self.render_context, self.images)
        self.renderer.render(self.render_context)

        return True

    def main(self):
        game_running = True
        while game_running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        game_running = False
                    case (pygame.KEYDOWN | pygame.KEYUP):
                        self.inputs.handle_keyboard_event(event)
                    case (pygame.JOYBUTTONDOWN | pygame.JOYBUTTONUP |
                          pygame.JOYAXISMOTION | pygame.JOYHATMOTION |
                          pygame.JOYDEVICEADDED | pygame.JOYDEVICEREMOVED):
                        self.inputs.handle_joystick_event(event)

            if not self.update():
                game_running = False

            self.clock.tick(FRAME_RATE)
        pygame.quit()


game = Game()
game.main()
