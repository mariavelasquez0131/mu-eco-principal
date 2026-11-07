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
            COIN_IMG = pygame.transform.smoothscale(raw_coin_img, (36, 36))
        except Exception:
            COIN_IMG = None
    return COIN_IMG


# --- DIBUJO DE UNICORNIO KAWAII EN LAS NUBES ---
def draw_cloud_unicorn(surf, cx, cy, scale=1.0, facing_right=True):
    s = scale
    u_surf = pygame.Surface((int(70 * s), int(60 * s)), pygame.SRCALPHA)
    
    body_color = (255, 255, 255)
    horn_color = (255, 220, 50)
    mane_color = (255, 140, 195)
    blush_color = (255, 150, 180, 180)
    eye_color = (50, 30, 45)

    # Cuerpo suave sentado sobre la nube
    pygame.draw.ellipse(u_surf, body_color, (int(14*s), int(22*s), int(36*s), int(26*s)))
    
    # Cabeza
    pygame.draw.circle(u_surf, body_color, (int(36*s), int(18*s)), int(14*s))
    # Hocico
    pygame.draw.ellipse(u_surf, (255, 240, 245), (int(42*s), int(18*s), int(14*s), int(10*s)))

    # Cuerno mágico dorado brillante
    horn_pts = [(int(34*s), int(10*s)), (int(42*s), int(0*s)), (int(38*s), int(11*s))]
    pygame.draw.polygon(u_surf, horn_color, horn_pts)

    # Melena mágica rosa pastel
    pygame.draw.circle(u_surf, mane_color, (int(26*s), int(10*s)), int(8*s))
    pygame.draw.circle(u_surf, (200, 160, 255), (int(22*s), int(18*s)), int(7*s))
    pygame.draw.circle(u_surf, (140, 220, 255), (int(18*s), int(26*s)), int(6*s))

    # Ojo sonriente kawaii
    pygame.draw.circle(u_surf, eye_color, (int(40*s), int(16*s)), max(1, int(2.5*s)))
    # Mejilla sonrojada
    pygame.draw.circle(u_surf, blush_color, (int(42*s), int(22*s)), max(1, int(3.5*s)))

    # Oreja
    pygame.draw.polygon(u_surf, body_color, [(int(30*s), int(10*s)), (int(32*s), int(2*s)), (int(36*s), int(8*s))])

    # Destellos alrededor del cuerno
    pygame.draw.circle(u_surf, (255, 255, 255), (int(43*s), int(1*s)), max(1, int(2*s)))

    if not facing_right:
        u_surf = pygame.transform.flip(u_surf, True, False)

    surf.blit(u_surf, (cx - 30 * s, cy - 40 * s))


