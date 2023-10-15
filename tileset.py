
import math
import os.path
import pygame
import xml.etree.ElementTree


class TileSetImage:
    source: str
    width: int
    height: int

    def __init__(self, node: xml.etree.ElementTree.Element):
        self.source = node.attrib['source']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])


class TileSet:
    name: str
    tilewidth: int
    tileheight: int
    tilecount: int
    columns: int
    image: TileSetImage
    surface: pygame.Surface
    properties: dict[int, dict[str, str | bool | int]]

    def __init__(self, root: xml.etree.ElementTree.Element, path: str):
        self.name = root.attrib['name']
        self.tilewidth = int(root.attrib['tilewidth'])
        self.tileheight = int(root.attrib['tileheight'])
        self.tilecount = int(root.attrib['tilecount'])
        self.columns = int(root.attrib['columns'])
        self.image = [TileSetImage(node)
                      for node in root if node.tag == 'image'][0]
        self.properties = {}

        img_path = os.path.join(os.path.dirname(path), self.image.source)
        print('loading tileset texture from ' + img_path)
        img = pygame.image.load(img_path)
        self.surface = pygame.Surface.convert_alpha(img)

        for tile in [tile for tile in root if tile.tag == 'tile']:
            tile_id = int(tile.attrib['id'])
            self.properties[tile_id] = {}
            for node in [node for node in tile if node.tag == 'properties']:
                for pnode in [pnode for pnode in node if pnode.tag == 'property']:
                    name = pnode.attrib['name']
                    typ = pnode.attrib.get('type', 'str')
                    val = pnode.attrib['value']
                    if typ == "str":
                        self.properties[tile_id][name] = val
                    elif typ == "int":
                        self.properties[tile_id][name] = int(val)
                    elif typ == "bool":
                        self.properties[tile_id][name] = (val == 'true')
                    else:
                        raise Exception(f'unsupported property type {typ}')
        print(self.properties)

    @property
    def rows(self) -> int:
        return math.ceil(self.tilecount / self.columns)

    def get_source_rect(self, index: int) -> pygame.Rect:
        index = index - 1
        if index < 0 or index > self.tilecount:
            raise Exception("index out of range")
        row = index // self.columns
        col = index % self.columns
        x = col * self.tilewidth
        y = row * self.tileheight
        return pygame.Rect(x, y, self.tilewidth, self.tileheight)


def load_tileset(path: str) -> TileSet:
    print('loading tileset from ' + path)
    root = xml.etree.ElementTree.parse(path).getroot()
    if not isinstance(root, xml.etree.ElementTree.Element):
        raise Exception('root was not an element')
    return TileSet(root, path)
