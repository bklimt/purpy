
from cursor import Cursor
from imagemanager import ImageManager
from inputmanager import InputSnapshot
from level import Level
from levelselect import LevelSelect
from render.rendercontext import RenderContext
from scene import Scene
from soundmanager import SoundManager
from switchstate import SwitchState
from tilemap import TileMap, load_map
from uibutton import UiButton


class Menu:
    parent: Scene | None
    images: ImageManager
    cursor: Cursor
    tilemap: TileMap
    buttons: list[UiButton]
    selected: int

    def __init__(self, path: str, parent: Scene | None, images: ImageManager):
        self.parent = parent
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

    def update(self, inputs: InputSnapshot, sounds: SoundManager) -> Scene | None:
        if inputs.cancel:
            return self.parent

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
                    return LevelSelect(self, action[12:], self.images)
                elif action.startswith('level:'):
                    return Level(self, action[6:], self.images)
                elif action.startswith('menu:'):
                    return Menu(action[5:], self, self.images)
                else:
                    raise Exception(f'invalid button action {action}')
        return self

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        context.player_batch.draw_rect(context.logical_area, '#330033')
        self.tilemap.draw_background(
            context, context.hud_batch, context.logical_area, (0, 0), self.switches)
        self.tilemap.draw_foreground(
            context, context.hud_batch, context.logical_area, (0, 0), self.switches)
        for button in self.buttons:
            button.draw(context, context.hud_batch, images.font)
        self.cursor.draw(context, context.hud_batch)
