import pygame
import random
import math
import sys

pygame.init()


SPRITE_WIDTH = 100
SPRITE_HEIGHT = 146

player_sprite_scale = 0.6
# --------------------------------------------------------------------

# Clase para manejar la hoja de sprites
class SpriteSheet:
    def __init__(self, filename):
        try:
            # Carga la hoja de sprites completa
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"No se pudo cargar la hoja de sprites: {filename}")
            raise SystemExit(e)

    def get_image(self, row, col, width, height, scale):
        # Crea una superficie en blanco para el sprite individual
        image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Copia la porción de la hoja de sprites que corresponde al sprite deseado
        image.blit(self.sheet, (0, 0), (col * width, row * height, width, height))
        # Escala el sprite al tamaño deseado
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)
        image = pygame.transform.scale(image, (scaled_width, scaled_height))
        return image


pygame.mixer.init()
pygame.mixer.music.load("Sonido.mp3")
pygame.mixer.music.play(-1)

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EndZone")
clock = pygame.time.Clock()

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 140, 0)
LIGHT_ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 200, 0)
DARK_RED = (150, 0, 0)
DARK_GREEN = (0, 150, 0)
DARK_BLUE = (0, 0, 150)
GRAY = (100, 100, 100)

button_font = pygame.font.SysFont("Arial", 25)
info_font = pygame.font.SysFont("Arial", 20)

def cargar_imagen_ruta(ruta, ancho_objetivo, alto_objetivo):
    try:
        imagen = pygame.image.load(ruta).convert_alpha()
        original_ancho, original_alto = imagen.get_size()
        if ruta == "Fondo.png":
            imagen_redimensionada = pygame.transform.scale(imagen, (ancho_objetivo, alto_objetivo))
        else:
            ratio = min(ancho_objetivo / original_ancho, alto_objetivo / original_alto)
            nuevo_ancho = int(original_ancho * ratio)
            nuevo_alto = int(original_alto * ratio)
            imagen_redimensionada = pygame.transform.smoothscale(imagen, (nuevo_ancho, nuevo_alto))
        return imagen_redimensionada
    except pygame.error as e:
        print(f"Error al cargar la imagen: {ruta}")
        raise SystemExit(e)

# Carga de animaciones del personaje desde la hoja de sprites
character_sheet = SpriteSheet('Jefe_Maestro_3.jpg')
animations = {
    'walk_up': [character_sheet.get_image(0, i, SPRITE_WIDTH, SPRITE_HEIGHT, player_sprite_scale) for i in range(4)],
    'walk_left': [character_sheet.get_image(1, i, SPRITE_WIDTH, SPRITE_HEIGHT, player_sprite_scale) for i in range(4)],
    'walk_down': [character_sheet.get_image(2, i, SPRITE_WIDTH, SPRITE_HEIGHT, player_sprite_scale) for i in range(4)],
    'walk_right': [character_sheet.get_image(3, i, SPRITE_WIDTH, SPRITE_HEIGHT, player_sprite_scale) for i in range(4)],
}
animations['idle_down'] = [animations['walk_down'][0]]
animations['idle_up'] = [animations['walk_up'][0]]
animations['idle_left'] = [animations['walk_left'][0]]
animations['idle_right'] = [animations['walk_right'][0]]

# Carga imágenes (todas en la misma carpeta)
zombie_imgs = [cargar_imagen_ruta(f"Zombie{i}.png", 80, 80) for i in range(1, 16)]
proyectil_img = cargar_imagen_ruta("Proyectil.png", 20, 20)
proyectil_jefe_img = cargar_imagen_ruta("ProyectilZombie.png", 30, 30)

jefe_imgs = {
    1: cargar_imagen_ruta("JefeFinal1.png", 100, 100),
    2: cargar_imagen_ruta("JefeFinal2.png", 130, 130),
    3: cargar_imagen_ruta("JefeFinal3.png", 150, 150)
}

blood_stain_img = cargar_imagen_ruta("Sangre.png", 50, 50)
fondo_juego_img = cargar_imagen_ruta("Fondo.png", WIDTH, HEIGHT)
logotipo_img = cargar_imagen_ruta("Logotipo.png", 300, 300)

