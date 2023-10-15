
import math
import os.path
import pygame
from tileset import TileSet, load_tileset
import xml.etree.ElementTree


class Layer:
    id: int
    name: str
    width: int
    height: int
    data: list[list[int]]
    player: bool

    def __init__(self, node: xml.etree.ElementTree.Element):
        self.id = int(node.attrib['id'])
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.player = False
        for properties in node:
            if properties.tag != 'properties':
                continue
            for prop in properties:
                if prop.tag != 'property':
                    continue
                name = prop.attrib['name']
                if name == 'player':
                    value = prop.attrib['value']
                    if value == 'true':
                        self.player = True

        self.data = []
        csv = (
            [data for data in node if data.tag == 'data'][0].text or ""
        ).strip()
        indices = [int(index.strip()) for index in csv.split(',')]
        if len(indices) != self.width * self.height:
            raise Exception('csv size does not match')
        for i in range(self.height):
            row: list[int] = []
            for j in range(self.width):
                row.append(indices[i * self.width + j])
            self.data.append(row)


class MapObject:
    id: int
    gid: int
    x: int
    y: int
    width: int
    height: int
    properties: dict[str, str | int | bool]

    def __init__(self, node: xml.etree.ElementTree.Element, tileset: TileSet):
        self.id = int(node.attrib['id'])
        self.gid = int(node.attrib['gid'])
        self.x = int(node.attrib['x'])
        self.y = int(node.attrib['y'])
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])
        self.properties = {}
        for k, v in tileset.properties.get(self.gid - 1, {}).items():
            self.properties[k] = v
        for props in [child for child in node if child.tag == 'properties']:
            for prop in [child for child in props if child.tag == 'property']:
                name = prop.attrib['name']
                typ = prop.get('type', 'string')
                val = prop.attrib['value']
                if typ == 'string':
                    self.properties[name] = val
                elif typ == 'int':
                    self.properties[name] = int(val)
                elif typ == 'bool':
                    self.properties[name] = (val == 'true')
                else:
                    raise Exception(f'invalid type {typ}')
        # For some reason, the position is the bottom left.
        self.y -= self.height

    def __repr__(self):
        return f'MapObject(id={self.id}, gid={self.gid}, x={self.x}, y={self.y}, properties={self.properties}'


class TileMap:
    width: int
    height: int
    tilewidth: int
    tileheight: int
    backgroundcolor: str
    tilesetsource: str
    tileset: TileSet
    layers: list[Layer]
    player_layer: int | None
    objects: list[MapObject]

    def __init__(self, root: xml.etree.ElementTree.Element, path: str):
        self.width = int(root.attrib['width'])
        self.height = int(root.attrib['height'])
        self.tilewidth = int(root.attrib['tilewidth'])
        self.tileheight = int(root.attrib['tileheight'])
        self.backgroundcolor = root.attrib['backgroundcolor']
        self.tilesetsource = [
            ts for ts in root if ts.tag == 'tileset'][0].attrib['source']
        self.tileset = load_tileset(os.path.join(
            os.path.dirname(path), self.tilesetsource))
        self.layers = [Layer(layer) for layer in root if layer.tag == 'layer']

        player_layers = [
            layer for layer
            in enumerate(self.layers)
            if layer[1].player]
        if len(player_layers) > 1:
            raise Exception('too many player layers')
        self.player_layer = None
        if len(player_layers) > 0:
            self.player_layer = player_layers[0][0]

        self.objects = []
        for object_group in [node for node in root if node.tag == 'objectgroup']:
            for obj in [obj for obj in object_group if obj.tag == 'object']:
                self.objects.append(MapObject(obj, self.tileset))
        for obj in self.objects:
            print(f'loaded object {obj}')

    def draw_background(self, surface: pygame.Surface, dest: pygame.Rect, offset: tuple[float, float]):
        surface.fill(self.backgroundcolor, dest)
        for layer in self.layers:
            self.draw_layer(surface, dest, offset, layer)
            if layer.player:
                return

    def draw_foreground(self, surface: pygame.Surface, dest: pygame.Rect, offset: tuple[float, float]):
        if self.player_layer is None:
            return
        drawing = False
        for layer in self.layers:
            if drawing:
                self.draw_layer(surface, dest, offset, layer)
            if layer.player:
                drawing = True

    def draw_layer(self, surface: pygame.Surface, dest: pygame.Rect, offset: tuple[float, float], layer: Layer):
        # pygame.draw.rect(surface, self.backgroundcolor, dest)

        offset_x = int(offset[0])
        offset_y = int(offset[1])
        row_count = math.ceil(dest.height / self.tileheight) + 1
        col_count = math.ceil(dest.width / self.tilewidth) + 1

        start_row = offset_y // -self.tileheight
        end_row = start_row + row_count
        if start_row < 0:
            start_row = 0
        if end_row > self.height:
            end_row = self.height

        start_col = offset_x // -self.tilewidth
        end_col = start_col + col_count
        if start_col < 0:
            start_col = 0
        if end_col > self.width:
            end_col = self.width

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                # Compute what to draw where.
                index = layer.data[row][col]
                if index == 0:
                    continue
                source = self.tileset.get_source_rect(index)
                pos_x = col * self.tilewidth + dest.left + offset_x
                pos_y = row * self.tileheight + dest.top + offset_y

                # If it's off the top/left side, trim it.
                if pos_x < dest.left:
                    source.left = source.left + (dest.left - pos_x)
                    source.width = source.width - (dest.left - pos_x)
                    pos_x = dest.left
                if pos_y < dest.top:
                    source.top = source.top + (dest.top - pos_y)
                    source.height = source.height - (dest.top - pos_y)
                    pos_y = dest.top
                if source.width <= 0 or source.height <= 0:
                    continue

                # If it's off the right/bottom side, trim it.
                pos_right = pos_x + self.tilewidth
                if pos_right >= dest.right:
                    source.width = source.width - (pos_right - dest.right)
                if source.width <= 0:
                    continue
                pos_bottom = pos_y + self.tileheight
                if pos_bottom >= dest.bottom:
                    source.height = source.height - \
                        (pos_bottom - dest.bottom)
                if source.height <= 0:
                    continue

                # Draw the rest of the turtle.
                pos = (pos_x, pos_y)
                surface.blit(self.tileset.surface, pos, source)

    def intersect(self, rect: pygame.Rect):
        row1 = rect.top // self.tileheight
        col1 = rect.left // self.tilewidth
        row2 = rect.bottom // self.tileheight
        col2 = rect.right // self.tilewidth
        if row1 < 0:
            row1 = 0
        if col1 < 0:
            col1 = 0
        if row2 < 0:
            row2 = 0
        if col2 < 0:
            col2 = 0
        for row in range(row1, row2+1):
            for col in range(col1, col2+1):
                for layer in self.layers:
                    if layer.player or self.player_layer is None:
                        index = layer.data[row][col]
                        if index == 0:
                            continue
                        return True
        return False


def load_map(path: str):
    print('loading map from ' + path)
    root = xml.etree.ElementTree.parse(path).getroot()
    if not isinstance(root, xml.etree.ElementTree.Element):
        raise Exception('root was not an element')
    return TileMap(root, path)
