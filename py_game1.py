import pygame, random
from personaje import Cubo
from enemigo import Enemigo
from bala import Bala
from item import Item

pygame.init()
pygame.mixer.init()

ANCHO = 600
ALTO = 1000
VENTANA = pygame.display.set_mode([ANCHO, ALTO])
FPS = 60
FUENTE = pygame.font.SysFont("Comic Sans", 40)
SONIDO_DISPARO = pygame.mixer.Sound('/python/1_game/audio/bala.mp3')
SONIDO_MUERTE = pygame.mixer.Sound('/python/1_game/audio/zombie-death.mp3')

jugando = True
reloj = pygame.time.Clock()
vida = 5
puntos = 0

tiempo_passado = 0
tiempo_passado_i = 0
tiempo_entre_enemigos = 400
tiempo_entre_enemigos_base = 1000

cubo = Cubo((ANCHO / 2), ALTO - 125)
enemigos = []
balas = []
items = []
ultima_bala = 0
tiempo_entre_balas = 500
tiempo_entre_items = 7500

enemigos.append(Enemigo(ANCHO / 2, 100))
items.append(Item(ANCHO / 2, 100))

def crear_bala():
    global ultima_bala
    
    if pygame.time.get_ticks() - ultima_bala > tiempo_entre_balas:
        balas.append(Bala(cubo.rect.centerx + 20, 860))
        ultima_bala = pygame.time.get_ticks()
        SONIDO_DISPARO.play()

w_presionada = False

def gestionar_teclas(teclas):
    if teclas[pygame.K_d]:
        if cubo.x + cubo.ancho <= ANCHO:
            cubo.x += cubo.velocidad
    if teclas[pygame.K_a]:
        if cubo.x >= 0:
            cubo.x -= cubo.velocidad
    if teclas[pygame.K_SPACE]:
        crear_bala()
    global w_presionada
    w_presionada = teclas[pygame.K_w]

def mostrar_fin_juego():
    global jugando
    jugando = False  # Para detener el bucle principal del juego

    nombre = ""  # Cadena para almacenar el nombre del jugador
    esperando_nombre = True  # Variable para controlar la entrada del nombre

    while esperando_nombre:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                esperando_nombre = False
                pygame.quit()
                quit()

            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_RETURN:
                    esperando_nombre = False
                elif evento.key == pygame.K_BACKSPACE:
                    nombre = nombre[:-1]  # Elimina el último carácter
                else:
                    nombre += evento.unicode  # Añade el carácter presionado

        # Dibuja el texto del fin del juego
        VENTANA.fill("black")
        texto_fin = FUENTE.render("Juego Terminado", True, "white")
        texto_nombre = FUENTE.render("Ingresa tu nombre: " + nombre, True, "white")
        texto_puntos_final = FUENTE.render(f"Tu puntuación: {puntos}", True, "white")

        VENTANA.blit(texto_fin, (ANCHO/2 - texto_fin.get_width()/2, ALTO/2 - 100))
        VENTANA.blit(texto_nombre, (ANCHO/2 - texto_nombre.get_width()/2, ALTO/2))
        VENTANA.blit(texto_puntos_final, (ANCHO/2 - texto_puntos_final.get_width()/2, ALTO/2 + 100))

        pygame.display.update()

    # Guardar la puntuación en el archivo
    with open('1_game/puntuaciones.txt', 'a') as archivo:
        archivo.write(f"{nombre} - {puntos}\n")

    pygame.quit()
    quit()

while jugando and vida > 0:
    tiempo_passado += reloj.tick(FPS)
    tiempo_passado_i += reloj.tick(FPS)

    if tiempo_passado > tiempo_entre_enemigos:
        enemigos.append(Enemigo(random.randint(0, ANCHO), -50))
        tiempo_passado = 0
        tiempo_entre_enemigos = random.randint(50, tiempo_entre_enemigos_base)
        if tiempo_entre_enemigos_base > 600:
            tiempo_entre_enemigos_base -= 20

    if tiempo_passado_i > tiempo_entre_items:
        items.append(Item(random.randint(0, ANCHO), -50))
        tiempo_passado_i = 0

    eventos = pygame.event.get()
    teclas = pygame.key.get_pressed()
    texto_vida = FUENTE.render(f"Vidas: {vida}", True, "white")
    texto_puntos = FUENTE.render(f"Puntos: {puntos}", True, "white")

    gestionar_teclas(teclas)

    for evento in eventos:  
        if evento.type == pygame.QUIT:
            jugando = False
            pygame.quit()

    VENTANA.fill("black")
    cubo.dibujar(VENTANA)    
    
    for enemigo in enemigos:
        enemigo.actualizar_velocidad(puntos, w_presionada)
        enemigo.dibujar(VENTANA)
        enemigo.movimiento()
        
        if pygame.Rect.colliderect(cubo.rect, enemigo.rect):
            vida -= 1
            print(f"Te quedan {vida} vidas")
            SONIDO_MUERTE.play()
            enemigos.remove(enemigo)
        
        if enemigo.y > ALTO:
            puntos += 3
            enemigos.remove(enemigo)
        
        opciones = [1, 2, 3]
        probabilidades = [45, 45, 10]
        
        for bala in balas:
            if pygame.Rect.colliderect(bala.rect, enemigo.rect):
                resultado = random.choices(opciones, probabilidades)[0]
                enemigo.vida -= resultado
                balas.remove(bala)
              
        if enemigo.vida <= 0:
            SONIDO_MUERTE.play()
            enemigos.remove(enemigo)
            puntos += 5
   
    for bala in balas:
        bala.dibujar(VENTANA)
        bala.movimiento()
        if bala.y < 0:
            balas.remove(bala)
            
    for item in items:
        item.dibujar(VENTANA)
        item.movimiento()
        
        if pygame.Rect.colliderect(item.rect, cubo.rect):
            items.remove(item)
            
            if item.tipo == 1:
                if tiempo_entre_balas >= 250:
                    tiempo_entre_balas -= 50
            if item.tipo == 2:
                if cubo.velocidad <= 28:
                    cubo.velocidad += 2
            if item.tipo == 3:
                if vida <= 6:
                    vida += 1
        if item.y > ALTO:
            items.remove(item)
        
    VENTANA.blit(texto_vida, (20, 20))
    VENTANA.blit(texto_puntos, (20, 60))
    pygame.display.update()

# Llamada a la función de fin del juego
mostrar_fin_juego()