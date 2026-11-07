import pygame

class HUD:
    def __init__(self, width):
        self.width = width
        self.font_title = pygame.font.SysFont("comicsansms", 15, bold=True)
        self.font_controls = pygame.font.SysFont("comicsansms", 18, bold=True)
        self.font_coin = pygame.font.SysFont("comicsansms", 22, bold=True)

    def draw(self, surf, coins_collected):
        # 1. Barra superior estilo ventana Kawaii Browser (como en la imagen de referencia)
        bar_h = 36
        pygame.draw.rect(surf, (255, 255, 255, 240), (0, 0, self.width, bar_h))
        pygame.draw.line(surf, (255, 185, 215), (0, bar_h), (self.width, bar_h), 2)

        # Título de la pestaña estilo Kawaii
        title_txt = self.font_title.render("Mundo Mario Bros Pastel - Flores y Aventura", True, (130, 80, 110))
        surf.blit(title_txt, (18, 9))

        # Botones decorativos circulares de ventana a la derecha
        btn_y = 18
        for i, col in enumerate([(255, 130, 160), (255, 205, 100), (120, 220, 140)]):
            pygame.draw.circle(surf, col, (self.width - 70 + i * 18, btn_y), 5)

        # 2. Panel de controles flotante blanco redondeado
        ctrl_w, ctrl_h = 390, 48
        ctrl_panel = pygame.Surface((ctrl_w, ctrl_h), pygame.SRCALPHA)
        pygame.draw.rect(ctrl_panel, (255, 255, 255, 220), ctrl_panel.get_rect(), border_radius=16)
        pygame.draw.rect(ctrl_panel, (255, 180, 215), ctrl_panel.get_rect(), width=2, border_radius=16)
        surf.blit(ctrl_panel, (20, bar_h + 16))
        
        info_text = self.font_controls.render("← → / A D : Mover  |  ESPACIO : Saltar", True, (110, 50, 90))
        surf.blit(info_text, (34, bar_h + 28))

        # 3. Contador de monedas estilo Mario Kawaii
        coin_w, coin_h = 160, 48
        coin_x = self.width - coin_w - 20
        coin_panel = pygame.Surface((coin_w, coin_h), pygame.SRCALPHA)
        pygame.draw.rect(coin_panel, (255, 255, 255, 220), coin_panel.get_rect(), border_radius=16)
        pygame.draw.rect(coin_panel, (255, 180, 215), coin_panel.get_rect(), width=2, border_radius=16)
        surf.blit(coin_panel, (coin_x, bar_h + 16))

        # Moneda dorada
        pygame.draw.ellipse(surf, (255, 210, 30), (coin_x + 14, bar_h + 26, 16, 26))
        pygame.draw.ellipse(surf, (255, 245, 140), (coin_x + 16, bar_h + 28, 12, 22))
        
        coin_txt = self.font_coin.render(f"x {coins_collected:02d}", True, (110, 60, 30))
        surf.blit(coin_txt, (coin_x + 42, bar_h + 27))
