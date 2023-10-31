
import os.path
import pygame

from door import Door
from font import Font
from imagemanager import ImageManager
from inputmanager import InputManager
from kill import KillScreen
from player import Player, PlayerState
from platforms import Bagel, MovingPlatform, Platform
from scene import Scene
from soundmanager import Sound, SoundManager
from star import Star
from tilemap import TileMap, load_map
from utils import Direction, cmp_in_direction, sign

TARGET_WALK_SPEED = 32
TARGET_AIRBORNE_SPEED = 16
WALK_SPEED_ACCELERATION = 1
MAX_GRAVITY = 24
WALL_SLIDE_SPEED = 4
GRAVITY_ACCELERATION = 1
JUMP_SPEED = 40
WALL_JUMP_HORIZONTAL_SPEED = 24
WALL_JUMP_VERTICAL_SPEED = 24
WALL_STICK_TIME = 30
WALL_SLIDE_TIME = 60
VIEWPORT_PAN_SPEED = 5
TOAST_TIME = 100
TOAST_HEIGHT = 12


class MoveResult:
    """ The results of trying to move. """
    offset: int
    tile_ids: set[int]
    platforms: set[Platform]

    def __init__(self):
        self.offset = 0
        self.tile_ids = set()
        self.platforms = set()


class PlatformMoveResult:
    offset: int
    platforms: set[Platform]

    def __init__(self):
        self.offset = 0
        self.platforms = set()


