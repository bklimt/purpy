
import math
import os.path
import pygame
import xml.etree.ElementTree

from constants import SUBPIXELS
from imagemanager import ImageManager
from render.rendercontext import RenderContext
from render.spritebatch import SpriteBatch
from switchstate import SwitchState
from tileset import TileSet, load_tileset
from utils import assert_bool, cmp_in_direction, intersect, load_properties, try_move_to_bounds, Direction


class ImageLayer:
    path: str
    surface: pygame.Surface

    def __init__(self, node: xml.etree.ElementTree.Element, path: str, images: ImageManager):
        image = [img for img in node if img.tag == 'image']
        source = image[0].attrib['source']
        self.path = os.path.join(os.path.dirname(path), source)
        self.surface = images.load_image(self.path)


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

    def __init__(self, root: xml.etree.ElementTree.Element, path: str, images: ImageManager):
        self.width = int(root.attrib['width'])
        self.height = int(root.attrib['height'])
        self.tilewidth = int(root.attrib['tilewidth'])
        self.tileheight = int(root.attrib['tileheight'])
        self.backgroundcolor = root.attrib.get('backgroundcolor', '#000000')
        self.tilesetsource = [
            ts for ts in root if ts.tag == 'tileset'][0].attrib['source']
        tileset_path = os.path.join(os.path.dirname(path), self.tilesetsource)
        self.tileset = load_tileset(tileset_path, images)

        self.properties = load_properties(root)
        print(f'map properties: {self.properties}')

        self.layers = []
        for layer in root:
            if layer.tag == 'layer':
                self.layers.append(TileLayer(layer))
            elif layer.tag == 'imagelayer':
                self.layers.append(ImageLayer(layer, path, images))

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

    def is_condition_met(self, tile: int, switches: SwitchState):
        condition = self.tileset.get_str_property(tile, 'condition')
        if condition is None:
            return True
        return switches.is_condition_true(condition)

    def draw_background(self,
                        context: RenderContext,
                        batch: SpriteBatch,
                        dest: pygame.Rect,
                        offset: tuple[int, int],
                        switches: SwitchState):
        batch.draw_rect(dest, self.backgroundcolor)
        for layer in self.layers:
            self.draw_layer(context, batch, layer, dest, offset, switches)
            if isinstance(layer, TileLayer) and layer.player:
                return

    def draw_foreground(self,
                        context: RenderContext,
                        batch: SpriteBatch,
                        dest: pygame.Rect,
                        offset: tuple[int, int],
                        switches: SwitchState):
        if self.player_layer is None:
            return
        drawing = False
        for layer in self.layers:
            if drawing:
                self.draw_layer(context, batch, layer, dest, offset, switches)
            if isinstance(layer, TileLayer) and layer.player:
                drawing = True

    def draw_layer(self,
                   context: RenderContext,
                   batch: SpriteBatch,
                   layer: TileLayer | ImageLayer,
                   dest: pygame.Rect,
                   offset: tuple[int, int],
                   switches: SwitchState):
        if isinstance(layer, ImageLayer):
            dest = pygame.Rect(
                offset[0],
                offset[1],
                layer.surface.get_width() * SUBPIXELS,
                layer.surface.get_height() * SUBPIXELS)
            batch.draw(layer.surface, dest)
            return

        offset_x = offset[0]
        offset_y = offset[1]
        tileheight = self.tileheight * SUBPIXELS
        tilewidth = self.tilewidth * SUBPIXELS
        row_count = math.ceil(dest.height / tileheight) + 1
        col_count = math.ceil(dest.width / tilewidth) + 1

        start_row = offset_y // -tileheight
        end_row = start_row + row_count
        if start_row < 0:
            start_row = 0
        if end_row > self.height:
            end_row = self.height

        start_col = offset_x // -tilewidth
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
                pos_x = col * tilewidth + dest.left + offset_x
                pos_y = row * tileheight + dest.top + offset_y

                # If it's off the top/left side, trim it.
                if pos_x < dest.left:
                    extra = (dest.left - pos_x) // SUBPIXELS
                    source.left += extra
                    source.width -= extra
                    pos_x = dest.left
                if pos_y < dest.top:
                    extra = (dest.top - pos_y) // SUBPIXELS
                    source.top += extra
                    source.height -= extra
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
                destination = pygame.Rect(
                    pos_x,
                    pos_y,
                    tilewidth,
                    tileheight)
                if index in self.tileset.animations:
                    self.tileset.animations[index].blit(
                        batch, destination, reverse=False)
                else:
                    batch.draw(self.tileset.surface, destination, source)

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
        # We keep track of two different offsets so that you can be "on" a
        # slope even if there's a higher block next to it. That way, if you're
        # at the top of a slope, you can be down the slope a little, and not
        # wait until you're completely clear of the flat area before falling.

        # This is the offset that stops the player.
        hard_offset: int = 0
        # This is the offset for being on a slope.
        soft_offset: int = 0
        tile_ids: set[int]

        def __init__(self):
            self.tile_ids = set()

        def consider_tile(self,
                          index: int,
                          hard_offset: int,
                          soft_offset: int,
                          direction: Direction):
            cmp = cmp_in_direction(
                hard_offset, self.hard_offset, direction)
            if cmp < 0:
                self.hard_offset = hard_offset

            cmp = cmp_in_direction(
                soft_offset, self.soft_offset, direction)
            if cmp < 0:
                self.soft_offset = soft_offset
                self.tile_ids = set([index])
            elif cmp == 0:
                self.tile_ids.add(index)

    def try_move_to(self,
                    player_rect: pygame.Rect,
                    direction: Direction,
                    switches: SwitchState,
                    is_backwards: bool) -> MoveResult:
        """ Returns the offset needed to account for the closest one. """
        result = TileMap.MoveResult()

        right_edge = self.width * self.tilewidth * SUBPIXELS
        bottom_edge = self.height * self.tileheight * SUBPIXELS

        if direction == Direction.LEFT and player_rect.x < 0:
            result.hard_offset = -player_rect.x
            result.soft_offset = result.hard_offset
            return result
        if direction == Direction.UP and player_rect.y < 0:
            result.hard_offset = -player_rect.y
            result.soft_offset = result.hard_offset
            return result
        if direction == Direction.RIGHT and player_rect.right >= right_edge:
            result.hard_offset = (right_edge - player_rect.right) - 1
            result.soft_offset = result.hard_offset
            return result
        if direction == Direction.DOWN and player_rect.bottom >= bottom_edge:
            result.hard_offset = (bottom_edge - player_rect.bottom) - 1
            result.soft_offset = result.hard_offset
            return result

        row1 = player_rect.top // (self.tileheight * SUBPIXELS)
        col1 = player_rect.left // (self.tilewidth * SUBPIXELS)
        row2 = player_rect.bottom // (self.tileheight * SUBPIXELS)
        col2 = player_rect.right // (self.tilewidth * SUBPIXELS)

        for row in range(row1, row2+1):
            for col in range(col1, col2+1):
                tile_rect = self.get_rect(row, col)
                tile_bounds = pygame.Rect(
                    tile_rect.x * SUBPIXELS,
                    tile_rect.y * SUBPIXELS,
                    tile_rect.w * SUBPIXELS,
                    tile_rect.h * SUBPIXELS)
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

                        soft_offset = try_move_to_bounds(
                            player_rect,
                            tile_bounds,
                            direction)
                        hard_offset = soft_offset

                        if self.tileset.is_slope(index):
                            slope = self.tileset.get_slope(index)
                            hard_offset = slope.try_move_to_bounds(
                                player_rect,
                                tile_bounds,
                                direction)

                        result.consider_tile(
                            index, hard_offset, soft_offset, direction)
        return result

    def get_preferred_view(self, player_rect: pygame.Rect) -> tuple[int | None, int | None]:
        preferred_x: int | None = None
        preferred_y: int | None = None
        for obj in self.objects:
            if obj.gid is not None:
                continue
            rect = obj.rect().copy()
            rect.x *= SUBPIXELS
            rect.y *= SUBPIXELS
            rect.w *= SUBPIXELS
            rect.h *= SUBPIXELS
            if not intersect(player_rect, rect):
                continue
            p_x = obj.properties.get('preferred_x', None)
            p_y = obj.properties.get('preferred_y', None)
            if isinstance(p_x, int):
                preferred_x = p_x * SUBPIXELS
            if isinstance(p_y, int):
                preferred_y = p_y * SUBPIXELS
        return (preferred_x, preferred_y)

    def update_animations(self):
        self.tileset.update_animations()


def load_map(path: str, images: ImageManager):
    print('loading map from ' + path)
    root = xml.etree.ElementTree.parse(path).getroot()
    if not isinstance(root, xml.etree.ElementTree.Element):
        raise Exception('root was not an element')
    return TileMap(root, path, images)
