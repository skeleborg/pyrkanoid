# -*- coding: utf-8 -*-

# Pygame
from pygame import *
import pygame.locals

# Implícitos
import sys
import random

# Propios
import sprite_factory
import powerups
import levels.level_factory as level_factory

# FUENTE SPRITE SHEETS: http://www.spriters-resource.com/nes/arkanoid/

# Inicializa los módulos de Pygame
pygame.init()

# ANCHO Y ALTO DE LA VENTANA
FRAME_WIDTH = 448  # FIELD_WIDTH * 2
FRAME_HEIGHT = 530  # FIELD_HEIGHT * 2 + SCORE_AREA_HEIGHT

# ALTO DEL PANEL PARA PUNTUACIONES
SCORE_AREA_HEIGHT = 50
SCORE = 0

# ANCHOS Y ALTOS DEL SPRITE PARA EL MARCO DEL ESCENARIO
FIELD_WIDTH = 224
FIELD_HEIGHT = 240
FIELD_BORDER = 16  # El doble del original, ya que va a estar reescalado

# Frames de las animaciones de los sprites que las tengan
block_sprite_frames = 6
powerup_sprite_frames = 8

# Controls checker
moving_left = False
moving_right = False
moving_bola = False

# Vidas por defecto
lives = 3

# Crear ventana
window = pygame.display.set_mode([FRAME_WIDTH, FRAME_HEIGHT])
pygame.display.set_caption('Arkanoid')
clock = pygame.time.Clock()

# Crear panel para puntuaciones
score_font = pygame.font.Font('./lib/fonts/VT323-Regular.ttf', 28)

# Pruebas de rendimiento
fps_font = pygame.font.Font('./lib/fonts/VT323-Regular.ttf', 28)

# Añadimos el escenario (224x240 POR DEFECTO, el ancho y alto reescalado se definen en FIELD_WIDTH y FIELD_HEIGHT)
field_sheet = pygame.image.load('./lib/img/fields.png')
# Superficie a extraer de la sprite sheet
field_sheet.set_clip(pygame.Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT))
# Sustituimos la imagen entera por la sección (subsuperficie) generada
field_sheet_set_area = field_sheet.subsurface(field_sheet.get_clip())
field_area = pygame.transform.scale(field_sheet_set_area, (FRAME_WIDTH, FRAME_HEIGHT - SCORE_AREA_HEIGHT))

# CREAMOS LOS SPRITES A PARTIR DE UN MÓDULO GENÉRICO EN sprite_factory.py
# Sprite sheets
vaus_sprite_sheet = image.load('./lib/img/vaus.png').convert_alpha()
# blocks_sprite_sheet = image.load('./lib/img/blocks_backgrounds.png').convert_alpha()
fields_sprite_sheet = image.load('./lib/img/fields.png').convert_alpha()

# Añadimos la nave
vaus_image = transform.scale2x(vaus_sprite_sheet.subsurface((0, 0, 32, 8)))
vaus = sprite_factory.SpriteFactory(vaus_image, [5, 0])
vaus_single_group = pygame.sprite.GroupSingle()
vaus_single_group.add(vaus)

# Añadimos la bola
ball_image = transform.scale2x(vaus_sprite_sheet.subsurface((40, 0, 5, 4)))
ball = sprite_factory.SpriteFactory(ball_image, [5, -5])
ball.moving = False
ball_group = pygame.sprite.Group()
ball_group.add(ball)

# Sprite para cada vida. Empezamos con tres
life_image = transform.scale2x(fields_sprite_sheet.subsurface((8, 239, 17, 9)))
lives_group = pygame.sprite.Group()

# Otros grupos (bloques, powerups, balas...)
block_group = level_factory.LevelFactory(13, 10, FIELD_WIDTH, SCORE_AREA_HEIGHT, FIELD_BORDER).add_sprites()
powerup_single_group = pygame.sprite.GroupSingle()
bullet_group = pygame.sprite.Group()  # Cada sprite será el recuadro entero que engloba las dos balas.


