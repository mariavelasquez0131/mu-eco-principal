import pygame
import os
import math
import random
from settings import WIDTH, CHAR_WIDTH, CHAR_HEIGHT
from sound_manager import sound_manager

# --- COMPAÑERO PERRITO HADA ---
class FairyDog:
    def __init__(self, owner):
        self.owner = owner
        self.size = 38
        self.x = owner.x
        self.y = owner.y
        self.anim_timer = 0.0
        self.sparkle_particles = []

        sprite_path = os.path.join("sprites", "perrito hada (acompañante).png")
        if os.path.exists(sprite_path):
            raw_img = pygame.image.load(sprite_path).convert_alpha()
        else:
            raw_img = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(raw_img, (255, 230, 200), (self.size // 2, self.size // 2), self.size // 2)

        self.sprite_right = pygame.transform.smoothscale(raw_img, (self.size, self.size))
        self.sprite_left = pygame.transform.flip(self.sprite_right, True, False)

    def update(self):
        self.anim_timer += 0.08
        float_y = math.sin(self.anim_timer * 2.5) * 6
        float_x = math.cos(self.anim_timer * 1.5) * 3

        # Posición deseada: a la altura del hombro del jugador
        if self.owner.facing_right:
            target_x = self.owner.x - 22 + float_x
        else:
            target_x = self.owner.x + CHAR_WIDTH - 12 + float_x

        target_y = self.owner.y + 6 + float_y

        # Movimiento elástico suave hacia el objetivo
        self.x += (target_x - self.x) * 0.14
        self.y += (target_y - self.y) * 0.14

        # Partículas mágicas de hada
        if random.random() < 0.35:
            self.sparkle_particles.append({
                'x': self.x + self.size / 2 + random.uniform(-6, 6),
                'y': self.y + self.size / 2 + random.uniform(-6, 6),
                'life': 22,
                'max_life': 22,
                'color': random.choice([(255, 230, 100), (255, 180, 220), (200, 240, 255)])
            })

        for p in self.sparkle_particles[:]:
            p['life'] -= 1
            p['y'] += 0.4
            if p['life'] <= 0:
                self.sparkle_particles.remove(p)

    def draw(self, surf):
        # Destellos mágicos
        for p in self.sparkle_particles:
            alpha = int((p['life'] / p['max_life']) * 255)
            s = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p['color'], alpha), (2, 2), 2)
            surf.blit(s, (p['x'], p['y']))

        # Halo de luz mágica suave
        halo_surf = pygame.Surface((self.size + 14, self.size + 14), pygame.SRCALPHA)
        pygame.draw.circle(halo_surf, (255, 240, 200, 55), ((self.size + 14) // 2, (self.size + 14) // 2), (self.size + 14) // 2)
        surf.blit(halo_surf, (self.x - 7, self.y - 7))

        # Dibujar perrito hada
        sprite = self.sprite_right if self.owner.facing_right else self.sprite_left
        surf.blit(sprite, (int(self.x), int(self.y)))


# --- CLASE JUGADOR CON ARMA Y ANIMACIÓN DE ATAQUE ARRIBA-ABAJO ---
class Player:
    def __init__(self, x, ground_y, start_y=None, max_health=5):
        self.spawn_x = x
        self.x = x
        self.ground_y = ground_y
        self.spawn_y = (ground_y - CHAR_HEIGHT) if start_y is None else start_y
        self.y = self.spawn_y
        self.vx = 0
        self.vy = 0
        self.speed = 4.8
        self.jump_power = -13
        self.gravity = 0.65
        self.facing_right = True
        self.is_grounded = True
        self.walk_timer = 0
        self.coins_collected = 0
        
        # Vidas configurables (5 vidas para Nivel 1, 7 vidas para Nivel 2)
        self.max_health = max_health
        self.health = max_health
        self.invincible_timer = 70 # Iniciar con más de 1 segundo de invulnerabilidad al aparecer
        self.has_triggered_10_bonus = False

        # Sistema de ataque con arma.png
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_duration = 16 # duración en frames
        self.attack_cooldown = 0
        self.attack_hitbox = None

        # Teletransporte por tuberías
        self.pipe_cooldown = 0

        # Cargar sprite del personaje principal
        sprite_path = os.path.join("sprites", "personaje principal.png")
        if os.path.exists(sprite_path):
            raw_img = pygame.image.load(sprite_path).convert_alpha()
        else:
            raw_img = pygame.Surface((CHAR_WIDTH, CHAR_HEIGHT), pygame.SRCALPHA)
            pygame.draw.circle(raw_img, (255, 60, 60), (CHAR_WIDTH // 2, CHAR_HEIGHT // 2), CHAR_WIDTH // 2)

        self.sprite_right = pygame.transform.smoothscale(raw_img, (CHAR_WIDTH, CHAR_HEIGHT))
        self.sprite_left = pygame.transform.flip(self.sprite_right, True, False)

        # Cargar sprite arma.png
        weapon_path = os.path.join("sprites", "arma.png")
        if os.path.exists(weapon_path):
            raw_weapon = pygame.image.load(weapon_path).convert_alpha()
        else:
            raw_weapon = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.rect(raw_weapon, (200, 160, 50), (12, 4, 8, 24))

        self.weapon_size = (38, 38)
        self.weapon_right = pygame.transform.smoothscale(raw_weapon, self.weapon_size)
        self.weapon_left = pygame.transform.flip(self.weapon_right, True, False)

        # Acompañante Perrito Hada
        self.fairy = FairyDog(self)

    def trigger_attack(self):
        if not self.is_attacking and self.attack_cooldown == 0 and self.health > 0:
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_cooldown = 22
            sound_manager.play_slash()

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

        if self.pipe_cooldown > 0:
            self.pipe_cooldown -= 1

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Lógica de ataque (Arriba -> Abajo)
        if self.is_attacking:
            self.attack_timer -= 1
            # Hitbox activa en la mitad del arco
            progress = (self.attack_duration - self.attack_timer) / self.attack_duration
            if 0.25 <= progress <= 0.85:
                hit_w = 48
                hit_h = 50
                if self.facing_right:
                    self.attack_hitbox = pygame.Rect(self.x + CHAR_WIDTH - 6, self.y + 12, hit_w, hit_h)
                else:
                    self.attack_hitbox = pygame.Rect(self.x - hit_w + 6, self.y + 12, hit_w, hit_h)
            else:
                self.attack_hitbox = None

            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_hitbox = None
        else:
            self.attack_hitbox = None

        # Movimiento
        self.vx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -self.speed
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = self.speed
            self.facing_right = True

        # Salto
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

        # Invulnerabilidad de 3 segundos (180 frames a 60 FPS) al llegar a 10 puntos/monedas
        if self.coins_collected >= 10 and not self.has_triggered_10_bonus:
            self.invincible_timer = 180 # 3 segundos
            self.has_triggered_10_bonus = True

        # Acceso y viaje por tuberías (Teclas Abajo / S para entrar al estar parado sobre una tubería)
        on_pipe_index = -1
        for i, p in enumerate(pipes):
            top_surface_y = p.y - p.lip_height
            head_x = p.x - (p.lip_width - p.width) // 2
            
            # 1. Colisión horizontal / lateral con el cuerpo de las tuberías (hitbox completa)
            pipe_box = pygame.Rect(head_x, top_surface_y, p.lip_width, p.height + p.lip_height)
            if player_rect.colliderect(pipe_box):
                # Aterrizar encima del tubo
                if self.vy > 0 and (self.y + CHAR_HEIGHT - self.vy) <= top_surface_y + 14:
                    self.y = top_surface_y - CHAR_HEIGHT
                    self.vy = 0
                    self.is_grounded = True
                    on_pipe_index = i
                # Colisión lateral izquierda o derecha
                elif self.vx > 0 and self.x + CHAR_WIDTH - self.vx <= head_x + 10:
                    self.x = head_x - CHAR_WIDTH
                elif self.vx < 0 and self.x - self.vx >= head_x + p.lip_width - 10:
                    self.x = head_x + p.lip_width

            # Detectar si está parado justo sobre la boca del tubo
            if (p.x - 14) <= (self.x + CHAR_WIDTH / 2) <= (p.x + p.lip_width + 6):
                if abs((self.y + CHAR_HEIGHT) - top_surface_y) <= 12:
                    on_pipe_index = i

        if on_pipe_index != -1 and (keys[pygame.K_DOWN] or keys[pygame.K_s]) and self.pipe_cooldown == 0:
            # Teletransportarse a la otra tubería
            other_index = (on_pipe_index + 1) % len(pipes)
            dest_pipe = pipes[other_index]
            self.x = dest_pipe.x + (dest_pipe.lip_width - CHAR_WIDTH) // 2
            self.y = (dest_pipe.y - dest_pipe.lip_height) - CHAR_HEIGHT - 8
            self.vy = -6.0 # Pequeño impulso de salida
            self.is_grounded = False
            self.pipe_cooldown = 45 # Evita ciclo infinito inmediato
            sound_manager.play_pipe()

        # Ataque con arma contra enemigos
        if self.attack_hitbox:
            for e in enemies:
                if e.alive:
                    e_box = pygame.Rect(e.x + 4, e.y + 4, e.width - 8, e.height - 8)
                    if self.attack_hitbox.colliderect(e_box):
                        hit_success = e.take_hit(knockback_dir=1 if self.facing_right else -1)
                        if hit_success:
                            sound_manager.play_bump()

        # Interacción física / contacto con enemigos
        for e in enemies:
            if e.alive:
                e_box = pygame.Rect(e.x + 6, e.y + 6, e.width - 12, e.height - 10)
                if player_rect.colliderect(e_box):
                    # Si el jugador salta y le pega en la cabeza: se elimina de 1 solo golpe
                    if self.vy > 0 and (self.y + CHAR_HEIGHT - self.vy) <= e.y + 20:
                        self.vy = -10.5 # Rebote del jugador hacia arriba
                        e.die() # Se elimina de 1 solo golpe en la cabeza
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

        # Actualizar hada acompañante
        self.fairy.update()

    def draw(self, surf):
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        sprite = self.sprite_right if self.facing_right else self.sprite_left
        bob = math.sin(self.walk_timer) * 3 if self.is_grounded and abs(self.vx) > 0 else 0
        
        # Sombra
        shadow_width = max(12, int(CHAR_WIDTH * 0.7 - (self.ground_y - (self.y + CHAR_HEIGHT)) * 0.15))
        shadow_rect = (int(self.x + CHAR_WIDTH / 2 - shadow_width / 2), self.ground_y - 4, shadow_width, 8)
        shadow_surf = pygame.Surface((shadow_width, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), (0, 0, shadow_width, 8))
        surf.blit(shadow_surf, (shadow_rect[0], shadow_rect[1]))

        # Dibujar jugador
        cur_player_y = self.y + bob
        surf.blit(sprite, (self.x, cur_player_y))

        # Dibujar Arma en la mano con animación de ataque (De arriba hacia abajo)
        self.draw_weapon(surf, cur_player_y)

        # Dibujar perrito hada
        self.fairy.draw(surf)

    def draw_weapon(self, surf, cur_y):
        # Calcular ángulo de ataque de arriba a abajo
        if self.is_attacking:
            progress = (self.attack_duration - self.attack_timer) / self.attack_duration
            # De +65 grados (arriba) a -75 grados (abajo)
            start_angle = 65
            end_angle = -75
            current_angle = start_angle + (end_angle - start_angle) * progress
        else:
            # En reposo sostenida en la mano
            current_angle = 15

        if self.facing_right:
            base_weapon = self.weapon_right
            hand_x = self.x + CHAR_WIDTH - 20
            hand_y = cur_y + CHAR_HEIGHT // 2 - 4
            rot_angle = current_angle
        else:
            base_weapon = self.weapon_left
            hand_x = self.x - 14
            hand_y = cur_y + CHAR_HEIGHT // 2 - 4
            rot_angle = -current_angle

        # Rotar arma
        rotated_weapon = pygame.transform.rotate(base_weapon, rot_angle)
        rect = rotated_weapon.get_rect(center=(hand_x + 18, hand_y + 16))
        surf.blit(rotated_weapon, rect.topleft)

        # Efecto visual de estela / corte en arco blanco-rosado durante el ataque
        if self.is_attacking and self.attack_hitbox:
            arc_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            arc_color = (255, 230, 245, 180)
            if self.facing_right:
                pygame.draw.arc(arc_surf, arc_color, (0, 0, 55, 55), math.radians(-50), math.radians(70), 5)
                surf.blit(arc_surf, (self.x + CHAR_WIDTH - 15, cur_y + 6))
            else:
                pygame.draw.arc(arc_surf, arc_color, (0, 0, 55, 55), math.radians(110), math.radians(230), 5)
                surf.blit(arc_surf, (self.x - 45, cur_y + 6))
