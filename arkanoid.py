# -*- coding: utf-8 -*-

# Pygame
from pygame import *
import pygame.locals

# Bibliotecas implícitas y externas
import sys
import random
import math
# import py2exe

# Propios
import sprite_factory
import powerups
import levels.level_factory as level_factory

# FUENTE SPRITE SHEETS: http://www.spriters-resource.com/nes/arkanoid/

# Inicializa los módulos de Pygame
# Primero reducimos el buffer necesario para cargar los sonidos. Esto reduce el retardo cuando se reproduzcan.
pygame.mixer.pre_init(buffer=512)
pygame.init()

# ANCHO Y ALTO DE LA VENTANA
FRAME_WIDTH = 448  # FIELD_WIDTH * 2
FRAME_HEIGHT = 544  # FIELD_HEIGHT * 2 + SCORE_AREA_HEIGHT

# ALTO DEL PANEL PARA PUNTUACIONES
SCORE_AREA_HEIGHT = 50
SCORE = 0

# ANCHOS Y ALTOS DEL SPRITE PARA EL MARCO DEL ESCENARIO
FIELD_WIDTH = 224
FIELD_HEIGHT = 240
# El doble del original, ya que va a estar reescalado. Este valor se considerará constante, sólo se empleará como
# operando para cálculos de escala
FIELD_BORDER = 16
# Resultado de calcular la proporción entre ancho actual de ventana y ancho de borde original. Su valor variará
# en función del escalado actual de la ventana
field_border_scale = 0

# Frames de las animaciones de los sprites que las tengan
block_sprite_frames = 6
powerup_sprite_frames = 8
surfaces = None

# SFX
vaus_ball_collision_sound = pygame.mixer.Sound('./lib/audio/vaus_ball_collision_sound.wav')
ball_block_collision_sound = pygame.mixer.Sound('./lib/audio/ball_block_collision_sound.wav')
# Para bloques irrompibles
ball_block_collision_sound_2 = pygame.mixer.Sound('./lib/audio/ball_block_collision_sound_2.wav')
vaus_elongate_sound = pygame.mixer.Sound('./lib/audio/vaus_elongate_sound.wav')
vaus_getlife_sound = pygame.mixer.Sound('./lib/audio/vaus_getlife_sound.wav')
vaus_shoot_sound = pygame.mixer.Sound('./lib/audio/vaus_shoot_sound.wav')
vaus_destroyed_sound = pygame.mixer.Sound('./lib/audio/vaus_destroyed_sound.wav')
# bullet_block_collision = pygame.mixer.Sound('./lib/audio/bullet_block_collision.wav')

# Controls checker
moving_left = False
moving_right = False
moving_bola = False

# Otras banderas
killed = False
scaled = False
run_first_time = True

# Vidas por defecto
lives = 3

# Crear ventana
window = pygame.display.set_mode([FRAME_WIDTH, FRAME_HEIGHT], RESIZABLE)
window.get_rect().center = (100, 100)
pygame.display.set_caption('Arkanoid')

clock = pygame.time.Clock()
FPS = 60

# Crear panel para puntuaciones
score_font = pygame.font.Font('./lib/fonts/VT323-Regular.ttf', 28)
score_area = score_font.render("SCORE: " + str(SCORE), True, pygame.Color('white'))

# Pruebas de rendimiento
fps_font = pygame.font.Font('./lib/fonts/VT323-Regular.ttf', 28)

# Añadimos el escenario (224x240 POR DEFECTO, el ancho y alto reescalado se definen en FIELD_WIDTH y FIELD_HEIGHT)
field_sheet = pygame.image.load('./lib/img/fields.png').convert().subsurface(Rect(0, 0, FIELD_WIDTH, FIELD_HEIGHT))
# Creamos duplicado por razones de reescalado
field_area = field_sheet

# CREAMOS LOS SPRITES A PARTIR DE UN MÓDULO GENÉRICO: sprite_factory.py
# Sprite sheets
vaus_sprite_sheet = image.load('./lib/img/vaus.png').convert_alpha()
# blocks_sprite_sheet = image.load('./lib/img/blocks_backgrounds.png').convert_alpha()
fields_sprite_sheet = image.load('./lib/img/fields.png').convert_alpha()