# Se restablecen valores por defecto y se (re)inicializa el juego
def new_game():
    vaus.rect.center = (FRAME_WIDTH / 2, FRAME_HEIGHT - 50)
    # Si había más de una bola antes en el grupo, se limpia el grupo y se añade una sola
    if len(ball_group) > 1:
        ball_group.empty()
        ball_group.add(ball)

    ball.rect.center = (vaus.rect.centerx + ball.rect.width, vaus.rect.top - ball.rect.height)


# sprite_group: grupo de sprites que colisiona con los bloques
# block_group: grupo de sprites que contiene los bloques
# Función genérica para colisiones entre bola-bloque y bala-bloque
def generate_powerup():
    probability = random.randint(0, 100)
    # probability <= 50 and
    if collided_block.sprite_type != ('SV' and 'GD') and len(powerup_single_group) == 0:
        powerup_sprite_sheet = transform.scale2x(image.load('./lib/img/powerups.png').subsurface(
            powerups.powerups_dict[collided_block.sprite_type][0]))
        powerup_image = powerup_sprite_sheet.subsurface(0, 0, 32, 14)
        powerup = sprite_factory.SpriteFactory(powerup_image, [0, 2],
                                               powerups.powerups_dict[collided_block.sprite_type][1],
                                               powerup_sprite_sheet, 8)
        powerup.rect.center = collided_block.rect.center
        powerup_single_group.add(powerup)

new_game()

