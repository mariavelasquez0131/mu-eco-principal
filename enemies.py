import pygame
import os
import math
from settings import WIDTH, GROUND_Y
from sound_manager import sound_manager

class PngEnemy:
    """Enemigo basado en sprites/enemigo.png que persigue al jugador y le quita vida"""
    def __init__(self, x, ground_y, speed=2.2, jump_power=-10.5):
        self.width = 54
        self.height = 54
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y - self.height
        self.vx = 0.0
        self.vy = 0.0
        self.speed = speed
        self.jump_power = jump_power
        self.gravity = 0.6
        self.is_grounded = True
        self.facing_right = False
        self.alive = True
        self.anim_walk = 0.0

        # Cargar sprite enemigo.png
        sprite_path = os.path.join("sprites", "enemigo.png")
        if os.path.exists(sprite_path):
            raw_img = pygame.image.load(sprite_path).convert_alpha()
        else:
            raw_img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(raw_img, (180, 40, 40), (self.width // 2, self.height // 2), self.width // 2)

        self.sprite_right = pygame.transform.smoothscale(raw_img, (self.width, self.height))
        self.sprite_left = pygame.transform.flip(self.sprite_right, True, False)

    def update(self, player, pipes, blocks):
        if not self.alive:
            return

        self.anim_walk += 0.18

        # 1. Inteligencia Artificial: Perseguir al jugador
        player_cx = player.x + player.sprite_right.get_width() / 2
        enemy_cx = self.x + self.width / 2

        dx = player_cx - enemy_cx
        dist = abs(dx)

        if dist > 8:
            if dx > 0:
                self.vx = self.speed
                self.facing_right = True
            else:
                self.vx = -self.speed
                self.facing_right = False
        else:
            self.vx = 0

        # Salto si el jugador está arriba o para esquivar
        if player.y + player.sprite_right.get_height() < self.y and self.is_grounded and dist < 220:
            self.vy = self.jump_power
            self.is_grounded = False

        # Aplicar gravedad
        self.vy += self.gravity
        self.y += self.vy
        self.x += self.vx

        # Límites del mundo
        if self.x < 10:
            self.x = 10
        elif self.x > WIDTH - self.width - 10:
            self.x = WIDTH - self.width - 10

        # Colisiones con tuberías
        enemy_box = pygame.Rect(self.x, self.y, self.width, self.height)
        for p in pipes:
            pipe_box = pygame.Rect(p.x, p.y - p.lip_height, p.lip_width, p.height + p.lip_height)
            if enemy_box.colliderect(pipe_box):
                if self.is_grounded and self.y + self.height >= pipe_box.top:
                    self.vy = -11.5
                    self.is_grounded = False
                elif self.vx > 0:
                    self.x = pipe_box.left - self.width
                elif self.vx < 0:
                    self.x = pipe_box.right

        # Colisiones con bloques flotantes
        for b in blocks:
            if enemy_box.colliderect(b.rect):
                if self.vy > 0 and self.y + self.height - self.vy <= b.rect.top + 8:
                    self.y = b.rect.top - self.height
                    self.vy = 0
                    self.is_grounded = True

        # Suelo
        floor_level = self.ground_y - self.height
        if self.y >= floor_level:
            self.y = floor_level
            self.vy = 0
            self.is_grounded = True

    def draw(self, surf):
        if not self.alive:
            return

        sprite = self.sprite_right if self.facing_right else self.sprite_left
        bob = math.sin(self.anim_walk) * 3 if self.is_grounded and abs(self.vx) > 0 else 0

        # Sombra
        shadow_w = int(self.width * 0.7)
        shadow_surf = pygame.Surface((shadow_w, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, shadow_w, 6))
        surf.blit(shadow_surf, (int(self.x + self.width / 2 - shadow_w / 2), self.ground_y - 3))

        surf.blit(sprite, (self.x, self.y + bob))
