
import datetime
import pygame

from args import Args
from constants import *
from imagemanager import ImageManager
from inputmanager import InputManager
from level import Level
from levelselect import LevelSelect
from menu import Menu
from render.rendercontext import RenderContext
from render.renderer import Renderer
from scene import Scene
from soundmanager import SoundManager

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
    frame: int

    def __init__(self, args: Args):
        pygame.init()
        pygame.display.set_caption('purpy')
        pygame.mouse.set_visible(False)

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
        self.inputs = InputManager(args.playback)
        self.sounds = SoundManager()
        self.frame = 0

        # self.scene = LevelSelect(None, 'assets/levels', self.images)
        self.scene = Menu('assets/menus/start.tmx', None, self.images)

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
        snapshot = self.inputs.update(self.frame)
        self.scene = self.scene.update(snapshot, self.sounds)
        self.frame += 1

        if self.scene is None:
            return False

        # Draw the scene.
        self.render_context.clear()
        self.scene.draw(self.render_context, self.images)
        self.renderer.render(self.render_context)

        return True

    def main(self, args: Args):
        start_time = datetime.datetime.now()
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
                    case (pygame.MOUSEMOTION | pygame.MOUSEBUTTONUP | pygame.MOUSEBUTTONDOWN):
                        self.inputs.handle_mouse_event(event)

            if not self.update():
                game_running = False

            if args.speed_test:
                self.clock.tick(0)
            else:
                self.clock.tick(FRAME_RATE)
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        fps = self.frame / duration.total_seconds()
        if args.speed_test:
            print(f"{fps} fps, {self.frame} frames in {duration.total_seconds()}s")
        pygame.quit()


args = Args()
print(f'args: {args}')

game = Game(args)
game.main(args)
