from enum import Enum
from typing import overload

import xml.etree.ElementTree

from utils import Direction


def load_properties(
        node: xml.etree.ElementTree.Element,
        properties: dict[str, str | int | bool] | None = None
) -> dict[str, str | int | bool]:
    if properties is None:
        properties = {}

    for pnode in node:
        if pnode.tag == 'properties' or pnode.tag == 'property':
            load_properties(pnode, properties)

    if node.tag == 'property':
        name = node.attrib['name']
        typ = node.attrib.get('type', 'str')
        val = node.attrib['value']
        if typ == "str":
            properties[name] = val
        elif typ == "int":
            properties[name] = int(val)
        elif typ == "bool":
            properties[name] = (val == 'true')
        else:
            raise Exception(f'unsupported property type {typ}')

    return properties


@overload
def get_bool(map: dict[str, bool | int | str], key: str) -> bool | None:
    pass


@overload
def get_bool(map: dict[str, bool | int | str], key: str, default: bool) -> bool:
    pass


def get_bool(map: dict[str, bool | int | str], key: str, default=None):
    val = map.get(key, default)
    if val is not None:
        if not isinstance(val, bool):
            raise Exception(f'expected bool, got {val}')
    return val


@overload
def get_int(map: dict[str, bool | int | str], key: str) -> int | None:
    pass


@overload
def get_int(map: dict[str, bool | int | str], key: str, default: int) -> int:
    pass


def get_int(map: dict[str, bool | int | str], key: str, default=None):
    val = map.get(key, default)
    if val is not None:
        if not isinstance(val, int):
            raise Exception(f'expected int, got {val}')
    return val


@overload
def get_str(map: dict[str, bool | int | str], key: str) -> str | None:
    pass


@overload
def get_str(map: dict[str, bool | int | str], key: str, default: str) -> str:
    pass


def get_str(map: dict[str, bool | int | str], key: str, default=None):
    val = map.get(key, default)
    if val is not None:
        if not isinstance(val, str):
            raise Exception(f'expected str, got {val}')
    return val


def set_defaults(dst: dict[str, bool | int | str], src: dict[str, bool | int | str]):
    for key in src:
        if key not in dst:
            dst[key] = src[key]


class TileProperties:
    raw: dict[str, str | bool | int]
    solid: bool
    alternate: int | None
    condition: str | None
    oneway: str | None
    slope: bool
    left_y: int
    right_y: int
    hitbox_top: int
    hitbox_left: int
    hitbox_right: int
    hitbox_bottom: int
    deadly: bool
    switch: str | None

    def __init__(self, map: dict[str, str | bool | int]):
        self.raw = map
        self.solid = get_bool(map, 'solid', True)
        self.alternate = get_int(map, 'alternate')
        self.condition = get_str(map, 'condition')
        self.oneway = get_str(map, 'oneway')
        self.slope = get_bool(map, 'slope', False)
        self.left_y = get_int(map, 'left_y', 0)
        self.right_y = get_int(map, 'right_y', 0)
        self.hitbox_left = get_int(map, 'hitbox_left', 0)
        self.hitbox_right = get_int(map, 'hitbox_right', 0)
        self.hitbox_top = get_int(map, 'hitbox_top', 0)
        self.hitbox_bottom = get_int(map, 'hitbox_bottom', 0)
        self.deadly = get_bool(map, 'deadly', False)
        self.switch = get_str(map, 'switch')


class TileSetProperties:
    raw: dict[str, str | bool | int]
    animations: str | None

    def __init__(self, map: dict[str, str | bool | int]):
        self.raw = map
        self.animations = get_str(map, 'animations')


class Overflow(Enum):
    OSCILLATE = 1
    WRAP = 2
    CLAMP = 3

    @classmethod
    def from_str(cls, s: str) -> 'Overflow':
        match s:
            case 'oscillate': return Overflow.OSCILLATE
            case 'wrap': return Overflow.WRAP
            case 'clamp': return Overflow.CLAMP
        raise Exception(f'invalid overflow type: {s}')


class ConveyorDirection(Enum):
    LEFT = 1,
    RIGHT = 2,

    @classmethod
    def from_str(cls, s: str) -> 'ConveyorDirection':
        match s:
            case 'W': return ConveyorDirection.LEFT
            case 'E': return ConveyorDirection.RIGHT
        raise Exception(f'invalid conveyor direction: {s}')


class ButtonType(Enum):
    ONE_SHOT = 1,
    TOGGLE = 2,
    MOMENTARY = 3,
    SMART = 4,

    @classmethod
    def from_str(cls, s: str) -> 'ButtonType':
        match s:
            case 'oneshot': return ButtonType.ONE_SHOT
            case 'toggle': return ButtonType.TOGGLE
            case 'momentary': return ButtonType.MOMENTARY
            case 'smart': return ButtonType.SMART
        raise Exception(f'invalid button type: {s}')


class MapObjectProperties:
    raw: dict[str, str | bool | int]
    # Types
    platform: bool
    bagel: bool
    spring: bool
    button: bool
    door: bool
    star: bool
    spawn: bool
    # Tiles
    solid: bool
    # Map Areas
    preferred_x: int | None
    preferred_y: int | None
    # Platforms
    distance: int
    speed: int | None
    condition: str | None
    overflow: Overflow
    direction: Direction
    convey: ConveyorDirection | None
    # Buttons
    button_type: ButtonType
    color: str | None
    # Doors
    sprite: str | None
    destination: str | None
    stars_needed: int
    # Spawn points
    facing_left: bool
    # Warp zones
    warp: str | None

    def __init__(self, map: dict[str, str | bool | int]):
        self.raw = map
        self.platform = get_bool(map, 'platform', False)
        self.bagel = get_bool(map, 'bagel', False)
        self.spring = get_bool(map, 'spring', False)
        self.button = get_bool(map, 'button', False)
        self.door = get_bool(map, 'door', False)
        self.star = get_bool(map, 'star', False)
        self.spawn = get_bool(map, 'spawn', False)
        self.solid = get_bool(map, 'solid', False)
        self.preferred_x = get_int(map, 'preferred_x')
        self.preferred_y = get_int(map, 'preferred_y')
        self.distance = get_int(map, 'distance', 0)
        self.speed = get_int(map, 'speed')
        self.condition = get_str(map, 'condition')
        self.overflow = Overflow.from_str(
            get_str(map, 'overflow', 'oscillate'))
        self.direction = Direction.from_str(get_str(map, 'direction', 'N'))
        convey_str = get_str(map, 'convey')
        self.convey = ConveyorDirection.from_str(
            convey_str) if convey_str is not None else None
        self.button_type = ButtonType.from_str(
            get_str(map, 'button_type', 'toggle'))
        self.color = get_str(map, 'color')
        self.sprite = get_str(map, 'sprite')
        self.destination = get_str(map, 'direction')
        self.stars_needed = get_int(map, 'stars_needed', 0)
        self.facing_left = get_bool(map, 'facing_left', False)
        self.warp = get_str(map, 'warp')
