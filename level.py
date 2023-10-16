
from font import Font
import inputmanager
import os.path
from player import Player, PlayerState
from platforms import Bagel, MovingPlatform, Platform
import pygame
import tilemap

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


class Level:
    name: str
    map: tilemap.TileMap
    platforms: list[Platform]
    player: Player
    wall_stick_counter: int = WALL_STICK_TIME
    wall_stick_facing_right: bool = False
    wall_slide_counter: int = WALL_SLIDE_TIME
    current_platform: Platform | None = None
    font: Font

    def __init__(self, map_path: str):
        self.name = os.path.splitext(os.path.basename(map_path))[0]
        self.font = Font()
        self.map = tilemap.load_map(map_path)
        self.player = Player()
        self.player.x = self.map.tilewidth * 16
        self.player.y = self.map.tileheight * 16
        self.transition: str = ''
        self.platforms = []
        for obj in self.map.objects:
            if obj.properties.get('platform', False):
                self.platforms.append(MovingPlatform(obj, self.map.tileset))
            if obj.properties.get('bagel', False):
                self.platforms.append(Bagel(obj, self.map.tileset))

    def intersect_ground(self, player_rect: pygame.Rect) -> bool:
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
        if self.map.intersect(player_rect):
            return True
        return False

    def intersect_vertical(self, player_rect: pygame.Rect, check_platforms: bool) -> bool:
        """ Checks the ground when falling or jumping. """
        if check_platforms:
            for platform in self.platforms:
                if platform.intersect_top(player_rect):
                    return True
        if self.map.intersect(player_rect):
            return True
        return False

    def intersect_horizontal(self, player_rect: pygame.Rect) -> bool:
        """ Checks for collisions when moving right or left. """
        return self.map.intersect(player_rect)

    def intersect_standing(self, player_rect: pygame.Rect) -> bool:
        """ Checks for collisions when the player is just, like, standing there being cool. """
        return self.map.intersect(player_rect)

    def is_on_ground(self) -> bool:
        if self.player.dy < 0:
            self.current_platform = None
            for platform in self.platforms:
                platform.occupied = False
            return False
        player_rect = self.player.rect(
            (self.player.x//16, (self.player.y+16)//16))
        return self.intersect_ground(player_rect)

    def is_pressing_against_wall(self, input: inputmanager.InputManager) -> bool:
        if input.is_left_down() and not input.is_right_down():
            player_rect = self.player.rect(
                ((self.player.x-1)//16, self.player.y//16))
            return self.intersect_horizontal(player_rect)
        if input.is_right_down() and not input.is_left_down():
            player_rect = self.player.rect(
                ((self.player.x+1)//16, self.player.y//16))
            return self.intersect_horizontal(player_rect)
        return False

    def update_horizontal(self, input: inputmanager.InputManager) -> bool:
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

    def update_vertical(self, input: inputmanager.InputManager) -> bool:
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

        new_x = self.player.x + self.current_platform.dx
        new_y = self.player.y + self.current_platform.dy
        player_rect = self.player.rect((new_x//16, new_y//16))
        if not self.intersect_standing(player_rect):
            self.player.x = new_x
            self.player.y = new_y
            # To make sure things stay pixel perfect, make sure the subpixels are the same.
            self.player.y = ((self.player.y // 16) * 16) + \
                (self.current_platform.y % 16)

    def update(self, input: inputmanager.InputManager):
        self.update_horizontal(input)
        self.update_vertical(input)

        on_ground = self.is_on_ground()
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

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        # Make sure the player is on the screen, and then center them if possible.
        player_x = self.player.x//16
        player_y = self.player.y//16
        player_draw_x = dest.width//2
        player_draw_y = dest.height//2
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
        map_offset = (
            player_draw_x - player_x,
            player_draw_y - player_y)

        # Do the actual drawing.
        self.map.draw_background(surface, dest, map_offset)
        for platform in self.platforms:
            platform.draw(surface, map_offset)
        self.player.draw(surface, (player_draw_x, player_draw_y))
        self.map.draw_foreground(surface, dest, map_offset)

        # Draw the text overlay.
        top_bar_bgcolor = pygame.Color(0, 0, 0, 63)
        top_bar_area = pygame.Rect(dest.left, dest.top, dest.width, 12)
        top_bar = pygame.Surface(top_bar_area.size, pygame.SRCALPHA)
        top_bar.fill(top_bar_bgcolor)
        surface.blit(top_bar, top_bar_area)
        # pygame.draw.rect(surface, text_back, top_bar)
        self.font.draw_string(surface, (2, 2), self.name)
