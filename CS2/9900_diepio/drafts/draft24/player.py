import math, pygame, diep_sprite
from constants import *

class PlayerCritter(diep_sprite.DiepSprite):
    def __init__(self, screen, x, y, color, radius, accel, hp, name):
        super().__init__(screen, x, y, color, radius, accel, hp,
                        sprite_type=TYPE_CRITTER,
                        draw_healthbar=True)
        self.vision_radius = 500
        self.name = name

    def update(self, sprites_in_range):
        pos = pygame.mouse.get_pos()
        x = pos[0] - self.screen.get_width()/2
        y = pos[1] - self.screen.get_height()/2
        self.angle = math.atan2(y,x)
        super().update()
