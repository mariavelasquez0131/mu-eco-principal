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
            HUD_COIN_IMG = pygame.transform.smoothscale(raw_coin_img, (28, 28))
        except Exception:
            HUD_COIN_IMG = None
    return HUD_COIN_IMG

class HUD:
    def __init__(self, width):
        self.width = width
        self.font_title = pygame.font.SysFont("comicsansms", 15, bold=True)
        self.font_controls = pygame.font.SysFont("comicsansms", 17, bold=True)
        self.font_coin = pygame.font.SysFont("comicsansms", 22, bold=True)
        self.font_gameover = pygame.font.SysFont("comicsansms", 44, bold=True)
        self.font_restart = pygame.font.SysFont("comicsansms", 22, bold=True)

    def draw_heart(self, surf, x, y, filled=True):
        color = (255, 70, 110) if filled else (220, 190, 205)
        r = 6
        pygame.draw.circle(surf, color, (x - 4, y), r)
        pygame.draw.circle(surf, color, (x + 4, y), r)
        points = [(x - 10, y + 2), (x + 10, y + 2), (x, y + 12)]
        pygame.draw.polygon(surf, color, points)
        if filled:
            pygame.draw.circle(surf, (255, 255, 255), (x - 5, y - 2), 2)

    def draw(self, surf, coins_collected, health=3, max_health=3):
        bar_h = 36
        pygame.draw.rect(surf, (255, 255, 255, 240), (0, 0, self.width, bar_h))
        pygame.draw.line(surf, (255, 185, 215), (0, bar_h), (self.width, bar_h), 2)

        title_txt = self.font_title.render("Mundo Mario Bros Pastel - Flores y Aventura", True, (130, 80, 110))
        surf.blit(title_txt, (18, 9))

        btn_y = 18
        for i, col in enumerate([(255, 130, 160), (255, 205, 100), (120, 220, 140)]):
            pygame.draw.circle(surf, col, (self.width - 70 + i * 18, btn_y), 5)

        # 1. Panel de Controles
        ctrl_w, ctrl_h = 420, 48
        ctrl_panel = pygame.Surface((ctrl_w, ctrl_h), pygame.SRCALPHA)
        pygame.draw.rect(ctrl_panel, (255, 255, 255, 220), ctrl_panel.get_rect(), border_radius=16)
        pygame.draw.rect(ctrl_panel, (255, 180, 215), ctrl_panel.get_rect(), width=2, border_radius=16)
        surf.blit(ctrl_panel, (20, bar_h + 16))
        
        info_text = self.font_controls.render("← → / A D : Mover | ESPACIO : Saltar | M : Mute", True, (110, 50, 90))
        surf.blit(info_text, (30, bar_h + 29))

        # 2. Panel de Vidas (Máximo 3 Vidas exactas)
        life_w, life_h = 145, 48
        life_x = 460
        life_panel = pygame.Surface((life_w, life_h), pygame.SRCALPHA)
        pygame.draw.rect(life_panel, (255, 255, 255, 220), life_panel.get_rect(), border_radius=16)
        pygame.draw.rect(life_panel, (255, 180, 215), life_panel.get_rect(), width=2, border_radius=16)
        surf.blit(life_panel, (life_x, bar_h + 16))

        for i in range(max_health):
            hx = life_x + 30 + i * 36
            hy = bar_h + 38
            self.draw_heart(surf, hx, hy, filled=(i < health))

        # 3. Contador de Monedas (Usando imagen moneda.png)
        coin_w, coin_h = 150, 48
        coin_x = self.width - coin_w - 20
        coin_panel = pygame.Surface((coin_w, coin_h), pygame.SRCALPHA)
        pygame.draw.rect(coin_panel, (255, 255, 255, 220), coin_panel.get_rect(), border_radius=16)
        pygame.draw.rect(coin_panel, (255, 180, 215), coin_panel.get_rect(), width=2, border_radius=16)
        surf.blit(coin_panel, (coin_x, bar_h + 16))

        coin_img = get_hud_coin()
        if coin_img:
            surf.blit(coin_img, (coin_x + 12, bar_h + 26))
        else:
            pygame.draw.ellipse(surf, (255, 210, 30), (coin_x + 14, bar_h + 26, 16, 26))
            pygame.draw.ellipse(surf, (255, 245, 140), (coin_x + 16, bar_h + 28, 12, 22))
        
        coin_txt = self.font_coin.render(f"x {coins_collected:02d}", True, (110, 60, 30))
        surf.blit(coin_txt, (coin_x + 46, bar_h + 27))

    def draw_game_over(self, surf, time_sec):
        overlay = pygame.Surface((self.width, HEIGHT), pygame.SRCALPHA)
        overlay.fill((20, 10, 25, 195))
        surf.blit(overlay, (0, 0))

        card_w, card_h = 560, 230
        card_x = (self.width - card_w) // 2
        card_y = (HEIGHT - card_h) // 2
        card = pygame.Surface((card_w, card_h), pygame.SRCALPHA)
        pygame.draw.rect(card, (255, 240, 248, 250), card.get_rect(), border_radius=24)
        pygame.draw.rect(card, (255, 140, 185), card.get_rect(), width=4, border_radius=24)
        surf.blit(card, (card_x, card_y))

        # Texto exacto solicitado: "Game Over, perdiste"
        pulse = math.sin(time_sec * 5) * 4
        title = self.font_gameover.render("Game Over, perdiste", True, (230, 50, 100))
        surf.blit(title, (card_x + (card_w - title.get_width()) // 2, card_y + 40 + pulse))

        prompt = self.font_restart.render("Presiona R o ESPACIO para reiniciar", True, (100, 60, 90))
        surf.blit(prompt, (card_x + (card_w - prompt.get_width()) // 2, card_y + 135))