# --- NUBES CON UNICORNIOS ENCIMA ---
class CloudKawaii:
    def __init__(self, x, y, speed, scale=1.0, has_unicorn=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.scale = scale
        self.has_unicorn = has_unicorn
        self.w = int(140 * scale)
        self.h = int(75 * scale)
        self.surface = pygame.Surface((self.w, self.h + int(50 * scale)), pygame.SRCALPHA)
        self.render_cloud()

    def render_cloud(self):
        w, h = self.w, self.h
        surf = self.surface
        offset_y = int(35 * self.scale) if self.has_unicorn else 0

        # Dibujar Unicornio si corresponde
        if self.has_unicorn:
            draw_cloud_unicorn(surf, w * 0.52, offset_y + h * 0.35, scale=self.scale * 0.95, facing_right=True)
        
        # Sombra y nubes
        shadow = (255, 230, 245, 190)
        white = (255, 255, 255, 250)
        
        pygame.draw.ellipse(surf, shadow, (w * 0.05, offset_y + h * 0.35, w * 0.9, h * 0.55))
        pygame.draw.ellipse(surf, white, (w * 0.08, offset_y + h * 0.3, w * 0.84, h * 0.55))
        pygame.draw.circle(surf, white, (int(w * 0.32), offset_y + int(h * 0.42)), int(h * 0.35))
        pygame.draw.circle(surf, white, (int(w * 0.54), offset_y + int(h * 0.34)), int(h * 0.38))
        pygame.draw.circle(surf, white, (int(w * 0.74), offset_y + int(h * 0.46)), int(h * 0.28))
        
        # Ojos sonrientes kawaii
        eye_color = (60, 45, 65)
        pygame.draw.ellipse(surf, eye_color, (w * 0.43, offset_y + h * 0.46, 5, 8))
        pygame.draw.ellipse(surf, eye_color, (w * 0.57, offset_y + h * 0.46, 5, 8))
        # Mejillas sonrojadas
        blush = (255, 130, 175, 160)
        pygame.draw.circle(surf, blush, (int(w * 0.37), offset_y + int(h * 0.55)), 6)
        pygame.draw.circle(surf, blush, (int(w * 0.63), offset_y + int(h * 0.55)), 6)

    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 140:
            self.x = -180
            self.y = random.randint(25, 200)

    def draw(self, surf):
        surf.blit(self.surface, (self.x, self.y))


# --- ARCOÍRIS PASTEL ---
class Rainbow:
    def __init__(self, cx, cy, radius_outer, thickness=7):
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
            eye_w, eye_h = 4, 12
            pygame.draw.ellipse(surf, (60, 45, 75), (self.x + self.width * 0.46, eye_y, eye_w, eye_h))
            pygame.draw.ellipse(surf, (60, 45, 75), (self.x + self.width * 0.54, eye_y, eye_w, eye_h))
            pygame.draw.circle(surf, (255, 130, 175, 140), (int(self.x + self.width * 0.40), int(eye_y + 12)), 7)
            pygame.draw.circle(surf, (255, 130, 175, 140), (int(self.x + self.width * 0.60), int(eye_y + 12)), 7)


# --- DULCES Y HONGOS ---
class Lollipop:
    def __init__(self, x, ground_y, radius=24):
        self.x = x
        self.ground_y = ground_y
        self.radius = radius
        self.stick_h = 65

    def draw(self, surf, time_sec):
        top_y = self.ground_y - self.stick_h
        pygame.draw.line(surf, (255, 255, 255), (self.x, self.ground_y), (self.x, top_y), 5)
        cx, cy = self.x, top_y
        colors = [(255, 130, 180), (255, 240, 140), (255, 170, 200)]
        pygame.draw.circle(surf, colors[0], (cx, cy), self.radius)
        pygame.draw.circle(surf, colors[1], (cx, cy), int(self.radius * 0.75))
        pygame.draw.circle(surf, colors[2], (cx, cy), int(self.radius * 0.5))
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy), int(self.radius * 0.25))
        pygame.draw.circle(surf, (255, 255, 255), (cx - int(self.radius*0.35), cy - int(self.radius*0.35)), 4)


class CuteMushroom:
    def __init__(self, x, ground_y, color=(255, 95, 120)):
        self.x = x
        self.ground_y = ground_y
        self.color = color

    def draw(self, surf):
        pygame.draw.rect(surf, (255, 245, 240), (self.x + 6, self.ground_y - 14, 12, 14), border_radius=4)
        pygame.draw.ellipse(surf, self.color, (self.x, self.ground_y - 28, 24, 18))
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 6, self.ground_y - 21), 3)
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 18, self.ground_y - 21), 3)
        pygame.draw.circle(surf, (255, 255, 255), (self.x + 12, self.ground_y - 25), 3)


# --- FLORES KAWAII ---
class FlowerKawaii:
    def __init__(self, x, ground_y):
        self.x = x
        self.ground_y = ground_y
        self.color = random.choices(FLOWER_COLORS, weights=FLOWER_WEIGHTS)[0]
        self.center_color = (255, 235, 120) if self.color != (255, 225, 80) else (255, 130, 160)
        self.size = random.randint(7, 12)
        self.sway_offset = random.uniform(0, 10)
        self.sway_speed = random.uniform(2.5, 4.2)
        self.stem_height = random.randint(18, 28)

    def draw(self, surf, time_sec):
        sway = math.sin(time_sec * self.sway_speed + self.sway_offset) * 3.5
        fx = self.x + sway
        fy = self.ground_y - self.stem_height

        pygame.draw.line(surf, (110, 205, 75), (self.x, self.ground_y), (fx, fy), 3)
        pygame.draw.ellipse(surf, (110, 205, 75), (self.x - 4 + sway * 0.4, self.ground_y - self.stem_height * 0.4, 6, 4))

        num_petals = 5
        petal_dist = self.size * 0.8
        for i in range(num_petals):
            ang = (i * 2 * math.pi / num_petals) + (sway * 0.05)
            px = fx + math.cos(ang) * petal_dist
            py = fy + math.sin(ang) * petal_dist
            pygame.draw.circle(surf, self.color, (int(px), int(py)), int(self.size * 0.58))

        pygame.draw.circle(surf, self.center_color, (int(fx), int(fy)), int(self.size * 0.42))
        if self.size >= 10 and self.color[0] == 255 and self.color[1] < 160:
            pygame.draw.circle(surf, (60, 40, 50), (int(fx - 2), int(fy)), 1)
            pygame.draw.circle(surf, (60, 40, 50), (int(fx + 2), int(fy)), 1)


