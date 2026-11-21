import pygame
import math
import os
from settings import WIDTH, HEIGHT

coin_sprite_path = os.path.join("sprites", "moneda.png")
if not os.path.exists(coin_sprite_path):
    coin_sprite_path = os.path.join("sprites", "monedas.png")

HUD_COIN_IMG = None

def get_hud_coin():
    global HUD_COIN_IMG
    if HUD_COIN_IMG is None and os.path.exists(coin_sprite_path):
        try:
            raw_coin_img = pygame.image.load(coin_sprite_path).convert_alpha()
            HUD_COIN_IMG = pygame.transform.smoothscale(raw_coin_img, (30, 30))
        except Exception:
            HUD_COIN_IMG = None
    return HUD_COIN_IMG

class HUD:
    def __init__(self, width):
        self.width = width
        self.font_title = pygame.font.SysFont("comicsansms", 16, bold=True)
        self.font_controls = pygame.font.SysFont("comicsansms", 16, bold=True)
        self.font_coin = pygame.font.SysFont("comicsansms", 22, bold=True)
        self.font_gameover = pygame.font.SysFont("comicsansms", 48, bold=True)
        self.font_win = pygame.font.SysFont("comicsansms", 52, bold=True)
        self.font_restart = pygame.font.SysFont("comicsansms", 24, bold=True)

    def draw_heart(self, surf, x, y, filled=True):
        color = (255, 70, 110) if filled else (220, 190, 205)
        r = 7
        pygame.draw.circle(surf, color, (x - 5, y), r)
        pygame.draw.circle(surf, color, (x + 5, y), r)
        points = [(x - 12, y + 2), (x + 12, y + 2), (x, y + 14)]
        pygame.draw.polygon(surf, color, points)
        if filled:
            pygame.draw.circle(surf, (255, 255, 255), (x - 6, y - 2), 2)

    def draw(self, surf, coins_collected, health=3, max_health=3, current_level=1, key_collected=False):
        bar_h = 40
        pygame.draw.rect(surf, (255, 255, 255, 240), (0, 0, self.width, bar_h))
        pygame.draw.line(surf, (255, 185, 215), (0, bar_h), (self.width, bar_h), 2)

        level_str = f"Mundo Pastel - ★ NIVEL {current_level} ★"
        title_txt = self.font_title.render(level_str, True, (130, 80, 110))
        surf.blit(title_txt, (20, 10))

        btn_y = 20
        for i, col in enumerate([(255, 130, 160), (255, 205, 100), (120, 220, 140)]):
            pygame.draw.circle(surf, col, (self.width - 80 + i * 20, btn_y), 6)

        # 1. Panel de Controles
        ctrl_w, ctrl_h = 490, 50
        ctrl_panel = pygame.Surface((ctrl_w, ctrl_h), pygame.SRCALPHA)
        pygame.draw.rect(ctrl_panel, (255, 255, 255, 225), ctrl_panel.get_rect(), border_radius=18)
        pygame.draw.rect(ctrl_panel, (255, 180, 215), ctrl_panel.get_rect(), width=2, border_radius=18)
        surf.blit(ctrl_panel, (18, bar_h + 16))
        
        info_text = self.font_controls.render("← →: Mover | ESPACIO: Saltar | E: Atacar | ↓/S: Tubos", True, (110, 50, 90))
        surf.blit(info_text, (26, bar_h + 30))

        # 2. Panel de Vidas dinámico (5 corazones en N1, 7 corazones en N2)
        heart_spacing = 31 if max_health > 5 else 38
        life_w = 40 + max_health * heart_spacing
        life_x = 524
        life_panel = pygame.Surface((life_w, life_h := 50), pygame.SRCALPHA)
        pygame.draw.rect(life_panel, (255, 255, 255, 225), life_panel.get_rect(), border_radius=18)
        pygame.draw.rect(life_panel, (255, 180, 215), life_panel.get_rect(), width=2, border_radius=18)
        surf.blit(life_panel, (life_x, bar_h + 16))

        for i in range(max_health):
            hx = life_x + 22 + i * heart_spacing
            hy = bar_h + 40
            self.draw_heart(surf, hx, hy, filled=(i < health))

        # 3. Panel de Objetivo (Nivel 1: Portal | Nivel 2: Llave Rosa-Dorado)
        obj_w, obj_h = 270, 50
        obj_x = life_x + life_w + 14
        obj_panel = pygame.Surface((obj_w, obj_h), pygame.SRCALPHA)
        pygame.draw.rect(obj_panel, (255, 255, 255, 225), obj_panel.get_rect(), border_radius=18)
        pygame.draw.rect(obj_panel, (255, 180, 215), obj_panel.get_rect(), width=2, border_radius=18)
        surf.blit(obj_panel, (obj_x, bar_h + 16))

        font_obj = pygame.font.SysFont("comicsansms", 14, bold=True)
        if current_level == 1:
            obj_txt = font_obj.render("OBJETIVO: Portal Rosa", True, (210, 60, 130))
            surf.blit(obj_txt, (obj_x + 18, bar_h + 31))
            pygame.draw.circle(surf, (255, 105, 180), (obj_x + obj_w - 24, bar_h + 41), 10)
            pygame.draw.circle(surf, (255, 230, 245), (obj_x + obj_w - 24, bar_h + 41), 5)
        else:
            if key_collected:
                obj_txt = font_obj.render("LLAVE: ¡Conseguida! ✓", True, (40, 160, 70))
            else:
                obj_txt = font_obj.render("LLAVE: Busca Llave Dorada", True, (200, 130, 10))
            surf.blit(obj_txt, (obj_x + 15, bar_h + 31))
            # Icono de llave
            kx = obj_x + obj_w - 24
            ky = bar_h + 41
            pygame.draw.circle(surf, (255, 215, 30), (kx, ky), 9)
            pygame.draw.circle(surf, (255, 110, 175), (kx, ky), 5)

        # 4. Contador de Monedas
        coin_w, coin_h = 140, 50
        coin_x = self.width - coin_w - 18
        coin_panel = pygame.Surface((coin_w, coin_h), pygame.SRCALPHA)
        pygame.draw.rect(coin_panel, (255, 255, 255, 225), coin_panel.get_rect(), border_radius=18)
        pygame.draw.rect(coin_panel, (255, 180, 215), coin_panel.get_rect(), width=2, border_radius=18)
        surf.blit(coin_panel, (coin_x, bar_h + 16))

        coin_img = get_hud_coin()
        if coin_img:
            surf.blit(coin_img, (coin_x + 12, bar_h + 26))
        else:
            pygame.draw.ellipse(surf, (255, 210, 30), (coin_x + 12, bar_h + 26, 18, 28))
            pygame.draw.ellipse(surf, (255, 245, 140), (coin_x + 14, bar_h + 28, 14, 24))
        
        coin_txt = self.font_coin.render(f"x {coins_collected:02d}", True, (110, 60, 30))
        surf.blit(coin_txt, (coin_x + 48, bar_h + 28))

    def draw_game_over(self, surf, time_sec):
        overlay = pygame.Surface((self.width, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 10, 25, 195))
        surf.blit(overlay, (0, 0))

        card_w, card_h = 600, 240
        card_x = (self.width - card_w) // 2
        card_y = (HEIGHT - card_h) // 2
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card, (255, 240, 248, 250), card.get_rect(), border_radius=26)
        pygame.draw.rect(card, (255, 140, 185), card.get_rect(), width=4, border_radius=26)
        surf.blit(card, (card_x, card_y))

        pulse = math.sin(time_sec * 5) * 4
        title = self.font_gameover.render("Game Over, perdiste", True, (230, 50, 100))
        surf.blit(title, (card_x + (card_w - title.get_width()) // 2, card_y + 45 + pulse))

        prompt = self.font_restart.render("Presiona R o ESPACIO para reiniciar", True, (100, 60, 90))
        surf.blit(prompt, (card_x + (card_w - prompt.get_width()) // 2, card_y + 145))

    def draw_victory(self, surf, time_sec):
        """Pantalla de victoria: Unicornio grande kawaii festejando y diciendo GANASTE"""
        overlay = pygame.Surface((self.width, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 230, 245, 185))
        surf.blit(overlay, (0, 0))

        card_w, card_h = 720, 480
        card_x = (self.width - card_w) // 2
        card_y = (HEIGHT - card_h) // 2
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card, (255, 255, 255, 245), card.get_rect(), border_radius=32)
        pygame.draw.rect(card, (255, 150, 195), card.get_rect(), width=5, border_radius=32)
        surf.blit(card, (card_x, card_y))

        # Dibujar Unicornio Mágico Grande de Victoria en el centro de la tarjeta
        uni_cx = self.width // 2
        uni_cy = card_y + 190 + math.sin(time_sec * 4) * 8
        self.draw_victory_unicorn(surf, uni_cx, uni_cy, scale=2.2)

        # Destellos y estrellas alrededor del unicornio
        for i in range(8):
            ang = time_sec * 2 + i * (math.pi / 4)
            sx = uni_cx + math.cos(ang) * 160
            sy = uni_cy - 40 + math.sin(ang) * 90
            star_color = [(255, 220, 50), (255, 140, 195), (140, 220, 255)][i % 3]
            pygame.draw.circle(surf, star_color, (int(sx), int(sy)), 6)
            pygame.draw.circle(surf, (255, 255, 255), (int(sx), int(sy)), 3)

        # Texto ¡GANASTE!
        pulse = math.sin(time_sec * 6) * 5
        win_title = self.font_win.render("¡GANASTE TODO EL JUEGO!", True, (240, 50, 130))
        surf.blit(win_title, (card_x + (card_w - win_title.get_width()) // 2, card_y + 35 + pulse))

        # Globo o mensaje del unicornio
        sub_title = self.font_restart.render("¡Derrotaste a todos y encontraste la Llave Dorada!", True, (120, 70, 110))
        surf.blit(sub_title, (card_x + (card_w - sub_title.get_width()) // 2, card_y + 365))

        prompt = self.font_controls.render("Presiona R o ESPACIO para jugar otra vez", True, (160, 100, 140))
        surf.blit(prompt, (card_x + (card_w - prompt.get_width()) // 2, card_y + 415))

    def draw_victory_unicorn(self, surf, cx, cy, scale=2.0):
        s = scale
        u_surf = pygame.Surface((int(100 * s), int(90 * s)), pygame.SRCALPHA)
        
        body_color = (255, 255, 255)
        horn_color = (255, 215, 40)
        mane_color = (255, 130, 185)
        blush_color = (255, 140, 175, 210)
        eye_color = (60, 30, 50)

        # Cuerpo
        pygame.draw.ellipse(u_surf, body_color, (int(20*s), int(36*s), int(52*s), int(34*s)))
        # Patitas alegres
        pygame.draw.ellipse(u_surf, (255, 235, 245), (int(24*s), int(58*s), int(20*s), int(15*s)))
        pygame.draw.ellipse(u_surf, (255, 235, 245), (int(50*s), int(58*s), int(20*s), int(15*s)))
        
        # Cabeza
        pygame.draw.circle(u_surf, body_color, (int(56*s), int(28*s)), int(20*s))
        # Hocico
        pygame.draw.ellipse(u_surf, (255, 230, 242), (int(64*s), int(28*s), int(18*s), int(14*s)))
        pygame.draw.circle(u_surf, (255, 140, 180), (int(76*s), int(33*s)), max(1, int(2.0*s)))

        # Cuerno brillante dorado
        horn_pts = [(int(52*s), int(16*s)), (int(64*s), int(0*s)), (int(58*s), int(17*s))]
        pygame.draw.polygon(u_surf, horn_color, horn_pts)

        # Melena arcoíris pastel
        pygame.draw.circle(u_surf, mane_color, (int(42*s), int(16*s)), int(11*s))
        pygame.draw.circle(u_surf, (200, 150, 255), (int(34*s), int(28*s)), int(10*s))
        pygame.draw.circle(u_surf, (130, 220, 255), (int(28*s), int(42*s)), int(9*s))
        pygame.draw.circle(u_surf, (255, 225, 120), (int(26*s), int(52*s)), int(8*s))

        # Ojo alegre cerrado ^ ^
        pygame.draw.arc(u_surf, eye_color, (int(60*s), int(22*s), int(10*s), int(8*s)), 0, math.pi, 2)
        # Mejilla sonrojada
        pygame.draw.circle(u_surf, blush_color, (int(64*s), int(34*s)), max(1, int(5.0*s)))

        # Orejita
        pygame.draw.polygon(u_surf, body_color, [(int(46*s), int(16*s)), (int(49*s), int(4*s)), (int(55*s), int(14*s))])

        # Destello cuerno
        pygame.draw.circle(u_surf, (255, 255, 255), (int(65*s), int(2*s)), max(1, int(3.5*s)))

        surf.blit(u_surf, (cx - int(50 * s), cy - int(45 * s)))