# --- IMÁGENES PARA ITEMS (DROPS) ---
medikit_img = cargar_imagen_ruta("medikit.png", 50, 50)
shield_img = cargar_imagen_ruta("chaleco.png", 50, 50)

# Variables de estado del juego
show_menu = True
run_game = False
show_instructions = False
show_level_selection = False
show_mode_selection = False
unlocked_levels = 1

menu_brasas = [{'x': random.randint(0, WIDTH), 'y': random.randint(0, HEIGHT), 'speed': random.uniform(0.2, 0.6)} for _ in range(60)]

def draw_button(text, x, y, w, h, base_color, hover_color, action=None, is_active=True):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    rect = pygame.Rect(x, y, w, h)
    is_hovered = rect.collidepoint(mouse)

    current_base_color = base_color if is_active else GRAY
    current_hover_color = hover_color if is_active else GRAY

    pygame.draw.rect(screen, WHITE, rect, border_radius=10)
    inner_rect = rect.inflate(-4, -4)
    pygame.draw.rect(screen, current_hover_color if is_hovered and is_active else current_base_color, inner_rect, border_radius=8)

    text_surf = button_font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

    if is_active and is_hovered and click[0] == 1 and action:
        pygame.time.wait(150)
        action()

def draw_health_bar(x, y, width, height, current_health, max_health, border_color, fill_color, back_color, label="", label_pos="above"):
    if label and label_pos == "above":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y - label_surf.get_height() - 5))

    back_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, back_color, back_rect)
    fill_width = 0
    if max_health > 0:
      fill_width = int(width * (current_health / max_health))
    fill_rect = pygame.Rect(x, y, fill_width, height)
    pygame.draw.rect(screen, fill_color, fill_rect)
    pygame.draw.rect(screen, border_color, back_rect, 2)

    if label and label_pos == "below":
        label_surf = info_font.render(label, True, WHITE)
        screen.blit(label_surf, (x, y + height + 5))

def draw_shield_bar(x, y, width, height, current_shield, max_shield, border_color, fill_color, back_color):
    back_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(screen, back_color, back_rect)
    fill_width = 0
    if max_shield > 0:
        fill_width = int(width * (current_shield / max_shield))
    fill_rect = pygame.Rect(x, y, fill_width, height)
    pygame.draw.rect(screen, fill_color, fill_rect)
    pygame.draw.rect(screen, border_color, back_rect, 2)

def draw_brasas(brazas):
    for b in brazas:
        b['y'] += b['speed']
        if b['y'] > HEIGHT:
            b['y'] = 0
            b['x'] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, DARK_GREEN, (int(b['x']), int(b['y'])), 2)

