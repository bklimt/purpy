
import typing

from imagemanager import ImageManager
from inputmanager import InputSnapshot
from render.rendercontext import RenderContext
from soundmanager import SoundManager


class Scene(typing.Protocol):
    def parent(self) -> 'Scene | None':
        raise Exception('abstract base class')

    def update(self, inputs: InputSnapshot, images: ImageManager, sounds: SoundManager) -> 'Scene | None':
        raise Exception('abstract base class')

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        raise Exception('abstract base class')
