# -*- coding: utf-8 -*-

from pygame import image, sprite, transform, Rect
import sprite_factory
import random

'''

CLASE PARA GENERAR NIVELES AUTOMÁTICAMENTE. LISTA DE SPRITES (BLOQUES)

'''


class LevelFactory(sprite.Group):

    '''

    COLORES DEL MAPA (LEYENDA)

    W = BLANCO
    S = SALMÓN
    B = AZUL
    G = VERDE
    R = ROJO
    DB = AZUL OSCURO
    M = MAGENTA
    O = NARANJA
    SV = PLATEADO
    GD = DORADO

    '''

    def __init__(self, blocks, rows, frame_width, grid_height, border_width):
        sprite.Group.__init__(self)
        self.sprite_sheet = './lib/img/blocks_backgrounds.png'
        self.blocks = blocks
        self.rows = rows
        self.frame_width = frame_width
        self.grid_height = grid_height
        self.border_width = border_width
        # Áreas de los bloques, según color, en el sprite sheet. Cada área es un rectángulo.
        # Los últimos dos valores forman parte de animaciones, por lo que su área será mayor (96x8 vs 16x8).
        self.color_dict = dict(
            W=(0, 64, 16, 8),
            S=(16, 64, 16, 8),
            B=(32, 64, 16, 8),
            G=(48, 64, 16, 8),
            R=(0, 72, 16, 8),
            DB=(16, 72, 16, 8),
            M=(32, 72, 16, 8),
            O=(48, 72, 16, 8),
            SV=(0, 80, 96, 8),
            GD=(0, 88, 96, 8)
        )

        # Color de bloque al azar, en formato de clave
        # print(random.choice(list(self.color_dict.keys())))

    def add_sprites(self):
        for row in range(1, self.rows):
            for block in range(1, self.blocks):
                key = random.choice(list(self.color_dict.keys()))
                random_block_color = self.color_dict[key]
                sprite_type = key
                # PASO 1: CREAR SPRITE A PARTIR DE SPRITE SHEET RECORTADA, DEFINIENDO SU POSICIÓN
                # PASO 1.1: RECORTAR ÁREA DE LA IMAGEN PARA HACERLA COINCIDIR CON EL BLOQUE CORRESPONDIENTE
                # Y REESCALAR AL DOBLE
                # El tercer valor del rectángulo corresponde a su ancho. Habrá que ver si es de una lista de sprites
                # de una animación o si ésta corresponde a un bloque individual
                if random_block_color[2] > 16:
                    # Estos bloques pueden ser permanentes (GD) o desaparecer tras el segundo golpe (SV)
                    # Además, son animables, cada elemento de la lista equivale a un fotograma de la animación, por lo
                    # que se carga aparte.
                    # Estos bloques tendrán una variable extra para almacenar los sprites de la animación en una nueva
                    # subsuperficie.
                    animation_sheet = transform.scale2x(image.load(self.sprite_sheet).convert().subsurface(Rect(random_block_color)))
                    block_sprite = sprite_factory.SpriteFactory(self.sprite_sheet, sprite_type=sprite_type, animation_sheet=animation_sheet, frames=6)
                    # Cogemos el primer fotograma para que sea la imagen general que se muestra mientras no se active la
                    # reproducción de la animación.
                    block_sprite_area = (random_block_color[0], random_block_color[1], random_block_color[2] // block_sprite.frames, random_block_color[3])
                    block_sprite.image = transform.scale2x(block_sprite.image.subsurface(Rect(block_sprite_area)))
                else:
                    # Estos bloques desaparecen
                    block_sprite = sprite_factory.SpriteFactory(self.sprite_sheet, sprite_type=sprite_type)
                    block_sprite.image = transform.scale2x(block_sprite.image.subsurface(Rect(random_block_color)))
                # Master image para reescalados sin pérdidas
                block_sprite.block_image_master = block_sprite.image
                if block_sprite.animation_sheet is not None:
                    block_sprite.animation_sheet_master = block_sprite.animation_sheet

                # PASO 2: UBICAR SPRITE
                block_sprite.rect = block_sprite.image.get_rect()
                block_sprite.rect.x = block_sprite.rect.width * block
                block_sprite.rect.y = block_sprite.rect.height * row + self.grid_height * 2
                # Para reubicar elementos en el reescalado
                block_sprite.position_master = block_sprite.rect.topleft

                # PASO 3: AÑADIR SPRITE AL GRUPO
                self.add(block_sprite)

        return self