# --- MONEDA USANDO SPRITE MONEDA.PNG ---
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
            # Escalar ligeramente con efecto de giro 3D
            spin = abs(math.cos(self.frame))
            spin_w = max(4, int(36 * spin))
            scaled_coin = pygame.transform.scale(coin_img, (spin_w, 36))
            surf.blit(scaled_coin, (int(self.x - spin_w / 2), int(self.y)))
        else:
            coin_w = max(4, int(abs(math.cos(self.frame)) * 20))
            coin_h = 24
            cx = int(self.x - coin_w / 2)
            cy = int(self.y)
            pygame.draw.ellipse(surf, (255, 215, 40), (cx, cy, coin_w, coin_h))
            pygame.draw.ellipse(surf, (255, 245, 140), (cx + 2, cy + 2, max(1, coin_w - 4), coin_h - 4))


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

        # Colisión con el jugador
        coin_rect = pygame.Rect(self.x - 16, self.y - 16, 32, 32)
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
            spin_w = max(4, int(30 * spin))
            scaled_coin = pygame.transform.scale(coin_img, (spin_w, 30))
            surf.blit(scaled_coin, (int(self.x - spin_w / 2), int(self.y - 15)))
        else:
            pygame.draw.circle(surf, (255, 215, 0), (int(self.x), int(self.y)), 12)


# --- BLOQUES ROSA CHICLE KAWAII ---
class FloatingBlockKawaii:
    def __init__(self, x, y, is_question=False):
        self.rect = pygame.Rect(x, y, 46, 46)
        self.is_question = is_question
        self.is_hit = False
        self.bounce_offset = 0

    def trigger_hit(self, coin_list):
        self.bounce_offset = -10
        if self.is_question and not self.is_hit:
            self.is_hit = True
            coin_list.append(FloatingCoin(self.rect.centerx, self.rect.y - 12))
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
                
                pygame.draw.rect(surf, border, (x, y, w, h), border_radius=8)
                pygame.draw.rect(surf, gold, (x + 3, y + 3, w - 6, h - 6), border_radius=6)
                pygame.draw.line(surf, highlight, (x + 5, y + 5), (x + w - 6, y + 5), 3)
                pygame.draw.line(surf, highlight, (x + 5, y + 5), (x + 5, y + h - 6), 3)

                pulse = math.sin(time_sec * 6) * 1.5
                font = pygame.font.SysFont("comicsansms", 24, bold=True)
                text = font.render("?", True, (255, 255, 255))
                surf.blit(text, (x + 16, y + 6 + pulse))
            else:
                used_c = (210, 175, 215)
                used_dark = (165, 130, 175)
                pygame.draw.rect(surf, used_dark, (x, y, w, h), border_radius=8)
                pygame.draw.rect(surf, used_c, (x + 3, y + 3, w - 6, h - 6), border_radius=6)
        else:
            pygame.draw.rect(surf, BLOCK_BORDER, (x, y, w, h), border_radius=8)
            pygame.draw.rect(surf, BLOCK_PINK, (x + 3, y + 3, w - 6, h - 6), border_radius=6)
            pygame.draw.line(surf, BLOCK_HIGHLIGHT, (x + 5, y + 5), (x + w - 6, y + 5), 2)
            pygame.draw.line(surf, BLOCK_HIGHLIGHT, (x + 5, y + 5), (x + 5, y + h - 6), 2)


