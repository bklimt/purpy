
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
from tilemap import TileMap, load_map

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
TOAST_TIME = 200
TOAST_HEIGHT = 12


def sign(n: int):
    if n < 0:
        return -1
    if n > 0:
        return 1
    return 0


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
    toast_position: int = -TOAST_HEIGHT
    toast_counter: int = TOAST_TIME

    platforms: list[Platform]
    current_platform: Platform | None = None
    switches: set[str]
    current_switch_tiles: set[int]
    doors: list[Door]
    current_door: Door | None

    def __init__(self, parent: Scene | None, map_path: str):
        self.parent = parent
        self.map_path = map_path
        self.name = os.path.splitext(os.path.basename(map_path))[0]
        self.previous_map_offset = None
        self.map = load_map(map_path)
        self.player = Player()
        self.player.x = self.map.tilewidth * 16
        self.player.y = self.map.tileheight * 16
        self.transition: str = ''
        self.platforms = []
        self.switches = set()
        self.current_switch_tiles = set()
        self.doors = []
        for obj in self.map.objects:
            if obj.properties.get('platform', False):
                self.platforms.append(MovingPlatform(obj, self.map.tileset))
            if obj.properties.get('bagel', False):
                self.platforms.append(Bagel(obj, self.map.tileset))
            if obj.properties.get('door', False):
                self.doors.append(Door(obj))

    def handle_switch_tiles(self, tiles: set[int], sounds: SoundManager):
        previous = self.current_switch_tiles
        self.current_switch_tiles = tiles
        for t in tiles:
            if t in previous:
                continue
            switch = self.map.tileset.get_str_property(t, 'switch')
            if switch is None:
                raise Exception('non-switch passed to switch code')
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

    def intersect_ground(self, player_rect: pygame.Rect, sounds: SoundManager) -> bool:
        """ Checks the ground underneath the player. """
        self.current_platform = None
        for platform in self.platforms:
            if platform.intersect_top(player_rect):
                platform.occupied = True
                self.current_platform = platform
                # To make sure things stay pixel perfect, make sure the subpixels are the same.
                self.player.y = ((self.player.y // 16) * 16) + \
                    (self.current_platform.y % 16)
            else:
                platform.occupied = False
        if self.current_platform is not None:
            return True
        tiles: list[int] = self.map.intersect(player_rect, self.switches)
        switch_tiles: set[int] = set([
            t for t in tiles if self.map.tileset.get_str_property(t, 'switch') is not None
        ])
        self.handle_switch_tiles(switch_tiles, sounds)
        if len(tiles) > 0:
            for tile in tiles:
                if self.map.tileset.get_bool_property(tile, 'deadly'):
                    self.player.is_dead = True
            return True
        return False

    def intersect_vertical(self, player_rect: pygame.Rect, check_platforms: bool) -> bool:
        """ Checks the ground when falling or jumping. """
        if check_platforms:
            for platform in self.platforms:
                if platform.intersect_top(player_rect):
                    return True
        if self.intersect_standing(player_rect):
            return True
        return False

    def intersect_horizontal(self, player_rect: pygame.Rect) -> bool:
        """ Checks for collisions when moving right or left. """
        return self.intersect_standing(player_rect)

    def intersect_standing(self, player_rect: pygame.Rect) -> bool:
        """ Checks for collisions when the player is just, like, standing there being cool. """
        if len(self.map.intersect(player_rect, self.switches)) > 0:
            return True
        for platform in self.platforms:
            if not platform.is_solid:
                continue
            if platform.intersect(player_rect):
                return True
        return False

    def is_on_ground(self, sounds: SoundManager) -> bool:
        if self.player.dy < 0:
            self.current_platform = None
            for platform in self.platforms:
                platform.occupied = False
            return False
        player_rect = self.player.rect(
            (self.player.x//16, (self.player.y+16)//16))
        return self.intersect_ground(player_rect, sounds)

    def is_pressing_against_wall(self, input: InputManager) -> bool:
        if input.is_left_down() and not input.is_right_down():
            player_rect = self.player.rect(
                ((self.player.x-1)//16, self.player.y//16))
            return self.intersect_horizontal(player_rect)
        if input.is_right_down() and not input.is_left_down():
            player_rect = self.player.rect(
                ((self.player.x+1)//16, self.player.y//16))
            return self.intersect_horizontal(player_rect)
        return False

    def update_horizontal(self, input: InputManager) -> bool:
        """ Handles moving right and left. Returns true if a wall is hit. """
        # Apply the input to adjust the target velocity.
        target_dx = 0
        if input.is_left_down() and not input.is_right_down():
            if self.player.state == PlayerState.AIRBORNE:
                # If you're in the air, you can only go fast if you already were.
                target_dx = min(self.player.dx, -1 * TARGET_AIRBORNE_SPEED)
            else:
                target_dx = -1 * TARGET_WALK_SPEED
        if input.is_right_down() and not input.is_left_down():
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

        # See if moving is possible.
        target_x = self.player.x + self.player.dx
        while self.player.x != target_x:
            delta = target_x - self.player.x
            if abs(delta) > 16:
                if delta < 0:
                    delta = -16
                else:
                    delta = 16
            new_x = self.player.x + delta
            player_rect = self.player.rect((new_x//16, self.player.y//16))
            if self.intersect_horizontal(player_rect):
                self.player.dx = 0
                return True
            else:
                self.player.x = new_x
        return False

    def update_vertical(self, input: InputManager) -> bool:
        """ Handles moving up and down. Returns true if a wall is hit. """
        if self.player.state == PlayerState.AIRBORNE:
            # Apply gravity.
            if self.player.dy < MAX_GRAVITY:
                self.player.dy += GRAVITY_ACCELERATION
            if self.player.dy > MAX_GRAVITY:
                self.player.dy = MAX_GRAVITY
        elif self.player.state == PlayerState.WALL_SLIDING:
            # When you first grab the wall, don't start sliding for a while.
            if self.wall_slide_counter > 0:
                self.wall_slide_counter -= 1
                self.player.dy = 0
            else:
                self.player.dy = WALL_SLIDE_SPEED
        else:
            self.player.dy = 0
        # print(f'state = {self.player.state}, dy = {self.player.dy}')

        # See if moving is possible.
        target_y = self.player.y + self.player.dy
        while self.player.y != target_y:
            delta = target_y - self.player.y
            if abs(delta) > 16:
                if delta < 0:
                    delta = -16
                else:
                    delta = 16
            new_y = self.player.y + delta
            player_rect = self.player.rect((self.player.x//16, new_y//16))
            if self.intersect_vertical(player_rect, self.player.dy >= 0):
                if self.player.dy < 0:
                    self.player.dy = 0
                return True
            else:
                self.player.y = new_y
        return False

    def update_move_with_platform(self):
        if self.current_platform is None:
            return
        platform = self.current_platform
        new_x = self.player.x + platform.dx
        new_y = self.player.y + platform.dy
        player_rect = self.player.rect((new_x//16, new_y//16))
        if not self.intersect_standing(player_rect):
            self.player.x = new_x
            self.player.y = new_y
            # To make sure things stay pixel perfect, make sure the subpixels are the same.
            self.player.y = ((self.player.y // 16) * 16) + (platform.y % 16)
        else:
            if platform.is_solid:
                print(f'crushed by platform {platform.id}')
                self.player.is_dead = True

    def handle_solid_platforms(self):
        for platform in self.platforms:
            player_rect = self.player.rect(
                (self.player.x//16, self.player.y//16))
            if not platform.is_solid:
                continue
            if platform.intersect(player_rect):
                new_x = self.player.x + sign(platform.dx) * 16
                new_y = self.player.y + sign(platform.dy)*16
                player_rect = self.player.rect((new_x//16, new_y//16))
                if not self.intersect_standing(player_rect):
                    self.player.x = new_x
                    self.player.y = new_y
                else:
                    self.player.is_dead = True

    def update(self, input: InputManager, sounds: SoundManager) -> Scene | None:
        if input.is_cancel_triggered():
            return self.parent
        if input.is_restart_down():
            return Level(self.parent, self.map_path)

        if self.player.state != PlayerState.STOPPED:
            self.update_horizontal(input)
        self.update_vertical(input)

        on_ground = self.is_on_ground(sounds)
        pressing_against_wall = self.is_pressing_against_wall(input)
        crouch_down = input.is_crouch_down()
        jump_pressed = input.is_jump_down()

        start_state = self.player.state
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

        player_rect = self.player.rect((self.player.x//16, self.player.y//16))
        in_wall = self.intersect_standing(player_rect)
        if in_wall:
            self.player.x -= 16

        for platform in self.platforms:
            platform.update()
        self.update_move_with_platform()

        self.handle_solid_platforms()

        self.current_door = None
        player_rect = self.player.rect((self.player.x//16, self.player.y//16))
        for door in self.doors:
            door.update(player_rect)
            if door.closed:
                if door.destination is not None:
                    return Level(self.parent, door.destination)                    
                return Level(self.parent, self.map_path)
            if door.active:
                self.current_door = door

        if True:
            inputs = []
            if on_ground:
                inputs.append('on_ground')
            if pressing_against_wall:
                inputs.append('pressing_against_wall')
            if crouch_down:
                inputs.append('crouch_down')
            if jump_pressed:
                inputs.append('jump_pressed')
            if in_wall:
                inputs.append('in_wall')
            if self.player.is_idle:
                inputs.append('idle')
            if self.current_platform is not None:
                inputs.append(f'platform={self.current_platform.id}')
            transition = f'{start_state} x ({", ".join(inputs)}) -> {self.player.state}'
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
        player_x: int = self.player.x//16
        player_y: int = self.player.y//16

        player_rect = self.player.rect((player_x, player_y))
        preferred_x, preferred_y = self.map.get_preferred_view(player_rect)
        player_draw_x: int = dest.width//2
        player_draw_y: int = dest.height//2
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
        images.font.draw_string(top_bar, (2, 2), self.name)
        surface.blit(top_bar, top_bar_area)
