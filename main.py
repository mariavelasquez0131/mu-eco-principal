import pygame
import sys
from settings import WIDTH, HEIGHT, FPS, GROUND_Y
from player import Player
from environment import Environment
from enemies import Enemy
from hud import HUD
from sound_manager import sound_manager

def main():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mundo Mario Bros Pastel - Flores y Aventura")
    clock = pygame.time.Clock()

    # Iniciar música dulce de fondo estilo caja musical retro
    sound_manager.start_music()

    # Módulos del juego
    environment = Environment(GROUND_Y)
    player = Player(450, GROUND_Y)
    hud = HUD(WIDTH)

    # Enemigos patrullando
    enemies = [
        Enemy(x=280, ground_y=GROUND_Y, min_x=200, max_x=500),
        Enemy(x=780, ground_y=GROUND_Y, min_x=540, max_x=1050),
    ]

    start_time = pygame.time.get_ticks()
    running = True

    while running:
        time_sec = (pygame.time.get_ticks() - start_time) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    sound_manager.toggle_mute()

        keys = pygame.key.get_pressed()

        # Actualizaciones de lógica
        environment.update()
        for enemy in enemies:
            enemy.update(environment.pipes)

        player.update(keys, environment.blocks, environment.pipes, environment.coins, enemies)

        # Renderizado
        environment.draw(screen, time_sec)
        
        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)
        hud.draw(screen, player.coins_collected)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
