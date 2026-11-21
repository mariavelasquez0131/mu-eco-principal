import pygame
import random
import math
import os
from settings import (
    WIDTH, HEIGHT, SKY_TOP, SKY_MID, SKY_BOTTOM,
    GRASS_TOP, GRASS_LIME, DIRT_BROWN, DIRT_DARK, DIRT_DOTS,
    HILL_LILA_LIGHT, HILL_LILA_DARK, HILL_PINK_LIGHT, HILL_PINK_DARK,
    BLOCK_PINK, BLOCK_BORDER, BLOCK_HIGHLIGHT,
    PIPE_PINK, PIPE_PINK_DARK, PIPE_PINK_LIGHT,
    FLOWER_COLORS, FLOWER_WEIGHTS
)
from sound_manager import sound_manager

# --- CARGAR SPRITE DE MONEDA ---
coin_sprite_path = os.path.join("sprites", "moneda.png")
if not os.path.exists(coin_sprite_path):
    coin_sprite_path = os.path.join("sprites", "monedas.png")

COIN_IMG = None

def get_coin_img():
    global COIN_IMG
    if COIN_IMG is None and os.path.exists(coin_sprite_path):
        try:
            raw_coin_img = pygame.image.load(coin_sprite_path).convert_alpha()
            COIN_IMG = pygame.transform.smoothscale(raw_coin_img, (38, 38))
        except Exception:
            COIN_IMG = None
    return COIN_IMG


