
import pygame

from player import Player
from tilemap import MapObject
from tileset import TileSet
from random import randint
from utils import try_move_to_bounds, Bounds, Direction

BAGEL_WAIT_TIME = 30
BAGEL_FALL_TIME = 150
BAGEL_MAX_GRAVITY = 11
BAGEL_GRAVITY_ACCELERATION = 1


def sign(n: int) -> int:
    if n == 0:
        return 0
    if n < 0:
        return -1
    if n > 0:
        return 1
    raise Exception('impossible')


class Platform:
    id: int
    tileset: TileSet
    tile_id: int
    x: int
    y: int
    dx: int
    dy: int
    occupied: bool
    is_solid: bool

    def __init__(self, obj: MapObject, tileset: TileSet):
        if obj.gid is None:
            raise Exception('platforms must have tile ids')

        self.id = obj.id
        self.tileset = tileset
        self.tile_id = obj.gid - 1
        self.x = obj.x * 16
        self.y = obj.y * 16
        self.dx = 0
        self.dy = 0
        self.occupied = False
        self.is_solid = bool(obj.properties.get('solid', False))

    def update(self):
        pass

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]
        if self.tile_id in self.tileset.animations:
            anim = self.tileset.animations[self.tile_id]
            anim.blit(surface, (x, y), False)
        else:
            area = self.tileset.get_source_rect(self.tile_id)
            surface.blit(self.tileset.surface, (x, y), area)

    def try_move_to(self, player_rect: Bounds, direction: Direction, is_backwards: bool) -> int:
        if self.is_solid:
            area = Bounds(
                self.x,
                self.y,
                self.tileset.tilewidth * 16,
                self.tileset.tileheight * 16)
            return try_move_to_bounds(player_rect, area, direction)
        else:
            if direction != Direction.DOWN:
                return 0
            if is_backwards:
                return 0
            area = Bounds(
                self.x,
                self.y,
                self.tileset.tilewidth * 16,
                4 * 16)
            return try_move_to_bounds(player_rect, area, direction)


class MovingPlatform(Platform):
    distance: int
    start_x: int
    start_y: int
    end_x: int
    end_y: int

    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        self.distance = int(obj.properties.get('distance', '0')) * 16
        self.speed = int(obj.properties.get('speed', '1'))
        self.start_x = self.x
        self.start_y = self.y
        d = str(obj.properties.get('direction', 'N')).upper()
        if d == 'N':
            self.distance *= self.tileset.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y - self.distance
        elif d == 'S':
            self.distance *= self.tileset.tileheight
            self.end_x = self.start_x
            self.end_y = self.start_y + self.distance
        elif d == 'E':
            self.distance *= self.tileset.tilewidth
            self.end_x = self.start_x + self.distance
            self.end_y = self.start_y
        elif d == 'W':
            self.distance *= self.tileset.tilewidth
            self.end_x = self.start_x - self.distance
            self.end_y = self.start_y
        else:
            raise Exception(f'unknown direction {d}')

        self.dx = sign(self.end_x - self.start_x) * self.speed
        self.dy = sign(self.end_y - self.start_y) * self.speed

    def update(self):
        if self.x == self.end_x:
            self.dx *= -1
            self.start_x, self.end_x = self.end_x, self.start_x
        if self.y == self.end_y:
            self.dy *= -1
            self.start_y, self.end_y = self.end_y, self.start_y
        self.x += self.dx
        self.y += self.dy


class Bagel(Platform):
    original_y: int
    falling: bool = False
    remaining: int = BAGEL_WAIT_TIME

    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        self.original_y = self.y

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]
        area = self.tileset.get_source_rect(self.tile_id)
        if self.occupied:
            x += randint(-1, 1)
            y += randint(-1, 1)
        surface.blit(self.tileset.surface, (x, y), area)

    def update(self):
        if self.falling:
            self.remaining -= 1
            if self.remaining == 0:
                self.dy = 0
                self.y = self.original_y
                self.falling = False
                self.remaining = BAGEL_WAIT_TIME
            else:
                self.dy += BAGEL_GRAVITY_ACCELERATION
                self.dy = max(self.dy, BAGEL_MAX_GRAVITY)
                self.y += self.dy
        else:
            if self.occupied:
                self.remaining -= 1
                if self.remaining == 0:
                    self.falling = True
                    self.remaining = BAGEL_FALL_TIME
                    self.dy = 0
            else:
                self.remaining = BAGEL_WAIT_TIME