# --- TUBERÍAS ROSA CHICLE ---
class PinkPipe:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.height = height
        self.width = 68
        self.lip_height = 28
        self.lip_width = 80

    def draw(self, surf):
        border = (195, 60, 120)
        body = PIPE_PINK
        light = PIPE_PINK_LIGHT
        dark = PIPE_PINK_DARK

        pygame.draw.rect(surf, border, (self.x - 2, self.y, self.width + 4, self.height), border_radius=4)
        pygame.draw.rect(surf, body, (self.x, self.y, self.width, self.height))
        pygame.draw.line(surf, light, (self.x + 10, self.y), (self.x + 10, self.y + self.height), 5)
        pygame.draw.rect(surf, dark, (self.x + self.width - 15, self.y, 12, self.height))

        head_x = self.x - (self.lip_width - self.width) // 2
        head_y = self.y - self.lip_height
        pygame.draw.rect(surf, border, (head_x - 2, head_y - 2, self.lip_width + 4, self.lip_height + 4), border_radius=6)
        pygame.draw.rect(surf, body, (head_x, head_y, self.lip_width, self.lip_height), border_radius=5)
        pygame.draw.line(surf, light, (head_x + 12, head_y + 3), (head_x + 12, head_y + self.lip_height - 3), 6)
        pygame.draw.rect(surf, dark, (head_x + self.lip_width - 18, head_y + 3, 14, self.lip_height - 6))


# --- FANTASMITAS KAWAII (BOOS) ---
class FloatingBooKawaii:
    def __init__(self, x, y, range_x=120):
        self.origin_x = x
        self.y = y
        self.range_x = range_x
        self.time_offset = random.uniform(0, 10)

    def draw(self, surf, time_sec):
        cur_x = self.origin_x + math.sin(time_sec * 1.5 + self.time_offset) * (self.range_x / 2)
        cur_y = self.y + math.sin(time_sec * 3.0 + self.time_offset) * 8
        
        body_color = (255, 255, 255, 240)
        shadow_c = (235, 245, 255)
        
        pygame.draw.circle(surf, shadow_c, (int(cur_x), int(cur_y + 2)), 14)
        pygame.draw.circle(surf, body_color, (int(cur_x), int(cur_y)), 14)
        
        pygame.draw.circle(surf, body_color, (int(cur_x - 12), int(cur_y + 2)), 5)
        pygame.draw.circle(surf, body_color, (int(cur_x + 12), int(cur_y + 2)), 5)

        pygame.draw.ellipse(surf, (60, 45, 75), (cur_x - 5, cur_y - 3, 3, 5))
        pygame.draw.ellipse(surf, (60, 45, 75), (cur_x + 2, cur_y - 3, 3, 5))
        pygame.draw.circle(surf, (255, 140, 180, 170), (int(cur_x - 7), int(cur_y + 4)), 3)
        pygame.draw.circle(surf, (255, 140, 180, 170), (int(cur_x + 7), int(cur_y + 4)), 3)


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
        self.size = random.uniform(5, 10)
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