# --- LLAVE MÁGICA ROSA CON DORADO (NIVEL 2) ---
class PinkGoldKey:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_y = y
        self.width = 44
        self.height = 44
        self.collected = False
        self.pulse = 0.0
        self.sparkles = []

    def update(self, player):
        if self.collected:
            return
        self.pulse += 0.08
        self.y = self.base_y + math.sin(self.pulse * 2) * 5

        # Destellos dorados y rosas
        if random.random() < 0.35:
            self.sparkles.append({
                'x': self.x + random.uniform(2, self.width - 2),
                'y': self.y + random.uniform(2, self.height - 2),
                'life': 18,
                'color': random.choice([(255, 220, 50), (255, 140, 200), (255, 255, 255)])
            })

        for s in self.sparkles[:]:
            s['life'] -= 1
            if s['life'] <= 0:
                self.sparkles.remove(s)

        # Colisión con el jugador
        key_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        player_rect = pygame.Rect(player.x, player.y, player.sprite_right.get_width(), player.sprite_right.get_height())
        if key_rect.colliderect(player_rect):
            self.collected = True
            sound_manager.play_coin()

    def draw(self, surf, time_sec):
        if self.collected:
            return

        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        # Destellos
        for s in self.sparkles:
            alpha = int((s['life'] / 18) * 230)
            psurf = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(psurf, (*s['color'], alpha), (2, 2), 2)
            surf.blit(psurf, (int(s['x']), int(s['y'])))

        # Halo resplandeciente dorado
        halo = pygame.Surface((self.width + 16, self.height + 16), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 215, 60, 65), ((self.width + 16) // 2, (self.height + 16) // 2), (self.width + 16) // 2)
        surf.blit(halo, (cx - (self.width + 16) // 2, cy - (self.height + 16) // 2))

        # Dibujar LLAVE ROSA CON DORADO
        # Cabeza de la llave en forma de corazón dorado con centro rosa
        r = 10
        gold = (255, 215, 40)
        gold_shadow = (210, 165, 20)
        pink = (255, 110, 175)
        pink_light = (255, 180, 220)

        # Parte superior de la llave (Anillo corazón dorado)
        head_cx = cx
        head_cy = cy - 8
        pygame.draw.circle(surf, gold_shadow, (head_cx - 5, head_cy), 8)
        pygame.draw.circle(surf, gold_shadow, (head_cx + 5, head_cy), 8)
        pygame.draw.circle(surf, gold, (head_cx - 5, head_cy), 7)
        pygame.draw.circle(surf, gold, (head_cx + 5, head_cy), 7)
        # Centro joya rosa
        pygame.draw.circle(surf, pink, (head_cx, head_cy), 5)
        pygame.draw.circle(surf, pink_light, (head_cx - 1, head_cy - 1), 2)

        # Vástago dorado de la llave
        shaft_x = cx - 3
        shaft_y = head_cy + 6
        pygame.draw.rect(surf, gold_shadow, (shaft_x, shaft_y, 6, 20), border_radius=2)
        pygame.draw.rect(surf, gold, (shaft_x + 1, shaft_y, 4, 19), border_radius=1)

        # Dientes de la llave (Rosa con borde dorado)
        pygame.draw.rect(surf, gold, (cx + 3, shaft_y + 8, 8, 4), border_radius=1)
        pygame.draw.rect(surf, pink, (cx + 3, shaft_y + 9, 6, 2))
        pygame.draw.rect(surf, gold, (cx + 3, shaft_y + 14, 6, 4), border_radius=1)
        pygame.draw.rect(surf, pink, (cx + 3, shaft_y + 15, 4, 2))


# --- PORTAL ROSA MÁGICO PARA ACABAR EL JUEGO ---
class PinkPortal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 72
        self.height = 110
        self.pulse = 0.0
        self.particles = []
        self.active = False # Solo se activa cuando todos los enemigos son derrotados

    def update(self):
        self.pulse += 0.06
        # Si está activo, emite más partículas mágicas resplandecientes
        chance = 0.55 if self.active else 0.15
        if random.random() < chance:
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(20, 48)
            colors = [(255, 140, 205), (255, 230, 255), (255, 215, 60), (200, 150, 255)] if self.active else [(180, 160, 180), (220, 180, 210)]
            self.particles.append({
                'x': self.x + self.width // 2 + math.cos(ang) * dist,
                'y': self.y + self.height // 2 + math.sin(ang) * (dist * 1.3),
                'vx': -math.cos(ang) * 0.9,
                'vy': -math.sin(ang) * 0.9,
                'life': 24,
                'color': random.choice(colors)
            })

        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self, surf, time_sec):
        cx = self.x + self.width // 2
        cy = self.y + self.height // 2

        # Partículas
        for p in self.particles:
            alpha = int((p['life'] / 24) * 230)
            psurf = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(psurf, (*p['color'], alpha), (3, 3), 3)
            surf.blit(psurf, (int(p['x']), int(p['y'])))

        wave = math.sin(self.pulse * (2.8 if self.active else 1.2)) * (4 if self.active else 1.5)
        outer_w = int(self.width + wave)
        outer_h = int(self.height + wave * 1.3)

        if self.active:
            # PORTAL ACTIVO Y RESPLANDECIENTE
            glow_surf = pygame.Surface((outer_w + 30, outer_h + 30), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (255, 120, 190, 100), (0, 0, outer_w + 30, outer_h + 30))
            surf.blit(glow_surf, (cx - (outer_w + 30) // 2, cy - (outer_h + 30) // 2))

            pygame.draw.ellipse(surf, (255, 70, 160), (cx - outer_w // 2, cy - outer_h // 2, outer_w, outer_h))
            mid_w = int(outer_w * 0.78)
            mid_h = int(outer_h * 0.80)
            pygame.draw.ellipse(surf, (255, 160, 225), (cx - mid_w // 2, cy - mid_h // 2, mid_w, mid_h))
            inner_w = int(outer_w * 0.52)
            inner_h = int(outer_h * 0.55)
            pygame.draw.ellipse(surf, (255, 235, 250), (cx - inner_w // 2, cy - inner_h // 2, inner_w, inner_h))
            pygame.draw.ellipse(surf, (255, 255, 255), (cx - inner_w // 4, cy - inner_h // 4, inner_w // 2, inner_h // 2))

            # Estrella dorada giratoria
            star_y = cy - outer_h // 2 - 16 + math.sin(time_sec * 4) * 4
            pygame.draw.circle(surf, (255, 230, 80), (cx, int(star_y)), 7)
            pygame.draw.circle(surf, (255, 255, 255), (cx, int(star_y)), 3)

            # Cartel "ENTRA AQUÍ"
            font_open = pygame.font.SysFont("comicsansms", 13, bold=True)
            txt_open = font_open.render("¡ABIERTO!", True, (255, 50, 130))
            surf.blit(txt_open, (cx - txt_open.get_width() // 2, cy + outer_h // 2 + 6))
        else:
            # PORTAL BLOQUEADO (en espera de eliminar los enemigos)
            glow_surf = pygame.Surface((outer_w + 14, outer_h + 14), pygame.SRCALPHA)
            pygame.draw.ellipse(glow_surf, (160, 130, 160, 60), (0, 0, outer_w + 14, outer_h + 14))
            surf.blit(glow_surf, (cx - (outer_w + 14) // 2, cy - (outer_h + 14) // 2))

            pygame.draw.ellipse(surf, (180, 120, 160), (cx - outer_w // 2, cy - outer_h // 2, outer_w, outer_h))
            mid_w = int(outer_w * 0.78)
            mid_h = int(outer_h * 0.80)
            pygame.draw.ellipse(surf, (210, 170, 200), (cx - mid_w // 2, cy - mid_h // 2, mid_w, mid_h))
            inner_w = int(outer_w * 0.52)
            inner_h = int(outer_h * 0.55)
            pygame.draw.ellipse(surf, (150, 120, 145), (cx - inner_w // 2, cy - inner_h // 2, inner_w, inner_h))

            # Candado / aviso de que faltan enemigos
            lock_font = pygame.font.SysFont("comicsansms", 12, bold=True)
            lock_txt = lock_font.render("BLOQUEADO", True, (130, 80, 110))
            surf.blit(lock_txt, (cx - lock_txt.get_width() // 2, cy + outer_h // 2 + 6))

    def collides_with(self, player):
        # Solo permite colisión/activación si el portal ya está activo
        if not self.active:
            return False
        portal_rect = pygame.Rect(self.x + 12, self.y + 10, self.width - 24, self.height - 20)
        player_rect = pygame.Rect(player.x, player.y, player.sprite_right.get_width(), player.sprite_right.get_height())
        return portal_rect.colliderect(player_rect)


# --- DIBUJO DE UNICORNIO KAWAII TOTALMENTE ENCIMA Y SOBREPUESTO A LA NUBE ---
def draw_cloud_unicorn(surf, cx, cy, scale=1.0, facing_right=True):
    s = scale
    u_surf = pygame.Surface((int(85 * s), int(75 * s)), pygame.SRCALPHA)
    
    body_color = (255, 255, 255)
    horn_color = (255, 220, 50)
    mane_color = (255, 140, 195)
    blush_color = (255, 150, 180, 190)
    eye_color = (50, 30, 45)

    # Cuerpo suave sentado sobre el lomo de la nube
    pygame.draw.ellipse(u_surf, body_color, (int(16*s), int(30*s), int(42*s), int(28*s)))
    pygame.draw.ellipse(u_surf, (255, 240, 248), (int(20*s), int(48*s), int(16*s), int(12*s)))
    pygame.draw.ellipse(u_surf, (255, 240, 248), (int(40*s), int(48*s), int(16*s), int(12*s)))
    
    # Cabeza
    pygame.draw.circle(u_surf, body_color, (int(45*s), int(24*s)), int(16*s))
    # Hocico
    pygame.draw.ellipse(u_surf, (255, 235, 245), (int(52*s), int(24*s), int(15*s), int(11*s)))
    pygame.draw.circle(u_surf, (255, 150, 180), (int(62*s), int(28*s)), max(1, int(1.5*s)))

    # Cuerno mágico dorado brillante
    horn_pts = [(int(42*s), int(14*s)), (int(52*s), int(0*s)), (int(47*s), int(15*s))]
    pygame.draw.polygon(u_surf, horn_color, horn_pts)

    # Melena mágica pastel (Rosa, Lila, Menta)
    pygame.draw.circle(u_surf, mane_color, (int(34*s), int(14*s)), int(9*s))
    pygame.draw.circle(u_surf, (200, 160, 255), (int(28*s), int(24*s)), int(8*s))
    pygame.draw.circle(u_surf, (140, 225, 255), (int(24*s), int(34*s)), int(7*s))

    # Ojo sonriente kawaii
    pygame.draw.circle(u_surf, eye_color, (int(50*s), int(22*s)), max(1, int(2.5*s)))
    # Mejilla sonrojada
    pygame.draw.circle(u_surf, blush_color, (int(52*s), int(29*s)), max(1, int(4.0*s)))

    # Orejita
    pygame.draw.polygon(u_surf, body_color, [(int(38*s), int(14*s)), (int(40*s), int(4*s)), (int(45*s), int(12*s))])

    # Destello de estrella mágica en el cuerno
    pygame.draw.circle(u_surf, (255, 255, 255), (int(53*s), int(1*s)), max(1, int(2.5*s)))

    if not facing_right:
        u_surf = pygame.transform.flip(u_surf, True, False)

    surf.blit(u_surf, (cx - int(38 * s), cy - int(54 * s)))


# --- NUBES CON UNICORNIOS ENCIMA ---
class CloudKawaii:
    def __init__(self, x, y, speed, scale=1.0, has_unicorn=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.scale = scale
        self.has_unicorn = has_unicorn
        self.w = int(150 * scale)
        self.h = int(80 * scale)

    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 160:
            self.x = -200
            self.y = random.randint(35, 280)

    def draw(self, surf):
        w, h = self.w, self.h
        x, y = self.x, self.y

        shadow = (255, 230, 245, 190)
        white = (255, 255, 255, 250)
        
        cloud_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(cloud_surf, shadow, (w * 0.05, h * 0.35, w * 0.9, h * 0.55))
        pygame.draw.ellipse(cloud_surf, white, (w * 0.08, h * 0.3, w * 0.84, h * 0.55))
        pygame.draw.circle(cloud_surf, white, (int(w * 0.32), int(h * 0.42)), int(h * 0.35))
        pygame.draw.circle(cloud_surf, white, (int(w * 0.54), int(h * 0.34)), int(h * 0.38))
        pygame.draw.circle(cloud_surf, white, (int(w * 0.74), int(h * 0.46)), int(h * 0.28))
        
        eye_color = (60, 45, 65)
        pygame.draw.ellipse(cloud_surf, eye_color, (w * 0.43, h * 0.46, 5, 8))
        pygame.draw.ellipse(cloud_surf, eye_color, (w * 0.57, h * 0.46, 5, 8))
        blush = (255, 130, 175, 160)
        pygame.draw.circle(cloud_surf, blush, (int(w * 0.37), int(h * 0.55)), 6)
        pygame.draw.circle(cloud_surf, blush, (int(w * 0.63), int(h * 0.55)), 6)

        surf.blit(cloud_surf, (x, y))

        if self.has_unicorn:
            unicorn_cx = x + w * 0.52
            unicorn_cy = y + h * 0.32
            draw_cloud_unicorn(surf, unicorn_cx, unicorn_cy, scale=self.scale * 1.05, facing_right=True)


# --- ARCOÍRIS PASTEL ---
class Rainbow:
    def __init__(self, cx, cy, radius_outer, thickness=8):
        self.cx = cx
        self.cy = cy
        self.radius = radius_outer
        self.thickness = thickness
        self.colors = [
            (255, 120, 160, 210),
            (255, 185, 90, 210),
            (255, 240, 100, 210),
            (145, 230, 140, 210),
            (120, 205, 255, 210),
            (205, 155, 255, 210)
        ]

    def draw(self, surf):
        r = self.radius
        for c in self.colors:
            rect = (self.cx - r, self.cy - r, r * 2, r * 2)
            pygame.draw.arc(surf, c, rect, 0, math.pi, self.thickness)
            r -= self.thickness


# --- COLINAS PASTEL KAWAII ---
class PastelHill:
    def __init__(self, x, y, width, height, light_c, dark_c, has_face=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.light_c = light_c
        self.dark_c = dark_c
        self.has_face = has_face

    def draw(self, surf):
        rect = (self.x, self.y - self.height, self.width, self.height * 2)
        pygame.draw.ellipse(surf, self.dark_c, (self.x, self.y - self.height + 4, self.width, self.height * 2))
        pygame.draw.ellipse(surf, self.light_c, rect)

        if self.has_face:
            eye_y = self.y - self.height * 0.58
            eye_w, eye_h = 5, 14
            pygame.draw.ellipse(surf, (60, 45, 75), (self.x + self.width * 0.46, eye_y, eye_w, eye_h))
            pygame.draw.ellipse(surf, (60, 45, 75), (self.x + self.width * 0.54, eye_y, eye_w, eye_h))
            pygame.draw.circle(surf, (255, 130, 175, 140), (int(self.x + self.width * 0.40), int(eye_y + 14)), 8)
            pygame.draw.circle(surf, (255, 130, 175, 140), (int(self.x + self.width * 0.60), int(eye_y + 14)), 8)


# --- DULCES Y HONGOS ---
class Lollipop:
    def __init__(self, x, ground_y, radius=26):
        self.x = x
        self.ground_y = ground_y
        self.radius = radius
        self.stick_h = 75

    def draw(self, surf, time_sec):
        top_y = self.ground_y - self.stick_h
        pygame.draw.line(surf, (255, 255, 255), (self.x, self.ground_y), (self.x, top_y), 6)
        cx, cy = self.x, top_y
        colors = [(255, 130, 180), (255, 240, 140), (255, 170, 200)]
        pygame.draw.circle(surf, colors[0], (cx, cy), self.radius)
        pygame.draw.circle(surf, colors[1], (cx, cy), int(self.radius * 0.75))
        pygame.draw.circle(surf, colors[2], (cx, cy), int(self.radius * 0.5))
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), int(self.radius * 0.25))
        pygame.draw.circle(surf, (255, 255, 255), (cx - int(self.radius*0.35), cy - int(self.radius*0.35)), 5)


class CuteMushroom:
    def __init__(self, x, ground_y, color=(255, 95, 120)):
        self.x = x
        self.ground_y = ground_y
        self.color = color

    def draw(self, surf):
        pygame.draw.rect(surf, (255, 245, 240), (self.x + 7, self.ground_y - 18, 14, 18), border_radius=5)
        pygame.draw.ellipse(surf, self.color, (self.x, self.ground_y - 34, 28, 22))
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 8, self.ground_y - 25), 4)
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 20, self.ground_y - 25), 4)
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 14, self.ground_y - 30), 4)


# --- FLORES KAWAII ---
class FlowerKawaii:
    def __init__(self, x, ground_y):
        self.x = x
        self.ground_y = ground_y
        self.color = random.choices(FLOWER_COLORS, weights=FLOWER_WEIGHTS)[0]
        self.center_color = (255, 235, 120) if self.color != (255, 225, 80) else (255, 130, 160)
        self.size = random.randint(8, 14)
        self.sway_offset = random.uniform(0, 10)
        self.sway_speed = random.uniform(2.5, 4.2)
        self.stem_height = random.randint(20, 32)

    def draw(self, surf, time_sec):
        sway = math.sin(time_sec * self.sway_speed + self.sway_offset) * 3.5
        fx = self.x + sway
        fy = self.ground_y - self.stem_height

        pygame.draw.line(surf, (110, 205, 75), (self.x, self.ground_y), (fx, fy), 3)
        pygame.draw.ellipse(surf, (110, 205, 75), (self.x - 4 + sway * 0.4, self.ground_y - self.stem_height * 0.4, 7, 5))

        num_petals = 5
        petal_dist = self.size * 0.8
        for i in range(num_petals):
            ang = (i * 2 * math.pi / num_petals) + (sway * 0.05)
            px = fx + math.cos(ang) * petal_dist
            py = fy + math.sin(ang) * petal_dist
            pygame.draw.circle(surf, self.color, (int(px), int(py)), int(self.size * 0.58))

        pygame.draw.circle(surf, self.center_color, (int(fx), int(fy)), int(self.size * 0.42))


# --- MONEDA VOLADORA USANDO MONEDA.PNG ---
class FloatingCoin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vy = -10.0
        self.gravity = 0.55
        self.alive = True
        self.frame = 0

    def update(self):
        self.y += self.vy
        self.vy += self.gravity
        self.frame += 0.28
        if self.vy > 3.5:
            self.alive = False

    def draw(self, surf):
        coin_img = get_coin_img()
        if coin_img:
            spin = abs(math.cos(self.frame))
            spin_w = max(4, int(38 * spin))
            scaled_coin = pygame.transform.scale(coin_img, (spin_w, 38))
            surf.blit(scaled_coin, (int(self.x - spin_w / 2), int(self.y)))
        else:
            pygame.draw.circle(surf, (255, 215, 40), (int(self.x), int(self.y)), 14)


# --- MONEDAS EN EL AIRE RECOLECTABLES EN EL ESCENARIO ---
class WorldCoin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.base_y = y
        self.alive = True
        self.frame = random.uniform(0, 10)

    def update(self, player):
        if not self.alive:
            return
        self.frame += 0.12
        self.y = self.base_y + math.sin(self.frame) * 4

        coin_rect = pygame.Rect(self.x - 18, self.y - 18, 36, 36)
        player_rect = pygame.Rect(player.x, player.y, player.sprite_right.get_width(), player.sprite_right.get_height())
        if coin_rect.colliderect(player_rect):
            self.alive = False
            player.coins_collected += 1
            sound_manager.play_coin()

    def draw(self, surf):
        if not self.alive:
            return
        coin_img = get_coin_img()
        if coin_img:
            spin = abs(math.cos(self.frame * 2))
            spin_w = max(4, int(34 * spin))
            scaled_coin = pygame.transform.scale(coin_img, (spin_w, 34))
            surf.blit(scaled_coin, (int(self.x - spin_w / 2), int(self.y - 17)))
        else:
            pygame.draw.circle(surf, (255, 215, 0), (int(self.x), int(self.y)), 13)


# --- BLOQUES ROSA CHICLE KAWAII ---
class FloatingBlockKawaii:
    def __init__(self, x, y, is_question=False):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.is_question = is_question
        self.is_hit = False
        self.bounce_offset = 0

    def trigger_hit(self, coin_list):
        self.bounce_offset = -11
        if self.is_question and not self.is_hit:
            self.is_hit = True
            coin_list.append(FloatingCoin(self.rect.centerx, self.rect.y - 14))
            sound_manager.play_coin()
            return True
        else:
            sound_manager.play_bump()
            return False

    def update(self):
        if self.bounce_offset < 0:
            self.bounce_offset += 1.4
            if self.bounce_offset > 0:
                self.bounce_offset = 0

    def draw(self, surf, time_sec):
        x = self.rect.x
        y = self.rect.y + self.bounce_offset
        w, h = self.rect.width, self.rect.height

        if self.is_question:
            if not self.is_hit:
                gold = (255, 140, 195)
                border = BLOCK_BORDER
                highlight = BLOCK_HIGHLIGHT
                
                pygame.draw.rect(surf, border, (x, y, w, h), border_radius=9)
                pygame.draw.rect(surf, gold, (x + 3, y + 3, w - 6, h - 6), border_radius=7)
                pygame.draw.line(surf, highlight, (x + 5, y + 5), (x + w - 6, y + 5), 3)
                pygame.draw.line(surf, highlight, (x + 5, y + 5), (x + 5, y + h - 6), 3)

                pulse = math.sin(time_sec * 6) * 1.5
                font = pygame.font.SysFont("comicsansms", 26, bold=True)
                text = font.render("?", True, (255, 255, 255))
                surf.blit(text, (x + 18, y + 7 + pulse))
            else:
                used_c = (210, 175, 215)
                used_dark = (165, 130, 175)
                pygame.draw.rect(surf, used_dark, (x, y, w, h), border_radius=9)
                pygame.draw.rect(surf, used_c, (x + 3, y + 3, w - 6, h - 6), border_radius=7)
        else:
            pygame.draw.rect(surf, BLOCK_BORDER, (x, y, w, h), border_radius=9)
            pygame.draw.rect(surf, BLOCK_PINK, (x + 3, y + 3, w - 6, h - 6), border_radius=7)
            pygame.draw.line(surf, BLOCK_HIGHLIGHT, (x + 5, y + 5), (x + w - 6, y + 5), 2)
            pygame.draw.line(surf, BLOCK_HIGHLIGHT, (x + 5, y + 5), (x + 5, y + h - 6), 2)


# --- TUBERÍAS ROSA CHICLE ACCESIBLES ---
class PinkPipe:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.height = height
        self.width = 76
        self.lip_height = 32
        self.lip_width = 92
        # Rectángulo de colisión completo para hitbox lateral y vertical
        head_x = self.x - (self.lip_width - self.width) // 2
        head_y = self.y - self.lip_height
        self.rect = pygame.Rect(head_x, head_y, self.lip_width, self.height + self.lip_height)

    def draw(self, surf):
        border = (195, 60, 120)
        body = PIPE_PINK
        light = PIPE_PINK_LIGHT
        dark = PIPE_PINK_DARK

        pygame.draw.rect(surf, border, (self.x - 2, self.y, self.width + 4, self.height), border_radius=5)
        pygame.draw.rect(surf, body, (self.x, self.y, self.width, self.height))
        pygame.draw.line(surf, light, (self.x + 12, self.y), (self.x + 12, self.y + self.height), 6)
        pygame.draw.rect(surf, dark, (self.x + self.width - 16, self.y, 14, self.height))

        head_x = self.x - (self.lip_width - self.width) // 2
        head_y = self.y - self.lip_height
        pygame.draw.rect(surf, border, (head_x - 2, head_y - 2, self.lip_width + 4, self.lip_height + 4), border_radius=7)
        pygame.draw.rect(surf, body, (head_x, head_y, self.lip_width, self.lip_height), border_radius=6)
        pygame.draw.line(surf, light, (head_x + 14, head_y + 3), (head_x + 14, head_y + self.lip_height - 3), 7)
        pygame.draw.rect(surf, dark, (head_x + self.lip_width - 20, head_y + 3, 16, self.lip_height - 6))

        arrow_x = head_x + self.lip_width // 2
        arrow_y = head_y - 14
        pygame.draw.polygon(surf, (255, 235, 120), [
            (arrow_x - 7, arrow_y),
            (arrow_x + 7, arrow_y),
            (arrow_x, arrow_y + 7)
        ])


# --- FANTASMITAS KAWAII (BOOS) ---
class FloatingBooKawaii:
    def __init__(self, x, y, range_x=140):
        self.origin_x = x
        self.y = y
        self.range_x = range_x
        self.time_offset = random.uniform(0, 10)

    def draw(self, surf, time_sec):
        cur_x = self.origin_x + math.sin(time_sec * 1.5 + self.time_offset) * (self.range_x / 2)
        cur_y = self.y + math.sin(time_sec * 3.0 + self.time_offset) * 10
        
        body_color = (255, 255, 255, 240)
        shadow_c = (235, 245, 255)
        
        pygame.draw.circle(surf, shadow_c, (int(cur_x), int(cur_y + 2)), 16)
        pygame.draw.circle(surf, body_color, (int(cur_x), int(cur_y)), 16)
        
        pygame.draw.circle(surf, body_color, (int(cur_x - 14), int(cur_y + 2)), 6)
        pygame.draw.circle(surf, body_color, (int(cur_x + 14), int(cur_y + 2)), 6)

        pygame.draw.ellipse(surf, (60, 45, 75), (cur_x - 6, cur_y - 3, 4, 6))
        pygame.draw.ellipse(surf, (60, 45, 75), (cur_x + 2, cur_y - 3, 4, 6))
        pygame.draw.circle(surf, (255, 140, 180, 170), (int(cur_x - 8), int(cur_y + 5)), 4)
        pygame.draw.circle(surf, (255, 140, 180, 170), (int(cur_x + 8), int(cur_y + 5)), 4)


# --- DESTELLOS Y CORAZONES FLOTANTES ---
class FloatingSparkle:
    def __init__(self):
        self.reset()
        self.y = random.uniform(0, HEIGHT)

    def reset(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(-30, 0)
        self.speed_y = random.uniform(0.6, 1.4)
        self.speed_x = random.uniform(-0.4, 0.4)
        self.is_heart = random.random() < 0.35
        self.size = random.uniform(6, 12)
        self.color = random.choice([
            (255, 150, 200, 220),
            (255, 220, 120, 220),
            (255, 255, 255, 230),
            (210, 175, 255, 220)
        ])
        self.pulse = random.uniform(0, 10)

    def update(self):
        self.pulse += 0.08
        self.y += self.speed_y
        self.x += self.speed_x
        if self.y > HEIGHT - 30:
            self.reset()

    def draw(self, surf):
        cur_size = self.size + math.sin(self.pulse) * 2
        if cur_size <= 1:
            return
        
        if self.is_heart:
            r = cur_size * 0.5
            cx, cy = int(self.x), int(self.y)
            pygame.draw.circle(surf, self.color, (int(cx - r/2), int(cy - r/2)), int(r/2))
            pygame.draw.circle(surf, self.color, (int(cx + r/2), int(cy - r/2)), int(r/2))
            points = [(cx - r, cy - r/4), (cx + r, cy - r/4), (cx, cy + r)]
            pygame.draw.polygon(surf, self.color, points)
        else:
            cx, cy = int(self.x), int(self.y)
            s = int(cur_size)
            pygame.draw.line(surf, self.color, (cx - s, cy), (cx + s, cy), 2)
            pygame.draw.line(surf, self.color, (cx, cy - s), (cx, cy + s), 2)
            pygame.draw.circle(surf, (255, 255, 255), (cx, cy), 2)


# --- CLASE PRINCIPAL DEL ENTORNO EXPANDIDO EN HORIZONTAL Y VERTICAL ---
class Environment:
    def __init__(self, ground_y, level=1):
        self.ground_y = ground_y
        self.level = level

        # Nubes animadas distribuidas en el cielo más amplio
        self.clouds = [
            CloudKawaii(70, 70, 0.30, 1.4, has_unicorn=True),
            CloudKawaii(420, 130, 0.42, 1.1, has_unicorn=False),
            CloudKawaii(820, 65, 0.36, 1.5, has_unicorn=True),
            CloudKawaii(1200, 110, 0.48, 1.2, has_unicorn=True),
            CloudKawaii(1550, 160, 0.38, 1.0, has_unicorn=False),
            CloudKawaii(250, 220, 0.35, 1.2, has_unicorn=True),
            CloudKawaii(980, 240, 0.40, 1.1, has_unicorn=False),
        ]

        # Arcoíris pastel gigantes
        self.rainbows = [
            Rainbow(340, 360, 310, thickness=9),
            Rainbow(1240, 390, 260, thickness=8),
            Rainbow(790, ground_y + 50, 180, thickness=8)
        ]

        # Colinas pastel más amplias y altas
        if self.level == 1:
            h_pink_l = HILL_PINK_LIGHT
            h_pink_d = HILL_PINK_DARK
            h_lila_l = HILL_LILA_LIGHT
            h_lila_d = HILL_LILA_DARK
        else:
            from settings import HILL_N2_LIGHT, HILL_N2_DARK
            h_pink_l = HILL_N2_LIGHT
            h_pink_d = HILL_N2_DARK
            h_lila_l = (220, 160, 240)
            h_lila_d = (190, 130, 210)

        self.hills = [
            PastelHill(-60, ground_y, 420, 260, h_pink_l, h_pink_d, has_face=False),
            PastelHill(280, ground_y, 480, 320, h_lila_l, h_lila_d, has_face=True),
            PastelHill(840, ground_y, 460, 250, h_pink_l, h_pink_d, has_face=True),
            PastelHill(1320, ground_y, 430, 300, h_lila_l, h_lila_d, has_face=False)
        ]

        # Tuberías Rosa Accesibles según nivel
        if self.level == 1:
            self.pipes = [
                PinkPipe(180, ground_y - 100, 100),
                PinkPipe(1420, ground_y - 125, 125)
            ]
        else:
            # En Nivel 2: nueva distribución de tuberías en posiciones estratégicas
            self.pipes = [
                PinkPipe(290, ground_y - 110, 110),
                PinkPipe(1240, ground_y - 130, 130)
            ]

        # Bloques y plataformas según el nivel con escaleras viables (Delta Y <= 85px, Delta X <= 140px)
        if self.level == 1:
            self.blocks = [
                # Escalera izquierda desde el suelo
                FloatingBlockKawaii(100, ground_y - 90, is_question=True),
                FloatingBlockKawaii(150, ground_y - 90, is_question=False),

                FloatingBlockKawaii(250, ground_y - 170, is_question=False),
                FloatingBlockKawaii(300, ground_y - 170, is_question=True),

                # Plataforma media izquierda
                FloatingBlockKawaii(400, ground_y - 210, is_question=False),
                FloatingBlockKawaii(450, ground_y - 210, is_question=True),
                FloatingBlockKawaii(500, ground_y - 210, is_question=False),

                # Escalera hacia la cima central (donde apareces)
                FloatingBlockKawaii(600, ground_y - 290, is_question=True),
                FloatingBlockKawaii(650, ground_y - 290, is_question=False),

                # Plataforma más alta central (Piso superior x=720..870, y=ground_y-370)
                FloatingBlockKawaii(720, ground_y - 370, is_question=True),
                FloatingBlockKawaii(770, ground_y - 370, is_question=False),
                FloatingBlockKawaii(820, ground_y - 370, is_question=True),

                # CAMINO VIABLE Y ESCALONADO HACIA EL PORTAL ROSA:
                # Plataforma baja intermedia en el suelo/centro
                FloatingBlockKawaii(550, ground_y - 90, is_question=False),
                FloatingBlockKawaii(600, ground_y - 90, is_question=True),
                FloatingBlockKawaii(880, ground_y - 100, is_question=True),
                FloatingBlockKawaii(930, ground_y - 100, is_question=False),

                # Escalón hacia la derecha (Delta Y <= 80px)
                FloatingBlockKawaii(1020, ground_y - 180, is_question=False),
                FloatingBlockKawaii(1070, ground_y - 180, is_question=True),
                FloatingBlockKawaii(1120, ground_y - 180, is_question=False),

                # Siguiente escalón (Delta Y = 80px, Delta X fácil)
                FloatingBlockKawaii(1190, ground_y - 260, is_question=True),
                FloatingBlockKawaii(1240, ground_y - 260, is_question=False),

                # Plataforma previa al portal (Delta Y = 80px)
                FloatingBlockKawaii(1310, ground_y - 340, is_question=False),
                FloatingBlockKawaii(1360, ground_y - 340, is_question=True),

                # Plataforma del PORTAL ROSA (Delta Y = 70px)
                FloatingBlockKawaii(1410, ground_y - 410, is_question=False),
                FloatingBlockKawaii(1460, ground_y - 410, is_question=True),
                FloatingBlockKawaii(1510, ground_y - 410, is_question=False),

                # Plataforma sobre la tubería derecha (atajo alternativo)
                FloatingBlockKawaii(1380, ground_y - 160, is_question=True),
            ]
        else:
            # NIVEL 2: NUEVO MAPA COMPLETO (Estructura de Fortaleza y Torres Flotantes Rosa Pastel)
            self.blocks = [
                # 1. Torre Flotante Izquierda (Escalones progresivos de inicio)
                FloatingBlockKawaii(80, ground_y - 85, is_question=True),
                FloatingBlockKawaii(130, ground_y - 85, is_question=False),
                FloatingBlockKawaii(180, ground_y - 165, is_question=False),
                FloatingBlockKawaii(230, ground_y - 165, is_question=True),
                
                # 2. Gran Terraza Flotante Rosa (Piso Intermedio)
                FloatingBlockKawaii(370, ground_y - 210, is_question=True),
                FloatingBlockKawaii(420, ground_y - 210, is_question=False),
                FloatingBlockKawaii(470, ground_y - 210, is_question=True),
                FloatingBlockKawaii(520, ground_y - 210, is_question=False),
                FloatingBlockKawaii(570, ground_y - 210, is_question=True),

                # 3. Escalón bajo central del suelo
                FloatingBlockKawaii(480, ground_y - 85, is_question=False),
                FloatingBlockKawaii(530, ground_y - 85, is_question=True),

                # 4. Torre Central Alta (Piso Superior - Atalaya de Nivel 2)
                FloatingBlockKawaii(640, ground_y - 280, is_question=False),
                FloatingBlockKawaii(690, ground_y - 280, is_question=True),
                FloatingBlockKawaii(740, ground_y - 355, is_question=False),
                FloatingBlockKawaii(790, ground_y - 355, is_question=True),
                FloatingBlockKawaii(840, ground_y - 355, is_question=False),

                # 5. Pasarela flotante conectora (Puente colgante de bloques)
                FloatingBlockKawaii(910, ground_y - 285, is_question=True),
                FloatingBlockKawaii(960, ground_y - 285, is_question=False),

                # 6. Plataforma media este
                FloatingBlockKawaii(1020, ground_y - 200, is_question=False),
                FloatingBlockKawaii(1070, ground_y - 200, is_question=True),
                FloatingBlockKawaii(1120, ground_y - 200, is_question=False),

                # 7. Escalera hacia el Santuario de la Llave Rosa con Dorado
                FloatingBlockKawaii(1190, ground_y - 280, is_question=True),
                FloatingBlockKawaii(1240, ground_y - 280, is_question=False),
                FloatingBlockKawaii(1310, ground_y - 355, is_question=True),
                FloatingBlockKawaii(1360, ground_y - 355, is_question=False),

                # 8. Cima del Gran Santuario Dorado de Nivel 2
                FloatingBlockKawaii(1410, ground_y - 425, is_question=False),
                FloatingBlockKawaii(1460, ground_y - 425, is_question=True),
                FloatingBlockKawaii(1510, ground_y - 425, is_question=False),

                # 9. Isla de escape lateral derecha
                FloatingBlockKawaii(1480, ground_y - 120, is_question=True),
                FloatingBlockKawaii(1530, ground_y - 120, is_question=False),
            ]

        # En el Nivel 1: hay Portal Rosa. En el Nivel 2: hay Llave Rosa con Dorado
        if self.level == 1:
            # Portal Rosa sobre la plataforma x=1410..1560, y=ground_y-410
            self.portal = PinkPortal(x=1440, y=ground_y - 410 - 110)
            self.key = None
        else:
            self.portal = None
            # Llave Rosa con Dorado sobre la cima del santuario en x=1460, y=ground_y-425
            self.key = PinkGoldKey(x=1460, y=ground_y - 425 - 55)

        # Monedas dispersas por el mapa según nivel
        if self.level == 1:
            self.world_coins = [
                WorldCoin(105, ground_y - 165),
                WorldCoin(255, ground_y - 245),
                WorldCoin(385, ground_y - 220),
                WorldCoin(435, ground_y - 220),
                WorldCoin(485, ground_y - 220),
                WorldCoin(535, ground_y - 220),
                WorldCoin(685, ground_y - 330),
                WorldCoin(735, ground_y - 330),
                WorldCoin(785, ground_y - 330),
                WorldCoin(755, ground_y - 460),
                WorldCoin(805, ground_y - 460),
                WorldCoin(905, ground_y - 240),
                WorldCoin(925, ground_y - 395),
                WorldCoin(1045, ground_y - 230),
                WorldCoin(1095, ground_y - 230),
                WorldCoin(1145, ground_y - 230),
                WorldCoin(1195, ground_y - 230),
                WorldCoin(1175, ground_y - 360),
                WorldCoin(1225, ground_y - 360),
                WorldCoin(1505, ground_y - 185),
                WorldCoin(218, ground_y - 150),
            ]
        else:
            # Monedas distribuidas en las nuevas torres y plataformas del Nivel 2
            self.world_coins = [
                WorldCoin(105, ground_y - 130),
                WorldCoin(205, ground_y - 210),
                WorldCoin(395, ground_y - 255),
                WorldCoin(445, ground_y - 255),
                WorldCoin(495, ground_y - 255),
                WorldCoin(545, ground_y - 255),
                WorldCoin(505, ground_y - 130),
                WorldCoin(665, ground_y - 325),
                WorldCoin(765, ground_y - 400),
                WorldCoin(815, ground_y - 400),
                WorldCoin(935, ground_y - 330),
                WorldCoin(1045, ground_y - 245),
                WorldCoin(1095, ground_y - 245),
                WorldCoin(1215, ground_y - 325),
                WorldCoin(1335, ground_y - 400),
                WorldCoin(1435, ground_y - 470),
                WorldCoin(1485, ground_y - 470),
                WorldCoin(1505, ground_y - 165),
                WorldCoin(328, ground_y - 155),
                WorldCoin(1278, ground_y - 175),
            ]

        # Dulces y hongos
        if self.level == 1:
            self.lollipops = [
                Lollipop(550, ground_y, radius=28),
                Lollipop(1300, ground_y, radius=24)
            ]
            self.mushrooms = [
                CuteMushroom(310, ground_y, color=(255, 90, 120)),
                CuteMushroom(710, ground_y, color=(255, 110, 150)),
                CuteMushroom(950, ground_y, color=(255, 90, 120)),
                CuteMushroom(1260, ground_y, color=(255, 130, 190)),
            ]
        else:
            # Decoración Nivel 2: nuevas posiciones con temática de pastelería rosa
            self.lollipops = [
                Lollipop(200, ground_y, radius=30),
                Lollipop(680, ground_y, radius=26),
                Lollipop(1120, ground_y, radius=28),
                Lollipop(1390, ground_y, radius=25)
            ]
            self.mushrooms = [
                CuteMushroom(220, ground_y, color=(255, 80, 140)),
                CuteMushroom(440, ground_y, color=(255, 120, 180)),
                CuteMushroom(860, ground_y, color=(255, 70, 130)),
                CuteMushroom(1050, ground_y, color=(255, 130, 195)),
                CuteMushroom(1500, ground_y, color=(255, 100, 160)),
            ]

        self.boos = [
            FloatingBooKawaii(300, 220, range_x=120),
            FloatingBooKawaii(820, 260, range_x=140),
            FloatingBooKawaii(1330, 230, range_x=110)
        ]

        # Flores densas a lo largo de los 1600 píxeles de ancho
        self.flowers = []
        random.seed(99)
        for fx in range(25, WIDTH - 25, 14):
            in_pipe = any((p.x - 14) <= fx <= (p.x + p.width + 14) for p in self.pipes)
            if not in_pipe:
                self.flowers.append(FlowerKawaii(fx + random.randint(-4, 4), ground_y + 4))

        self.sparkles = [FloatingSparkle() for _ in range(55)]
        self.coins = []

    def update(self, player):
        if self.portal:
            self.portal.update()
        if self.key:
            self.key.update(player)

        for cloud in self.clouds:
            cloud.update()

        for s in self.sparkles:
            s.update()

        for b in self.blocks:
            b.update()

        for wc in self.world_coins:
            wc.update(player)

        for c in self.coins[:]:
            c.update()
            if not c.alive:
                self.coins.remove(c)

    def draw_sky(self, surf):
        half_h = HEIGHT // 2
        sky_top = SKY_TOP if self.level == 1 else (255, 140, 185)
        sky_mid = SKY_MID if self.level == 1 else (255, 185, 215)
        sky_bottom = SKY_BOTTOM if self.level == 1 else (255, 240, 220)

        for y in range(half_h):
            ratio = y / half_h
            r = int(sky_top[0] + (sky_mid[0] - sky_top[0]) * ratio)
            g = int(sky_top[1] + (sky_mid[1] - sky_top[1]) * ratio)
            b = int(sky_top[2] + (sky_mid[2] - sky_top[2]) * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        for y in range(half_h, HEIGHT):
            ratio = (y - half_h) / (HEIGHT - half_h)
            r = int(sky_mid[0] + (sky_bottom[0] - sky_mid[0]) * ratio)
            g = int(sky_mid[1] + (sky_bottom[1] - sky_mid[1]) * ratio)
            b = int(sky_mid[2] + (sky_bottom[2] - sky_mid[2]) * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    def draw(self, surf, time_sec):
        self.draw_sky(surf)

        for rainbow in self.rainbows:
            rainbow.draw(surf)

        for hill in self.hills:
            hill.draw(surf)

        for cloud in self.clouds:
            cloud.draw(surf)

        for boo in self.boos:
            boo.draw(surf, time_sec)

        for lolli in self.lollipops:
            lolli.draw(surf, time_sec)

        for mush in self.mushrooms:
            mush.draw(surf)

        for pipe in self.pipes:
            pipe.draw(surf)

        for block in self.blocks:
            block.draw(surf, time_sec)

        # Dibujar Portal Rosa (Nivel 1) o Llave Rosa con Dorado (Nivel 2)
        if self.portal:
            self.portal.draw(surf, time_sec)
        if self.key:
            self.key.draw(surf, time_sec)

        for wc in self.world_coins:
            wc.draw(surf)

        for coin in self.coins:
            coin.draw(surf)

        # Suelo temático rosa en Nivel 2 y clásico verde lima en Nivel 1
        if self.level == 1:
            dirt_main = DIRT_BROWN
            dirt_dark = DIRT_DARK
            dirt_dots = DIRT_DOTS
            grass_top = GRASS_TOP
            grass_light = GRASS_LIME
        else:
            from settings import DIRT_N2_BROWN, DIRT_N2_DARK, DIRT_N2_DOTS, GRASS_N2_TOP, GRASS_N2_LIME
            dirt_main = DIRT_N2_BROWN
            dirt_dark = DIRT_N2_DARK
            dirt_dots = DIRT_N2_DOTS
            grass_top = GRASS_N2_TOP
            grass_light = GRASS_N2_LIME

        pygame.draw.rect(surf, dirt_main, (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
        pygame.draw.rect(surf, grass_top, (0, self.ground_y, WIDTH, 24))
        pygame.draw.line(surf, grass_light, (0, self.ground_y + 2), (WIDTH, self.ground_y + 2), 3)

        for gx in range(0, WIDTH, 22):
            pygame.draw.polygon(surf, grass_top, [
                (gx, self.ground_y + 24),
                (gx + 11, self.ground_y + 32),
                (gx + 22, self.ground_y + 24)
            ])

        for tx in range(0, WIDTH, 40):
            for ty in range(self.ground_y + 40, HEIGHT, 28):
                off = 20 if (ty // 28) % 2 == 0 else 0
                pygame.draw.rect(surf, dirt_dark, (tx + off, ty, 18, 9), border_radius=3)
                pygame.draw.rect(surf, dirt_dots, (tx + off + 2, ty + 2, 14, 4), border_radius=2)

        for flower in self.flowers:
            flower.draw(surf, time_sec)

        for sparkle in self.sparkles:
            sparkle.draw(surf)
