import pygame
import os
import math
from settings import WIDTH, CHAR_WIDTH, CHAR_HEIGHT
from sound_manager import sound_manager

class Player:
    def __init__(self, x, ground_y):
        self.spawn_x = x
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y - CHAR_HEIGHT
        self.vx = 0
        self.vy = 0
        self.speed = 4.8
        self.jump_power = -13
        self.gravity = 0.65
        self.facing_right = True
        self.is_grounded = True
        self.walk_timer = 0
        self.coins_collected = 0
        
        # Máximo 3 vidas exactas
        self.max_health = 3
        self.health = 3
        self.invincible_timer = 0

        # Cargar sprite del personaje principal
        sprite_path = os.path.join("sprites", "personaje principal.png")
        if os.path.exists(sprite_path):
            raw_img = pygame.image.load(sprite_path).convert_alpha()
        else:
            raw_img = pygame.Surface((CHAR_WIDTH, CHAR_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(raw_img, (255, 60, 60), (CHAR_WIDTH // 2, CHAR_HEIGHT // 2), CHAR_WIDTH // 2)

        self.sprite_right = pygame.transform.smoothscale(raw_img, (CHAR_WIDTH, CHAR_HEIGHT))
        self.sprite_left = pygame.transform.flip(self.sprite_right, True, False)

    def take_damage(self, push_direction=1):
        if self.invincible_timer == 0 and self.health > 0:
            self.health -= 1
            self.invincible_timer = 60 # 1 segundo de parpadeo invulnerable
            sound_manager.play_hurt()
            self.vy = -7.5
            self.vx = push_direction * 5

    def update(self, keys, blocks, pipes, coin_list, enemies):
        if self.health <= 0:
            return

        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_right = True

        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.is_grounded:
            self.vy = self.jump_power
            self.is_grounded = False
            sound_manager.play_jump()

        self.vy += self.gravity
        self.y += self.vy
        self.x += self.vx

        if self.x < 10:
            self.x = 10
        elif self.x > WIDTH - CHAR_WIDTH - 10:
            self.x = WIDTH - CHAR_WIDTH - 10

        # Colisión con bloques flotantes
        player_rect = pygame.Rect(self.x + 14, self.y, CHAR_WIDTH - 28, CHAR_HEIGHT)
        for b in blocks:
            if player_rect.colliderect(b.rect):
                if self.vy > 0 and self.y + CHAR_HEIGHT - self.vy <= b.rect.top + 8:
                    self.y = b.rect.top - CHAR_HEIGHT
                    self.vy = 0
                    self.is_grounded = True
                elif self.vy < 0 and self.y - self.vy >= b.rect.bottom - 10:
                    self.y = b.rect.bottom
                    self.vy = 1
                    got_coin = b.trigger_hit(coin_list)
                    if got_coin:
                        self.coins_collected += 1

        # Colisión con tuberías
        for p in pipes:
            top_surface_y = p.y - p.lip_height
            if (p.x - 12) <= (self.x + CHAR_WIDTH / 2) <= (p.x + p.lip_width + 5):
                if self.vy > 0 and self.y + CHAR_HEIGHT - self.vy <= top_surface_y + 10:
                    self.y = top_surface_y - CHAR_HEIGHT
                    self.vy = 0
                    self.is_grounded = True

        # Interacción única con enemigos creados a partir de enemigo.png
        for e in enemies:
            if e.alive:
                e_box = pygame.Rect(e.x + 6, e.y + 6, e.width - 12, e.height - 10)
                if player_rect.colliderect(e_box):
                    # Si el jugador salta encima los repele hacia atrás
                    if self.vy > 0 and (self.y + CHAR_HEIGHT - self.vy) <= e.y + 18:
                        self.vy = -10.0
                        e.vx = -5 if self.facing_right else 5
                        sound_manager.play_bump()
                    else:
                        push_dir = 1 if self.x > e.x else -1
                        self.take_damage(push_dir)

        # Suelo
        floor_level = self.ground_y - CHAR_HEIGHT
        if self.y >= floor_level:
            self.y = floor_level
            self.vy = 0
            self.is_grounded = True

        if abs(self.vx) > 0 and self.is_grounded:
            self.walk_timer += 0.25
        else:
            self.walk_timer = 0

    def draw(self, surf):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        sprite = self.sprite_right if self.facing_right else self.sprite_left
        bob = math.sin(self.walk_timer) * 3 if self.is_grounded and abs(self.vx) > 0 else 0
        
        shadow_width = max(12, int(CHAR_WIDTH * 0.7 - (self.ground_y - (self.y + CHAR_HEIGHT)) * 0.15))
        shadow_rect = (int(self.x + CHAR_WIDTH / 2 - shadow_width / 2), self.ground_y - 4, shadow_width, 8)
        shadow_surf = pygame.Surface((shadow_width, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), (0, 0, shadow_width, 8))
        surf.blit(shadow_surf, (shadow_rect[0], shadow_rect[1]))

        surf.blit(sprite, (self.x, self.y + bob))
