# pyrkanoid
Arkanoid en Python con pygame. Primer proyecto.

# NOTA DE LA DESARROLLADORA
He decidido dejar el código inacabado, como mínimo temporalmente: presenta fallos que hasta
ahora soy incapaz de corregir, y entiendo que hay partes del código igualmente mal
implementadas o muy mejorables que se han sacrificado en pos de terminar antes. Se decidió
también a última hora que, dado que las varias reescrituras del código derivaron en nuevos fallos,
lo mejor sería "parchear" esos nuevos escapes para mantener el juego más estable. Salvo lo indicado,
el programa puede ser aceptablemente jugable.

# CÓMO FUNCIONA
Unos detalles sobre cómo funciona el diseño y las mecánicas:

- El juego genera un bloque homogéneo de fichas de forma aleatoria con el generador en
levels/level_factory.py.
- Una vez se agotan las vidas, sale un menú de "Fin del juego" en el que se dan las opciones de
"Reintentar" y "Salir". "Reintentar" genera un nuevo bloque de fichas aleatoriamente. "Salir" hace
la misma función que pulsar el aspa de la esquina superior derecha de la ventana.

Romper las fichas de colores genera una serie de "powerups" que tienen distintos efectos según su
color:
- Rojo: lo que llamo "modo láser". Habilita el elemento controlado por el jugador (a partir de
      ahora me referiré a ello como "Vaus") para generar proyectiles que permitan romper las fichas más
      rápido, además de las que rompa la propia bola. También cambia el aspecto de Vaus.
- Azul oscuro: prolonga la longitud de Vaus para facilitar la intercepción de la bola.
- Naranja: le da una propiedad "pegajosa" a Vaus. Una vez la bola impacta contra Vaus, ésta se
      detiene hasta que el jugador vuelve a ponerla en marcha con la tecla [BARRA ESPACIADORA].
- Magenta: añade más bolas a la pantalla hasta que este número sea de tres como máximo. Las bolas
      extra son una copia de la original y se comportarán del mismo modo. Si se consume otro "powerup"
      magenta cuando ya hay más de una bola en pantalla, se generarán o no más bolas dependiendo de ese
      máximo permitido.
- Plateado: añade una vida.
    El resto de "powerups" no tienen una función definida aparte de la consecuente suma de puntos. Esto
    se quedará así.
    
- La pantalla es redimensionable y los gráficos y otros parámetros de los sprites que puedan ser
dependientes de esta redimensión son reescalados. Se ha cuidado que el comportamiento del juego sea igual
en la medida de lo posible, aunque hay cosas que he dejado como estaban, como las velocidades verticales
de los sprites correspondientes a las balas y los "powerups".
- El menú de "Fin del juego" es horroroso. Lo sé. Pero quería hacerlo.

# FALLOS CONOCIDOS
Hay ocasiones en las que he visto que la bola se sale de los límites del escenario. He intentado en numerosas
ocasiones reproducir este comportamiento, hasta ahora sin éxito. Espero que en un futuro pueda subsanarlo.
