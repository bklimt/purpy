
from enum import Enum

import pygame


class DockDirection(Enum):
    FLOATING = 1
    LEFT = 2
    RIGHT = 3
    TOP = 4
    BOTTOM = 5
    CENTER = 6


class Window:
    rect: pygame.Rect
    color: pygame.Color
    children: list['Window']
    docked: DockDirection = DockDirection.FLOATING

    def __init__(self, rect: pygame.Rect, color: pygame.Color):
        self.rect = rect
        self.color = color
        self.children = []

    def add_child(self, window):
        self.children.append(window)

    def draw(self, canvas: pygame.Surface, parent_rect: pygame.Rect):
        my_rect = self.rect.move(parent_rect.topleft)
        my_rect = my_rect.clip(parent_rect)
        pygame.draw.rect(canvas, self.color, my_rect)
        for child in self.children:
            child.draw(canvas, my_rect)

    def get_preferred_width(self, height: int) -> int:
        # TODO: get the preferred width of each child.
        return 50

    def get_preferred_height(self, width: int) -> int:
        # TODO: get the preferred height of each child.
        return 50

    def lay_out(self):
        # Figure out the height of each part.
        total = 0
        for child in self.children:
            if child.docked == DockDirection.TOP or child.docked == DockDirection.BOTTOM:
                total += child.get_preferred_height


class WindowDemo:
    desktop: pygame.Surface
    main_window: Window

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('purpy')
        self.desktop = pygame.display.set_mode((900, 900))

        self.main_window = Window(pygame.Rect(100, 100, 640, 480),
                                  pygame.Color(255, 255, 255))

        title_bar = Window(pygame.Rect(10, 10, 50, 50),
                           pygame.Color(0, 0, 127))
        title_bar.docked = DockDirection.TOP
        self.main_window.add_child(title_bar)

    def update(self) -> bool:
        self.main_window.draw(self.desktop, pygame.Rect(0, 0, 900, 900))
        return True

    def run(self):
        clock = pygame.time.Clock()
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

            if not game_running:
                break

            game_running = self.update()
            pygame.display.update()

            clock.tick(60)
        pygame.quit()


if __name__ == '__main__':
    demo = WindowDemo()
    demo.run()