class Conveyor(Platform):
    def __init__(self, obj: MapObject, tileset: TileSet):
        super().__init__(obj, tileset)
        speed = int(obj.properties.get('speed', 24))
        if obj.properties.get('convey', 'E') == 'E':
            self.dx = speed
        else:
            self.dx = -1 * speed

    def update(self):
        pass


class Wire(Platform):
    width: int
    height: int
    wire_y_sub: list[int]
    wire_dy_sub: list[int]

    def __init__(self, obj: MapObject, tileset: TileSet):
        obj.gid = 1
        super().__init__(obj, tileset)
        self.wire_y_sub = []
        self.wire_dy_sub = []
        self.width = obj.width
        self.height = obj.height
        for i in range(self.width):
            self.wire_y_sub.append(randint(0, (self.height * 16) - 1))
            self.wire_dy_sub.append(0)

    def update(self):
        for _ in range(3):
            new_wire_y_sub = []
            for i in range(self.width):
                left = 0
                right = 0
                center = self.wire_y_sub[i]  # + self.wire_dy_sub[i]
                if i > 0:
                    left = self.wire_y_sub[i - 1]
                if i < len(self.wire_y_sub) - 1:
                    right = self.wire_y_sub[i + 1]
                # Compute the harmonic mean.
                # num = 3 * left * center * right
                # den = left * center + center * right + left * right
                # avg = 0 if den == 0 else num // den
                avg = (2 * left + center + 2 * right) // 5
                if avg < 0:
                    avg = 0
                if avg >= self.height * 16:
                    avg = self.height * 16 - 1
                new_wire_y_sub.append(avg)
                self.wire_dy_sub[i] = avg - self.wire_y_sub[i]
            self.wire_y_sub = new_wire_y_sub

    def draw(self, surface: pygame.Surface, offset: tuple[int, int]):
        x = self.x//16 + offset[0]
        y = self.y//16 + offset[1]

        for i in range(self.width):
            yy = y + (self.wire_y_sub[i] // 16)
            surface.set_at((x + i, yy), pygame.Color(255, 255, 255))

    def try_move_to(self, player_rect: Bounds, direction: Direction, is_backwards: bool) -> int:
        if direction != Direction.DOWN:
            return 0
        if is_backwards:
            return 0

        area = Bounds(
            self.x,
            self.y,
            self.width * 16,
            self.height * 16)

        if player_rect.bottom_sub <= area.top_sub:
            return 0
        if player_rect.top_sub >= area.bottom_sub:
            return 0
        if player_rect.right_sub <= area.left_sub:
            return 0
        if player_rect.left_sub >= area.right_sub:
            return 0

        if direction != Direction.DOWN:
            return 0

        actor_center_x_sub = (player_rect.left_sub +
                              player_rect.right_sub) // 2
        i = (actor_center_x_sub - area.x_sub) // 16
        i = (actor_center_x_sub - area.x_sub) // 16
        if i < 0:
            return 0
        if i >= len(self.wire_y_sub):
            return 0
        target_y_sub: int = area.y_sub + self.wire_y_sub[i]

        if target_y_sub < player_rect.bottom_sub:
            return target_y_sub - player_rect.bottom_sub
        else:
            return 0

    def pluck(self, player_rect: Bounds):
        area = Bounds(
            self.x,
            self.y,
            self.width * 16,
            self.height * 16)

        if player_rect.bottom_sub < area.top_sub:
            return
        if player_rect.top_sub >= area.bottom_sub:
            return
        if player_rect.right_sub <= area.left_sub:
            return
        if player_rect.left_sub >= area.right_sub:
            return

        actor_center_x_sub = (player_rect.left_sub +
                              player_rect.right_sub) // 2
        i = (actor_center_x_sub - area.x_sub) // 16
        if i < 0:
            return
        if i >= len(self.wire_y_sub):
            return
        # self.wire_y_sub[i] = randint(0, area.h_sub - 1)
        self.wire_y_sub[i] = area.h_sub - 1
        self.wire_dy_sub[i] = 0

        self.update()
