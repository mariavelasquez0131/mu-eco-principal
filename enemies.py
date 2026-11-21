import pygame
import os
import math
import random
from settings import WIDTH, GROUND_Y
from sound_manager import sound_manager

class PngEnemy:
    """
    Enemigo inteligente basado en PNG (soporta enemigo.png y caca enemigo.png).
    Comienza deambulando y patrullando por el mapa; si ve al jugador (distancia de visión),
    entra en estado de persecución activa.
    Tiene 3 puntos de vida; al ser atacado 3 veces con el arma desaparece.
    """
    def __init__(self, x, ground_y, sprite_name="enemigo.png", speed=2.2, jump_power=-10.5, sight_range=340):
        self.width = 54
        self.height = 54
        self.x = x
        self.ground_y = ground_y
        self.y = ground_y - self.height
        self.vx = random.choice([-1.4, 1.4])
        self.vy = 0.0
        self.speed = speed
        self.patrol_speed = 1.3
        self.jump_power = jump_power
        self.sight_range = sight_range
        self.gravity = 0.6
        self.is_grounded = True
        self.facing_right = self.vx > 0
        self.alive = True
        self.anim_walk = random.uniform(0, 10)
        
        # Sistema de 3 vidas para el enemigo
        self.max_health = 3
        self.health = 3
        self.hit_cooldown = 0
        self.flash_timer = 0
        self.death_particles = []

        # Estados: 'patrol' (deambulando) o 'chase' (persiguiendo)
        self.state = 'patrol'
        self.patrol_timer = random.randint(60, 160)

        # Cargar sprite especificado
        sprite_path = os.path.join("sprites", sprite_name)
        if os.path.exists(sprite_path):
            raw_img = pygame.image.load(sprite_path).convert_alpha()
        else:
            raw_img = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(raw_img, (180, 70, 70), (self.width // 2, self.height // 2), self.width // 2)

        self.sprite_right = pygame.transform.smoothscale(raw_img, (self.width, self.height))
        self.sprite_left = pygame.transform.flip(self.sprite_right, True, False)

    def die(self):
        """Elimina inmediatamente al enemigo con explosión de partículas"""
        if not self.alive:
            return
        self.health = 0
        self.alive = False
        for _ in range(24):
            self.death_particles.append({
                'x': self.x + self.width / 2,
                'y': self.y + self.height / 2,
                'vx': random.uniform(-5, 5),
                'vy': random.uniform(-7, 2),
                'color': random.choice([(255, 120, 150), (255, 230, 120), (255, 255, 255), (140, 220, 255)]),
                'radius': random.randint(3, 7),
                'life': 28
            })

    def take_hit(self, knockback_dir=1):
        """Al ser golpeado por el arma del jugador: pierde 1 vida (3 para desaparecer)"""
        if not self.alive or self.hit_cooldown > 0:
            return False

        self.health -= 1
        self.hit_cooldown = 18 # Evita que un solo golpe cuente múltiple
        self.flash_timer = 15
        self.vx = knockback_dir * 8.5
        self.vy = -6.5
        self.is_grounded = False
        self.state = 'chase' # Se pone en alerta inmediata

        # Si llega a 0 vidas, desaparece
        if self.health <= 0:
            self.die()
        return True

    def update(self, player, pipes, blocks):
        # Actualizar partículas si acaba de desaparecer
        if not self.alive:
            for p in self.death_particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] += 0.3
                p['life'] -= 1
                if p['life'] <= 0:
                    self.death_particles.remove(p)
            return

        if self.hit_cooldown > 0:
            self.hit_cooldown -= 1

        if self.flash_timer > 0:
            self.flash_timer -= 1

        self.anim_walk += 0.16

        player_cx = player.x + player.sprite_right.get_width() / 2
        enemy_cx = self.x + self.width / 2
        dx = player_cx - enemy_cx
        dist = abs(dx)

        # 1. Comprobar si "ve" al jugador (rango vertical aumentado para mayor dificultad)
        if dist <= self.sight_range and abs(player.y - self.y) < 320:
            self.state = 'chase'
        elif dist > self.sight_range + 100:
            self.state = 'patrol'

        # 2. Movimiento según estado
        if self.state == 'chase':
            # Perseguir activamente
            if dist > 8:
                if dx > 0:
                    self.vx = self.speed
                    self.facing_right = True
                else:
                    self.vx = -self.speed
                    self.facing_right = False
            else:
                self.vx = 0

            # Salto si el jugador está arriba para intentar alcanzarlo
            if player.y + player.sprite_right.get_height() < self.y and self.is_grounded and dist < 220:
                self.vy = self.jump_power
                self.is_grounded = False
        else:
            # Deambular pacíficamente por el mapa
            self.patrol_timer -= 1
            if self.patrol_timer <= 0:
                self.patrol_timer = random.randint(90, 200)
                self.vx = -self.vx
                self.facing_right = self.vx > 0
            else:
                self.vx = self.patrol_speed if self.facing_right else -self.patrol_speed

        # Aplicar gravedad
        self.vy += self.gravity
        self.y += self.vy
        self.x += self.vx

        # Límites del mundo
        if self.x < 10:
            self.x = 10
            self.vx = abs(self.vx)
            self.facing_right = True
        elif self.x > WIDTH - self.width - 10:
            self.x = WIDTH - self.width - 10
            self.vx = -abs(self.vx)
            self.facing_right = False

        # Colisiones con tuberías
        enemy_box = pygame.Rect(self.x, self.y, self.width, self.height)
        for p in pipes:
            pipe_box = pygame.Rect(p.x, p.y - p.lip_height, p.lip_width, p.height + p.lip_height)
            if enemy_box.colliderect(pipe_box):
                if self.state == 'chase' and self.is_grounded and self.y + self.height >= pipe_box.top:
                    self.vy = -11.5
                    self.is_grounded = False
                elif self.vx > 0:
                    self.x = pipe_box.left - self.width
                    self.vx = -self.vx
                    self.facing_right = False
                elif self.vx < 0:
                    self.x = pipe_box.right
                    self.vx = -self.vx
                    self.facing_right = True

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
        # Si murió, renderizar sus partículas de desaparición
        if not self.alive:
            for p in self.death_particles:
                pygame.draw.circle(surf, p['color'], (int(p['x']), int(p['y'])), p['radius'])
            return

        # Efecto de destello blanco/rojo al recibir golpe
        if self.flash_timer > 0 and (self.flash_timer // 3) % 2 == 0:
            # Sombra
            shadow_w = int(self.width * 0.7)
            shadow_surf = pygame.Surface((shadow_w, 6), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, shadow_w, 6))
            surf.blit(shadow_surf, (int(self.x + self.width / 2 - shadow_w / 2), self.ground_y - 3))
            # Dibujo translúcido
            flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surf.fill((255, 80, 80, 160))
            surf.blit(flash_surf, (self.x, self.y))
            return

        sprite = self.sprite_right if self.facing_right else self.sprite_left
        bob = math.sin(self.anim_walk) * 3 if self.is_grounded and abs(self.vx) > 0 else 0

        # Sombra
        shadow_w = int(self.width * 0.7)
        shadow_surf = pygame.Surface((shadow_w, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 60), (0, 0, shadow_w, 6))
        surf.blit(shadow_surf, (int(self.x + self.width / 2 - shadow_w / 2), self.ground_y - 3))

        surf.blit(sprite, (self.x, self.y + bob))

        # Barra / puntos de vida del enemigo (3 vidas)
        hp_bar_w = 36
        hp_bar_h = 5
        bar_x = self.x + (self.width - hp_bar_w) // 2
        bar_y = self.y - 12
        pygame.draw.rect(surf, (255, 255, 255), (bar_x - 1, bar_y - 1, hp_bar_w + 2, hp_bar_h + 2), border_radius=3)
        pygame.draw.rect(surf, (80, 80, 80), (bar_x, bar_y, hp_bar_w, hp_bar_h), border_radius=2)
        
        # Segmentos de vida verde/amarillo/rojo
        segment_w = (hp_bar_w - 2) / self.max_health
        for i in range(self.health):
            col = (255, 70, 90) if self.health == 1 else (255, 200, 50) if self.health == 2 else (100, 225, 90)
            pygame.draw.rect(surf, col, (bar_x + 1 + int(i * segment_w), bar_y + 1, int(segment_w) - 1, hp_bar_h - 2))

        # Indicador de alerta sutil cuando persigue al jugador
        if self.state == 'chase':
            alert_font = pygame.font.SysFont("comicsansms", 13, bold=True)
            alert_txt = alert_font.render("!", True, (255, 60, 80))
            surf.blit(alert_txt, (self.x + self.width // 2 - 2, bar_y - 14))