# Creamos el sprite nave
vaus_image = transform.scale2x(vaus_sprite_sheet.subsurface((0, 0, 32, 8)).convert_alpha())
vaus_pos = (FRAME_WIDTH // 2, FRAME_HEIGHT - 100)
vaus_vel = [5, 0]
vaus = sprite_factory.SpriteFactory(vaus_image, vaus_vel)
vaus_single_group = sprite.GroupSingle()
vaus_single_group.add(vaus)

# Creamos el sprite bola
ball_image = transform.scale2x(vaus_sprite_sheet.subsurface((40, 0, 5, 4)))
ball_vel = [3, -3]
ball = sprite_factory.SpriteFactory(ball_image, ball_vel)
ball.moving = False
ball_group = sprite.Group()
ball_group.add(ball)

# Sprite para cada vida. Empezamos con tres
life_image = transform.scale2x(fields_sprite_sheet.subsurface((8, 239, 17, 9)))
lives_group = sprite.Group()

# Otros grupos (bloques, powerups, balas...)
block_group = level_factory.LevelFactory(13, 10, FIELD_WIDTH, SCORE_AREA_HEIGHT, FIELD_BORDER).add_sprites()
block_image = block_group.sprites()[0].image.get_rect()

# Creamos la estructura del sprite powerup. El sprite se generará dinámicamente durante el juego
powerup_sprite_sheet = image.load('./lib/img/powerups.png').convert_alpha()  # Se redimensionará al doble después
powerup_frames = 8
powerup_dim = (16, 7)
powerup_single_group = sprite.GroupSingle()

# Creamos la estructura de la bala para el modo de vaus "láser". Las balas se generarán dinámicamente durante el juego
bullet_image = vaus_sprite_sheet.subsurface((40, 17, 16, 6))
bullet_group = sprite.Group()  # Cada sprite será el recuadro entero que engloba las dos balas.

# VARIABLES PARA REESCALADO DE RESOLUCIÓN Y AUXILIARES PARA REESCALADO DE GRÁFICOS SIN PÉRDIDAS DE IMAGEN
scale_x, scale_y = 1.0, 1.0
# Proporción del tamaño de los gráficos respecto de la ventana
vaus_scale = (FRAME_WIDTH // vaus_single_group.sprite.image.get_width(),
              FRAME_HEIGHT // vaus_single_group.sprite.image.get_height())
ball_scale = (FRAME_WIDTH // ball.image.get_width(), FRAME_HEIGHT // ball.image.get_height())
life_scale = (FRAME_WIDTH // life_image.get_width(), FRAME_HEIGHT // life_image.get_height())
powerup_block_scale = (FRAME_WIDTH // block_image.width, FRAME_HEIGHT // block_image.height)
bullet_scale = (FRAME_WIDTH // bullet_image.get_width(), FRAME_HEIGHT // bullet_image.get_height())


'''
RECALCULA GRÁFICOS, RECTÁNGULOS Y POSICIONES DEPENDIENDO DE LOS CAMBIOS DE TAMAÑO DE LA PANTALLA, SI SE PRODUCEN.
ADAPTA LAS PROPORCIONES DE LOS CUADROS DE ANIMACIONES QUE SUPONEN UN CAMBIO DE TAMAÑO EN ALGUNOS SPRITES (como vaus)
'''
def render(previous_width, previous_height, new_dimensions=[]):
    global vaus_image, vaus_scale, window, field_area, field_border_scale, scaled, vaus_image, vaus_scale

    if scaled:
        # Variables auxiliares para calcular los nuevos rectángulos para las colisiones
        old_rect_x, old_rect_y = 0, 0

        # Actualizamos las dimensiones de la superficie de la ventana y el gráfico que hace de fondo
        window = display.set_mode(new_dimensions, RESIZABLE)
        field_area = transform.scale(field_sheet, window.get_size())

        # Calcular proporción del borde del escenario respecto del ancho de la pantalla
        field_border_scale = window.get_width() // (FRAME_WIDTH // FIELD_BORDER)

        # TODO REPASAR VELOCIDAD VAUS Y BOLA (¿LA BOLA VA MÁS RÁPIDO REESCALADA?)

        if not run_first_time:
            vaus_single_group.sprite.image = transform.scale(vaus_image,
                                                             (window.get_width() // vaus_scale[0],
                                                              window.get_height() // vaus_scale[1]))
            old_rect_x = float(vaus_single_group.sprite.rect.x)
            old_rect_y = float(vaus_single_group.sprite.rect.y)
            vaus_single_group.sprite.rect = vaus_single_group.sprite.image.get_rect()
            vaus_single_group.sprite.rect.topleft = (window.get_width() / (previous_width / old_rect_x), \
                                                     (window.get_height() / (previous_height / old_rect_y)))
            vaus_single_group.sprite.vel = [window.get_width() / (previous_width / vaus_vel[0]), 0]

            for life in lives_group:
                life.image = transform.scale(life_image, (window.get_width() // life_scale[0], \
                                                          window.get_height() // life_scale[1]))
                old_rect_x = float(life.rect.x)
                old_rect_y = float(life.rect.y)
                life.rect = life.image.get_rect()
                life.rect.topleft = (window.get_width() / (previous_width / old_rect_x), \
                                     window.get_height() / (previous_height / old_rect_y))

        for ball in ball_group:
            for ball in ball_group:
                ball.image = transform.scale(ball_image, (window.get_width() // ball_scale[0], \
                                                          window.get_height() // ball_scale[1]))
            old_rect_x = float(ball.rect.x)
            old_rect_y = float(ball.rect.y)
            ball.rect = ball.image.get_rect()
            ball.rect.topleft = (window.get_width() / (previous_width / old_rect_x), \
                                 window.get_height() / (previous_height / old_rect_y))
            ball.vel = [window.get_width() / (previous_width / ball_vel[0]),
                        window.get_height() / (previous_height / ball_vel[1])]

        for block in block_group:
            if block.animation_sheet is not None:
                block.animation_sheet = transform.scale(block.animation_sheet_master, \
                                                        (window.get_width() // powerup_block_scale[0] * block.frames, \
                                                         window.get_height() // powerup_block_scale[1]))
                block.image = block.animation_sheet.subsurface(0, 0, block.animation_sheet.get_width() // block.frames, \
                                                               block.animation_sheet.get_height())
            else:
                block.image = transform.scale(block.block_image_master, (window.get_width() // powerup_block_scale[0], \
                                                                         window.get_height() // powerup_block_scale[1]))
            old_rect_x = float(block.rect.x)
            old_rect_y = float(block.rect.y)
            block.rect = block.image.get_rect()
            block.rect.topleft = (window.get_width() / (FRAME_WIDTH / block.position_master[0]), \
                                  window.get_height() / (FRAME_HEIGHT / block.position_master[1]))

        if len(powerup_single_group) > 0:
            powerup_single_group.sprite.animation_sheet = transform.scale(
                powerup_single_group.sprite.animation_sheet_master, \
                (window.get_width() // powerup_block_scale[0] * powerup_frames, \
                 window.get_height() // powerup_block_scale[1]))
            powerup_single_group.sprite.image = \
                powerup_single_group.sprite.animation_sheet.subsurface(0, 0, \
                                                                        powerup_single_group.sprite.animation_sheet.get_width() // powerup_frames, \
                                                                        powerup_single_group.sprite.animation_sheet.get_height())

            old_rect_x = float(powerup_single_group.sprite.rect.x)
            old_rect_y = float(powerup_single_group.sprite.rect.y)
            powerup_single_group.sprite.rect = powerup_single_group.sprite.image.get_rect()
            powerup_single_group.sprite.rect.topleft = (window.get_width() / (previous_width / old_rect_x), \
                                                        window.get_height() / (previous_height / old_rect_y))

        if len(bullet_group) > 0:
            for bullet in bullet_group:
                bullet.image = transform.scale(bullet_image, (window.get_width() // bullet_scale[0], \
                                                              window.get_height() // bullet_scale[1]))
                old_rect_x = float(bullet.rect.x)
                old_rect_y = float(bullet.rect.y)
                bullet.rect = bullet.image.get_rect()
                bullet.rect.topleft = (window.get_width() / (previous_width / old_rect_x), \
                                       window.get_height() / (previous_height / old_rect_y))

        scaled = False

    if vaus_single_group.sprite.animate:
        vaus_single_group.sprite.update(surfaces=surfaces)
        # Como hay animaciones de Vaus en las que varía el tamaño de la imagen del cuadro, hay que recalcular la
        # escala para que no se esté calculando continuamente respecto del tamaño de la imagen original (compartido
        # por el modo "láser").
        vaus_scale = (FRAME_WIDTH // vaus_single_group.sprite.image.get_width(), \
                      FRAME_HEIGHT // vaus_single_group.sprite.image.get_height())
        vaus_single_group.sprite.image = transform.scale(vaus_single_group.sprite.image, \
                                                         (window.get_width() // (
                                                         vaus_scale[0]), \
                                                          window.get_height() // (
                                                          vaus_scale[1])))
        old_rect_center = (vaus_single_group.sprite.rect.centerx, vaus_single_group.sprite.rect.centery)
        vaus_single_group.sprite.rect = vaus_single_group.sprite.image.get_rect()
        vaus_single_group.sprite.rect.center = old_rect_center
        vaus_image = vaus_single_group.sprite.image


'''
RENDERIZAR UNA SOLA IMAGEN. ESTA FUNCIÓN SERÁ LLAMADA UNA VEZ PARA GRÁFICOS GENERADOS EN EL CURSO DEL JUEGO DESDE CERO,
COMO LAS VIDAS EN PANTALLA
'''
def render_single(graphic, graphic_image, graphic_scale):
    graphic.image = transform.scale(graphic_image, (window.get_width() // graphic_scale[0], \
                                                    window.get_height() // graphic_scale[1]))
    graphic.rect = graphic.image.get_rect()


'''
RESTABLECER VALORES POR DEFECTO Y (RE)INICIALIZAR EL JUEGO
'''
def new_game():
    global run_first_time

    vaus = sprite_factory.SpriteFactory(vaus_image)
    # Renderizamos para adaptar la imagen a la resolución actual (p.e., si es más grande)
    render_single(vaus, vaus_image, vaus_scale)
    vaus.rect.center = (window.get_width() // 2, window.get_height() - 100)
    vaus_single_group.add(vaus)

    # La bola depende de la posición de Vaus
    ball.rect.center = (vaus.rect.centerx + ball.rect.width, vaus.rect.top - ball.rect.height)

    for l in range(0, lives):
        life = sprite_factory.SpriteFactory(life_image)
        # Como las vidas son unos gráficos que se generan de cero cada vez que se reinicia el juego, necesitamos
        # hacer un renderizado previo para detectar sus dimensiones en relación con las actuales de la ventana.
        render_single(life, life_image, life_scale)
        life.rect.center = (l * life.image.get_width() + life.image.get_width(), window.get_height() - 30)
        # Por defecto el valor de 'position_master' será cero, hay que asignar un valor al crear la nueva partida.
        life.position_master = life.rect.center
        lives_group.add(life)

    if hasattr(vaus, 'sticky'):
        vaus.sticky = False
    if hasattr(vaus, 'shoot'):
        vaus.shoot = False
    # Si había más de una bola antes en el grupo, se limpia el grupo y se añade una sola
    if len(ball_group) > 1:
        ball_group.empty()
        ball_group.add(ball)
    elif len(ball_group) == 0:
        ball_group.add(ball)
        ball.vel = [5, -5]

    # Si hay algún powerup en pantalla, se elimina
    if len(powerup_single_group) > 0:
        powerup_single_group.empty()
    # Si hay alguna bala en pantalla, se elimina
    if len(bullet_group) > 0:
        bullet_group.empty()

    # Modificamos una pequeña bandera para evitar renderizar gráficos dos veces. En la primera ejecución del juego, se
    # renderizan dos veces los gráficos de vidas y vaus, tanto en esta función como en el evento del VideoResize
    # inicial, por lo que nos aseguramos aquí de que el renderizado no se repita. No es una cuestión de pérdida de
    # calidad, ya que no se estaría cambiando la dimensión del gráfico más de una vez para adaptarlo a la pantalla,
    # sino que se pretende evitar repetir una operación innecesariamente.
    if run_first_time:
        run_first_time = False


'''
COMPROBAR COLISIONES DE VAUS
'''
def check_vaus_collisions():
    if moving_left and vaus_single_group.sprite.rect.left >= field_border_scale:# and not hasattr(vaus_single_group.sprite, 'surfaces'):
        #if not ('surfaces' in locals()):
        if not vaus_single_group.sprite.animate:
            vaus_single_group.sprite.update(-vaus.vel[0], 0)
        #elif 'surfaces' in locals():
        elif vaus_single_group.sprite.animate:
            vaus_single_group.sprite.update(-vaus.vel[0], 0, surfaces)
        # Si la bola sigue en el estado inicial, se mueve con la nave, ya que está "posada"
        for ball in ball_group:
            if not ball.moving:
                ball.update(-vaus.vel[0], 0)

    if moving_right and vaus_single_group.sprite.rect.right <= window.get_width() - field_border_scale:
        #if not ('surfaces' in locals()):
        if not vaus_single_group.sprite.animate:
            vaus_single_group.sprite.update(vaus.vel[0], 0)
        #elif 'surfaces' in locals():
        elif vaus_single_group.sprite.animate:
            vaus_single_group.sprite.update(vaus.vel[0], 0, surfaces)
        for ball in ball_group:
            if not ball.moving:
                ball.update(vaus.vel[0], 0)


'''
COMPROBAR COLISIONES DE LA BOLA
'''
def check_ball_collisions():
    global lives, surfaces, killed
    for ball in ball_group:
        if ball.moving:
            if ball.rect.right >= window.get_width() - field_border_scale or ball.rect.left <= field_border_scale:
                ball.vel[0] *= -1
            if ball.rect.top <= SCORE_AREA_HEIGHT + field_border_scale:
                ball.vel[1] *= -1
            if ball.rect.bottom >= window.get_height() and len(ball_group) == 1:
                # Se resta una vida y se restablecen los estados de los sprites nave y bola
                lives -= 1
                lives_group.empty()
                ball.moving = False
                # Generamos y ejecutamos la animación de Vaus destruyéndose
                vaus_single_group.sprite.animation_sheet = vaus_sprite_sheet
                surfaces = [(0, 40, 32, 8), (40, 35, 42, 19), (91, 34, 44, 23)]
                vaus_single_group.sprite.frames = 3
                vaus_single_group.sprite.current_frame = 0
                vaus_single_group.sprite.animate = True
                killed = True
                vaus_destroyed_sound.play()
                if lives == 0:
                    # TODO MOSTRAR MENSAJE DE "FIN DEL JUEGO" EN PANTALLA Y FINALIZAR EL JUEGO
                    print("FIN DEL JUEGO")
                    new_game()
            elif ball.rect.bottom >= window.get_height() and len(ball_group) > 1:
                ball.kill()
            ball.update(ball.vel[0], ball.vel[1])

        if sprite.collide_rect(vaus_single_group.sprite, ball) and not hasattr(vaus_single_group.sprite, 'sticky'):
            vaus_ball_collision_sound.play()
            if vaus_single_group.sprite.rect.top <= ball.rect.bottom >= vaus_single_group.sprite.rect.y:
                ball.vel[1] *= -1
            if (ball.rect.left < vaus_single_group.sprite.rect.right or ball.rect.right > vaus_single_group.sprite.rect.left) \
                    and ball.rect.y >= vaus_single_group.sprite.rect.y:
                ball.vel[0] *= -1

        elif sprite.collide_rect(vaus_single_group.sprite, ball) and hasattr(vaus_single_group.sprite, 'sticky'):
            ball.moving = False
            ball.rect.y = vaus_single_group.sprite.rect.top - ball.rect.height
            ball.vel[1] *= -1


'''
COMPROBAR COLISIONES CONTRA BLOQUES
'''
def check_block_collisions():
    global SCORE
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
                ball_block_collision_sound_2.play()
                collided_block.animate = True
            if collided_block_type == 'SV' and not collided_block.breakable:
                collided_block.breakable = True
            elif collided_block.breakable:
                ball_block_collision_sound.play()
                collided_block.kill()
                SCORE += 10
                if not collided_block_type == 'SV':
                    generate_powerup(collided_block)
            # TODO CORREGIR CAMBIOS DE TRAYECTORIA AL CHOCAR CONTRA BLOQUES
            if ball_collided.rect.top < collided_block.rect.top or ball_collided.rect.bottom > collided_block.rect.bottom:
                ball_collided.vel[1] *= -1
            if ball_collided.rect.left < collided_block.rect.left or ball_collided.rect.right > collided_block.rect.right:
                ball_collided.vel[0] *= -1


'''
COMPROBAR EFECTO DE COLISIONES DE POWERUPS CONTRA VAUS
'''
def check_powerup_collisions():
    global surfaces, lives
    if pygame.sprite.groupcollide(vaus_single_group, powerup_single_group, False, False):
        # TODO FINALIZAR ASIGNACIÓN DE POWERUPS
        if hasattr(vaus_single_group.sprite, 'shoot') and powerup_single_group.sprite.sprite_type not in ['P', 'B', 'C', 'D']:
            vaus_single_group.sprite.shoot = False
        if hasattr(vaus_single_group.sprite, 'sticky') and powerup_single_group.sprite.sprite_type not in ['P', 'C', 'D', 'E']:
            vaus_single_group.sprite.sticky = False
        if powerup_single_group.sprite.sprite_type == 'S':
            vaus_single_group.sprite.sticky = True
        elif powerup_single_group.sprite.sprite_type == 'C':
            pass
        elif powerup_single_group.sprite.sprite_type == 'L':
            vaus_single_group.sprite.animation_sheet = vaus_sprite_sheet
            surfaces = powerups.change_vaus_behavior('L', vaus_single_group.sprite)
        elif powerup_single_group.sprite.sprite_type == 'E':
            vaus_single_group.sprite.animation_sheet = vaus_sprite_sheet
            surfaces = powerups.change_vaus_behavior('E', vaus_single_group.sprite)
            vaus_elongate_sound.play()
        elif powerup_single_group.sprite.sprite_type == 'D':
            pass
        elif powerup_single_group.sprite.sprite_type == 'B':
            while len(ball_group) < 4:
                # Se toman las dimensiones de la bola original, determinadas por su imagen
                ball_group.add(sprite_factory.SpriteFactory(ball_group.sprites()[0].image, [-ball.vel[0], -ball.vel[1]]))
                for bola in ball_group:
                    bola.rect.center = (ball.rect.x, ball.rect.y)
                    bola.moving = True
        elif powerup_single_group.sprite.sprite_type == 'P':
            lives += 1
            new_life = sprite_factory.SpriteFactory(life_image)
            render_single(new_life, life_image, life_scale)
            # NOTA: en un grupo de sprites, el contenido NO ESTÁ ORDENADO, por lo que si queremos ubicar un nuevo
            # sprite a la derecha del último que se ve, tendremos que ordenar antes los sprites según centro en x
            new_life.rect.center = (sorted(lives_group.sprites(), key=lambda life: life.rect.centerx)[-1].rect.centerx +\
                                    lives_group.sprites()[0].rect.width, lives_group.sprites()[0].rect.centery)
            lives_group.add(new_life)
            vaus_getlife_sound.play()
        powerup_single_group.empty()


# COMPROBAR COLISIONES DE LAS BALAS EN EL MODO "LÁSER" DE VAUS
def check_bullet_collisions():
    global SCORE, collided_bullet
    if len(bullet_group) > 0:
        for bullet in bullet_group:
            bullet.update(bullet.vel[0], bullet.vel[1])
            if bullet.rect.top <= (SCORE_AREA_HEIGHT + field_border_scale):
                bullet.kill()
        collision = pygame.sprite.groupcollide(bullet_group, block_group, False, False)
        if len(collision) > 0:
            # bullet_block_collision.play()
            for collided_bullet, block_sprite in collision.items():
                collided_block = block_sprite.pop()
                collided_block_type = collided_block.sprite_type
                if not collided_block.breakable:
                    collided_block.animate = True
                if collided_block_type == 'SV' and not collided_block.breakable:
                    collided_block.breakable = True
                elif collided_block.breakable:
                    generate_powerup(collided_block)
                    collided_block.kill()
                    SCORE += 10
            collided_bullet.kill()


# GENERAR POWERUP
# sprite_group: grupo de sprites que colisiona con los bloques
# block_group: grupo de sprites que contiene los bloques
# Función genérica para colisiones entre bola-bloque y bala-bloque
def generate_powerup(collided_block):
    global powerup_block_scale
    # probability = random.randint(0, 100)
    probability = 0     # Test
    if probability <= 50 and collided_block.sprite_type not in ['SV', 'GD'] and len(powerup_single_group) == 0:
        # Como estamos escalando todos los gráficos al doble, realizamos aquí primero un escalado respecto a las
        # dimensiones de la ventana, y doblamos esas proporciones para aplicar al mismo tiempo el escalado doble
        # sobre los mismos parámetros.
        powerup_animation_sheet = transform.scale(powerup_sprite_sheet.subsurface( \
            powerups.powerups_dict[collided_block.sprite_type][0]), \
            (window.get_width() // powerup_block_scale[0] * powerup_frames, window.get_height() // powerup_block_scale[1]))
        # Primera imagen del powerup
        powerup_image = powerup_animation_sheet.subsurface(0, 0, powerup_animation_sheet.get_width() // powerup_frames,
                                                           powerup_animation_sheet.get_height())
        powerup = sprite_factory.SpriteFactory(powerup_image, [0, 2],
                                               powerups.powerups_dict[collided_block.sprite_type][1],
                                               powerup_animation_sheet, powerup_frames)
        # Spritesheet auxiliar para no perder calidad de imagen en el reescalado
        powerup.animation_sheet_master = powerup_animation_sheet
        powerup.rect.center = collided_block.rect.center
        powerup_single_group.add(powerup)


new_game()

# BUCLE PRINCIPAL DEL JUEGO
while True:

    # CONTROLES Y EVENTOS
    for event in pygame.event.get():
        previous_width = window.get_width()
        previous_height = window.get_height()

        if event.type == pygame.VIDEORESIZE:
            scaled = True
            new_dimensions = event.size
            # <Event(16-VideoResize {'h': 530, 'size': (642, 530), 'w': 642})>
            if event.w != previous_width:
                scale_x = event.w / previous_width
            if event.h != previous_height:
                scale_y = event.h / previous_height

        # Posibles entradas del teclado y mouse
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
            if hasattr(vaus_single_group.sprite, 'shoot') and vaus_single_group.sprite.shoot:
                bullet = sprite_factory.SpriteFactory(bullet_image, [0, -5])
                bullet.image = transform.scale(bullet_image, (
                window.get_width() // bullet_scale[0], window.get_height() // bullet_scale[1]))
                bullet.rect = bullet.image.get_rect()
                bullet.rect.center = (vaus_single_group.sprite.rect.centerx, vaus_single_group.sprite.rect.top)
                bullet_group.add(bullet)
                vaus_shoot_sound.play()

        if event.type == pygame.KEYUP:
            moving_left = False
            moving_right = False

        # DETENER JUEGO
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # COLISIONES
    check_vaus_collisions()
    check_ball_collisions()
    check_block_collisions()
    check_powerup_collisions()
    check_bullet_collisions()

    # REDIBUJAR ESCENA
    render(previous_width, previous_height, new_dimensions)

    window.fill(pygame.Color("black"))
    window.blit(score_area, (10, SCORE_AREA_HEIGHT // 3))
    window.blit(field_area, (0, SCORE_AREA_HEIGHT))

    # FPS test
    fps_area = fps_font.render("FPS: " + str(clock.get_fps()), True, pygame.Color('yellow'))
    window.blit(fps_area, (150, SCORE_AREA_HEIGHT / 3))
    # print(clock.get_fps())

    # Animación de vaus para pérdida de una vida
    if not vaus_single_group.sprite.animate and killed:
        # Redefinimos la imagen y escala de Vaus, debido a los cambios sufridos con la animación de "muerte".
        vaus_image = transform.scale2x(vaus_sprite_sheet.subsurface((0, 0, 32, 8)).convert_alpha())
        vaus_scale = (FRAME_WIDTH // vaus_image.get_width(), \
                      FRAME_HEIGHT // vaus_image.get_height())
        vaus_single_group.empty()
        ball_group.empty()
        killed = False
        new_game()
    vaus_single_group.draw(window)

    bullet_group.draw(window)
    ball_group.draw(window)

    block_group.update()
    block_group.draw(window)

    lives_group.draw(window)

    if len(powerup_single_group) > 0:
        powerup_single_group.draw(window)
        powerup_single_group.sprite.animate = True
        powerup_single_group.update(powerup_single_group.sprite.vel[0], powerup_single_group.sprite.vel[1])
        if powerup_single_group.sprite.rect.y >= window.get_height():
            powerup_single_group.sprite.kill()

    pygame.display.flip()

    # Lock FPS
    # TODO cambiar
    if killed:
        FPS = 5
    else:
        FPS = 60
    clock.tick(FPS)