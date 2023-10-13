
import inputmanager
from player import Player, PlayerState
import pygame
import tilemap

TARGET_WALK_SPEED = 32
TARGET_AIRBORNE_SPEED = 16
WALK_SPEED_ACCELERATION = 1
MAX_GRAVITY = 24
WALL_SLIDE_SPEED = 2
GRAVITY_ACCELERATION = 1
JUMP_SPEED = 32
WALL_JUMP_HORIZONTAL_SPEED = 24
WALL_JUMP_VERTICAL_SPEED = 24


class Level:
    map: tilemap.TileMap
    player: Player

    def __init__(self):
        self.map = tilemap.load_map('assets/purple.tmx')
        self.player = Player()
        self.player.x = self.map.tilewidth * 16
        self.player.y = self.map.tileheight * 16
        self.transition: str = ''

    def is_on_ground(self) -> bool:
        player_rect = self.player.rect(
            (self.player.x//16, (self.player.y+16)//16))
        return self.map.intersect(player_rect)

    def is_pressing_against_wall(self, input: inputmanager.InputManager) -> bool:
        if input.is_left_down() and not input.is_right_down():
            player_rect = self.player.rect(
                ((self.player.x-1)//16, self.player.y//16))
            return self.map.intersect(player_rect)
        if input.is_right_down() and not input.is_left_down():
            player_rect = self.player.rect(
                ((self.player.x+1)//16, self.player.y//16))
            return self.map.intersect(player_rect)
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
            if self.map.intersect(player_rect):
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
            if self.map.intersect(player_rect):
                if self.player.dy < 0:
                    self.player.dy = 0
                return True
            else:
                self.player.y = new_y
        return False

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
                print("was standing and is now falling")
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
            elif not pressing_against_wall:
                self.player.state = PlayerState.AIRBORNE
        elif self.player.state == PlayerState.CROUCHING:
            if not crouch_down:
                self.player.state = PlayerState.STANDING

        player_rect = self.player.rect((self.player.x//16, self.player.y//16))
        in_wall = self.map.intersect(player_rect)
        if in_wall:
            self.player.x -= 16

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
            transition = f'{start_state} x ({", ".join(inputs)}) -> {self.player.state}'
            if transition != self.transition:
                self.transition = transition
                print(transition)

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        self.map.draw(surface, dest, (0, 0))
        self.player.draw(surface, (self.player.x//16, self.player.y//16))
