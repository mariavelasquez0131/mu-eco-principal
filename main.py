import pygame
import sys
from settings import WIDTH, HEIGHT, FPS, GROUND_Y, CHAR_HEIGHT
from player import Player
from environment import Environment
from enemies import PngEnemy
from hud import HUD
from sound_manager import sound_manager

def main():
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    # Ventana grande (1600 x 900)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mundo Mario Bros Pastel - Flores y Aventura")
    clock = pygame.time.Clock()

    sound_manager.start_music()

    current_level = 1

    def spawn_level(lvl):
        env = Environment(GROUND_Y, level=lvl)
        if lvl == 1:
            # Aparecer en la plataforma más alta central (x=770, y=GROUND_Y - 370 - CHAR_HEIGHT) con 5 vidas
            highest_x = 770
            highest_y = (GROUND_Y - 370) - CHAR_HEIGHT
            ply = Player(highest_x, GROUND_Y, start_y=highest_y, max_health=5)
            
            # Enemigos Nivel 1 (variados en suelo y plataformas con salto y persecución)
            enemies = [
                PngEnemy(x=260, ground_y=GROUND_Y, sprite_name="enemigo.png", speed=2.3, jump_power=-11.0, sight_range=360),
                PngEnemy(x=480, ground_y=GROUND_Y, sprite_name="caca enemigo.png", speed=2.5, jump_power=-11.3, sight_range=380),
                PngEnemy(x=700, ground_y=GROUND_Y, sprite_name="enemigo.png", speed=2.4, jump_power=-11.0, sight_range=360),
                PngEnemy(x=880, ground_y=GROUND_Y, sprite_name="caca enemigo.png", speed=2.6, jump_power=-11.4, sight_range=400),
                PngEnemy(x=1050, ground_y=GROUND_Y, sprite_name="enemigo.png", speed=2.4, jump_power=-11.0, sight_range=370),
                PngEnemy(x=1220, ground_y=GROUND_Y, sprite_name="caca enemigo.png", speed=2.7, jump_power=-11.6, sight_range=410),
                PngEnemy(x=1380, ground_y=GROUND_Y, sprite_name="enemigo.png", speed=2.5, jump_power=-11.2, sight_range=390),
                # Enemigos patrullando en plataformas intermedias
                PngEnemy(x=430, ground_y=GROUND_Y - 210, sprite_name="caca enemigo.png", speed=2.2, jump_power=-10.8, sight_range=340),
                PngEnemy(x=1050, ground_y=GROUND_Y - 180, sprite_name="enemigo.png", speed=2.3, jump_power=-10.9, sight_range=350),
            ]
        else:
            # Nivel 2: Comienza en el sector izquierdo con 2 vidas adicionales (7 vidas en total)
            start_x = 100
            start_y = (GROUND_Y - 85) - CHAR_HEIGHT
            ply = Player(start_x, GROUND_Y, start_y=start_y, max_health=7)

            # Enemigos Nivel 2: Mayor desafío (10 enemigos ágiles protegiendo el nuevo mapa y la llave dorada)
            enemies = [
                PngEnemy(x=240, ground_y=GROUND_Y, sprite_name="caca enemigo.png", speed=2.7, jump_power=-11.6, sight_range=400),
                PngEnemy(x=440, ground_y=GROUND_Y, sprite_name="enemigo.png", speed=2.6, jump_power=-11.5, sight_range=380),
                PngEnemy(x=620, ground_y=GROUND_Y, sprite_name="caca enemigo.png", speed=2.8, jump_power=-11.8, sight_range=420),
                PngEnemy(x=800, ground_y=GROUND_Y, sprite_name="enemigo.png", speed=2.7, jump_power=-11.6, sight_range=390),
                PngEnemy(x=980, ground_y=GROUND_Y, sprite_name="caca enemigo.png", speed=2.9, jump_power=-12.0, sight_range=430),
                PngEnemy(x=1160, ground_y=GROUND_Y, sprite_name="enemigo.png", speed=2.7, jump_power=-11.6, sight_range=400),
                PngEnemy(x=1360, ground_y=GROUND_Y, sprite_name="caca enemigo.png", speed=2.8, jump_power=-11.8, sight_range=420),
                # Enemigos en las nuevas terrazas y plataformas del Nivel 2
                PngEnemy(x=470, ground_y=GROUND_Y - 210, sprite_name="enemigo.png", speed=2.5, jump_power=-11.2, sight_range=360),
                PngEnemy(x=790, ground_y=GROUND_Y - 355, sprite_name="caca enemigo.png", speed=2.6, jump_power=-11.4, sight_range=380),
                PngEnemy(x=1240, ground_y=GROUND_Y - 280, sprite_name="enemigo.png", speed=2.6, jump_power=-11.5, sight_range=390),
            ]
        return env, ply, enemies
        return env, ply, enemies

    environment, player, enemies = spawn_level(current_level)
    hud = HUD(WIDTH)

    start_time = pygame.time.get_ticks()
    running = True
    game_won = False
    level_transition_timer = 0

    while running:
        time_sec = (pygame.time.get_ticks() - start_time) / 1000.0

        all_enemies_defeated = len(enemies) > 0 and all(not e.alive for e in enemies)

        # LÓGICA DE NIVEL 1:
        if current_level == 1:
            # El portal rosa SOLO se activa y funciona cuando derrotas a todos los enemigos
            environment.portal.active = all_enemies_defeated

            # Al cruzar el portal rosa activo -> Pasar al Nivel 2
            if environment.portal.collides_with(player):
                sound_manager.play_coin()
                current_level = 2
                environment, player, enemies = spawn_level(2)
                level_transition_timer = 90 # 1.5 seg de aviso en pantalla
        
        # LÓGICA DE NIVEL 2:
        elif current_level == 2:
            key_collected = environment.key.collected if environment.key else False
            # Para ganar todo el juego: Matar a todos los enemigos Y encontrar la llave rosa con dorado
            if not game_won and all_enemies_defeated and key_collected:
                game_won = True
                sound_manager.play_coin()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_m:
                    sound_manager.toggle_mute()
                elif event.key == pygame.K_e and player.health > 0 and not game_won:
                    player.trigger_attack()
                elif (event.key == pygame.K_r or event.key == pygame.K_SPACE) and (player.health <= 0 or game_won):
                    current_level = 1
                    environment, player, enemies = spawn_level(1)
                    game_won = False

        keys = pygame.key.get_pressed()

        # Solo actualizar movimiento del jugador y física si sigue vivo y no ha ganado
        if player.health > 0 and not game_won:
            environment.update(player)
            for enemy in enemies:
                enemy.update(player, environment.pipes, environment.blocks)
            player.update(keys, environment.blocks, environment.pipes, environment.coins, enemies)

        # Renderizado del escenario ampliado
        environment.draw(screen, time_sec)
        
        # Dibujar enemigos
        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        # HUD con indicador de Nivel y Estado de la Llave
        is_key_done = environment.key.collected if (current_level == 2 and environment.key) else False
        hud.draw(screen, player.coins_collected, player.health, player.max_health, current_level=current_level, key_collected=is_key_done)

        # Banner de transición de nivel al pasar por el portal
        if level_transition_timer > 0:
            level_transition_timer -= 1
            font_trans = pygame.font.SysFont("comicsansms", 36, bold=True)
            txt_trans = font_trans.render("¡BIENVENIDO AL NIVEL 2!", True, (255, 60, 150))
            sub_trans = pygame.font.SysFont("comicsansms", 20, bold=True).render("¡Derrota a todos los enemigos y encuentra la Llave Rosa con Dorado!", True, (120, 60, 110))
            
            box_w, box_h = 760, 100
            box_x = (WIDTH - box_w) // 2
            box_y = 120
            bg_panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
            pygame.draw.rect(bg_panel, (255, 255, 255, 235), bg_panel.get_rect(), border_radius=20)
            pygame.draw.rect(bg_panel, (255, 130, 190), bg_panel.get_rect(), width=3, border_radius=20)
            screen.blit(bg_panel, (box_x, box_y))
            screen.blit(txt_trans, (box_x + (box_w - txt_trans.get_width()) // 2, box_y + 12))
            screen.blit(sub_trans, (box_x + (box_w - sub_trans.get_width()) // 2, box_y + 60))

        # 1. Si el jugador perdió todas sus vidas: Game Over
        if player.health <= 0:
            hud.draw_game_over(screen, time_sec)
        # 2. Si completó el Nivel 2 (enemigos + llave): Sale el Unicornio diciendo ¡GANASTE TODO EL JUEGO!
        elif game_won:
            hud.draw_victory(screen, time_sec)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
