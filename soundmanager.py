
import pygame.mixer

from enum import Enum


class Sound(Enum):
    CLICK = 0
    STAR = 1


class SoundManager:
    sounds: dict[Sound, pygame.mixer.Sound]

    def __init__(self):
        self.sounds = {
            Sound.CLICK: pygame.mixer.Sound('assets/sounds/click.wav'),
            Sound.STAR: pygame.mixer.Sound('assets/sounds/star.wav'),
        }

    def play(self, sound: Sound):
        self.sounds[sound].play()
