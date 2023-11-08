
import math
import os.path
import pygame
import xml.etree.ElementTree

from tileset import TileSet, load_tileset
from utils import assert_bool, cmp_in_direction, intersect, load_properties, try_move_to_bounds, Bounds, Direction


class ImageLayer:
    path: str
    surface: pygame.Surface

    def __init__(self, node: xml.etree.ElementTree.Element, path: str):
        images = [img for img in node if img.tag == 'image']
        source = images[0].attrib['source']
        self.path = os.path.join(os.path.dirname(path), source)
        self.surface = pygame.image.load(self.path)


class TileLayer:
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
    gid: int | None
    x: int
    y: int
    width: int
    height: int
    properties: dict[str, str | int | bool]

    def __init__(self, node: xml.etree.ElementTree.Element, tileset: TileSet):
        self.id = int(node.attrib['id'])
        self.x = int(node.attrib['x'])
        self.y = int(node.attrib['y'])
        self.width = int(node.attrib['width'])
        self.height = int(node.attrib['height'])
        gid_str = node.attrib.get('gid', None)
        self.gid = int(gid_str) if gid_str is not None else None
        self.properties = {}
        if self.gid is not None:
            for k, v in tileset.tile_properties.get(self.gid - 1, {}).items():
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
        # For some reason, the position is the bottom left sometimes?
        if self.gid is not None:
            self.y -= self.height

    def rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def __repr__(self):
        return f'MapObject(id={self.id}, gid={self.gid}, x={self.x}, y={self.y}, w={self.width}, h={self.height}, properties={self.properties}'


