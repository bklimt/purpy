from typing import overload
import xml.etree.ElementTree


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


class TileProperties:
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
    raw: dict[str, str | bool | int]

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