class Level(Scene):
    parent: Scene | None
    map_path: str
    name: str
    map: TileMap
    player: Player

    wall_stick_counter: int = WALL_STICK_TIME
    wall_stick_facing_right: bool = False
    wall_slide_counter: int = WALL_SLIDE_TIME

    previous_map_offset: None | tuple[int, int]
    toast_text: str
    toast_position: int = -TOAST_HEIGHT
    toast_counter: int = TOAST_TIME

    # platforms, stars, and doors
    platforms: list[Platform]
    stars: list[Star]
    doors: list[Door]

    current_platform: Platform | None = None
    switches: set[str]
    current_switch_tiles: set[int]
    current_door: Door | None

    def __init__(self, parent: Scene | None, map_path: str):
        self.parent = parent
        self.map_path = map_path
        self.name = os.path.splitext(os.path.basename(map_path))[0]
        self.toast_text = self.name
        self.previous_map_offset = None
        self.map = load_map(map_path)
        self.player = Player()
        self.player.x = self.map.tilewidth * 16
        self.player.y = self.map.tileheight * 16
        self.transition: str = ''
        self.platforms = []
        self.stars = []
        self.doors = []
        self.switches = set()
        self.current_switch_tiles = set()
        self.star_count = 0
        for obj in self.map.objects:
            if obj.properties.get('platform', False):
                self.platforms.append(MovingPlatform(obj, self.map.tileset))
            if obj.properties.get('bagel', False):
                self.platforms.append(Bagel(obj, self.map.tileset))
            if obj.properties.get('door', False):
                self.doors.append(Door(obj))
            if obj.properties.get('star', False):
                self.stars.append(Star(obj, self.map.tileset))

    #
    # Movement.
    #

    def update_player_trajectory_x(self, inputs: InputManager):
        # Apply controller input.
        target_dx = 0
        if inputs.is_left_down() and not inputs.is_right_down():
            if self.player.state == PlayerState.AIRBORNE:
                # If you're in the air, you can only go fast if you already were.
                target_dx = min(self.player.dx, -1 * TARGET_AIRBORNE_SPEED)
            else:
                target_dx = -1 * TARGET_WALK_SPEED
        if inputs.is_right_down() and not inputs.is_left_down():
            if self.player.state == PlayerState.AIRBORNE:
                # If you're in the air, you can only go fast if you already were.
                target_dx = max(self.player.dx, TARGET_AIRBORNE_SPEED)
            else:
                target_dx = TARGET_WALK_SPEED
        if self.player.state == PlayerState.CROUCHING:
            target_dx = 0

        # Change the velocity toward the target velocity.
        if self.player.dx < target_dx:
            self.player.dx += WALK_SPEED_ACCELERATION
        if self.player.dx > target_dx:
            self.player.dx -= WALK_SPEED_ACCELERATION

    def update_player_trajectory_y(self, inputs: InputManager):
        if self.player.state == PlayerState.WALL_SLIDING:
            # When you first grab the wall, don't start sliding for a while.
            if self.wall_slide_counter > 0:
                self.wall_slide_counter -= 1
                self.player.dy = 0
            else:
                self.player.dy = WALL_SLIDE_SPEED
        elif self.player.state == PlayerState.STANDING:
            # Fall at least one pixel so that we hit the ground again.
            self.player.dy = max(self.player.dy, 16)
        else:
            # Apply gravity.
            if self.player.dy < MAX_GRAVITY:
                self.player.dy += GRAVITY_ACCELERATION
            if self.player.dy > MAX_GRAVITY:
                self.player.dy = MAX_GRAVITY

    def find_platform_intersections(self, player_rect: pygame.Rect, direction: Direction) -> PlatformMoveResult:
        result = PlatformMoveResult()
        for platform in self.platforms:
            distance = platform.try_move_to(player_rect, direction)
            if distance == 0:
                continue

            cmp = cmp_in_direction(distance, result.offset, direction)
            if cmp < 0:
                result.offset = distance
                result.platforms = set([platform])
            elif cmp == 0:
                result.platforms.add(platform)
        return result

    def try_move_player(self, direction: Direction) -> MoveResult:
        """ Returns how far this player needs to move in direction to not intersect, in sub-pixels. """
        player_rect = self.player.get_target_bounds_rect(direction)

        map_result = self.map.try_move_to(
            player_rect, direction, self.switches)
        platform_result = self.find_platform_intersections(
            player_rect, direction)

        result = MoveResult()
        if cmp_in_direction(platform_result.offset, map_result.offset, direction) <= 0:
            result.offset = platform_result.offset
            result.platforms = platform_result.platforms
        else:
            result.offset = map_result.offset
            result.tile_ids = map_result.tile_ids

        result.offset *= 16

        return result

    def move_player_x(self, inputs: InputManager) -> bool:
        pushing_against_wall: bool = False
        dx = self.player.dx
        if self.current_platform is not None:
            dx += self.current_platform.dx
        self.player.x += dx
        if dx < 0 or (dx == 0 and not self.player.facing_right):
            # Moving left.
            offset = self.try_move_player(Direction.WEST).offset
            if offset != 0 and inputs.is_left_down():
                pushing_against_wall = True
            self.player.x += offset
            self.player.x += self.try_move_player(Direction.EAST).offset
        else:
            # Moving right.
            offset = self.try_move_player(Direction.EAST).offset
            if offset != 0 and inputs.is_right_down():
                pushing_against_wall = True
            self.player.x += offset
            self.player.x += self.try_move_player(Direction.WEST).offset

        # If you're against the wall, you're stopped.
        if pushing_against_wall:
            self.player.dx = 0

        return pushing_against_wall

    def move_player_y(self, sounds: SoundManager) -> bool:
        on_ground: bool = False
        dy = self.player.dy
        if self.current_platform is not None:
            dy += self.current_platform.dy
        self.player.y += dy

        if dy <= 0:
            # Moving up.
            move_result = self.try_move_player(Direction.NORTH)
            if move_result.offset != 0:
                # We're on the ceiling.
                self.player.dy = 0
            self.player.y += move_result.offset
            self.player.y += self.try_move_player(Direction.SOUTH).offset
            # TODO: Make this work even when the platform is going up...???
            self.handle_current_platforms(set())
        else:
            # Moving down.
            move_result = self.try_move_player(Direction.SOUTH)
            if move_result.offset != 0:
                on_ground = True
            self.handle_spikes(move_result.tile_ids)
            self.handle_switch_tiles(move_result.tile_ids, sounds)
            self.handle_current_platforms(move_result.platforms)
            self.player.y += move_result.offset
            self.player.y += self.try_move_player(Direction.NORTH).offset
        return on_ground

    def handle_spikes(self, tiles: set[int]):
        for tile_id in tiles:
            if self.map.tileset.get_bool_property(tile_id, 'deadly', False):
                self.player.is_dead = True

    def handle_current_platforms(self, platforms: set[Platform]):
        self.current_platform = None
        for platform in self.platforms:
            platform.occupied = False

        for platform in platforms:
            platform.occupied = True
            # TODO: Be smarter about what platform we pick.
            self.current_platform = platform

    def handle_switch_tiles(self, tiles: set[int], sounds: SoundManager):
        previous = self.current_switch_tiles
        self.current_switch_tiles = set()
        for t in tiles:
            switch = self.map.tileset.get_str_property(t, 'switch')
            if switch is None:
                continue
            self.current_switch_tiles.add(t)
            if t in previous:
                continue
            if switch.startswith('!'):
                if switch[1:] in self.switches:
                    sounds.play(Sound.CLICK)
                    print(f'switched off {switch[1:]}')
                    self.switches.remove(switch[1:])
            elif switch.startswith('~'):
                sounds.play(Sound.CLICK)
                print(f'toggled {switch[1:]}')
                if switch[1:] in self.switches:
                    self.switches.remove(switch[1:])
                else:
                    self.switches.add(switch[1:])
            else:
                sounds.play(Sound.CLICK)
                print(f'switched on {switch}')
                self.switches.add(switch)

    def update_player_state(
            self,
            on_ground: bool,
            pressing_against_wall: bool,
            jump_pressed: bool,
            crouch_down: bool):
        if self.player.state == PlayerState.STANDING:
            if not on_ground:
                self.player.state = PlayerState.AIRBORNE
                self.player.dy = 0
            elif crouch_down:
                self.player.state = PlayerState.CROUCHING
            elif jump_pressed:
                if self.current_door is not None:
                    self.player.state = PlayerState.STOPPED
                    self.current_door.close()
                else:
                    self.player.state = PlayerState.AIRBORNE
                    self.player.dy = -1 * JUMP_SPEED
        elif self.player.state == PlayerState.AIRBORNE:
            if on_ground:
                self.player.state = PlayerState.STANDING
                self.player.dy = 0
            else:
                if pressing_against_wall and self.player.dy >= 0:
                    self.player.state = PlayerState.WALL_SLIDING
                    self.wall_slide_counter = WALL_SLIDE_TIME
        elif self.player.state == PlayerState.WALL_SLIDING:
            if jump_pressed:
                self.player.state = PlayerState.AIRBORNE
                self.player.dy = -1 * WALL_JUMP_VERTICAL_SPEED
                if self.player.facing_right:
                    self.player.dx = -1 * WALL_JUMP_HORIZONTAL_SPEED
                else:
                    self.player.dx = WALL_JUMP_HORIZONTAL_SPEED
            elif on_ground:
                self.player.state = PlayerState.STANDING
            elif pressing_against_wall:
                self.wall_stick_counter = WALL_STICK_TIME
                self.wall_stick_facing_right = self.player.facing_right
            else:
                if self.wall_stick_facing_right != self.player.facing_right:
                    self.player.state = PlayerState.AIRBORNE
                elif self.wall_stick_counter > 0:
                    self.wall_stick_counter -= 1
                else:
                    self.player.state = PlayerState.AIRBORNE
        elif self.player.state == PlayerState.CROUCHING:
            if not on_ground:
                self.player.state = PlayerState.AIRBORNE
                self.player.dy = 0
            elif not crouch_down:
                self.player.state = PlayerState.STANDING

    def update(self, inputs: InputManager, sounds: SoundManager) -> Scene | None:
        if inputs.is_cancel_triggered():
            return self.parent
        if inputs.is_restart_down():
            return Level(self.parent, self.map_path)

        for platform in self.platforms:
            platform.update()

        if self.player.state != PlayerState.STOPPED:
            self.update_player_trajectory_x(inputs)
            self.update_player_trajectory_y(inputs)

        pressing_against_wall = self.move_player_x(inputs)
        on_ground = self.move_player_y(sounds)
        jump_pressed = inputs.is_jump_down()
        crouch_down = inputs.is_crouch_down()

        start_state = self.player.state
        self.update_player_state(
            on_ground, pressing_against_wall, jump_pressed, crouch_down)

        player_rect = self.player.get_target_bounds_rect(Direction.NONE)
        # TODO: Fix when you get stuck in walls.
        # in_wall = self.intersect_standing(player_rect)
        # if in_wall:
        #     self.player.x -= 16
        #     player_rect = self.player.get_target_bounds_rect(Direction.NONE)

        self.current_door = None
        for door in self.doors:
            door.update(player_rect)
            if door.closed:
                if door.destination is not None:
                    return Level(self.parent, door.destination)
                return Level(self.parent, self.map_path)
            if door.active:
                self.current_door = door

        for star in self.stars:
            if star.intersects(player_rect):
                sounds.play(Sound.STAR)
                self.stars.remove(star)
                self.star_count += 1
                self.toast_text = f'STARS x {self.star_count}'
                self.toast_counter = TOAST_TIME

        if True:
            attribs = []
            if on_ground:
                attribs.append('on_ground')
            if pressing_against_wall:
                attribs.append('pressing_against_wall')
            if crouch_down:
                attribs.append('crouch_down')
            if jump_pressed:
                attribs.append('jump_pressed')
            # if in_wall:
            #     attribs.append('in_wall')
            if self.player.is_idle:
                attribs.append('idle')
            if self.current_platform is not None:
                attribs.append(f'platform={self.current_platform.id}')
            transition = f'{start_state} x ({", ".join(attribs)}) -> {self.player.state}'
            if transition != self.transition:
                self.transition = transition
                print(transition)

        if self.player.is_dead:
            return KillScreen(self, lambda: Level(self.parent, self.map_path))

        if self.toast_counter == 0:
            if self.toast_position > -TOAST_HEIGHT:
                self.toast_position -= 1
        else:
            self.toast_counter -= 1
            if self.toast_position < 0:
                self.toast_position += 1

        return self

    def draw(self, surface: pygame.Surface, dest: pygame.Rect, images: ImageManager):
        # Make sure the player is on the screen, and then center them if possible.
        player_rect = self.player.get_target_bounds_rect(Direction.NONE)
        preferred_x, preferred_y = self.map.get_preferred_view(player_rect)
        player_x = self.player.x // 16
        player_y = self.player.y // 16
        player_draw_x: int = dest.width // 2
        player_draw_y: int = dest.height // 2
        if player_draw_x > player_x:
            player_draw_x = player_x
        if player_draw_y > player_y + 4:
            player_draw_y = player_y + 4
        if player_draw_x < player_x + dest.width - (self.map.width * self.map.tilewidth):
            player_draw_x = (
                player_x + dest.width -
                (self.map.width * self.map.tilewidth))
        if player_draw_y < player_y + dest.height - (self.map.height * self.map.tileheight):
            player_draw_y = (
                player_y + dest.height -
                (self.map.height * self.map.tileheight))
        map_offset: tuple[int, int] = (
            player_draw_x - player_x,
            player_draw_y - player_y)

        if preferred_x is not None:
            map_offset = (-preferred_x, map_offset[1])
            player_draw_x = player_x + map_offset[0]
        if preferred_y is not None:
            map_offset = (map_offset[0], -preferred_y)
            player_draw_y = player_y + map_offset[1]

        # Don't let the viewport move too much in between frames.
        if self.previous_map_offset is not None:
            prev = self.previous_map_offset
            if abs(map_offset[0] - prev[0]) > VIEWPORT_PAN_SPEED:
                if prev[0] < map_offset[0]:
                    map_offset = (prev[0] + VIEWPORT_PAN_SPEED, map_offset[1])
                elif prev[0] > map_offset[0]:
                    map_offset = (prev[0] - VIEWPORT_PAN_SPEED, map_offset[1])
                player_draw_x = player_x + map_offset[0]
            if abs(map_offset[1] - prev[1]) > VIEWPORT_PAN_SPEED:
                if prev[1] < map_offset[1]:
                    map_offset = (map_offset[0], prev[1] + VIEWPORT_PAN_SPEED)
                elif prev[1] > map_offset[1]:
                    map_offset = (map_offset[0], prev[1] - VIEWPORT_PAN_SPEED)
                player_draw_y = player_y + map_offset[1]
        self.previous_map_offset = map_offset

        # Do the actual drawing.
        self.map.draw_background(surface, dest, map_offset, self.switches)
        for door in self.doors:
            door.draw_background(surface, map_offset)
        for platform in self.platforms:
            platform.draw(surface, map_offset)
        for star in self.stars:
            star.draw(surface, map_offset)
        self.player.draw(surface, (player_draw_x, player_draw_y))
        for door in self.doors:
            door.draw_foreground(surface, map_offset)
        self.map.draw_foreground(surface, dest, map_offset, self.switches)

        # Draw the text overlay.
        top_bar_bgcolor = pygame.Color(0, 0, 0, 127)
        top_bar_area = pygame.Rect(
            dest.left, dest.top + self.toast_position, dest.width, TOAST_HEIGHT)
        top_bar = pygame.Surface(top_bar_area.size, pygame.SRCALPHA)
        top_bar.fill(top_bar_bgcolor)
        images.font.draw_string(top_bar, (2, 2), self.toast_text)
        surface.blit(top_bar, top_bar_area)
