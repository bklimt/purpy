
import os.path
import pygame
import typing

from gameobject.button import Button
from gameobject.door import Door
from imagemanager import ImageManager
from inputmanager import InputManager
from kill import KillScreen
from player import Player, PlayerState
from gameobject.platforms import Bagel, Conveyor, MovingPlatform, Platform, Spring
from render.rendercontext import RenderContext
from scene import Scene
from soundmanager import Sound, SoundManager
from gameobject.star import Star
from switchstate import SwitchState
from tilemap import TileMap, load_map
from utils import Direction, cmp_in_direction, opposite_direction, sign

# Horizontal speed.
TARGET_WALK_SPEED = 24
WALK_SPEED_ACCELERATION = 1
WALK_SPEED_DECELERATION = 3
SLIDE_SPEED_DECELERATION = 1

# Vertical speed.
COYOTE_TIME = 6  # How long to hover in the air before officially falling.
JUMP_GRACE_TIME = 12  # How long to remember jump was pressed while falling.
JUMP_INITIAL_SPEED = 48
JUMP_ACCELERATION = 2
JUMP_MAX_GRAVITY = 32
FALL_ACCELERATION = 5
FALL_MAX_GRAVITY = 32

SPRING_BOUNCE_DURATION = 30
SPRING_BOUNCE_VELOCITY = JUMP_INITIAL_SPEED
SPRING_JUMP_DURATION = 10
SPRING_JUMP_VELOCITY = 78

# Wall sliding.
WALL_SLIDE_SPEED = 4
WALL_JUMP_HORIZONTAL_SPEED = 48
WALL_JUMP_VERTICAL_SPEED = 48
WALL_STICK_TIME = 30
WALL_SLIDE_TIME = 60

VIEWPORT_PAN_SPEED = 5*16

TOAST_TIME = 100
TOAST_HEIGHT = 12


