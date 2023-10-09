
import math
import os.path
import pygame
import tileset as ts
import xml.etree.ElementTree


class Layer:
    id: int
    name: str
    width: int
    height: int
    data: list[list[int]]

    def __init__(self, node: xml.etree.ElementTree.Element):
        self.id = int(node.attrib['id'])
        self.name = node.attrib['name']
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])

        self.data = []
        csv = ([data for data in node if data.tag == 'data']
               [0].text or "").strip()
        indices = [int(index.strip()) for index in csv.split(',')]
        if len(indices) != self.width * self.height:
            raise Exception('csv size does not match')
        for i in range(self.height):
            row: list[int] = []
            for j in range(self.width):
                row.append(indices[i * self.width + j])
            self.data.append(row)


class TileMap:
    width: int
    height: int
    tilewidth: int
    tileheight: int
    tilesetsource: str
    tileset: ts.TileSet
    layers: list[Layer]

    def __init__(self, root: xml.etree.ElementTree.Element, path: str):
        self.width = int(root.attrib['width'])
        self.height = int(root.attrib['height'])
        self.tilewidth = int(root.attrib['tilewidth'])
        self.tileheight = int(root.attrib['tileheight'])
        self.tilesetsource = [
            ts for ts in root if ts.tag == 'tileset'][0].attrib['source']
        self.tileset = ts.load_tileset(os.path.join(
            os.path.dirname(path), self.tilesetsource))
        self.layers = [Layer(layer) for layer in root if layer.tag == 'layer']

    def draw(self, surface: pygame.Surface, dest: pygame.Rect, offset: tuple[float, float]):
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
                for layer in self.layers:
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


def load_map(path: str):
    print('loading map from ' + path)
    root = xml.etree.ElementTree.parse(path).getroot()
    if not isinstance(root, xml.etree.ElementTree.Element):
        raise Exception('root was not an element')
    return TileMap(root, path)