def mostrar_pantalla_info(titulo, descripcion, volver_a_menu=False):
    esperando = True
    titulo_font = pygame.font.SysFont("Arial Black", 36)
    descripcion_font = pygame.font.SysFont("Arial", 24)
    instruccion_font = pygame.font.SysFont("Arial", 20)
    while esperando:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)
        panel_rect = pygame.Surface((600, 300), pygame.SRCALPHA)
        panel_rect.fill((0, 0, 0, 180))
        screen.blit(panel_rect, (WIDTH // 2 - 300, HEIGHT // 2 - 150))
        titulo_surf = titulo_font.render(titulo, True, ORANGE if "¡Has muerto!" not in titulo else RED)
        screen.blit(titulo_surf, (WIDTH // 2 - titulo_surf.get_width() // 2, HEIGHT // 2 - 130))
        lineas = descripcion.split("\n")
        for i, linea in enumerate(lineas):
            texto_surf = descripcion_font.render(linea, True, WHITE)
            screen.blit(texto_surf, (WIDTH // 2 - texto_surf.get_width() // 2, HEIGHT // 2 - 60 + i * 35))
        instruccion_text = "Presiona ENTER para continuar..."
        if volver_a_menu:
            instruccion_text = "Presiona ENTER para volver al menú..."
        instruccion = instruccion_font.render(instruccion_text, True, CYAN)
        screen.blit(instruccion, (WIDTH // 2 - instruccion.get_width() // 2, HEIGHT // 2 + 100))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                esperando = False

def mostrar_historia(nivel):
    historias = {
        1: ("UNA INFECCIÓN RARA Y PELIGROSA", "Un virus desconocido comenzó a propagarse entre la población.\nLos infectados ya no eran humanos..."),
        2: ("CIUDADES EN RUINAS", "La infección se ha extendido. Las ciudades han caído.\nPocos quedan en pie..."),
        3: ("ÚLTIMA RESISTENCIA", "Esta es tu última oportunidad.\nAcaba con el brote antes de que el mundo desaparezca.")
    }
    if nivel in historias:
        titulo, descripcion = historias[nivel]
        mostrar_pantalla_info(titulo, descripcion)

def infinite_mode_loop():
    global run_game, show_menu, show_mode_selection

    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_radius = 25
    player_speed = 4
    player_health = 100
    player_max_health = 100
    player_shield = 50
    player_max_shield = 100
    score = 0

    projectiles = []
    projectile_speed = 7
    shoot_delay = 400
    last_shot_time = pygame.time.get_ticks()

    enemies = []
    enemy_base_speed = 1.5
    enemy_spawn_delay = 2000
    last_enemy_spawn = pygame.time.get_ticks()

    pickups = []
    MEDIKIT_CHANCE = 0.08
    SHIELD_CHANCE = 0.10

    blood_stains = []
    player_action = 'idle'
    player_direction = 'down'
    frame_index = 0
    animation_speed = 0.2

    start_time = pygame.time.get_ticks()
    running = True

    while running:
        clock.tick(60)
        screen.blit(fondo_juego_img, (0, 0))

        for stain in blood_stains[:]:
            stain_surface = blood_stain_img.copy()
            stain_surface.set_alpha(stain['alpha'])
            screen.blit(stain_surface, (stain['x'] - stain_surface.get_width() // 2, stain['y'] - stain_surface.get_height() // 2))
            stain['alpha'] -= 1
            if stain['alpha'] <= 0:
                blood_stains.remove(stain)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

        keys = pygame.key.get_pressed()
        is_moving = any([keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]])
        player_action = 'walk' if is_moving else 'idle'

        if keys[pygame.K_w]:
            player_pos[1] -= player_speed
            player_direction = 'up'
        if keys[pygame.K_s]:
            player_pos[1] += player_speed
            player_direction = 'down'
        if keys[pygame.K_a]:
            player_pos[0] -= player_speed
            player_direction = 'left'
        if keys[pygame.K_d]:
            player_pos[0] += player_speed
            player_direction = 'right'

        player_pos[0] = max(player_radius, min(player_pos[0], WIDTH - player_radius))
        player_pos[1] = max(player_radius, min(player_pos[1], HEIGHT - player_radius))

        animation_key = f"{player_action}_{player_direction}"
        if animation_key not in animations:
            animation_key = 'idle_down'
        frame_index += animation_speed
        current_animation_list = animations[animation_key]
        if frame_index >= len(current_animation_list):
            frame_index = 0
        current_player_img = current_animation_list[int(frame_index)]

        now = pygame.time.get_ticks()

        elapsed_seconds = (now - start_time) / 1000
        current_spawn_delay = max(300, enemy_spawn_delay - (elapsed_seconds // 15) * 100)
        current_enemy_speed = min(4.0, enemy_base_speed + (elapsed_seconds // 25) * 0.2)

        if now - last_shot_time >= shoot_delay:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx, dy = mouse_x - player_pos[0], mouse_y - player_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx, 'dy': dy})
            last_shot_time = now

        for p in projectiles[:]:
            p['x'] += p['dx'] * projectile_speed
            p['y'] += p['dy'] * projectile_speed
            if not (0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT):
                projectiles.remove(p)

        if now - last_enemy_spawn >= current_spawn_delay:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top': x, y = random.randint(0, WIDTH), -40
            elif side == 'bottom': x, y = random.randint(0, WIDTH), HEIGHT + 40
            elif side == 'left': x, y = -40, random.randint(0, HEIGHT)
            else: x, y = WIDTH + 40, random.randint(0, HEIGHT)
            enemy_img = random.choice(zombie_imgs)
            enemies.append({'x': x, 'y': y, 'speed': current_enemy_speed, 'img': enemy_img})
            last_enemy_spawn = now

        for enemy in enemies[:]:
            dx, dy = player_pos[0] - enemy['x'], player_pos[1] - enemy['y']
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            enemy['x'] += dx * enemy['speed']
            enemy['y'] += dy * enemy['speed']

            if math.hypot(enemy['x'] - player_pos[0], enemy['y'] - player_pos[1]) < 40:
                damage = 10
                if player_shield > 0:
                    player_shield = max(0, player_shield - damage)
                else:
                    player_health = max(0, player_health - damage)
                enemy['x'] -= dx * 20
                enemy['y'] -= dy * 20

            for p in projectiles[:]:
                if math.hypot(enemy['x'] - p['x'], enemy['y'] - p['y']) < 30:
                    if enemy in enemies:
                        blood_stains.append({'x': enemy['x'], 'y': enemy['y'], 'alpha': 255})
                        enemies.remove(enemy)
                        projectiles.remove(p)
                        score += 10

                        if random.random() < MEDIKIT_CHANCE:
                            pickups.append({'x': enemy['x'], 'y': enemy['y'], 'type': 'medikit', 'img': medikit_img})
                        elif random.random() < SHIELD_CHANCE:
                            pickups.append({'x': enemy['x'], 'y': enemy['y'], 'type': 'shield', 'img': shield_img})
                        break

        for item in pickups[:]:
            if math.hypot(item['x'] - player_pos[0], item['y'] - player_pos[1]) < 35:
                if item['type'] == 'medikit':
                    player_health = min(player_max_health, player_health + 25)
                elif item['type'] == 'shield':
                    player_shield = min(player_max_shield, player_shield + 40)
                pickups.remove(item)

        for item in pickups:
            screen.blit(item['img'], (item['x'] - item['img'].get_width() // 2, item['y'] - item['img'].get_height() // 2))

        player_rect = current_player_img.get_rect(center=tuple(player_pos))
        screen.blit(current_player_img, player_rect)

        for enemy in enemies:
            screen.blit(enemy['img'], (enemy['x'] - enemy['img'].get_width() // 2, enemy['y'] - enemy['img'].get_height() // 2))

        for p in projectiles:
            screen.blit(proyectil_img, (p['x'] - proyectil_img.get_width() // 2, p['y'] - proyectil_img.get_height() // 2))

        # HUD para Modo Infinito
        screen.blit(info_font.render(f"Puntuación: {score}", True, WHITE), (10, 10))
        draw_health_bar(10, HEIGHT - 70, 200, 25, player_health, player_max_health, WHITE, GREEN, DARK_RED)
        screen.blit(medikit_img, (10 + 200 + 5, HEIGHT - 70))
        draw_shield_bar(10, HEIGHT - 35, 200, 25, player_shield, player_max_shield, WHITE, CYAN, DARK_BLUE)
        screen.blit(shield_img, (10 + 200 + 5, HEIGHT - 35))

        if player_health <= 0:
            mostrar_pantalla_info("¡Has muerto!", f"Sobreviviste hasta alcanzar una puntuación de: {score}\n¡Inténtalo de nuevo!", volver_a_menu=True)
            running = False

        pygame.display.flip()

    run_game = False
    show_menu = True
    show_mode_selection = False

def game_loop(starting_level):
    global run_game, show_menu, show_level_selection, unlocked_levels

    player_pos = [WIDTH // 2, HEIGHT // 2]
    player_radius = 25
    base_speed = 4
    player_speed = base_speed
    player_health = 100
    player_max_health = 100
    player_xp = 0
    player_level = 1
    xp_to_next = 50
    nivel_actual = starting_level
    max_nivel = 3
    habilidad_actual = 1
    habilidad_nombres = {1: "Doble Tiro", 2: "Relentizador", 3: "Velocidad"}
    ralentizar_enemigos = False
    ralentizador_fin = 0
    projectiles = []
    projectile_speed = 7
    shoot_delay = 500
    last_shot_time = pygame.time.get_ticks()
    enemies = []
    enemy_base_speed = 1.5 + (starting_level - 1) * 0.5
    enemy_spawn_delay = 1500 - (starting_level - 1) * 200
    enemy_spawn_delay = max(400, enemy_spawn_delay)
    enemy_speed = enemy_base_speed
    last_enemy_spawn = pygame.time.get_ticks()
    jefe_activo = False
    jefe_pos = None
    jefe_vida = 0
    jefe_max_vida = 0
    jefe_danio = 0
    jefe_speed = 0
    jefe_proyectiles = []
    jefe_disparo_delay = 0
    ultimo_disparo_jefe = 0
    blood_stains = []
    player_action = 'idle'
    player_direction = 'down'
    frame_index = 0
    animation_speed = 0.2

    mostrar_historia(nivel_actual)
    running = True

    while running:
        clock.tick(60)
        screen.blit(fondo_juego_img, (0, 0))

        for stain in blood_stains[:]:
            stain_surface = blood_stain_img.copy()
            stain_surface.set_alpha(stain['alpha'])
            screen.blit(stain_surface, (stain['x'] - stain_surface.get_width() // 2, stain['y'] - stain_surface.get_height() // 2))
            stain['alpha'] -= 1
            if stain['alpha'] <= 0:
                blood_stains.remove(stain)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break

        keys = pygame.key.get_pressed()
        is_moving = any([keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d]])
        player_action = 'walk' if is_moving else 'idle'

        if keys[pygame.K_w]:
            player_pos[1] -= player_speed
            player_direction = 'up'
        if keys[pygame.K_s]:
            player_pos[1] += player_speed
            player_direction = 'down'
        if keys[pygame.K_a]:
            player_pos[0] -= player_speed
            player_direction = 'left'
        if keys[pygame.K_d]:
            player_pos[0] += player_speed
            player_direction = 'right'

        player_pos[0] = max(player_radius, min(player_pos[0], WIDTH - player_radius))
        player_pos[1] = max(player_radius, min(player_pos[1], HEIGHT - player_radius))

        animation_key = f"{player_action}_{player_direction}"
        if animation_key not in animations:
            animation_key = 'idle_down'

        frame_index += animation_speed
        current_animation_list = animations[animation_key]
        if frame_index >= len(current_animation_list):
            frame_index = 0
        current_player_img = current_animation_list[int(frame_index)]

        now = pygame.time.get_ticks()

        if now - last_shot_time >= shoot_delay:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - player_pos[0]
            dy = mouse_y - player_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx, 'dy': dy})
            if habilidad_actual == 1:
                offset = math.pi / 12
                cos_off = math.cos(offset)
                sin_off = math.sin(offset)
                dx1, dy1 = dx * cos_off - dy * sin_off, dx * sin_off + dy * cos_off
                dx2, dy2 = dx * cos_off + dy * sin_off, -dx * sin_off + dy * cos_off
                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx1, 'dy': dy1})
                projectiles.append({'x': player_pos[0], 'y': player_pos[1], 'dx': dx2, 'dy': dy2})
            last_shot_time = now

        for p in projectiles[:]:
            p['x'] += p['dx'] * projectile_speed
            p['y'] += p['dy'] * projectile_speed
            if not (0 <= p['x'] <= WIDTH and 0 <= p['y'] <= HEIGHT):
                projectiles.remove(p)

        if ralentizar_enemigos and now > ralentizador_fin:
            ralentizar_enemigos = False
            enemy_speed = enemy_base_speed

        if not jefe_activo and now - last_enemy_spawn >= enemy_spawn_delay:
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top': x, y = random.randint(0, WIDTH), 0
            elif side == 'bottom': x, y = random.randint(0, WIDTH), HEIGHT
            elif side == 'left': x, y = 0, random.randint(0, HEIGHT)
            else: x, y = WIDTH, random.randint(0, HEIGHT)
            enemy_img = random.choice(zombie_imgs)
            enemies.append({'x': x, 'y': y, 'speed': enemy_speed, 'img': enemy_img})
            last_enemy_spawn = now

        for enemy in enemies[:]:
            dx = player_pos[0] - enemy['x']
            dy = player_pos[1] - enemy['y']
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist
                dy /= dist
            enemy['x'] += dx * enemy['speed']
            enemy['y'] += dy * enemy['speed']

            if math.hypot(enemy['x'] - player_pos[0], enemy['y'] - player_pos[1]) < 40:
                player_health -= 1

            for p in projectiles[:]:
                if math.hypot(enemy['x'] - p['x'], enemy['y'] - p['y']) < 30:
                    if enemy in enemies:
                        blood_stains.append({'x': enemy['x'], 'y': enemy['y'], 'alpha': 255})
                        enemies.remove(enemy)
                        projectiles.remove(p)
                        player_xp += 20
                        if player_xp >= xp_to_next:
                            player_level += 1
                            player_xp = 0
                            xp_to_next += 25

                            if nivel_actual == 1 and player_level >= 5 and not jefe_activo:
                                jefe_activo, jefe_pos, jefe_vida, jefe_max_vida, jefe_speed, jefe_danio, jefe_disparo_delay = True, [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)], 8, 8, 2, 10, 1000
                                jefe_proyectiles.clear(); enemies.clear()
                            elif nivel_actual == 2 and player_level >= 6 and not jefe_activo:
                                jefe_activo, jefe_pos, jefe_vida, jefe_max_vida, jefe_speed, jefe_danio, jefe_disparo_delay = True, [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)], 15, 15, 3, 15, 800
                                jefe_proyectiles.clear(); enemies.clear()
                            elif nivel_actual == 3 and player_level >= 10 and not jefe_activo:
                                jefe_activo, jefe_pos, jefe_vida, jefe_max_vida, jefe_speed, jefe_danio, jefe_disparo_delay = True, [random.randint(100, WIDTH - 100), random.randint(100, HEIGHT - 100)], 25, 25, 4, 20, 300
                                jefe_proyectiles.clear(); enemies.clear()

                            if player_level == 2: habilidad_actual = 2
                            elif player_level == 3: habilidad_actual = 3

        if jefe_activo:
            dx, dy = player_pos[0] - jefe_pos[0], player_pos[1] - jefe_pos[1]
            dist = math.hypot(dx, dy)
            if dist != 0:
                dx /= dist; dy /= dist
            jefe_pos[0] += dx * jefe_speed; jefe_pos[1] += dy * jefe_speed

            if now - ultimo_disparo_jefe >= jefe_disparo_delay:
                jdx, jdy = player_pos[0] - jefe_pos[0], player_pos[1] - jefe_pos[1]
                dist = math.hypot(jdx, jdy)
                if dist != 0:
                    jdx /= dist; jdy /= dist
                jefe_proyectiles.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'dx': jdx, 'dy': jdy})
                ultimo_disparo_jefe = now

            for j in jefe_proyectiles[:]:
                j['x'] += j['dx'] * 5; j['y'] += j['dy'] * 5
                if not (0 <= j['x'] <= WIDTH and 0 <= j['y'] <= HEIGHT):
                    jefe_proyectiles.remove(j)
                elif math.hypot(j['x'] - player_pos[0], j['y'] - player_pos[1]) < player_radius:
                    player_health -= jefe_danio
                    jefe_proyectiles.remove(j)

            if math.hypot(jefe_pos[0] - player_pos[0], jefe_pos[1] - player_pos[1]) < player_radius + 25:
                player_health -= jefe_danio // 2

            for p in projectiles[:]:
                if math.hypot(jefe_pos[0] - p['x'], jefe_pos[1] - p['y']) < 30:
                    jefe_vida -= 1
                    projectiles.remove(p)

            if jefe_vida <= 0:
                blood_stains.append({'x': jefe_pos[0], 'y': jefe_pos[1], 'alpha': 255})
                jefe_activo = False
                jefe_proyectiles.clear()
                if nivel_actual < max_nivel:
                    unlocked_levels = max(unlocked_levels, nivel_actual + 1)
                    mostrar_pantalla_info(f"¡Nivel {nivel_actual} Completado!", "Has derrotado al jefe.\n¡Prepárate para la siguiente!", volver_a_menu=True)
                    running = False
                else:
                    mostrar_pantalla_info("¡HAS GANADO!", "El brote ha sido contenido.\nLa humanidad tiene una segunda oportunidad.", volver_a_menu=True)
                    running = False
                ralentizar_enemigos = False

        if habilidad_actual == 2 and not ralentizar_enemigos and player_level >= 2:
            if keys[pygame.K_SPACE]:
                ralentizar_enemigos = True
                enemy_speed = enemy_base_speed / 2.5
                ralentizador_fin = now + 5000

        if habilidad_actual == 3: player_speed = base_speed * 1.8
        elif habilidad_actual == 1 or habilidad_actual == 2: player_speed = base_speed

        player_rect = current_player_img.get_rect(center=tuple(player_pos))
        screen.blit(current_player_img, player_rect)
        for enemy in enemies:
            screen.blit(enemy['img'], (enemy['x'] - enemy['img'].get_width() // 2, enemy['y'] - enemy['img'].get_height() // 2))
        for p in projectiles:
            screen.blit(proyectil_img, (p['x'] - proyectil_img.get_width() // 2, p['y'] - proyectil_img.get_height() // 2))

        if jefe_activo:
            jefe_img = jefe_imgs.get(nivel_actual)
            if jefe_img:
                screen.blit(jefe_img, (int(jefe_pos[0] - jefe_img.get_width() // 2), int(jefe_pos[1] - jefe_img.get_height() // 2)))
            for j in jefe_proyectiles:
                screen.blit(proyectil_jefe_img, (int(j['x'] - proyectil_jefe_img.get_width() // 2), int(j['y'] - proyectil_jefe_img.get_height() // 2)))

        # HUD para Modo Campaña
        screen.blit(info_font.render(f"Nivel: {player_level}", True, WHITE), (10, 10))
        screen.blit(info_font.render(f"XP: {player_xp}/{xp_to_next}", True, WHITE), (10, 35))
        screen.blit(info_font.render(f"Fase: {nivel_actual}", True, WHITE), (10, 60))
        screen.blit(info_font.render(f"Habilidad: {habilidad_nombres[habilidad_actual]}", True, WHITE), (10, 85))

        if habilidad_actual == 2 and ralentizar_enemigos:
            tiempo_restante = (ralentizador_fin - now) / 1000
            screen.blit(info_font.render(f"Ralentizador activo: {tiempo_restante:.1f}s", True, WHITE), (10, 110))

        draw_health_bar(10, HEIGHT - 35, 200, 25, player_health, player_max_health, WHITE, GREEN, DARK_RED, "Barra de salud de Kenner", "above")

        if jefe_activo:
            jefe_labels = {1: "Portador", 2: "Acechador", 3: "Susurrador"}
            jefe_label_text = f"Salud del {jefe_labels.get(nivel_actual, 'Jefe')}"
            draw_health_bar(WIDTH - 260, 50, 250, 25, jefe_vida, jefe_max_vida, WHITE, RED, DARK_RED, jefe_label_text, "below")

        if player_health <= 0:
            mostrar_pantalla_info("¡Has muerto!", "La infección ha consumido el mundo.\nNo hay esperanza...", volver_a_menu=True)
            running = False

        pygame.display.flip()

    run_game = False
    show_menu = False
    show_level_selection = True

def start_level(level):
    global run_game, show_level_selection, show_mode_selection
    show_level_selection = False
    show_mode_selection = False
    run_game = True
    game_loop(level)

def start_infinite_mode():
    global run_game, show_mode_selection
    show_mode_selection = False
    run_game = True
    infinite_mode_loop()

def show_level_selection_screen():
    global show_menu, show_level_selection, show_mode_selection
    show_menu = False
    show_mode_selection = False
    show_level_selection = True

def show_mode_selection_screen():
    global show_menu, show_mode_selection
    show_menu = False
    show_mode_selection = True

def mode_selection_menu():
    global show_menu, show_mode_selection

    mode_menu_running = True
    while mode_menu_running:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)

        title_font = pygame.font.SysFont("Arial Black", 40)
        title_surf = title_font.render("Selecciona un Modo de Juego", True, ORANGE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 150))

        draw_button("Modo Campaña", WIDTH // 2 - 125, 250, 250, 50, ORANGE, LIGHT_ORANGE, show_level_selection_screen)
        draw_button("Modo Infinito", WIDTH // 2 - 125, 320, 250, 50, CYAN, (0, 200, 200), start_infinite_mode)

        def return_to_main_menu():
            nonlocal mode_menu_running
            mode_menu_running = False
            global show_mode_selection, show_menu
            show_mode_selection = False
            show_menu = True

        draw_button("Volver", WIDTH // 2 - 125, 420, 250, 50, GRAY, (150, 150, 150), return_to_main_menu)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not show_mode_selection:
            mode_menu_running = False

        pygame.display.flip()

def exit_game():
    pygame.quit()
    sys.exit()

def show_instructions_screen():
    global show_menu, show_instructions
    show_instructions = True
    show_menu = False

def level_selection_menu():
    global show_menu, show_level_selection, unlocked_levels

    level_menu_running = True
    while level_menu_running:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)

        title_font = pygame.font.SysFont("Arial Black", 40)
        title_surf = title_font.render("Selecciona un Nivel", True, ORANGE)
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 70))

        button_y_start = HEIGHT // 2 - 100
        button_height = 50
        button_spacing = 70

        for i in range(1, 4):
            level_text = f"Nivel {i}"
            is_level_unlocked = (i <= unlocked_levels)
            action = (lambda lvl=i: start_level(lvl)) if is_level_unlocked else None
            draw_button(level_text, WIDTH // 2 - 100, button_y_start + (i - 1) * button_spacing, 200, button_height, ORANGE, LIGHT_ORANGE, action, is_active=is_level_unlocked)

        def return_to_mode_selection():
            nonlocal level_menu_running
            global show_level_selection, show_mode_selection
            level_menu_running = False
            show_level_selection = False
            show_mode_selection = True

        draw_button("Volver", WIDTH // 2 - 100, button_y_start + 3 * button_spacing, 200, button_height, CYAN, (0, 200, 200), return_to_mode_selection)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if not show_level_selection:
            level_menu_running = False

        pygame.display.flip()

# Bucle principal
while True:
    clock.tick(60)

    if show_menu:
        screen.fill(BLACK)
        draw_brasas(menu_brasas)
        screen.blit(logotipo_img, (WIDTH // 2 - logotipo_img.get_width() // 2, 40))
        draw_button("Iniciar", WIDTH // 2 - 100, 360, 200, 50, ORANGE, LIGHT_ORANGE, show_mode_selection_screen)
        draw_button("Instrucciones", WIDTH // 2 - 100, 430, 200, 50, ORANGE, LIGHT_ORANGE, show_instructions_screen)
        draw_button("Salir", WIDTH // 2 - 100, 500, 200, 50, ORANGE, LIGHT_ORANGE, exit_game)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        pygame.display.flip()

    elif show_instructions:
        mostrar_pantalla_info(
            "INSTRUCCIONES",
            "Muévete con W A S D\n"
            "Apunta con el ratón y dispara automáticamente\n"
            "Presiona ESPACIO para usar la habilidad (Modo Campaña)\n"
            "Presiona ESCAPE para salir de la partida\n"
            "¡Sobrevive y derrota a los jefes!",
            volver_a_menu=True
        )
        show_instructions = False
        show_menu = True

    elif show_mode_selection:
        mode_selection_menu()

    elif show_level_selection:
        level_selection_menu()

    elif run_game:
        # Los bucles de juego se manejan dentro de sus propias funciones.
        # Esta rama se deja vacía intencionadamente.
        pass