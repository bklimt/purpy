
import pygame

from gui.component import Component, EdgeSpacing
from gui.window import Window
from inputmanager import InputManager

FRAME_RATE = 60


class Desktop:
    clock = pygame.time.Clock()
    surface: pygame.Surface
    window: Window
    mouse_component: Component | None

    def __init__(self):
        pygame.init()
        pygame.display.set_caption('purpy')
        self.surface = pygame.display.set_mode((1600, 1200))

        self.window = Window()
        self.window.border = EdgeSpacing(1)
        self.window.set_area(pygame.Rect(50, 50, 1200, 1000))

        self.mouse_component = None

    def update_mouse(self, inputs: InputManager):
        if inputs.is_mouse_pressed():
            self.mouse_component = self.window.get_component_at(
                inputs.mouse_position)
            if self.mouse_component:
                self.mouse_component.mouse_pressed(inputs.mouse_position)
        if self.mouse_component:
            if inputs.state.is_mouse_button_down(1):
                self.mouse_component.mouse_dragged(inputs.mouse_position)
            else:
                self.mouse_component.mouse_released(inputs.mouse_position)
                current = self.window.get_component_at(inputs.mouse_position)
                if self.mouse_component == current:
                    self.mouse_component.mouse_clicked(inputs.mouse_position)
                self.mouse_component = None

    def update(self, inputs: InputManager) -> bool:
        inputs.update()
        self.update_mouse(inputs)
        self.surface.fill('#007f7f')
        self.window.draw(self.surface)
        pygame.display.flip()
        return True

    def main(self):
        inputs = InputManager()
        game_running = True
        while game_running:
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        game_running = False
                    case (pygame.KEYDOWN | pygame.KEYUP):
                        inputs.handle_keyboard_event(event)
                    case (pygame.JOYBUTTONDOWN | pygame.JOYBUTTONUP |
                          pygame.JOYAXISMOTION | pygame.JOYHATMOTION |
                          pygame.JOYDEVICEADDED | pygame.JOYDEVICEREMOVED):
                        inputs.handle_joystick_event(event)
                    case (pygame.MOUSEMOTION | pygame.MOUSEBUTTONDOWN | pygame.MOUSEBUTTONUP):
                        inputs.handle_mouse_event(event)

            if not self.update(inputs):
                game_running = False

            self.clock.tick(FRAME_RATE)
        pygame.quit()


if __name__ == '__main__':
    desktop = Desktop()
    desktop.main()