class Level:
    parent: Scene | None
    map_path: str
    name: str
    map: TileMap
    player: Player

    wall_stick_counter: int = WALL_STICK_TIME
    wall_stick_facing_right: bool = False
    wall_slide_counter: int = WALL_SLIDE_TIME

    coyote_counter: int = COYOTE_TIME
    jump_grace_counter: int = 0
    spring_counter: int = 0

    previous_map_offset: None | tuple[int, int]
    toast_text: str
    toast_position: int = -TOAST_HEIGHT
    toast_counter: int = TOAST_TIME

    # platforms, stars, and doors
    platforms: list[Platform]
    stars: list[Star]
    doors: list[Door]

    current_platform: Platform | None = None
    current_slopes: set[int]
    switches: SwitchState
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
        self.player.x = 128
        self.player.y = 128
        self.transition: str = ''
        self.platforms = []
        self.stars = []
        self.doors = []
        self.switches = SwitchState()
        self.current_switch_tiles = set()
        self.star_count = 0
        self.current_slopes = set()
        for obj in self.map.objects:
            if obj.properties.get('platform', False):
                self.platforms.append(MovingPlatform(obj, self.map.tileset))
            if obj.properties.get('bagel', False):
                self.platforms.append(Bagel(obj, self.map.tileset))
            if obj.properties.get('convey', '') != '':
                self.platforms.append(Conveyor(obj, self.map.tileset))
            if obj.properties.get('spring', '') != '':
                self.platforms.append(Spring(obj, self.map.tileset))
            if obj.properties.get('button', False):
                self.platforms.append(Button(obj, self.map.tileset))
            if obj.properties.get('door', False):
                self.doors.append(Door(obj))
            if obj.properties.get('star', False):
                self.stars.append(Star(obj, self.map.tileset))

    #
    # Movement.
    #

    def update_player_trajectory_x(self, inputs: InputManager):
        if self.player.state == PlayerState.CROUCHING:
            if self.player.dx > 0:
                self.player.dx = max(0, self.player.dx -
                                     SLIDE_SPEED_DECELERATION)
            elif self.player.dx < 0:
                self.player.dx = min(0, self.player.dx +
                                     SLIDE_SPEED_DECELERATION)
            return

        # Apply controller input.
        target_dx = 0
        if inputs.is_left_down() and not inputs.is_right_down():
            target_dx = -1 * TARGET_WALK_SPEED
        elif inputs.is_right_down() and not inputs.is_left_down():
            target_dx = TARGET_WALK_SPEED

        # Change the velocity toward the target velocity.
        if self.player.dx > 0:
            # We're facing right.
            if target_dx > self.player.dx:
                self.player.dx += WALK_SPEED_ACCELERATION
                self.player.dx = min(target_dx, self.player.dx)
            if target_dx < self.player.dx:
                self.player.dx -= WALK_SPEED_DECELERATION
                self.player.dx = max(target_dx, self.player.dx)
        elif self.player.dx < 0:
            # We're facing left.
            if target_dx > self.player.dx:
                self.player.dx += WALK_SPEED_DECELERATION
                self.player.dx = min(target_dx, self.player.dx)
            if target_dx < self.player.dx:
                self.player.dx -= WALK_SPEED_ACCELERATION
                self.player.dx = max(target_dx, self.player.dx)
        else:
            # We're stopped.
            if target_dx > self.player.dx:
                self.player.dx += WALK_SPEED_ACCELERATION
                self.player.dx = min(target_dx, self.player.dx)
            if target_dx < self.player.dx:
                self.player.dx -= WALK_SPEED_ACCELERATION
                self.player.dx = max(target_dx, self.player.dx)

    def update_player_trajectory_y(self, inputs: InputManager):
        if (self.player.state == PlayerState.STANDING or
                self.player.state == PlayerState.CROUCHING):
            # Fall at least one pixel so that we hit the ground again.
            self.player.dy = max(self.player.dy, 1)
        elif self.player.state == PlayerState.JUMPING:
            # Apply gravity.
            if self.player.dy < JUMP_MAX_GRAVITY:
                self.player.dy += JUMP_ACCELERATION
            self.player.dy = min(self.player.dy, JUMP_MAX_GRAVITY)
        elif self.player.state == PlayerState.FALLING:
            # Apply gravity.
            if self.player.dy < FALL_MAX_GRAVITY:
                self.player.dy += FALL_ACCELERATION
            self.player.dy = min(self.player.dy, FALL_MAX_GRAVITY)
        if self.player.state == PlayerState.WALL_SLIDING:
            # When you first grab the wall, don't start sliding for a while.
            if self.wall_slide_counter > 0:
                self.wall_slide_counter -= 1
                self.player.dy = 0
            else:
                self.player.dy = WALL_SLIDE_SPEED

    class PlatformIntersectionResult:
        offset: int
        platforms: set[Platform]

        def __init__(self):
            self.offset = 0
            self.platforms = set()

    def find_platform_intersections(self,
                                    player_rect: pygame.Rect,
                                    direction: Direction,
                                    is_backwards: bool = False
                                    ) -> PlatformIntersectionResult:
        result = Level.PlatformIntersectionResult()
        for platform in self.platforms:
            distance = platform.try_move_to(
                player_rect, direction, is_backwards)
            if distance == 0:
                continue

            cmp = cmp_in_direction(distance, result.offset, direction)
            if cmp < 0:
                result.offset = distance
                result.platforms = set([platform])
            elif cmp == 0:
                result.platforms.add(platform)
        return result

    class TryMovePlayerResult:
        """ The results of trying to move. """
        offset: int
        tile_ids: set[int]
        platforms: set[Platform]

        def __init__(self):
            self.offset = 0
            self.tile_ids = set()
            self.platforms = set()

    def try_move_player(self, direction: Direction, is_backwards: bool = False) -> TryMovePlayerResult:
        """ Returns how far this player needs to move in direction to not intersect, in sub-pixels. """
        player_rect = self.player.get_target_bounds_rect(direction)

        map_result = self.map.try_move_to(
            player_rect, direction, self.switches, is_backwards)
        platform_result = self.find_platform_intersections(
            player_rect, direction, is_backwards)

        result = Level.TryMovePlayerResult()
        if cmp_in_direction(platform_result.offset, map_result.hard_offset, direction) <= 0:
            result.offset = platform_result.offset
            result.platforms = platform_result.platforms
        else:
            result.offset = map_result.hard_offset
            result.tile_ids = map_result.tile_ids

        return result

    class MoveAndCheckResult:
        on_ground: bool = False
        on_tile_ids: set[int] = set()
        on_platforms: set[Platform] = set()
        hit_ceiling: bool = False
        against_wall: bool = False
        crushed_by_platform: bool = False
        stuck_in_wall: bool = False

    def move_and_check(self,
                       forward: Direction,
                       apply_offset: typing.Callable[[int], typing.Any]
                       ) -> MoveAndCheckResult:
        """ Returns whether the first move hit a wall or platform. """
        move_result1 = self.try_move_player(forward)
        apply_offset(move_result1.offset)

        # Try the opposite direction.
        move_result2 = self.try_move_player(
            opposite_direction(forward), is_backwards=True)
        offset = move_result2.offset
        apply_offset(offset)

        result = Level.MoveAndCheckResult()
        if forward == Direction.DOWN:
            result.on_ground = move_result1.offset != 0
            result.on_tile_ids = set(move_result1.tile_ids)
            result.on_platforms = set(move_result1.platforms)
        if forward == Direction.UP:
            # If we're traveling up, then if we hit something below, it's not the ground,
            # unless we're standing on a platform.
            if (self.player.state != PlayerState.JUMPING and
                    self.player.state != PlayerState.FALLING):
                result.on_ground = move_result2.offset != 0
            result.hit_ceiling = move_result1.offset != 0
            result.on_tile_ids = set(move_result2.tile_ids)
            result.on_platforms = set(move_result2.platforms)
        if forward == Direction.LEFT or forward == Direction.RIGHT:
            result.against_wall = move_result1.offset != 0

        # See if we're crushed.
        if offset != 0:
            crush_check = self.try_move_player(forward)
            if crush_check.offset != 0:
                crushed = False
                for platform in move_result1.platforms:
                    if platform.is_solid:
                        crushed = True
                for platform in move_result2.platforms:
                    if platform.is_solid:
                        crushed = True
                if crushed:
                    result.crushed_by_platform = True
                else:
                    result.stuck_in_wall = True

        return result

    class MovePlayerXResult:
        pushing_against_wall: bool = False
        stuck_in_wall: bool = False
        crushed_by_platform: bool = False

    def move_player_x(self, inputs: InputManager) -> MovePlayerXResult:
        result = Level.MovePlayerXResult()

        dx = self.player.dx
        if self.current_platform is not None:
            dx += self.current_platform.dx
        self.player.x += dx

        def inc_x(offset):
            self.player.x += offset

        move_result: Level.MoveAndCheckResult
        pushing: bool
        if dx < 0 or (dx == 0 and not self.player.facing_right):
            # Moving left.
            move_result = self.move_and_check(Direction.LEFT, inc_x)
            pushing = inputs.is_left_down()
        else:
            # Moving right.
            move_result = self.move_and_check(Direction.RIGHT, inc_x)
            pushing = inputs.is_right_down()

        result.pushing_against_wall = pushing and move_result.against_wall
        result.crushed_by_platform = move_result.crushed_by_platform
        result.stuck_in_wall = move_result.stuck_in_wall

        # If you're against the wall, you're stopped.
        if result.pushing_against_wall:
            self.player.dx = 0

        return result

    class MovePlayerYResult:
        on_ground: bool = False
        platforms: set[Platform] = set()
        tile_ids: set[int] = set()
        stuck_in_wall: bool = False
        crushed_by_platform: bool = False

    def get_slope_dy(self):
        slope_fall = 0
        for slope_id in self.current_slopes:
            slope = self.map.tileset.get_slope(slope_id)
            left_y = slope.left_y
            right_y = slope.right_y
            fall: int = 0
            if self.player.dx > 0 or (self.player.dx == 0 and self.player.facing_right):
                # The player is facing right.
                if right_y > left_y:
                    fall = (right_y - left_y) * 16
            else:
                # The player is facing left.
                if left_y > right_y:
                    fall = (left_y - right_y) * 16
            slope_fall = max(fall, slope_fall)
        return slope_fall

    def move_player_y(self, sounds: SoundManager) -> MovePlayerYResult:
        result = Level.MovePlayerYResult()

        dy = self.player.dy
        if self.current_platform is not None:
            # This could be positive or negative.
            dy += self.current_platform.dy

        # If you're on a slope, make sure to fall at least the slope amount.
        if dy >= 0:
            dy = max(dy, self.get_slope_dy())

        self.player.y += dy

        def inc_y(offset):
            self.player.y += offset

        if dy <= 0:
            # Moving up.
            move_result = self.move_and_check(Direction.UP, inc_y)
            if move_result.hit_ceiling:
                self.player.dy = 0

            result.on_ground = move_result.on_ground
            result.crushed_by_platform = move_result.crushed_by_platform
            result.stuck_in_wall = move_result.stuck_in_wall

            self.handle_slopes(move_result.on_tile_ids)
            self.handle_current_platforms(move_result.on_platforms)
        else:
            # Moving down.
            move_result = self.move_and_check(Direction.DOWN, inc_y)
            result.on_ground = move_result.on_ground
            result.tile_ids = set(move_result.on_tile_ids)
            result.platforms = set(move_result.on_platforms)
            result.crushed_by_platform = move_result.crushed_by_platform
            result.stuck_in_wall = move_result.stuck_in_wall

            self.handle_spikes(move_result.on_tile_ids)
            self.handle_switch_tiles(move_result.on_tile_ids, sounds)
            self.handle_slopes(move_result.on_tile_ids)
            self.handle_current_platforms(move_result.on_platforms)

        return result

    def handle_slopes(self, tiles: set[int]) -> None:
        self.current_slopes.clear()
        for tile_id in tiles:
            if self.map.tileset.get_bool_property(tile_id, 'slope', False):
                self.current_slopes.add(tile_id)

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
            sounds.play(Sound.CLICK)
            self.switches.apply_command(switch)

    class PlayerMovementResult:
        on_ground: bool = False
        pushing_against_wall: bool = False
        jump_down: bool = False
        jump_triggered: bool = False
        crouch_down: bool = False
        stuck_in_wall: bool = False
        crushed_by_platform: bool = False

    def update_player_movement(self, inputs: InputManager, sounds: SoundManager) -> PlayerMovementResult:
        self.update_player_trajectory_x(inputs)
        self.update_player_trajectory_y(inputs)

        result = Level.PlayerMovementResult()
        x_result = self.move_player_x(inputs)
        y_result = self.move_player_y(sounds)

        result.on_ground = y_result.on_ground
        result.pushing_against_wall = x_result.pushing_against_wall
        result.jump_down = inputs.is_jump_down()
        result.jump_triggered = inputs.is_jump_triggered()
        result.crouch_down = inputs.is_crouch_down()
        result.stuck_in_wall = x_result.stuck_in_wall or y_result.stuck_in_wall
        result.crushed_by_platform = x_result.crushed_by_platform or y_result.crushed_by_platform

        return result

    def update_player_state(self, movement: PlayerMovementResult):
        if movement.on_ground:
            self.coyote_counter = COYOTE_TIME
        else:
            if self.coyote_counter > 0:
                self.coyote_counter -= 1

        if self.jump_grace_counter > 0:
            self.jump_grace_counter -= 1

        if movement.crushed_by_platform:
            self.player.state = PlayerState.STOPPED
            self.player.is_dead = True
        elif self.player.state == PlayerState.STANDING:
            if (isinstance(self.current_platform, Spring) and
                    self.current_platform.launch):
                self.jump_grace_counter = 0
                self.player.state = PlayerState.JUMPING
                if movement.jump_triggered or self.jump_grace_counter > 0:
                    self.spring_counter = SPRING_JUMP_DURATION
                    self.player.dy = -1 * SPRING_JUMP_VELOCITY
                else:
                    self.spring_counter = SPRING_BOUNCE_DURATION
                    self.player.dy = -1 * SPRING_BOUNCE_VELOCITY
            elif self.coyote_counter == 0:
                self.player.state = PlayerState.FALLING
                self.player.dy = 0
                if self.current_platform is not None:
                    self.player.dx = self.current_platform.dx
            elif movement.crouch_down:
                self.player.state = PlayerState.CROUCHING
            elif movement.jump_triggered or self.jump_grace_counter > 0:
                if self.current_door is not None:
                    if self.current_door.is_open:
                        self.player.state = PlayerState.STOPPED
                        self.current_door.close()
                else:
                    self.jump_grace_counter = 0
                    self.player.state = PlayerState.JUMPING
                    if (isinstance(self.current_platform, Spring) and
                            self.current_platform.should_boost()):
                        self.spring_counter = SPRING_JUMP_DURATION
                        self.player.dy = -1 * SPRING_JUMP_VELOCITY
                    else:
                        self.spring_counter = 0
                        self.player.dy = -1 * JUMP_INITIAL_SPEED
                    if self.current_platform is not None:
                        self.player.dx += self.current_platform.dx
        elif self.player.state == PlayerState.FALLING:
            if movement.jump_triggered:
                self.jump_grace_timer = JUMP_GRACE_TIME
            if movement.on_ground:
                self.player.state = PlayerState.STANDING
                self.player.dy = 0
            else:
                if movement.pushing_against_wall and self.player.dy >= 0:
                    self.player.state = PlayerState.WALL_SLIDING
                    self.wall_slide_counter = WALL_SLIDE_TIME
        elif self.player.state == PlayerState.JUMPING:
            if movement.on_ground:
                self.player.state = PlayerState.STANDING
                self.player.dy = 0
            elif self.player.dy >= 0:
                self.player.state = PlayerState.FALLING
            else:
                if not movement.jump_down:
                    if self.spring_counter == 0:
                        self.player.state = PlayerState.FALLING
                        self.player.dy = 0
                    else:
                        self.spring_counter -= 1
        elif self.player.state == PlayerState.WALL_SLIDING:
            if movement.jump_triggered:
                self.player.state = PlayerState.JUMPING
                self.player.dy = -1 * WALL_JUMP_VERTICAL_SPEED
                if self.player.facing_right:
                    self.player.dx = -1 * WALL_JUMP_HORIZONTAL_SPEED
                else:
                    self.player.dx = WALL_JUMP_HORIZONTAL_SPEED
            elif movement.on_ground:
                self.player.state = PlayerState.STANDING
            elif movement.pushing_against_wall:
                self.wall_stick_counter = WALL_STICK_TIME
                self.wall_stick_facing_right = self.player.facing_right
            else:
                if self.wall_stick_facing_right != self.player.facing_right:
                    self.player.state = PlayerState.FALLING
                elif self.wall_stick_counter > 0:
                    self.wall_stick_counter -= 1
                else:
                    self.player.state = PlayerState.FALLING
        elif self.player.state == PlayerState.CROUCHING:
            if not movement.on_ground:
                self.player.state = PlayerState.FALLING
                self.player.dy = 0
            elif not movement.crouch_down:
                self.player.state = PlayerState.STANDING

    def update(self, inputs: InputManager, sounds: SoundManager) -> Scene | None:
        if inputs.is_cancel_triggered():
            return self.parent
        if inputs.is_restart_down():
            return Level(self.parent, self.map_path)

        self.map.update_animations()

        for platform in self.platforms:
            platform.update(self.switches, sounds)

        movement = Level.PlayerMovementResult()
        if self.player.state != PlayerState.STOPPED:
            movement = self.update_player_movement(inputs, sounds)

        start_state: PlayerState = self.player.state
        self.update_player_state(movement)

        # Make sure you aren't stuck in a wall.
        player_rect = self.player.get_target_bounds_rect(Direction.NONE)
        in_wall = movement.stuck_in_wall
        crushed = movement.crushed_by_platform

        self.current_door = None
        for door in self.doors:
            door.update(player_rect, self.star_count)
            if door.is_closed:
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
            if movement.on_ground:
                attribs.append('on_ground')
            if movement.pushing_against_wall:
                attribs.append('pushing_against_wall')
            if movement.crouch_down:
                attribs.append('crouch_down')
            if movement.jump_triggered:
                attribs.append('jump_triggered')
            if movement.jump_down:
                attribs.append('jump_down')
            if in_wall:
                attribs.append('in_wall')
            if crushed:
                attribs.append('crushed')
            if self.player.is_idle:
                attribs.append('idle')
            if self.current_platform is not None:
                attribs.append(f'platform={self.current_platform.id}')
            if len(self.current_slopes) > 0:
                attribs.append(f'slopes={self.current_slopes}')
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

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        dest = context.logical_area

        # TODO: Figure out what logical area means...
        dest = pygame.Rect(dest.x * 16, dest.y * 16, dest.w * 16, dest.h * 16)

        # Make sure the player is on the screen, and then center them if possible.
        player_rect = self.player.get_target_bounds_rect(Direction.NONE)
        preferred_x, preferred_y = self.map.get_preferred_view(player_rect)
        player_x = self.player.x
        player_y = self.player.y
        player_draw_x: int = dest.width // 2
        player_draw_y: int = dest.height // 2
        if player_draw_x > player_x:
            player_draw_x = player_x
        if player_draw_y > player_y + 4:
            player_draw_y = player_y + 4
        if player_draw_x < player_x + dest.width - (self.map.width * self.map.tilewidth * 16):
            player_draw_x = (
                player_x + dest.width -
                (self.map.width * self.map.tilewidth * 16))
        if player_draw_y < player_y + dest.height - (self.map.height * self.map.tileheight * 16):
            player_draw_y = (
                player_y + dest.height -
                (self.map.height * self.map.tileheight * 16))
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
        surface = context.player_surface
        dest = pygame.Rect(dest.x//16, dest.y//16, dest.w//16, dest.h//16)
        self.map.draw_background(surface, dest, map_offset, self.switches)
        for door in self.doors:
            door.draw_background(surface, map_offset, images)
        for platform in self.platforms:
            platform.draw(surface, map_offset)
        for star in self.stars:
            star.draw(context, map_offset)
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
        context.hud_surface.blit(top_bar, top_bar_area)

        context.dark = self.map.is_dark

        spotlight_pos = (player_draw_x + 12, player_draw_y + 12)
        spotlight_radius = 120.0
        context.add_light(spotlight_pos, spotlight_radius)
