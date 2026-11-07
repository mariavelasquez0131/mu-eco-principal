import pygame
import sys
from settings import WIDTH, HEIGHT, FPS, GROUND_Y
from player import Player
from environment import Environment
from enemies import PngEnemy
from hud import HUD
from sound_manager import sound_manager

def main():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mundo Mario Bros Pastel - Flores y Aventura")
    clock = pygame.time.Clock()

    sound_manager.start_music()

    def reset_game():
        env = Environment(GROUND_Y)
        ply = Player(450, GROUND_Y)
        
        # Múltiples enemigos creados a partir de enemigo.png (sin enemigos generados por IA)
        enemies = [
            PngEnemy(x=220, ground_y=GROUND_Y, speed=1.9, jump_power=-10.0),
            PngEnemy(x=780, ground_y=GROUND_Y, speed=2.3, jump_power=-11.0),
            PngEnemy(x=1050, ground_y=GROUND_Y, speed=2.5, jump_power=-11.5),
        ]
        return env, ply, enemies

    environment, player, enemies = reset_game()
    hud = HUD(WIDTH)

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
                elif (event.key == pygame.K_r or event.key == pygame.K_SPACE) and player.health <= 0:
                    environment, player, enemies = reset_game()

        keys = pygame.key.get_pressed()

        # Solo actualizar física si el jugador sigue vivo
        if player.health > 0:
            environment.update(player)
            for enemy in enemies:
                enemy.update(player, environment.pipes, environment.blocks)
            player.update(keys, environment.blocks, environment.pipes, environment.coins, enemies)

        # Renderizado
        environment.draw(screen, time_sec)
        
        # Dibujar enemigos basados en enemigo.png
        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)
        hud.draw(screen, player.coins_collected, player.health, player.max_health)

        # Pantalla de "Game Over, perdiste" al llegar a 0 vidas
        if player.health <= 0:
            hud.draw_game_over(screen, time_sec)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
