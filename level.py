
import inputmanager
import player as play
import pygame
import tilemap


class Level:
    # These are in 1/16 sub-pixels.
    x: int = 0
    y: int = 0
    dx: int = 0
    dy: int = 0
    map: tilemap.TileMap
    player: play.Player

    def __init__(self):
        self.map = tilemap.load_map('assets/purple.tmx')
        self.x = self.map.tilewidth * 16
        self.y = self.map.tileheight * 16
        self.player = play.Player()

    def update_horizontal(self, input: inputmanager.InputManager):
        # Apply the input to adjust the velocity.
        target_dx = 0
        if input.is_left_down() and not input.is_right_down():
            target_dx = -16
        if input.is_right_down() and not input.is_left_down():
            target_dx = 16
        if self.dx < target_dx:
            self.dx += 1
        if self.dx > target_dx:
            self.dx -= 1

        # See if moving is possible.
        new_x = self.x + self.dx
        player_rect = self.player.rect((new_x//16, self.y//16))
        if not self.map.intersect(player_rect):
            self.x = new_x

    def update_vertical(self, input: inputmanager.InputManager):
        # Apply gravity.
        if self.dy < 16:
            self.dy += 1
        if input.is_jump_down():
            self.dy = -16

        # See if moving is possible.
        new_y = self.y + self.dy
        player_rect = self.player.rect((self.x//16, new_y//16))
        if not self.map.intersect(player_rect):
            self.y = new_y

    def update(self, input: inputmanager.InputManager):
        self.update_horizontal(input)
        self.update_vertical(input)

    def draw(self, surface: pygame.Surface, dest: pygame.Rect):
        self.map.draw(surface, dest, (0, 0))
        self.player.draw(surface, (self.x//16, self.y//16))
