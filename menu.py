
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
    reload_path: str | None
    images: ImageManager
    cursor: Cursor
    tilemap: TileMap
    buttons: list[UiButton]
    selected: int
    switches: SwitchState

    def __init__(self, path: str, parent: Scene | None, reload_path: str | None, images: ImageManager):
        self.previous = parent
        self.reload_path = reload_path
        self.images = images
        self.cursor = Cursor(images)
        self.tilemap = load_map(path, images)
        self.switches = SwitchState()
        self.buttons = []
        self.selected = 0
        for obj in self.tilemap.objects:
            if obj.properties.uibutton is not None:
                self.buttons.append(
                    UiButton(obj, self.tilemap.tilewidth, self.tilemap.tileheight, images))

    def parent(self) -> Scene | None:
        return self.previous

    def update(self, inputs: InputSnapshot, images: ImageManager, sounds: SoundManager) -> Scene | None:
        if inputs.cancel:
            return self.previous

        if inputs.menu_down:
            self.selected = (self.selected + 1) % len(self.buttons)
        if inputs.menu_up:
            self.selected = (self.selected - 1) % len(self.buttons)

        self.cursor.update(inputs)
        for i, button in enumerate(self.buttons):
            selected = i == self.selected
            action = button.update(selected, inputs, sounds)
            if action is not None:
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
