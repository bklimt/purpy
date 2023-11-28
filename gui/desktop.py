
import pygame

from component import EdgeSpacing
from window import Window

FRAME_RATE = 60


class Desktop:
    clock = pygame.time.Clock()
    surface: pygame.Surface
    window: Window

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('purpy')
        self.surface = pygame.display.set_mode((1600, 1200))

        self.window = Window()
        self.window.border = EdgeSpacing(1)
        self.window.set_area(pygame.Rect(50, 50, 1200, 1000))

    def update(self) -> bool:
        self.surface.fill('#007f7f')
        self.window.draw(self.surface)
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
                        pass

            if not self.update():
                game_running = False

            self.clock.tick(FRAME_RATE)
        pygame.quit()


if __name__ == '__main__':
    desktop = Desktop()
    desktop.main()
