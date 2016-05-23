# -*- coding: utf-8 -*-

from pygame import sprite, image, transform

'''
Fábrica de sprites para generar todos los sprites del juego (originalmente sólo bloques y power-ups)
'''


class SpriteFactory(sprite.Sprite):
    def __init__(self, img, vel=[0, 0], sprite_type=None, animation_sheet=None, frames=0):
        sprite.Sprite.__init__(self)
        if type(img).__name__ == "str":
            self.image = image.load(img).convert_alpha()
        else:
            self.image = img.convert_alpha()
        self.rect = self.image.get_rect()
        self.sprite_type = sprite_type
        # Banderas que usaremos para iniciar animaciones o movimiento cuando el juego las requiera
        self.moving = False
        self.animate = False
        self.state = ""
        self.vel = vel
        if self.sprite_type == 'SV' or self.sprite_type == 'GD':
            self.breakable = False
        else:
            self.breakable = True
        self.animation_sheet = animation_sheet  # Image (Surface)
        if self.animation_sheet is not None:
            self.frames = frames
            self.current_frame = 0
            self.animation_sheet_rect = self.animation_sheet.get_rect()

    def update(self, pos_x=0, pos_y=0, surfaces=None):
        self.rect.x += pos_x
        self.rect.y += pos_y
        if self.animate:
            self.play_animation(self.frames, surfaces)

    def play_animation(self, frames, surfaces=None):

        if surfaces is None:
            if self.current_frame >= frames - 1:
                self.current_frame = 0
                self.animate = False
            elif self.current_frame < frames and surfaces is None:
                self.current_frame += 1

            new_area = (self.current_frame * self.rect.width, 0, self.rect.width, self.rect.height)
            # Ver que sólo se cambia la imagen, no es necesario volver a obtener el rectángulo porque ya está
            # definido; de volver a obtenerlo, los nuevos fotogramas se dibujarán en la posición (0, 0).
            self.image = self.animation_sheet.subsurface(new_area)

        elif surfaces is not None:
            # La animación no repetirá el ciclo aquí, sino que finalizará en el sprite final
            if self.current_frame >= self.frames - 1:
                self.animate = False
            else:
                self.current_frame += 1

            center = self.rect.center
            self.image = transform.scale2x(self.animation_sheet.subsurface(surfaces[self.current_frame]))
            self.rect = self.image.get_rect()
            self.rect.center = center

        return self.animate
