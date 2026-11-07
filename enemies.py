import pygame
import math
from settings import WIDTH, GROUND_Y
from sound_manager import sound_manager

class Enemy:
    def __init__(self, x, ground_y, min_x=0, max_x=WIDTH):
        self.width = 44
        self.height = 42
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y - self.height
        self.vx = -1.4
        self.min_x = min_x
        self.max_x = max_x
        self.alive = True
        self.is_flattened = False
        self.flatten_timer = 0
        self.anim_walk = 0.0

    def update(self, pipes):
        if not self.alive:
            return

        if self.is_flattened:
            self.flatten_timer += 1
            if self.flatten_timer > 35:
                self.alive = False
            return

        self.x += self.vx
        self.anim_walk += 0.16

        if self.x <= self.min_x:
            self.x = self.min_x
            self.vx = abs(self.vx)
        elif self.x + self.width >= self.max_x:
            self.x = self.max_x - self.width
            self.vx = -abs(self.vx)

        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for p in pipes:
            pipe_box = pygame.Rect(p.x, p.y - p.lip_height, p.lip_width, p.height + p.lip_height)
            if enemy_rect.colliderect(pipe_box):
                if self.vx > 0:
                    self.x = pipe_box.left - self.width
                    self.vx = -self.vx
                else:
                    self.x = pipe_box.right
                    self.vx = -self.vx

    def stomp(self):
        self.is_flattened = True
        sound_manager.play_bump()

    def draw(self, surf):
        if not self.alive:
            return

        x = int(self.x)
        y = int(self.y)

        if self.is_flattened:
            flat_h = 16
            flat_y = self.ground_y - flat_h
            pygame.draw.ellipse(surf, (230, 90, 130), (x - 2, flat_y, self.width + 4, flat_h))
            # Ojos cerrados > <
            pygame.draw.line(surf, (60, 20, 40), (x + 10, flat_y + 4), (x + 16, flat_y + 11), 2)
            pygame.draw.line(surf, (60, 20, 40), (x + 16, flat_y + 4), (x + 10, flat_y + 11), 2)
            pygame.draw.line(surf, (60, 20, 40), (x + 28, flat_y + 4), (x + 34, flat_y + 11), 2)
            pygame.draw.line(surf, (60, 20, 40), (x + 34, flat_y + 4), (x + 28, flat_y + 11), 2)
            return

        # Goomba Kawaii Pastel (Hongo caramelo rosa/frambuesa con patitas)
        foot_tilt = math.sin(self.anim_walk) * 3
        foot_color = (195, 70, 110)
        pygame.draw.ellipse(surf, foot_color, (x + 3, y + self.height - 10 + foot_tilt, 16, 12))
        pygame.draw.ellipse(surf, foot_color, (x + self.width - 19, y + self.height - 10 - foot_tilt, 16, 12))

        # Cabeza hongo
        head_color = (255, 105, 150)
        head_dark = (220, 75, 120)
        pygame.draw.ellipse(surf, head_dark, (x, y + 2, self.width, self.height - 6))
        pygame.draw.ellipse(surf, head_color, (x + 1, y, self.width - 2, self.height - 8))

        # Lunares blancos suaves
        pygame.draw.circle(surf, (255, 255, 255), (x + 11, y + 9), 4)
        pygame.draw.circle(surf, (255, 255, 255), (x + self.width - 12, y + 9), 4)

        # Base / cuerpo crema
        pygame.draw.ellipse(surf, (255, 240, 225), (x + 9, y + self.height - 20, self.width - 18, 14))

        # Ojitos kawaii
        pupil_off = 2 if self.vx > 0 else 0
        pygame.draw.ellipse(surf, (255, 255, 255), (x + 10, y + 16, 8, 11))
        pygame.draw.ellipse(surf, (255, 255, 255), (x + self.width - 18, y + 16, 8, 11))
        pygame.draw.ellipse(surf, (60, 30, 50), (x + 12 + pupil_off, y + 19, 5, 7))
        pygame.draw.ellipse(surf, (60, 30, 50), (x + self.width - 16 + pupil_off, y + 19, 5, 7))
        
        # Mejillas sonrojadas
        pygame.draw.circle(surf, (255, 160, 190), (x + 7, y + 27), 4)
        pygame.draw.circle(surf, (255, 160, 190), (x + self.width - 7, y + 27), 4)