class TileMap:
    width: int
    height: int
    tilewidth: int
    tileheight: int
    backgroundcolor: str
    tilesetsource: str
    tileset: TileSet
    layers: list[ImageLayer | TileLayer]
    player_layer: int | None
    objects: list[MapObject]
    properties: dict[str, str | int | bool]

    def __init__(self, root: xml.etree.ElementTree.Element, path: str):
        self.width = int(root.attrib['width'])
        self.height = int(root.attrib['height'])
        self.tilewidth = int(root.attrib['tilewidth'])
        self.tileheight = int(root.attrib['tileheight'])
        self.backgroundcolor = root.attrib.get('backgroundcolor', '#000000')
        self.tilesetsource = [
            ts for ts in root if ts.tag == 'tileset'][0].attrib['source']
        self.tileset = load_tileset(os.path.join(
            os.path.dirname(path), self.tilesetsource))

        self.properties = load_properties(root)
        print(f'map properties: {self.properties}')

        self.layers = []
        for layer in root:
            if layer.tag == 'layer':
                self.layers.append(TileLayer(layer))
            elif layer.tag == 'imagelayer':
                self.layers.append(ImageLayer(layer, path))

        player_layers = [
            layer for layer
            in enumerate(self.layers)
            if isinstance(layer[1], TileLayer) and layer[1].player]
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

    @property
    def is_dark(self) -> bool:
        return assert_bool(self.properties.get('dark', False))

    def is_condition_met(self, tile: int, switches: set[str]):
        condition = self.tileset.get_str_property(tile, 'condition')
        if condition is None:
            return True
        if condition.startswith('!'):
            return condition[1:] not in switches
        else:
            return condition in switches

    def draw_background(self, surface: pygame.Surface, dest: pygame.Rect, offset: tuple[float, float], switches: set[str]):
        surface.fill(self.backgroundcolor, dest)
        for layer in self.layers:
            self.draw_layer(surface, layer, dest, offset, switches)
            if isinstance(layer, TileLayer) and layer.player:
                return

    def draw_foreground(self, surface: pygame.Surface, dest: pygame.Rect, offset: tuple[float, float], switches: set[str]):
        if self.player_layer is None:
            return
        drawing = False
        for layer in self.layers:
            if drawing:
                self.draw_layer(surface, layer, dest, offset, switches)
            if isinstance(layer, TileLayer) and layer.player:
                drawing = True

    def draw_layer(self, surface: pygame.Surface, layer: TileLayer | ImageLayer, dest: pygame.Rect, offset: tuple[float, float], switches: set[str]):
        # pygame.draw.rect(surface, self.backgroundcolor, dest)

        if isinstance(layer, ImageLayer):
            surface.blit(layer.surface, offset)
            return

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
                index -= 1

                if not self.is_condition_met(index, switches):
                    alt = self.tileset.get_int_property(index, 'alternate')
                    if alt is None:
                        continue
                    index = alt

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
                if index in self.tileset.animations:
                    self.tileset.animations[index].blit(surface, pos, False)
                else:
                    surface.blit(self.tileset.surface, pos, source)

    def get_rect(self, row: int, col: int) -> pygame.Rect:
        return pygame.Rect(
            col * self.tilewidth,
            row * self.tileheight,
            self.tilewidth,
            self.tileheight)

    def is_solid_in_direction(self, tile_id: int, direction: Direction, is_backwards: bool) -> bool:
        oneway = self.tileset.get_str_property(tile_id, 'oneway')
        if oneway is None:
            return True
        if is_backwards:
            return False
        match direction:
            case Direction.UP:
                return oneway == 'S'
            case Direction.DOWN:
                return oneway == 'N'
            case Direction.RIGHT:
                return oneway == 'W'
            case Direction.LEFT:
                return oneway == 'E'
        raise Exception('unexpection direction')

    class MoveResult:
        # This is the offset that stops the player.
        hard_offset_sub: int = 0
        # This is the offset for being on a slope.
        soft_offset_sub: int = 0
        tile_ids: set[int]

        def __init__(self):
            self.tile_ids = set()

        def consider_tile(self,
                          index: int,
                          hard_offset_sub: int,
                          soft_offset_sub: int,
                          direction: Direction):
            cmp = cmp_in_direction(
                hard_offset_sub, self.hard_offset_sub, direction)
            if cmp < 0:
                self.hard_offset_sub = hard_offset_sub

            cmp = cmp_in_direction(
                soft_offset_sub, self.soft_offset_sub, direction)
            if cmp < 0:
                self.soft_offset_sub = soft_offset_sub
                self.tile_ids = set([index])
            elif cmp == 0:
                self.tile_ids.add(index)

    def try_move_to(self,
                    bounds: Bounds,
                    direction: Direction,
                    switches: set[str],
                    is_backwards: bool) -> MoveResult:
        """ Returns the offset needed to account for the closest one. """
        result = TileMap.MoveResult()
        player_rect = bounds.rect
        row1 = player_rect.top // self.tileheight
        col1 = player_rect.left // self.tilewidth
        row2 = player_rect.bottom // self.tileheight
        col2 = player_rect.right // self.tilewidth
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
                tile_rect = self.get_rect(row, col)
                tile_bounds = Bounds(
                    tile_rect.x * 16,
                    tile_rect.y * 16,
                    tile_rect.w * 16,
                    tile_rect.h * 16)
                for layer in self.layers:
                    if not isinstance(layer, TileLayer):
                        continue
                    if layer.player or self.player_layer is None:
                        index = layer.data[row][col]
                        if index == 0:
                            continue
                        index -= 1
                        if not self.is_condition_met(index, switches):
                            alt = self.tileset.get_int_property(
                                index, 'alternate')
                            if alt is None:
                                continue
                            # Use an alt tile instead of the original.
                            index = alt
                        if not self.tileset.get_bool_property(index, 'solid', True):
                            continue
                        if not self.is_solid_in_direction(index, direction, is_backwards):
                            continue

                        soft_offset_sub = try_move_to_bounds(
                            bounds,
                            tile_bounds,
                            direction)
                        hard_offset_sub = soft_offset_sub

                        if self.tileset.is_slope(index):
                            slope = self.tileset.get_slope(index)
                            hard_offset_sub = slope.try_move_to_bounds(
                                bounds,
                                tile_bounds,
                                direction)

                        result.consider_tile(
                            index, hard_offset_sub, soft_offset_sub, direction)
        return result

    def intersect(self, bounds: Bounds, switches: set[str]) -> list[int]:
        ans = []
        rect = bounds.rect
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
                    if not isinstance(layer, TileLayer):
                        continue
                    if layer.player or self.player_layer is None:
                        index = layer.data[row][col]
                        if index == 0:
                            continue
                        index -= 1
                        if not self.is_condition_met(index, switches):
                            alt = self.tileset.get_int_property(
                                index, 'alternate')
                            if alt is None:
                                continue
                            # Use an alt tile instead of the original.
                            index = alt
                        if not self.tileset.get_bool_property(index, 'solid', True):
                            continue
                        ans.append(index)
        return ans

    def get_preferred_view(self, player_rect: pygame.Rect) -> tuple[int | None, int | None]:
        preferred_x: int | None = None
        preferred_y: int | None = None
        for obj in self.objects:
            if obj.gid is not None:
                continue
            if not intersect(player_rect, obj.rect()):
                continue
            p_x = obj.properties.get('preferred_x', None)
            p_y = obj.properties.get('preferred_y', None)
            if isinstance(p_x, int):
                preferred_x = p_x
            if isinstance(p_y, int):
                preferred_y = p_y
        return (preferred_x, preferred_y)

    def update_animations(self):
        self.tileset.update_animations()


def load_map(path: str):
    print('loading map from ' + path)
    root = xml.etree.ElementTree.parse(path).getroot()
    if not isinstance(root, xml.etree.ElementTree.Element):
        raise Exception('root was not an element')
    return TileMap(root, path)
