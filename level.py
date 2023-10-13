
import inputmanager
from player import Player, PlayerState
import pygame
import tilemap


class Level:
    map: tilemap.TileMap
    player: Player

    def __init__(self):
        self.map = tilemap.load_map('assets/purple.tmx')
        self.player = Player()
        self.player.x = self.map.tilewidth * 16
        self.player.y = self.map.tileheight * 16

    def update_horizontal(self, input: inputmanager.InputManager):
        # Apply the input to adjust the velocity.
        target_dx = 0
        if input.is_left_down() and not input.is_right_down():
            target_dx = -32
        if input.is_right_down() and not input.is_left_down():
            target_dx = 32
        if self.player.state == PlayerState.CROUCHING:
            target_dx = 0
        if self.player.dx < target_dx:
            self.player.dx += 1
        if self.player.dx > target_dx:
            self.player.dx -= 1

        # See if moving is possible.
        new_x = self.player.x + self.player.dx
        player_rect = self.player.rect((new_x//16, self.player.y//16))
        if self.map.intersect(player_rect):
            self.player.dx = 0
        else:
            self.player.x = new_x

    def update_vertical(self, input: inputmanager.InputManager):
        # Apply gravity.
        if self.player.dy < 24:
            self.player.dy += 3
        if self.player.state == PlayerState.STANDING and input.is_jump_down():
            self.player.dy = -64
            self.player.state = PlayerState.AIRBORNE

        if self.player.dy > 24:
            self.player.dy = 24

        # See if moving is possible.
        new_y = self.player.y + self.player.dy
        player_rect = self.player.rect((self.player.x//16, new_y//16))
        if self.map.intersect(player_rect):
            if self.player.dy > 0 and self.player.state == PlayerState.AIRBORNE:
                self.player.state = PlayerState.STANDING
            self.player.dy = 0
        else:
            self.player.y = new_y
            if self.player.dy > 0:
                self.player.state = PlayerState.AIRBORNE

    def update(self, input: inputmanager.InputManager):
        if input.is_crouch_down():
            if self.player.state == PlayerState.STANDING:
                self.player.state = PlayerState.CROUCHING
        else:
            if self.player.state == PlayerState.CROUCHING:
                self.player.state = PlayerState.STANDING

        self.update_horizontal(input)
        self.update_vertical(input)

        player_rect = self.player.rect((self.player.x//16, self.player.y//16))
        if self.map.intersect(player_rect):
            self.player.x -= 16

        # print(f"state = {self.player.state}")

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        self.map.draw(surface, dest, (0, 0))
        self.player.draw(surface, (self.player.x//16, self.player.y//16))