# BUCLE PRINCIPAL DEL JUEGO
while True:

    window.fill(pygame.Color("black"))
    # Posibles entradas del teclado y mouse
    for event in pygame.event.get():
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            moving_left = True
        if keys[pygame.K_RIGHT]:
            moving_right = True

        # Movimiento inicial para empezar a acelerar la bola
        if keys[pygame.K_SPACE]:
            for ball in ball_group:
                if not ball.moving:
                    ball.moving = True
            # DISPARAR
            if hasattr(vaus, 'shoot') and vaus.shoot:
                bullet = sprite_factory.SpriteFactory(vaus_sprite_sheet.subsurface((40, 17, 16, 6)), [0, -5])
                bullet.rect.center = (vaus.rect.centerx, vaus.rect.top)
                bullet_group.add(bullet)

        if event.type == pygame.KEYUP:
            moving_left = False
            moving_right = False

        # DETENER JUEGO
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # CONTROLES
    if moving_left and vaus.rect.left >= FIELD_BORDER and not hasattr(vaus, 'surfaces'):
        if not ('surfaces' in locals()):
            vaus.update(-vaus.vel[0], 0)
        elif 'surfaces' in locals():
            vaus.update(-vaus.vel[0], 0, surfaces)
        # Si la bola sigue en el estado inicial, se mueve con la nave, ya que está "posada"
        for ball in ball_group:
            if not ball.moving:
                ball.update(-vaus.vel[0], 0)

    if moving_right and vaus.rect.right <= FRAME_WIDTH - FIELD_BORDER:
        if not ('surfaces' in locals()):
            vaus.update(vaus.vel[0], 0)
        elif 'surfaces' in locals():
            vaus.update(vaus.vel[0], 0, surfaces)
        for ball in ball_group:
            if not ball.moving:
                ball.update(vaus.vel[0], 0)

    for ball in ball_group:
        if ball.moving:
            if ball.rect.right >= FRAME_WIDTH - FIELD_BORDER or ball.rect.left <= FIELD_BORDER:
                ball.vel[0] *= -1
            if ball.rect.top <= SCORE_AREA_HEIGHT + FIELD_BORDER:
                ball.vel[1] *= -1
            if ball.rect.bottom >= FRAME_HEIGHT and len(ball_group) == 1:
                # Se resta una vida y se restablecen los estados de los sprites nave y bola
                lives_group.empty()
                ball.moving = False
                # surfaces = []
                lives -= 1
                if lives == 0:
                    # TODO MOSTRAR MENSAJE DE "FIN DEL JUEGO" EN PANTALLA Y FINALIZAR EL JUEGO
                    print("FIN DEL JUEGO")
                new_game()
            elif ball.rect.bottom >= FRAME_HEIGHT and len(ball_group) > 1:
                ball.kill()
            ball.update(ball.vel[0], ball.vel[1])

    # COLISIONES
    # Recordemos que "bola" pertenece a un grupo de sprites, por lo que habrá que comprobar antes que el elemento
    # encontrado es del tipo "Bola".
    # Si hay más de una, habrá que calcular las colisiones por cada una de ellas.

    for ball in ball_group:
        if pygame.sprite.collide_rect(vaus, ball) and not hasattr(vaus, 'sticky'):
            # Si la bola choca contra el borde derecho o izquierdo de vaus se va a comportar de forma extraña
            # Cubrimos esa posibilidad con una condición nueva
            # TODO REVISAR. PARECE QUE EN EL TOPLEFT Y TOPRIGHT DE VAUS SIGUE SIN FUNCIONAR

            if ((vaus.rect.topleft[1] <= ball.rect.bottomright[1] and vaus.rect.bottomleft[1] >= ball.rect.topright[1])\
                    or (vaus.rect.topright[1] <= ball.rect.bottomleft[1] and vaus.rect.bottomright[1] >= ball.rect.topleft[1])) \
                    and vaus.rect.y < ball.rect.y:
                print("Choque lateral")
                ball.vel[0] *= -1
                ball.vel[1] *= -1
            else:
                ball.vel[1] *= -1
        elif pygame.sprite.collide_rect(vaus, ball) and hasattr(vaus, 'sticky'):
            ball.moving = False
            ball.rect.y = vaus.rect.top - ball.rect.height
            ball.vel[1] *= -1

    # COMPORTAMIENTO AL DESTRUIR BLOQUES. GENERAR POWERUPS AL DESTRUIR BLOQUES.
    if len(pygame.sprite.groupcollide(ball_group, block_group, False, False)) > 0:
        # No vamos a dejar que el sprite del grupo de bloques desaparezca, ya que habrá que analizar primero
        # los distintos casos que pueden darse.
        # El resultado de esta sentencia genera un diccionario con el sprite del primer grupo como clave, y el/los
        # sprites del segundo grupo implicados en la colisión como valores; por ello, si hay una colisión se llena
        # el diccionario, y procedemos a generar el código consecuente en función de lo que necesitemos hacer.
        # print(pygame.sprite.groupcollide(ball_group, block_group, False, False))
        collision = pygame.sprite.groupcollide(ball_group, block_group, False, False)
        for ball_collided, block_sprite in collision.items():
            collided_block = block_sprite.pop()
            collided_block_type = collided_block.sprite_type
            if not collided_block.breakable:
                collided_block.animate = True
            if collided_block_type == 'SV' and not collided_block.breakable:
                collided_block.breakable = True
            elif collided_block.breakable:
                collided_block.kill()
                SCORE += 10
                if not collided_block_type == 'SV':
                    generate_powerup()
            # TODO ARREGLAR CAMBIO TRAYECTORIA BOLA
            if ((collided_block.rect.topleft[1] <= ball.rect.bottomright[1] and collided_block.rect.bottomleft[1] >= ball.rect.topright[1])\
                    or (collided_block.rect.topright[1] <= ball.rect.bottomleft[1] and collided_block.rect.bottomright[1] >= ball.rect.topleft[1])) \
                    and collided_block.rect.y < ball.rect.y:
                ball_collided.vel[0] *= -1
            else:
                ball_collided.vel[1] *= -1

    # COMPORTAMIENTO VAUS AL COLISIONAR CON DETERMINADO POWERUP.
    if pygame.sprite.groupcollide(vaus_single_group, powerup_single_group, False, False):
        # TODO CAMBIAR ESTADO DE VAUS O LA BOLA, AL ASOCIADO AL POWERUP CONTRA EL QUE COLISIONA
        if hasattr(vaus, 'shoot') and powerup_single_group.sprite.sprite_type != ('P', 'B', 'C', 'D'):
            vaus.shoot = False
        if hasattr(vaus, 'sticky') and powerup_single_group.sprite.sprite_type != ('P', 'C', 'D', 'E'):
            vaus.sticky = False
        if powerup_single_group.sprite.sprite_type == 'S':
            vaus.sticky = True
        elif powerup_single_group.sprite.sprite_type == 'C':
            pass
        elif powerup_single_group.sprite.sprite_type == 'L':
            vaus.animation_sheet = vaus_sprite_sheet
            surfaces = powerups.change_vaus_behavior('L', vaus)
        elif powerup_single_group.sprite.sprite_type == 'E':
            vaus.animation_sheet = vaus_sprite_sheet
            surfaces = powerups.change_vaus_behavior('E', vaus)
        elif powerup_single_group.sprite.sprite_type == 'D':
            pass
        elif powerup_single_group.sprite.sprite_type == 'B':
            while len(ball_group) < 4:
                ball_group.add(sprite_factory.SpriteFactory(ball_image, [-ball.vel[0], -ball.vel[1]]))
                for bola in ball_group:
                    bola.rect.center = (ball.rect.x, ball.rect.y)
                    bola.moving = True
        elif powerup_single_group.sprite.sprite_type == 'P':
            lives += 1
            lives_group.empty()
        powerup_single_group.empty()

    # ¡¡REDIBUJAR TODA LA ESCENA!!
    score_area = score_font.render("SCORE: " + str(SCORE), True, pygame.Color('white'))
    fps_area = fps_font.render("FPS: " + str(clock.get_fps()), True, pygame.Color('yellow'))
    window.blit(score_area, (10, SCORE_AREA_HEIGHT / 3))
    window.blit(field_area, (0, SCORE_AREA_HEIGHT))
    window.blit(fps_area, (150, SCORE_AREA_HEIGHT / 3))

    if vaus.animate:
        vaus.update(surfaces=surfaces)
    vaus_single_group.draw(window)

    if len(bullet_group) > 0:
        for bullet in bullet_group:
            bullet.update(bullet.vel[0], bullet.vel[1])
            if bullet.rect.top <= FIELD_HEIGHT:
                bullet.kill()
            if pygame.sprite.groupcollide(bullet_group, block_group, False, False):
                collision = pygame.sprite.groupcollide(bullet_group, block_group, False, False)
                for collided_bullet, block_sprite in collision.items():
                    collided_block = block_sprite.pop()
                    collided_block_type = collided_block.sprite_type
                    if not collided_block.breakable:
                        collided_block.animate = True
                    if collided_block_type == 'SV' and not collided_block.breakable:
                        collided_block.breakable = True
                    elif collided_block.breakable:
                        print("Bala choca contra bloque")
                        generate_powerup()
                    collided_block.kill()
                    collided_bullet.kill()
                    SCORE += 10

    bullet_group.draw(window)
    ball_group.draw(window)

    block_group.update()
    block_group.draw(window)

    for l in range(0, lives):
        life = sprite_factory.SpriteFactory(life_image)
        life.rect.center = (l * life.rect.width + FIELD_BORDER * 3, 520)
        lives_group.add(life)
    lives_group.draw(window)

    if len(powerup_single_group) > 0:
        powerup_single_group.draw(window)
        powerup_single_group.sprite.animate = True
        powerup_single_group.update(powerup_single_group.sprite.vel[0], powerup_single_group.sprite.vel[1])
        if powerup_single_group.sprite.rect.y >= FRAME_HEIGHT:
            powerup_single_group.sprite.kill()

    pygame.display.flip()

    # Limitar FPS (si no lo especificamos, el movimiento será tan rápido que será imperceptible)
    clock.tick(30)


