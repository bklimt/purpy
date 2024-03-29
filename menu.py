
# Import the whole module to avoid a circular reference.
import level
import levelselect

from cursor import Cursor
from imagemanager import ImageManager
from inputmanager import InputSnapshot
from render.rendercontext import RenderContext
from scene import Scene
from soundmanager import SoundManager
from switchstate import SwitchState
from tilemap import TileMap, load_map
from uibutton import UiButton


class Menu:
    previous: Scene | None
    cancel_action: str
    reload_path: str | None
    images: ImageManager
    cursor: Cursor
    tilemap: TileMap
    buttons: list[UiButton]
    horizontal_button_order: list[int]
    vertical_button_order: list[int]
    selected: int
    switches: SwitchState

    def __init__(self, path: str, parent: Scene | None, reload_path: str | None, images: ImageManager):
        self.previous = parent
        self.reload_path = reload_path
        self.images = images
        self.cursor = Cursor(images)
        self.tilemap = load_map(path, images)
        self.switches = SwitchState()

        self.cancel_action = self.tilemap.properties.cancel_action

        self.buttons = []
        for obj in self.tilemap.objects:
            if obj.properties.uibutton:
                self.buttons.append(
                    UiButton(obj, self.tilemap.tilewidth, self.tilemap.tileheight, images))

        button_positions = [(i, button.x, button.y)
                            for (i, button) in enumerate(self.buttons)]
        button_positions.sort(key=lambda b: (b[2], b[1]))
        self.horizontal_button_order = [b[0] for b in button_positions]
        button_positions.sort(key=lambda b: (b[1], b[2]))
        self.vertical_button_order = [b[0] for b in button_positions]
        self.selected = self.vertical_button_order[0]

    def parent(self) -> Scene | None:
        return self.previous

    def next_button(self, delta: int, order: list[int]):
        pos = order.index(self.selected)
        new_pos = (pos + len(order) + delta) % len(order)
        self.selected = order[new_pos]

    def perform_action(self, action: str) -> Scene | None:
        if action.startswith('levelselect:'):
            return levelselect.LevelSelect(self, action[12:], self.images)
        elif action.startswith('level:'):
            return level.Level(self, action[6:], self.images)
        elif action.startswith('menu:'):
            return Menu(action[5:], self, None, self.images)
        elif action == 'pop':
            return self.previous
        elif action == 'pop2':
            if self.previous is None:
                raise Exception('tried to exit with empty scene stack')
            return self.previous.parent()
        elif action == 'reload':
            if self.reload_path is None:
                raise Exception(
                    'tried to reload when level path not set')
            if self.previous is None:
                raise Exception('tried to exit with empty scene stack')
            return level.Level(self.previous.parent(), self.reload_path, self.images)
        else:
            raise Exception(f'invalid button action {action}')

    def update(self, inputs: InputSnapshot, images: ImageManager, sounds: SoundManager) -> Scene | None:
        if inputs.cancel:
            return self.perform_action(self.cancel_action)

        if inputs.menu_down:
            self.next_button(1, self.vertical_button_order)
        if inputs.menu_up:
            self.next_button(-1, self.vertical_button_order)
        if inputs.menu_left:
            self.next_button(-1, self.horizontal_button_order)
        if inputs.menu_right:
            self.next_button(1, self.horizontal_button_order)

        self.cursor.update(inputs)
        for i, button in enumerate(self.buttons):
            selected = i == self.selected
            action = button.update(selected, inputs, sounds)
            if action is not None:
                return self.perform_action(action)

        return self

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        context.player_batch.draw_rect(context.logical_area, '#330033')

        if self.previous is not None:
            self.previous.draw(context, images)

        self.tilemap.draw_background(
            context, context.hud_batch, context.logical_area, (0, 0), self.switches)
        self.tilemap.draw_foreground(
            context, context.hud_batch, context.logical_area, (0, 0), self.switches)
        for button in self.buttons:
            button.draw(context, context.hud_batch, images.font)
        self.cursor.draw(context, context.hud_batch)
