# -*- coding: utf-8 -*-

from pygame import Surface

'''
Diccionario de powerups.

Se accederá a él para elegir la subsuperficie del sprite sheet correspondiente a la animación de cada powerup,
según el color del bloque que se rompa. También contiene string que representan los estados que modificarán el
comportamiento de los sprites según el powerup que colisiones con vaus.
'''

powerups_dict = dict(
    O=[(0, 0, 128, 7), 'S'],
    G=[(0, 8, 128, 7), 'C'],
    R=[(0, 16, 128, 7), 'L'],
    DB=[(0, 24, 128, 7), 'E'],
    B=[(0, 32, 128, 7), 'D'],
    M=[(0, 40, 128, 7), 'B'],
    W=[(0, 48, 128, 7), 'P'],
    S=[(0, 16, 128, 7), 'L']
)

'''

Funciones para definir el comportamiento de vaus dependiendo del powerup con el que colisione
state = string con el carácter que indica el estado (definido por el color/letra del sprite)

'C' -
'L' - Laser
'E' - Elongated
'D' -
'P' - Extra Life

'''


def change_vaus_behavior(state, vaus):
    # TODO CAMBIAR ESTADO DE VAUS O LA BOLA, AL ASOCIADO AL POWERUP CONTRA EL QUE COLISIONA ¡¡¡¡REPASAR!!!!
    if state == 'C':
        pass
    elif state == 'L':
        '''
        VAUS LASER
        '''
        surfaces = []
        laser_sheet_area = Surface((160, 8))    # 32 * 5
        laser1_posx = 0
        laser2_posx = 32
        laser3_posx = 64
        laser4_posx = 96
        laser5_posx = 128

        # En este caso el área 1 coincide con el área del recuadro para el estado inicial
        area1 = (0, 0, 32, 8)
        surfaces.append(area1)

        area2 = Surface((32, 8))
        area2_borderlaser = (64, 8, 8, 8)
        area2_normalbody = (80, 0, 8, 7)
        area2_borderright = (112, 0, 8, 8)  # borde izquierdo vaus láser
        area2.blit(vaus.animation_sheet.subsurface(area2_borderlaser), (0, 0))
        area2.blit(vaus.animation_sheet.subsurface(area2_normalbody), (8, 0))
        area2.blit(vaus.animation_sheet.subsurface(area2_normalbody), (16, 0))
        area2.blit(vaus.animation_sheet.subsurface(area2_borderright), (24, 0))
        surfaces.append((laser2_posx, 0, area2.get_width(), area2.get_height()))

        area3 = Surface((32, 8))
        # Vamos reciclando piezas del vaus láser de áreas anteriores (por ejemplo, podemos reusar el borde del láser)
        area3_laserbody = (80, 8, 8, 7)
        area3.blit(vaus.animation_sheet.subsurface(area2_borderlaser), (0, 0))
        area3.blit(vaus.animation_sheet.subsurface(area3_laserbody), (8, 0))
        area3.blit(vaus.animation_sheet.subsurface(area2_normalbody), (16, 0))
        area3.blit(vaus.animation_sheet.subsurface(area2_borderright), (24, 0))
        surfaces.append((laser3_posx, 0, area3.get_width(), area3.get_height()))

        area4 = Surface((32, 8))
        area4.blit(vaus.animation_sheet.subsurface(area2_borderlaser), (0, 0))
        area4.blit(vaus.animation_sheet.subsurface(area3_laserbody), (8, 0))
        area4.blit(vaus.animation_sheet.subsurface(area3_laserbody), (16, 0))
        area4.blit(vaus.animation_sheet.subsurface(area2_borderright), (24, 0))
        surfaces.append((laser4_posx, 0, area4.get_width(), area4.get_height()))

        area5 = (0, 16, 32, 8)
        surfaces.append((laser5_posx, 0, area5[2], area5[3]))

        laser_sheet_area.blit(vaus.animation_sheet.subsurface(area1), (laser1_posx, 0))
        laser_sheet_area.blit(area2, (laser2_posx, 0))
        laser_sheet_area.blit(area3, (laser3_posx, 0))
        laser_sheet_area.blit(area4, (laser4_posx, 0))
        laser_sheet_area.blit(vaus.animation_sheet.subsurface(area5), (laser5_posx, 0))

        vaus.animation_sheet = laser_sheet_area
        vaus.frames = 5
        vaus.current_frame = 0
        vaus.animate = True
        vaus.shoot = True
        return surfaces

    elif state == 'E':
        '''
        VAUS ELONGATED
        '''
        # Creamos superficie uniendo subsuperficies de una misma sprite sheet
        # 4 fotogramas
        # Listado en blanco de áreas, sobre el que se iterará en play_animation() (sprite_factory.py)
        surfaces = []
        elongated_sheet_area = Surface((120, 8))
        elongated1_posx = 0
        elongated2_posx = 32    # Ancho elongated1
        elongated3_posx = 72   # Ancho elongated1 más ancho elongated2 (32 + 40 = 72)
        # areax = área calculada DE LA SPRITE SHEET ORIGINAL
        # Original: 32x8
        # Esta primera área vale tanto para el sprite en la original como para el sprite en la nueva sprite sheet
        area1 = (0, 0, 32, 8)
        surfaces.append(area1)

        # Elongated 1: 40x8
        area2 = Surface((40, 8))
        area2_borderleft = (64, 0, 8, 8)
        area2_center = (80, 0, 8, 7)  # x3
        area2_borderright = (112, 0, 8, 8)
        area2.blit(vaus.animation_sheet.subsurface(area2_borderleft), (0, 0))
        area2.blit(vaus.animation_sheet.subsurface(area2_center), (8, 0))
        area2.blit(vaus.animation_sheet.subsurface(area2_center), (16, 0))
        area2.blit(vaus.animation_sheet.subsurface(area2_center), (24, 0))
        area2.blit(vaus.animation_sheet.subsurface(area2_borderright), (32, 0))
        # Ubicación del segundo sprite en la nueva sprite sheet
        surfaces.append((elongated2_posx, 0, area2.get_width(), area2.get_height()))

        # Elongated final: 48x8
        area3 = (0, 8, 48, 8)
        # Ubicación del tercer sprite en la nueva sprite sheet
        surfaces.append((elongated3_posx, 0, area3[2], area3[3]))

        # Pintamos las áreas en la superficie en blanco
        elongated_sheet_area.blit(vaus.animation_sheet.subsurface(area1), (elongated1_posx, 0))
        elongated_sheet_area.blit(area2, (elongated2_posx, 0))
        elongated_sheet_area.blit(vaus.animation_sheet.subsurface(area3), (elongated3_posx, 0))

        vaus.animation_sheet = elongated_sheet_area
        vaus.frames = 3
        vaus.current_frame = 0
        vaus.animate = True
        return surfaces

    elif state == 'D':
        pass
    elif state == 'P':
        pass
