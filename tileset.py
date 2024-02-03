
import math
import os.path
import pygame
import typing
import xml.etree.ElementTree

from slope import Slope
from spritesheet import Animation
from properties import load_properties, TileProperties, TileSetProperties


class TileSetImage:
    source: str
    width: int
    height: int

    def __init__(self, node: xml.etree.ElementTree.Element):
        self.source = node.attrib['source']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])


class ImageLoader(typing.Protocol):
    def load_image(self, path: str) -> pygame.Surface:
        raise Exception('abstract protocol')


class TileSet:
    name: str
    firstgid: int
    tilewidth: int
    tileheight: int
    tilecount: int
    columns: int
    image: TileSetImage
    surface: pygame.Surface
    animations: dict[int, Animation]
    slopes: dict[int, Slope]
    properties: TileSetProperties
    default_tile_properties: TileProperties
    tile_properties: dict[int, TileProperties]

    def __init__(self, root: xml.etree.ElementTree.Element, path: str, firstgid: int, images: ImageLoader):
        self.name = root.attrib['name']
        self.firstgid = firstgid
        self.tilewidth = int(root.attrib['tilewidth'])
        self.tileheight = int(root.attrib['tileheight'])
        self.tilecount = int(root.attrib['tilecount'])
        self.columns = int(root.attrib['columns'])
        self.image = [TileSetImage(node)
                      for node in root if node.tag == 'image'][0]

        img_path = os.path.join(os.path.dirname(path), self.image.source)
        print('loading tileset texture from ' + img_path)
        self.surface = images.load_image(img_path)

        self.properties = TileSetProperties(load_properties(root))

        self.slopes = {}
        self.default_tile_properties = TileProperties({})
        self.tile_properties = {}
        for tile in [tile for tile in root if tile.tag == 'tile']:
            tile_id = int(tile.attrib['id'])
            self.tile_properties[tile_id] = TileProperties(
                load_properties(tile))
            if self.tile_properties[tile_id].slope:
                self.slopes[tile_id] = Slope(self.tile_properties[tile_id])

        print(f'tileset properties: {self.properties}')
        print(f'tile properties: {self.tile_properties}')

        self.animations = {}
        tile_animations_path = self.properties.animations
        if tile_animations_path is not None:
            tile_animations_path = os.path.join(
                os.path.dirname(path), tile_animations_path)
            self.load_tile_animations(tile_animations_path, images)

    def load_tile_animations(self, path: str, images: ImageLoader):
        """ Loads a directory of animations to replace tiles. """
        print(f'loading tile animations from {path}')
        filenames = os.listdir(path)
        for filename in filenames:
            if filename.endswith('.png'):
                tile_id = int(filename[:-4])
                filepath = os.path.join(path, filename)
                print(f'loading animation for tile {tile_id} from {filepath}')
                surface = images.load_image(filepath)
                animation = Animation(surface, 8, 8)
                self.animations[tile_id] = animation
            else:
                print(f'skipping file {filename}')

    def get_local_index(self, tile_gid: int) -> int | None:
        if tile_gid < self.firstgid:
            return None
        return tile_gid - self.firstgid

    def get_global_index(self, tile_id: int) -> int:
        return tile_id + self.firstgid

    def gid_sort_key(self) -> int:
        return -self.firstgid

    def is_slope(self, tile_id: int) -> bool:
        return tile_id in self.slopes

    def get_slope(self, tile_id: int) -> Slope:
        return self.slopes[tile_id]

    def get_tile_properties(self, tile_id: int) -> TileProperties:
        return self.tile_properties.get(tile_id, self.default_tile_properties)

    def update_animations(self):
        for tile_id in self.animations.keys():
            self.animations[tile_id].update()

    @property
    def rows(self) -> int:
        return math.ceil(self.tilecount / self.columns)

    def get_source_rect(self, index: int) -> pygame.Rect:
        if index < 0 or index > self.tilecount:
            raise Exception("index out of range")
        row = index // self.columns
        col = index % self.columns
        x = col * self.tilewidth
        y = row * self.tileheight
        return pygame.Rect(x, y, self.tilewidth, self.tileheight)


def load_tileset(path: str, firstgid: int, images: ImageLoader) -> TileSet:
    print('loading tileset from ' + path)
    root = xml.etree.ElementTree.parse(path).getroot()
    if not isinstance(root, xml.etree.ElementTree.Element):
        raise Exception('root was not an element')
    return TileSet(root, path, firstgid, images)