# --- CLASE PRINCIPAL DEL ENTORNO ---
class Environment:
    def __init__(self, ground_y):
        self.ground_y = ground_y

        # Nubes animadas (Varias con UNICORNIOS encima)
        self.clouds = [
            CloudKawaii(50, 50, 0.32, 1.3, has_unicorn=True),
            CloudKawaii(380, 110, 0.45, 1.0, has_unicorn=False),
            CloudKawaii(720, 45, 0.38, 1.4, has_unicorn=True),
            CloudKawaii(1040, 85, 0.5, 1.1, has_unicorn=True),
            CloudKawaii(1350, 130, 0.4, 0.95, has_unicorn=False)
        ]

        # Arcoíris pastel
        self.rainbows = [
            Rainbow(280, 280, 240, thickness=7),
            Rainbow(980, 310, 200, thickness=6),
            Rainbow(640, ground_y + 40, 140, thickness=6)
        ]

        # Colinas pastel
        self.hills = [
            PastelHill(-40, ground_y, 320, 190, HILL_PINK_LIGHT, HILL_PINK_DARK, has_face=False),
            PastelHill(240, ground_y, 380, 230, HILL_LILA_LIGHT, HILL_LILA_DARK, has_face=True),
            PastelHill(680, ground_y, 360, 180, HILL_PINK_LIGHT, HILL_PINK_DARK, has_face=True),
            PastelHill(1040, ground_y, 340, 220, HILL_LILA_LIGHT, HILL_LILA_DARK, has_face=False)
        ]

        # Tuberías Rosa
        self.pipes = [
            PinkPipe(160, ground_y - 85, 85),
            PinkPipe(1120, ground_y - 110, 110)
        ]

        # Bloques
        self.blocks = [
            FloatingBlockKawaii(320, ground_y - 150, is_question=False),
            FloatingBlockKawaii(366, ground_y - 150, is_question=True),
            FloatingBlockKawaii(412, ground_y - 150, is_question=False),
            FloatingBlockKawaii(458, ground_y - 150, is_question=True),
            FloatingBlockKawaii(504, ground_y - 150, is_question=False),
            FloatingBlockKawaii(412, ground_y - 70, is_question=True),
            FloatingBlockKawaii(458, ground_y - 70, is_question=False),
            FloatingBlockKawaii(820, ground_y - 165, is_question=True),
            FloatingBlockKawaii(866, ground_y - 165, is_question=False),
            FloatingBlockKawaii(912, ground_y - 165, is_question=True),
            FloatingBlockKawaii(958, ground_y - 165, is_question=False),
        ]

        # Monedas dispersas por el mundo
        self.world_coins = [
            WorldCoin(343, ground_y - 195),
            WorldCoin(389, ground_y - 195),
            WorldCoin(435, ground_y - 195),
            WorldCoin(481, ground_y - 195),
            WorldCoin(843, ground_y - 210),
            WorldCoin(889, ground_y - 210),
            WorldCoin(935, ground_y - 210),
            WorldCoin(194, ground_y - 130), # Sobre la tubería rosa
        ]

        # Dulces
        self.lollipops = [
            Lollipop(440, ground_y, radius=24),
            Lollipop(1030, ground_y, radius=20)
        ]

        self.mushrooms = [
            CuteMushroom(260, ground_y, color=(255, 90, 120)),
            CuteMushroom(580, ground_y, color=(255, 110, 150)),
            CuteMushroom(760, ground_y, color=(255, 90, 120)),
            CuteMushroom(990, ground_y, color=(255, 130, 190)),
        ]

        self.boos = [
            FloatingBooKawaii(250, 170, range_x=100),
            FloatingBooKawaii(670, 200, range_x=120),
            FloatingBooKawaii(1070, 180, range_x=90)
        ]

        # Flores (muchas rosas)
        self.flowers = []
        random.seed(99)
        for fx in range(20, WIDTH - 20, 13):
            in_pipe = any((p.x - 12) <= fx <= (p.x + p.width + 12) for p in self.pipes)
            if not in_pipe:
                self.flowers.append(FlowerKawaii(fx + random.randint(-4, 4), ground_y + 4))

        self.sparkles = [FloatingSparkle() for _ in range(40)]
        self.coins = []

    def update(self, player):
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
        for y in range(half_h):
            ratio = y / half_h
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * ratio)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * ratio)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))
        for y in range(half_h, HEIGHT):
            ratio = (y - half_h) / (HEIGHT - half_h)
            r = int(SKY_MID[0] + (SKY_BOTTOM[0] - SKY_MID[0]) * ratio)
            g = int(SKY_MID[1] + (SKY_BOTTOM[1] - SKY_MID[1]) * ratio)
            b = int(SKY_MID[2] + (SKY_BOTTOM[2] - SKY_MID[2]) * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (WIDTH, y))

    def draw(self, surf, time_sec):
        self.draw_sky(surf)

        for rainbow in self.rainbows:
            rainbow.draw(surf)

        for hill in self.hills:
            hill.draw(surf)

        # Nubes con unicornios
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

        # Monedas flotantes del mundo y monedas emergentes de bloques
        for wc in self.world_coins:
            wc.draw(surf)

        for coin in self.coins:
            coin.draw(surf)

        # Suelo
        pygame.draw.rect(surf, DIRT_BROWN, (0, self.ground_y, WIDTH, HEIGHT - self.ground_y))
        pygame.draw.rect(surf, GRASS_TOP, (0, self.ground_y, WIDTH, 22))
        pygame.draw.line(surf, GRASS_LIME, (0, self.ground_y + 2), (WIDTH, self.ground_y + 2), 3)

        for gx in range(0, WIDTH, 20):
            pygame.draw.polygon(surf, GRASS_TOP, [
                (gx, self.ground_y + 22),
                (gx + 10, self.ground_y + 30),
                (gx + 20, self.ground_y + 22)
            ])

        for tx in range(0, WIDTH, 36):
            for ty in range(self.ground_y + 36, HEIGHT, 26):
                off = 18 if (ty // 26) % 2 == 0 else 0
                pygame.draw.rect(surf, DIRT_DARK, (tx + off, ty, 16, 8), border_radius=3)
                pygame.draw.rect(surf, DIRT_DOTS, (tx + off + 2, ty + 2, 12, 4), border_radius=2)

        for flower in self.flowers:
            flower.draw(surf, time_sec)

        for sparkle in self.sparkles:
            sparkle.draw(surf)
