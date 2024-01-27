
import os.path
import pygame
import typing

from constants import *
from gameobject.button import Button
from gameobject.door import Door
from imagemanager import ImageManager
from inputmanager import InputSnapshot
from kill import KillScreen
from player import Player2, PlayerState
from gameobject.platforms import Bagel, Conveyor, MovingPlatform, Platform, Spring
from render.rendercontext import RenderContext
from scene import Scene
from soundmanager import Sound, SoundManager
from gameobject.star import Star
from switchstate import SwitchState
from tilemap import TileMap, load_map
from utils import Direction, cmp_in_direction, opposite_direction


class Level:
    parent: Scene | None
    name: str
    map: TileMap
    player: Player2

    restart_func: typing.Callable[[], Scene]
    next_func: typing.Callable[[str], Scene]

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

    def __init__(self, parent: Scene | None, map_path: str, images: ImageManager):
        self.parent = parent
        self.restart_func = lambda: Level(parent, map_path, images)
        self.next_func = lambda destination: Level(parent, destination, images)
        # self.map_path = map_path
        self.name = os.path.splitext(os.path.basename(map_path))[0]
        self.toast_text = self.name
        self.previous_map_offset = None
        self.map = load_map(map_path, images)
        self.player = Player2(images)
        self.player.x = (128 * SUBPIXELS) // 16
        self.player.y = (128 * SUBPIXELS) // 16
        self.transition: str = ''
        self.platforms = []
        self.stars = []
        self.doors = []
        self.current_door = None
        self.switches = SwitchState()
        self.current_switch_tiles = set()
        self.star_count = 0
        self.current_slopes = set()
        for obj in self.map.objects:
            if obj.properties.get('platform', False):
                self.platforms.append(MovingPlatform(obj, self.map))
            if obj.properties.get('bagel', False):
                self.platforms.append(Bagel(obj, self.map))
            if obj.properties.get('convey', '') != '':
                self.platforms.append(Conveyor(obj, self.map))
            if obj.properties.get('spring', '') != '':
                self.platforms.append(Spring(obj, self.map, images))
            if obj.properties.get('button', False):
                self.platforms.append(Button(obj, self.map, images))
            if obj.properties.get('door', False):
                self.doors.append(Door(obj, images))
            if obj.properties.get('star', False):
                self.stars.append(Star(obj, self.map))

    #
    # Movement.
    #

    def update_player_trajectory_x(self, inputs: InputSnapshot):
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
        if inputs.player_left and not inputs.player_right:
            target_dx = -1 * TARGET_WALK_SPEED
        elif inputs.player_right and not inputs.player_left:
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

    def update_player_trajectory_y(self, inputs: InputSnapshot):
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

    def move_player_x(self, inputs: InputSnapshot) -> MovePlayerXResult:
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
            pushing = inputs.player_left
        else:
            # Moving right.
            move_result = self.move_and_check(Direction.RIGHT, inc_x)
            pushing = inputs.player_right

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
            slope = self.map.get_slope(slope_id)
            if slope is None:
                raise Exception("slope is not a slope")
            left_y = slope.left_y
            right_y = slope.right_y
            fall: int = 0
            if self.player.dx > 0 or (self.player.dx == 0 and self.player.facing_right):
                # The player is facing right.
                if right_y > left_y:
                    fall = right_y - left_y
            else:
                # The player is facing left.
                if left_y > right_y:
                    fall = left_y - right_y
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
            if self.map.is_slope(tile_id):
                self.current_slopes.add(tile_id)

    def handle_spikes(self, tiles: set[int]):
        for tile_id in tiles:
            props = self.map.get_tile_properties(tile_id)
            if props.get('deadly', False):
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
            props = self.map.get_tile_properties(t)
            switch = props.get('switch', None)
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

    def update_player_movement(self, inputs: InputSnapshot, sounds: SoundManager) -> PlayerMovementResult:
        self.update_player_trajectory_x(inputs)
        self.update_player_trajectory_y(inputs)

        result = Level.PlayerMovementResult()
        x_result = self.move_player_x(inputs)
        y_result = self.move_player_y(sounds)

        result.on_ground = y_result.on_ground
        result.pushing_against_wall = x_result.pushing_against_wall
        result.jump_down = inputs.player_jump_down
        result.jump_triggered = inputs.player_jump_trigger
        result.crouch_down = inputs.player_crouch
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

    def update(self, inputs: InputSnapshot, sounds: SoundManager) -> Scene | None:
        if inputs.cancel:
            return self.parent
        # if inputs.is_restart_down():
        #    return self.restart_func()

        self.map.update_animations()

        for platform in self.platforms:
            platform.update(self.switches, sounds)

        movement = Level.PlayerMovementResult()
        if self.player.state != PlayerState.STOPPED:
            movement = self.update_player_movement(inputs, sounds)

        start_state: PlayerState = self.player.state
        self.update_player_state(movement)

        # Make sure you aren't stuck in a wall.
        player_rect = self.player.get_target_bounds_rect(None)
        in_wall = movement.stuck_in_wall
        crushed = movement.crushed_by_platform

        self.current_door = None
        for door in self.doors:
            door.update(player_rect, self.star_count)
            if door.is_closed:
                if door.destination is not None:
                    return self.next_func(door.destination)
                return self.restart_func()
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
            attrib_list = ", ".join(attribs)
            transition = f'{start_state} x ({attrib_list}) -> {self.player.state}'
            if transition != self.transition:
                self.transition = transition
                print(transition)

        if self.player.is_dead:
            return KillScreen(self, self.restart_func)

        if self.toast_counter == 0:
            if self.toast_position > -TOAST_HEIGHT:
                self.toast_position -= TOAST_SPEED
        else:
            self.toast_counter -= 1
            if self.toast_position < 0:
                self.toast_position += TOAST_SPEED

        return self

    def draw(self, context: RenderContext, images: ImageManager) -> None:
        dest = context.logical_area

        # Make sure the player is on the screen, and then center them if possible.
        player_rect = self.player.get_target_bounds_rect(None)
        preferred_x, preferred_y = self.map.get_preferred_view(player_rect)
        player_x = self.player.x
        player_y = self.player.y
        player_draw_x: int = dest.width // 2
        player_draw_y: int = dest.height // 2
        # Don't waste space on the sides of the screen beyond the map.
        if player_draw_x > player_x:
            player_draw_x = player_x
        # The map is drawn 4 pixels from the top of the screen.
        if player_draw_y > player_y + 4:
            player_draw_y = player_y + 4
        right_limit = dest.width - \
            (self.map.width * self.map.tilewidth * SUBPIXELS)
        if player_draw_x < player_x + right_limit:
            player_draw_x = player_x + right_limit
        bottom_limit = dest.height - \
            (self.map.height * self.map.tileheight * SUBPIXELS)
        if player_draw_y < player_y + bottom_limit:
            player_draw_y = player_y + bottom_limit
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
        self.map.draw_background(context, context.player_batch,
                                 dest, map_offset, self.switches)
        for door in self.doors:
            door.draw_background(
                context, context.player_batch, map_offset, images)
        for platform in self.platforms:
            platform.draw(context, context.player_batch, map_offset)
        for star in self.stars:
            star.draw(context, map_offset)
        self.player.draw(context, context.player_batch,
                         (player_draw_x, player_draw_y))
        for door in self.doors:
            door.draw_foreground(context, context.player_batch, map_offset)
        self.map.draw_foreground(context, context.player_batch,
                                 dest, map_offset, self.switches)

        # Draw the text overlay.
        top_bar_bgcolor = pygame.Color(0, 0, 0, 127)
        top_bar_area = pygame.Rect(
            dest.left, dest.top + self.toast_position, dest.width, TOAST_HEIGHT)
        if top_bar_area.bottom > 0:
            context.hud_batch.draw_rect(top_bar_area, top_bar_bgcolor)
            images.font.draw_string(
                context.hud_batch,
                (top_bar_area.x + 2*SUBPIXELS,
                 top_bar_area.y + 2*SUBPIXELS),
                self.toast_text)

        context.dark = self.map.is_dark

        spotlight_pos = (
            player_draw_x + 12 * SUBPIXELS,
            player_draw_y + 12 * SUBPIXELS)
        spotlight_radius = 120.0 * SUBPIXELS
        context.add_light(spotlight_pos, spotlight_radius)
