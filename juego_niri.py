"""
JUEGO DE DETECCIÓN DE CARIES EN IMÁGENES NIRI - VERSIÓN FINAL
Juego educativo para entrenar la detección de caries en imágenes de infrarrojo cercano
Autor: Sistema de entrenamiento odontológico - Nicole Rodrigues

ARCHIVO: juego_caries.py
"""

# ============================================================================
# IMPORTACIÓN DE LIBRERÍAS
# ============================================================================

import pygame
import json
import sys
import math
import random
from datetime import datetime
import os
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

# ============================================================================
# INICIALIZACIÓN DE PYGAME
# ============================================================================

pygame.init()
pygame.font.init()
pygame.mixer.init()

# ============================================================================
# CONSTANTES DEL JUEGO
# ============================================================================

ANCHO_VENTANA = 1380
ALTO_VENTANA = 820

COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_AZUL = (59, 130, 246)
COLOR_VERDE = (34, 197, 94)
COLOR_ROJO = (239, 68, 68)
COLOR_AMARILLO = (250, 204, 21)
COLOR_GRIS = (148, 163, 184)
COLOR_FONDO = (15, 23, 42)

ESTADO_MENU = "menu"
ESTADO_JUGANDO = "jugando"
ESTADO_RESULTADOS = "resultados"

EXPERIENCIA_PRINCIPIANTE = "principiante"
EXPERIENCIA_AVANZADO = "avanzado"

DIFICULTAD_FACIL = "easy"
DIFICULTAD_MEDIA = "medium"
DIFICULTAD_DIFICIL = "hard"

# ============================================================================
# CLASE PRINCIPAL DEL JUEGO
# ============================================================================

class JuegoDeteccionCaries:
    """Clase principal que controla todo el juego"""
    
    def __init__(self):
        """Constructor: inicializa todas las variables"""
        
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("🦷 Juego de Detección de Caries en imágenes NIRI")
        
        self.reloj = pygame.time.Clock()
        self.estado = ESTADO_MENU
        
        self.nombre_jugador = ""
        self.experiencia = None
        
        self.puntos = 0
        self.vidas = 10
        self.racha = 0
        self.racha_maxima = 0
        self.tiempo_inicio = 0
        self.tiempo_actual = 0
        
        self.pregunta_actual = 0
        self.respondida = False
        self.mostrar_feedback = False
        
        self.puntos_poligono = []
        self.datos_juego = []
        self.imagenes_cargadas = {}
        self.resultados_detallados = []
        
        self.mensaje_feedback = ""
        self.es_correcto = False
        self.precision_actual = 0.0
        self.fuente_titulo = pygame.font.Font(None, 60)
        self.fuente_grande = pygame.font.Font(None, 52)
        self.fuente_mediana = pygame.font.Font(None, 36)
        self.fuente_pequena = pygame.font.Font(None, 26)
        
        self.ranking = []
        self.cargar_ranking()
        
        self.input_activo = False
        
        self.fondo_imagen = None
        self.cargar_fondo()
        
        self.musica_cargada = False
        self.cargar_musica()
        
        self.archivo_excel = "datos_juego_caries.xlsx"
        self.inicializar_excel()
        
        self.cargar_datos_desde_json()
    
    def cargar_fondo(self):
        """Carga la imagen de fondo de la pantalla"""
        try:
            if os.path.exists('fondo_pantalla.jpg'):
                self.fondo_imagen = pygame.image.load('fondo_pantalla.jpg')
                self.fondo_imagen = pygame.transform.scale(self.fondo_imagen, (ANCHO_VENTANA, ALTO_VENTANA))
                print("✅ Imagen de fondo cargada")
            else:
                print("⚠️  No se encontró fondo_pantalla.jpg (opcional)")
                self.fondo_imagen = None
        except Exception as e:
            print(f"⚠️  Error al cargar fondo: {e}")
            self.fondo_imagen = None
    
    def cargar_musica(self):
        """Carga y reproduce la música de fondo en bucle"""
        try:
            if os.path.exists('soundtrak_caries.mp3'):
                pygame.mixer.music.load('soundtrak_caries.mp3')
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play(-1)
                self.musica_cargada = True
                print("✅ Música de fondo cargada y reproduciendo")
            else:
                print("⚠️  No se encontró soundtrak_caries.mp3 (opcional)")
        except Exception as e:
            print(f"⚠️  Error al cargar música: {e}")
    
    def inicializar_excel(self):
        """Crea o carga el archivo Excel para guardar datos"""
        try:
            if os.path.exists(self.archivo_excel):
                self.workbook = openpyxl.load_workbook(self.archivo_excel)
                print(f"✅ Excel cargado: {self.archivo_excel}")
            else:
                self.workbook = Workbook()
                self.crear_hojas_excel()
                self.workbook.save(self.archivo_excel)
                print(f"✅ Excel creado: {self.archivo_excel}")
        except Exception as e:
            print(f"⚠️  Error con Excel: {e}")
            self.workbook = Workbook()
    
    def crear_hojas_excel(self):
        """Crea las hojas del Excel con formato"""
        if 'Sheet' in self.workbook.sheetnames:
            del self.workbook['Sheet']
        
        ws_partidas = self.workbook.create_sheet('Partidas', 0)
        headers_partidas = ['Fecha', 'Hora', 'Jugador', 'Experiencia', 'Puntos', 'Precisión %', 'Vidas Restantes', 'Racha Máxima', 'Tiempo Total (seg)', 'Preguntas Totales', 'Aciertos']
        ws_partidas.append(headers_partidas)
        
        ws_respuestas = self.workbook.create_sheet('Respuestas', 1)
        headers_respuestas = ['Fecha', 'Jugador', 'Pregunta #', 'Imagen', 'Dificultad', 'Correcto', 'Precisión %', 'Puntos', 'Tiempo (seg)']
        ws_respuestas.append(headers_respuestas)
        
        ws_ranking = self.workbook.create_sheet('Ranking', 2)
        headers_ranking = ['Posición', 'Jugador', 'Puntos', 'Precisión %', 'Experiencia', 'Fecha']
        ws_ranking.append(headers_ranking)
        
        for ws in [ws_partidas, ws_respuestas, ws_ranking]:
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
                cell.alignment = Alignment(horizontal="center", vertical="center")
    
    def guardar_partida_excel(self):
        """Guarda los datos de la partida en Excel"""
        try:
            total_preguntas = len(self.resultados_detallados)
            aciertos = sum(1 for r in self.resultados_detallados if r['correcto'])
            precision = (aciertos / total_preguntas * 100) if total_preguntas > 0 else 0
            
            fecha = datetime.now().strftime("%Y-%m-%d")
            hora = datetime.now().strftime("%H:%M:%S")
            
            ws_partidas = self.workbook['Partidas']
            ws_partidas.append([fecha, hora, self.nombre_jugador, self.experiencia, self.puntos, round(precision, 1), self.vidas, self.racha_maxima, int(self.tiempo_actual), total_preguntas, aciertos])
            
            ws_respuestas = self.workbook['Respuestas']
            tiempo_por_pregunta = self.tiempo_actual / total_preguntas if total_preguntas > 0 else 0
            
            for resultado in self.resultados_detallados:
                nombre_imagen = self.datos_juego[resultado['pregunta'] - 1]['imageName']
                dificultad = self.datos_juego[resultado['pregunta'] - 1]['difficulty']
                ws_respuestas.append([fecha, self.nombre_jugador, resultado['pregunta'], nombre_imagen, dificultad, 'SÍ' if resultado['correcto'] else 'NO', resultado['precision'], resultado['puntos'], round(tiempo_por_pregunta, 1)])
            
            self.actualizar_ranking_excel()
            self.workbook.save(self.archivo_excel)
            print(f"✅ Datos guardados en Excel: {self.archivo_excel}")
            
        except Exception as e:
            print(f"⚠️  Error al guardar en Excel: {e}")
    
    def actualizar_ranking_excel(self):
        """Actualiza la hoja de ranking en Excel"""
        try:
            ws_ranking = self.workbook['Ranking']
            ws_ranking.delete_rows(2, ws_ranking.max_row)
            
            for idx, entrada in enumerate(self.ranking, start=1):
                ws_ranking.append([idx, entrada['nombre'], entrada['puntos'], entrada['precision'], entrada['experiencia'], entrada['fecha']])
        except Exception as e:
            print(f"⚠️  Error al actualizar ranking en Excel: {e}")
    
    def cargar_datos_desde_json(self):
        """Carga las imágenes etiquetadas desde el archivo JSON"""
        print("📦 Cargando imágenes desde JSON...")
        
        archivo_json = 'etiquetas_caries.json'
        
        if not os.path.exists(archivo_json):
            print(f"❌ No se encontró: {archivo_json}")
            print("📁 Usando imágenes de respaldo...")
            self.cargar_datos_simulados()
            return
        
        try:
            with open(archivo_json, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            
            print(f"✅ Archivo JSON cargado: {len(datos)} imágenes")
            
            for dato in datos:
                nombre_imagen = dato['imageName']
                ruta_imagen = os.path.join('imagenes', nombre_imagen)
                
                if not os.path.exists(ruta_imagen):
                    print(f"⚠️  No se encontró: {ruta_imagen}")
                    continue
                
                try:
                    imagen = pygame.image.load(ruta_imagen)
                    self.imagenes_cargadas[dato['imageName']] = imagen
                    self.datos_juego.append(dato)
                    print(f"✅ Cargada: {nombre_imagen} ({dato['difficulty']})")
                except Exception as e:
                    print(f"❌ Error cargando {nombre_imagen}: {e}")
            
            print(f"\n🎉 Total cargadas: {len(self.datos_juego)} imágenes")
            
            if len(self.datos_juego) == 0:
                print("⚠️  No se cargaron imágenes, usando respaldo")
                self.cargar_datos_simulados()
        
        except Exception as e:
            print(f"❌ Error al leer JSON: {e}")
            self.cargar_datos_simulados()
    
    def cargar_datos_simulados(self):
        """Método de respaldo: crea imágenes simuladas"""
        datos_ejemplo = []
        
        configuraciones = [
            (600, 400, (300, 130), 70, DIFICULTAD_FACIL, "Simulada 1 - Caries Superior"),
            (600, 400, (175, 195), 65, DIFICULTAD_FACIL, "Simulada 2 - Caries Izquierda"),
            (600, 400, (210, 290), 60, DIFICULTAD_MEDIA, "Simulada 3 - Caries Centro-Inferior"),
        ]
        
        for idx, (ancho, alto, pos_caries, tam_caries, dificultad, nombre) in enumerate(configuraciones):
            superficie = pygame.Surface((ancho, alto))
            superficie.fill((180, 180, 180))
            
            for _ in range(500):
                x = random.randint(0, ancho)
                y = random.randint(0, alto)
                color_punto = random.randint(160, 200)
                pygame.draw.circle(superficie, (color_punto, color_punto, color_punto), (x, y), 1)
            
            centro_x, centro_y = pos_caries
            color_caries = (60, 60, 60)
            pygame.draw.circle(superficie, color_caries, (centro_x, centro_y), tam_caries)
            
            for r in range(tam_caries, 0, -5):
                intensidad = 60 + int((tam_caries - r) * 0.8)
                intensidad = min(intensidad, 100)
                pygame.draw.circle(superficie, (intensidad, intensidad, intensidad), (centro_x, centro_y), r, 2)
            
            self.imagenes_cargadas[nombre] = superficie
            
            num_puntos = 12
            poligono_correcto = []
            for i in range(num_puntos):
                angulo = (2 * math.pi * i) / num_puntos
                radio_poligono = tam_caries * 0.85
                x = centro_x + radio_poligono * math.cos(angulo)
                y = centro_y + radio_poligono * math.sin(angulo)
                poligono_correcto.append({'x': x, 'y': y})
            
            dato = {'imageName': nombre, 'difficulty': dificultad, 'polygons': [poligono_correcto], 'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
            datos_ejemplo.append(dato)
        
        self.datos_juego = datos_ejemplo
        print(f"✅ {len(self.datos_juego)} imágenes simuladas cargadas")
    
    def cargar_ranking(self):
        """Carga el ranking desde archivo JSON"""
        try:
            with open('ranking.json', 'r', encoding='utf-8') as archivo:
                self.ranking = json.load(archivo)
        except FileNotFoundError:
            self.ranking = []
        except Exception as e:
            print(f"Error al cargar ranking: {e}")
            self.ranking = []
    
    def guardar_ranking(self):
        """Guarda el ranking en archivo JSON"""
        try:
            with open('ranking.json', 'w', encoding='utf-8') as archivo:
                json.dump(self.ranking, archivo, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar ranking: {e}")
    
    def agregar_al_ranking(self):
        """Agrega la puntuación actual al ranking"""
        total_preguntas = len(self.resultados_detallados)
        aciertos = sum(1 for r in self.resultados_detallados if r['correcto'])
        precision = (aciertos / total_preguntas * 100) if total_preguntas > 0 else 0
        
        entrada = {
            'nombre': self.nombre_jugador,
            'experiencia': self.experiencia,
            'puntos': self.puntos,
            'precision': round(precision, 1),
            'racha_maxima': self.racha_maxima,
            'fecha': datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
        self.ranking.append(entrada)
        self.ranking.sort(key=lambda x: x['puntos'], reverse=True)
        self.ranking = self.ranking[:10]
        self.guardar_ranking()
    
    def calcular_precision(self, poligono_jugador, poligonos_correctos):
        """Calcula precisión del polígono del jugador"""
        if len(poligono_jugador) < 3:
            return 0.0
        
        mejor_coincidencia = 0.0
        for poligono_correcto in poligonos_correctos:
            coincidencia = self.calcular_superposicion(poligono_jugador, poligono_correcto)
            if coincidencia > mejor_coincidencia:
                mejor_coincidencia = coincidencia
        
        return mejor_coincidencia
    
    def calcular_superposicion(self, poli1, poli2):
        """Calcula superposición entre dos polígonos"""
        centro1 = self.obtener_centroide(poli1)
        centro2 = self.obtener_centroide(poli2)
        
        distancia = math.sqrt((centro1[0] - centro2[0]) ** 2 + (centro1[1] - centro2[1]) ** 2)
        
        area1 = self.calcular_area_poligono(poli1)
        area2 = self.calcular_area_poligono(poli2)
        area_promedio = (area1 + area2) / 2
        distancia_maxima = math.sqrt(area_promedio)
        
        if distancia_maxima > 0:
            puntuacion_distancia = max(0, 1 - (distancia / distancia_maxima))
        else:
            puntuacion_distancia = 0
        
        if max(area1, area2) > 0:
            puntuacion_area = min(area1, area2) / max(area1, area2)
        else:
            puntuacion_area = 0
        
        precision = (puntuacion_distancia * 0.6 + puntuacion_area * 0.4) * 100
        return precision
    
    def obtener_centroide(self, poligono):
        """Calcula el centroide de un polígono"""
        suma_x = sum(p['x'] if isinstance(p, dict) else p[0] for p in poligono)
        suma_y = sum(p['y'] if isinstance(p, dict) else p[1] for p in poligono)
        n = len(poligono)
        return (suma_x / n, suma_y / n)
    
    def calcular_area_poligono(self, poligono):
        """Calcula área usando fórmula de Gauss"""
        area = 0.0
        n = len(poligono)
        
        for i in range(n):
            j = (i + 1) % n
            
            if isinstance(poligono[i], dict):
                x1, y1 = poligono[i]['x'], poligono[i]['y']
                x2, y2 = poligono[j]['x'], poligono[j]['y']
            else:
                x1, y1 = poligono[i]
                x2, y2 = poligono[j]
            
            area += x1 * y2
            area -= x2 * y1
        
        return abs(area / 2.0)
    
    def iniciar_juego(self):
        """Inicia una nueva partida"""
        if self.experiencia == EXPERIENCIA_PRINCIPIANTE:
            datos_filtrados = [d for d in self.datos_juego if d['difficulty'] in [DIFICULTAD_FACIL, DIFICULTAD_MEDIA]]
        else:
            datos_filtrados = [d for d in self.datos_juego if d['difficulty'] in [DIFICULTAD_MEDIA, DIFICULTAD_DIFICIL]]
        
        random.shuffle(datos_filtrados)
        self.datos_juego = datos_filtrados
        
        print(f"\n🎲 Imágenes aleatorizadas: {len(self.datos_juego)}")
        
        self.puntos = 0
        self.vidas = 10
        self.racha = 0
        self.racha_maxima = 0
        self.pregunta_actual = 0
        self.resultados_detallados = []
        self.puntos_poligono = []
        self.respondida = False
        self.mostrar_feedback = False
        self.tiempo_inicio = pygame.time.get_ticks() / 1000
        self.estado = ESTADO_JUGANDO
    
    def enviar_respuesta(self):
        """Procesa la respuesta del jugador"""
        pregunta = self.datos_juego[self.pregunta_actual]
        poligonos_correctos = pregunta['polygons']
        es_caso_negativo = pregunta.get('es_negativo', False)
        
        puntos_ganados = 0
        es_correcto = False
        mensaje = ""
        precision = 0.0
        
        if es_caso_negativo:
            if len(self.puntos_poligono) < 3:
                es_correcto = True
                precision = 100.0
                puntos_ganados = 100
                mensaje = "¡Excelente! Identificaste correctamente que NO hay caries "
                
                self.racha += 1
                if self.racha > self.racha_maxima:
                    self.racha_maxima = self.racha
                
                if self.racha >= 3:
                    bonus_racha = self.racha * 5
                    puntos_ganados += bonus_racha
                    mensaje += f"Racha x{self.racha} (+{bonus_racha})"
                
                self.puntos += puntos_ganados
            else:
                mensaje = "Incorrecto. Esta imagen NO tiene caries (falso positivo)"
                self.vidas -= 1
                self.racha = 0
        else:
            if len(self.puntos_poligono) < 3:
                mensaje = "Incorrecto. Hay caries pero no las marcaste"
                self.vidas -= 1
                self.racha = 0
            else:
                precision = self.calcular_precision(self.puntos_poligono, poligonos_correctos)
                
                if precision >= 80:
                    es_correcto = True
                    puntos_ganados = int(precision)
                    
                    tiempo_transcurrido = (pygame.time.get_ticks() / 1000) - self.tiempo_inicio
                    tiempo_por_pregunta = tiempo_transcurrido / (self.pregunta_actual + 1)
                    
                    if tiempo_por_pregunta < 30:
                        bonus_velocidad = int((30 - tiempo_por_pregunta) / 2)
                        puntos_ganados += bonus_velocidad
                        mensaje = f"¡Excelente! +{puntos_ganados} puntos ({bonus_velocidad} bonus velocidad)"
                    else:
                        mensaje = f"¡Correcto! +{puntos_ganados} puntos"
                    
                    self.racha += 1
                    if self.racha > self.racha_maxima:
                        self.racha_maxima = self.racha
                    
                    if self.racha >= 3:
                        bonus_racha = self.racha * 5
                        puntos_ganados += bonus_racha
                        mensaje += f"Racha x{self.racha} (+{bonus_racha})"
                    
                    self.puntos += puntos_ganados
                else:
                    mensaje = f"Incorrecto. Precisión: {precision:.1f}%"
                    self.vidas -= 1
                    self.racha = 0
        
        self.precision_actual = precision
        self.es_correcto = es_correcto
        self.mensaje_feedback = mensaje
        self.respondida = True
        self.mostrar_feedback = True
        
        self.resultados_detallados.append({'pregunta': self.pregunta_actual + 1, 'correcto': es_correcto, 'precision': round(precision, 1), 'puntos': puntos_ganados})
        
        pygame.time.set_timer(pygame.USEREVENT, 3000)
    
    def siguiente_pregunta(self):
        """Avanza a la siguiente pregunta"""
        if self.vidas <= 0:
            self.terminar_juego()
            return
        
        if self.pregunta_actual + 1 >= len(self.datos_juego):
            self.terminar_juego()
            return
        
        self.pregunta_actual += 1
        self.puntos_poligono = []
        self.respondida = False
        self.mostrar_feedback = False
    
    def terminar_juego(self):
        """Finaliza el juego"""
        self.tiempo_actual = (pygame.time.get_ticks() / 1000) - self.tiempo_inicio
        self.agregar_al_ranking()
        self.guardar_partida_excel()
        self.estado = ESTADO_RESULTADOS
    
    def dibujar_menu(self):
        """Dibuja el menú principal"""
        if self.fondo_imagen:
            self.ventana.blit(self.fondo_imagen, (0, 0))
        else:
            self.ventana.fill(COLOR_FONDO)
        
        titulo = self.fuente_titulo.render("¿ERES CAPAZ DE DETECTAR CARIES EN IMÁGENES NIRI?", True, COLOR_BLANCO)
        rect_titulo = titulo.get_rect(center=(ANCHO_VENTANA // 2, 80))
        self.ventana.blit(titulo, rect_titulo)
        
        subtitulo = self.fuente_pequena.render("Demuestra tu habilidad para detectar caries en imágenes NIRI", True, COLOR_GRIS)
        rect_subtitulo = subtitulo.get_rect(center=(ANCHO_VENTANA // 2, 130))
        self.ventana.blit(subtitulo, rect_subtitulo)
        
        y_actual = 180
        texto_nombre = self.fuente_mediana.render("Tu nombre:", True, COLOR_BLANCO)
        self.ventana.blit(texto_nombre, (100, y_actual))
        
        color_input = COLOR_AZUL if self.input_activo else COLOR_GRIS
        pygame.draw.rect(self.ventana, color_input, (100, y_actual + 40, 400, 50), 2)
        texto_input = self.fuente_mediana.render(self.nombre_jugador, True, COLOR_BLANCO)
        self.ventana.blit(texto_input, (110, y_actual + 50))
        self.rect_input = pygame.Rect(100, y_actual + 40, 400, 50)
        
        y_actual += 120
        texto_experiencia = self.fuente_mediana.render("Nivel de Experiencia en imágenes NIRI:", True, COLOR_BLANCO)
        self.ventana.blit(texto_experiencia, (100, y_actual))
        
        y_actual += 50
        color_principiante = COLOR_VERDE if self.experiencia == EXPERIENCIA_PRINCIPIANTE else COLOR_GRIS
        rect_principiante = pygame.Rect(100, y_actual, 250, 80)
        pygame.draw.rect(self.ventana, color_principiante, rect_principiante, 3)
        
        texto_prin = self.fuente_mediana.render("0-5 años", True, COLOR_BLANCO)
        self.ventana.blit(texto_prin, (130, y_actual + 10))
        texto_prin_desc = self.fuente_pequena.render("Casos fáciles y medios", True, COLOR_GRIS)
        self.ventana.blit(texto_prin_desc, (130, y_actual + 45))
        self.rect_principiante = rect_principiante
        
        color_avanzado = COLOR_VERDE if self.experiencia == EXPERIENCIA_AVANZADO else COLOR_GRIS
        rect_avanzado = pygame.Rect(380, y_actual, 250, 80)
        pygame.draw.rect(self.ventana, color_avanzado, rect_avanzado, 3)
        
        texto_avan = self.fuente_mediana.render("5+ años", True, COLOR_BLANCO)
        self.ventana.blit(texto_avan, (410, y_actual + 10))
        texto_avan_desc = self.fuente_pequena.render("Casos medios y difíciles", True, COLOR_GRIS)
        self.ventana.blit(texto_avan_desc, (410, y_actual + 45))
        self.rect_avanzado = rect_avanzado
        
        y_actual += 130

        instrucciones = [
            "Instrucciones:",
            "1. Ingresa tu nombre y selecciona tu nivel de experiencia",
            "2. Dibuja polígonos marcando los bordes de las caries",
            "3. Gana puntos por precisión y velocidad",
            "4. Mantén una racha para bonificaciones extra"
        ]

        for i, linea in enumerate(instrucciones):
            fuente = self.fuente_mediana if i == 0 else self.fuente_pequena
            color = COLOR_BLANCO if i == 0 else COLOR_GRIS
            texto = fuente.render(linea, True, color)
            self.ventana.blit(texto, (100, y_actual + i * 30))
        
        y_actual += 170
        puede_iniciar = (len(self.nombre_jugador) > 0 and self.experiencia is not None and len(self.datos_juego) > 0)
        
        color_boton = COLOR_VERDE if puede_iniciar else COLOR_GRIS
        rect_boton = pygame.Rect(ANCHO_VENTANA // 2 - 150, y_actual, 300, 60)
        pygame.draw.rect(self.ventana, color_boton, rect_boton, 0 if puede_iniciar else 3)
        
        texto_boton = self.fuente_grande.render("INICIAR JUEGO", True, COLOR_BLANCO)
        rect_texto = texto_boton.get_rect(center=rect_boton.center)
        self.ventana.blit(texto_boton, rect_texto)
        self.rect_iniciar = rect_boton if puede_iniciar else None
        
        if len(self.ranking) > 0:
            y_ranking = 180
            x_ranking = ANCHO_VENTANA - 420
            
            titulo_ranking = self.fuente_mediana.render("Top 5", True, COLOR_AMARILLO)
            self.ventana.blit(titulo_ranking, (x_ranking, y_ranking))
            
            for i, entrada in enumerate(self.ranking[:5]):
                y_pos = y_ranking + 40 + i * 60
                pygame.draw.rect(self.ventana, (30, 41, 59), (x_ranking, y_pos, 350, 50))
                
                pos_texto = self.fuente_mediana.render(f"#{i+1}", True, COLOR_AMARILLO)
                self.ventana.blit(pos_texto, (x_ranking + 10, y_pos + 5))
                
                nombre_texto = self.fuente_pequena.render(entrada['nombre'], True, COLOR_BLANCO)
                self.ventana.blit(nombre_texto, (x_ranking + 60, y_pos + 5))
                
                puntos_texto = self.fuente_mediana.render(str(entrada['puntos']), True, COLOR_VERDE)
                self.ventana.blit(puntos_texto, (x_ranking + 250, y_pos + 5))
                
                precision_texto = self.fuente_pequena.render(f"{entrada['precision']}%", True, COLOR_GRIS)
                self.ventana.blit(precision_texto, (x_ranking + 60, y_pos + 28))
    
    def dibujar_jugando(self):
        """Dibuja la pantalla de juego - versión simplificada para ahorrar espacio"""
        if self.fondo_imagen:
            self.ventana.blit(self.fondo_imagen, (0, 0))
        else:
            self.ventana.fill(COLOR_FONDO)
        
        pregunta = self.datos_juego[self.pregunta_actual]
        nombre_imagen = pregunta['imageName']
        
        # Panel superior con stats (código simplificado - funciona igual)
        y_stats = 20
        self.ventana.blit(self.fuente_mediana.render(f"Pregunta: {self.pregunta_actual + 1}/{len(self.datos_juego)}", True, COLOR_BLANCO), (20, y_stats))
        self.ventana.blit(self.fuente_mediana.render(f"Puntos: {self.puntos}", True, COLOR_VERDE), (220, y_stats))
        self.ventana.blit(self.fuente_mediana.render("Vidas: ", True, COLOR_ROJO), (420, y_stats))
        for i in range(self.vidas):
            pygame.draw.circle(self.ventana, COLOR_ROJO, (510 + i * 22, y_stats + 12), 8)
        tiempo = int((pygame.time.get_ticks() / 1000) - self.tiempo_inicio)
        self.ventana.blit(self.fuente_mediana.render(f"Tiempo: {tiempo//60}:{tiempo%60:02d}", True, COLOR_AZUL), (800, y_stats))
        
        if self.racha >= 3:
            texto_racha = self.fuente_grande.render(f"RACHA x{self.racha}", True, COLOR_AMARILLO)
            if pygame.time.get_ticks() % 1000 < 500:
                self.ventana.blit(texto_racha, texto_racha.get_rect(center=(ANCHO_VENTANA // 2, y_stats + 50)))
        
        y_imagen = 100 if self.racha < 3 else 140
        
        if nombre_imagen in self.imagenes_cargadas:
            imagen = self.imagenes_cargadas[nombre_imagen]
            escala = min(800 / imagen.get_width(), (ALTO_VENTANA - y_imagen - 80) / imagen.get_height(), 1.0)
            imagen_escalada = pygame.transform.scale(imagen, (int(imagen.get_width() * escala), int(imagen.get_height() * escala)))
            rect_imagen = imagen_escalada.get_rect(topleft=(50, y_imagen))
            self.ventana.blit(imagen_escalada, rect_imagen)
            
            if len(self.puntos_poligono) > 0:
                puntos_pantalla = [(rect_imagen.left + p[0] * escala, rect_imagen.top + p[1] * escala) for p in self.puntos_poligono]
                if len(puntos_pantalla) > 1:
                    pygame.draw.lines(self.ventana, COLOR_AZUL, False, puntos_pantalla, 3)
                for i, punto in enumerate(puntos_pantalla):
                    pygame.draw.circle(self.ventana, COLOR_VERDE if i == 0 else COLOR_AZUL, punto, 6)
            
            if self.mostrar_feedback and not pregunta.get('es_negativo', False):
                for poligono_correcto in pregunta['polygons']:
                    puntos_correctos = [(rect_imagen.left + p['x'] * escala, rect_imagen.top + p['y'] * escala) for p in poligono_correcto]
                    if len(puntos_correctos) > 2:
                        pygame.draw.polygon(self.ventana, COLOR_VERDE, puntos_correctos, 3)
            
            self.rect_imagen = rect_imagen
            self.escala_imagen = escala
        
              # *** PANEL LATERAL DERECHO ***
        x_panel = ANCHO_VENTANA - 380
        y_panel = y_imagen
        ancho_panel = 360
        
        # Fondo del panel
        pygame.draw.rect(
            self.ventana, 
            (30, 41, 59), 
            (x_panel, y_panel, ancho_panel, ALTO_VENTANA - y_panel - 20)
        )
        
        # Título del panel
        titulo_panel = self.fuente_mediana.render("Tu Progreso", True, COLOR_BLANCO)
        self.ventana.blit(titulo_panel, (x_panel + 20, y_panel + 20))
        
        y_info = y_panel + 70
        
        # Dificultad de la pregunta
        dificultad = pregunta['difficulty']
        color_dificultad = (
            COLOR_VERDE if dificultad == DIFICULTAD_FACIL 
            else COLOR_AMARILLO if dificultad == DIFICULTAD_MEDIA 
            else COLOR_ROJO
        )
        texto_dificultad_label = self.fuente_pequena.render("Dificultad:", True, COLOR_GRIS)
        self.ventana.blit(texto_dificultad_label, (x_panel + 20, y_info))
        
        texto_dificultad = self.fuente_pequena.render(
            dificultad.upper(), 
            True, 
            color_dificultad
        )
        self.ventana.blit(texto_dificultad, (x_panel + 220, y_info))
        
        # Racha actual
        y_info += 40
        texto_racha_label = self.fuente_pequena.render("Racha actual:", True, COLOR_GRIS)
        self.ventana.blit(texto_racha_label, (x_panel + 20, y_info))
        texto_racha_valor = self.fuente_pequena.render(str(self.racha), True, COLOR_AMARILLO)
        self.ventana.blit(texto_racha_valor, (x_panel + 220, y_info))
        
        # Mejor racha
        y_info += 40
        texto_max_racha_label = self.fuente_pequena.render("Mejor racha:", True, COLOR_GRIS)
        self.ventana.blit(texto_max_racha_label, (x_panel + 20, y_info))
        texto_max_racha_valor = self.fuente_pequena.render(
            str(self.racha_maxima), 
            True, 
            COLOR_VERDE
        )
        self.ventana.blit(texto_max_racha_valor, (x_panel + 220, y_info))
        
        # Puntos marcados
        y_info += 40
        texto_puntos_label = self.fuente_pequena.render("Puntos marcados:", True, COLOR_GRIS)
        self.ventana.blit(texto_puntos_label, (x_panel + 20, y_info))
        texto_puntos_valor = self.fuente_pequena.render(
            str(len(self.puntos_poligono)), 
            True, 
            COLOR_AZUL
        )
        self.ventana.blit(texto_puntos_valor, (x_panel + 220, y_info))
        
        # Instrucciones
        y_info += 60
        instrucciones = [
            "Instrucciones:",
            "• Click para añadir puntos",
            "• Primer punto en verde",
            "• Mínimo 3 puntos",
            "• Presiona ESPACIO para",
            "  deshacer último punto",
            "• Presiona ENTER para",
            "  limpiar todo"
        ]
        
        for i, linea in enumerate(instrucciones):
            fuente = self.fuente_pequena
            color = COLOR_BLANCO if i == 0 else COLOR_GRIS
            texto = fuente.render(linea, True, color)
            self.ventana.blit(texto, (x_panel + 20, y_info + i * 25))
        
        # Botones de control
        y_botones = ALTO_VENTANA - 180
        puede_enviar = len(self.puntos_poligono) >= 3 and not self.respondida
        puede_enviar_vacio = len(self.puntos_poligono) == 0 and not self.respondida
        
        rect_enviar = pygame.Rect(x_panel + 20, y_botones + 110, 320, 50)
        pygame.draw.rect(self.ventana, COLOR_VERDE if (puede_enviar or puede_enviar_vacio) else COLOR_GRIS, rect_enviar, 0 if (puede_enviar or puede_enviar_vacio) else 2)
        texto_enviar = self.fuente_mediana.render("ENVIAR RESPUESTA" if len(self.puntos_poligono) >= 3 else "SIN CARIES (ENVIAR)" if not self.respondida else "Esperando...", True, COLOR_BLANCO)
        self.ventana.blit(texto_enviar, texto_enviar.get_rect(center=rect_enviar.center))
        self.rect_enviar = rect_enviar if (puede_enviar or puede_enviar_vacio) else None
        
        if self.mostrar_feedback:
            superficie_feedback = pygame.Surface((ANCHO_VENTANA, 150), pygame.SRCALPHA)
            pygame.draw.rect(superficie_feedback, (34, 197, 94, 200) if self.es_correcto else (239, 68, 68, 200), (0, 0, ANCHO_VENTANA, 150))
            self.ventana.blit(superficie_feedback, (0, ALTO_VENTANA // 2 - 75))
            texto_mensaje = self.fuente_grande.render(self.mensaje_feedback, True, COLOR_BLANCO)
            self.ventana.blit(texto_mensaje, texto_mensaje.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 - 20)))
            texto_precision = self.fuente_mediana.render(f"Precisión: {self.precision_actual:.1f}%", True, COLOR_BLANCO)
            self.ventana.blit(texto_precision, texto_precision.get_rect(center=(ANCHO_VENTANA // 2, ALTO_VENTANA // 2 + 20)))
    
    def dibujar_resultados(self):
        """Dibuja la pantalla de resultados"""
        if self.fondo_imagen:
            self.ventana.blit(self.fondo_imagen, (0, 0))
        else:
            self.ventana.fill(COLOR_FONDO)
        
        total_preguntas = len(self.resultados_detallados)
        aciertos = sum(1 for r in self.resultados_detallados if r['correcto'])
        precision = (aciertos / total_preguntas * 100) if total_preguntas > 0 else 0
        
        if precision >= 90: nivel, icono, color_nivel = "EXPERTO MAESTRO", " ", COLOR_AMARILLO
        elif precision >= 80: nivel, icono, color_nivel = "EXPERTO", " ", COLOR_VERDE
        elif precision >= 70: nivel, icono, color_nivel = "AVANZADO", " ", COLOR_AZUL
        elif precision >= 60: nivel, icono, color_nivel = "INTERMEDIO", " ", (168, 85, 247)
        else: nivel, icono, color_nivel = "PRINCIPIANTE", " ", COLOR_GRIS
        
        self.ventana.blit(self.fuente_titulo.render(icono, True, COLOR_BLANCO), self.fuente_titulo.render(icono, True, COLOR_BLANCO).get_rect(center=(ANCHO_VENTANA // 2, 80)))
        self.ventana.blit(self.fuente_titulo.render("¡Juego Completado!", True, COLOR_BLANCO), self.fuente_titulo.render("¡Juego Completado!", True, COLOR_BLANCO).get_rect(center=(ANCHO_VENTANA // 2, 170)))
        self.ventana.blit(self.fuente_grande.render(nivel, True, color_nivel), self.fuente_grande.render(nivel, True, color_nivel).get_rect(center=(ANCHO_VENTANA // 2, 230)))
        self.ventana.blit(self.fuente_pequena.render("Datos guardados en Excel", True, COLOR_VERDE), self.fuente_pequena.render("Datos guardados en Excel", True, COLOR_VERDE).get_rect(center=(ANCHO_VENTANA // 2, 270)))
        
        rect_volver = pygame.Rect(ANCHO_VENTANA // 2 - 150, ALTO_VENTANA - 100, 300, 60)
        pygame.draw.rect(self.ventana, COLOR_AZUL, rect_volver)
        self.ventana.blit(self.fuente_grande.render("VOLVER AL MENÚ", True, COLOR_BLANCO), self.fuente_grande.render("VOLVER AL MENÚ", True, COLOR_BLANCO).get_rect(center=rect_volver.center))
        self.rect_volver = rect_volver
    
    def manejar_eventos(self):
        """Procesa eventos del usuario"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            if evento.type == pygame.USEREVENT and self.estado == ESTADO_JUGANDO and self.respondida:
                self.siguiente_pregunta()
            
            if self.estado == ESTADO_MENU:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    pos = evento.pos
                    if hasattr(self, 'rect_input') and self.rect_input.collidepoint(pos): self.input_activo = True
                    else: self.input_activo = False
                    if hasattr(self, 'rect_principiante') and self.rect_principiante.collidepoint(pos): self.experiencia = EXPERIENCIA_PRINCIPIANTE
                    if hasattr(self, 'rect_avanzado') and self.rect_avanzado.collidepoint(pos): self.experiencia = EXPERIENCIA_AVANZADO
                    if hasattr(self, 'rect_iniciar') and self.rect_iniciar and self.rect_iniciar.collidepoint(pos): self.iniciar_juego()
                
                if evento.type == pygame.KEYDOWN and self.input_activo:
                    if evento.key == pygame.K_BACKSPACE: self.nombre_jugador = self.nombre_jugador[:-1]
                    elif evento.key == pygame.K_RETURN: self.input_activo = False
                    elif len(self.nombre_jugador) < 20: self.nombre_jugador += evento.unicode
            
            elif self.estado == ESTADO_JUGANDO:
                if evento.type == pygame.MOUSEBUTTONDOWN:
                    pos = evento.pos
                    if not self.respondida and hasattr(self, 'rect_imagen') and self.rect_imagen.collidepoint(pos):
                        x = (pos[0] - self.rect_imagen.left) / self.escala_imagen
                        y = (pos[1] - self.rect_imagen.top) / self.escala_imagen
                        self.puntos_poligono.append((x, y))
                    if hasattr(self, 'rect_enviar') and self.rect_enviar and self.rect_enviar.collidepoint(pos): self.enviar_respuesta()
                
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE and not self.respondida and len(self.puntos_poligono) > 0: self.puntos_poligono.pop()
                    if evento.key == pygame.K_RETURN and not self.respondida: self.puntos_poligono = []
                    if evento.key == pygame.K_e and not self.respondida: self.enviar_respuesta()
            
            elif self.estado == ESTADO_RESULTADOS:
                if evento.type == pygame.MOUSEBUTTONDOWN and hasattr(self, 'rect_volver') and self.rect_volver.collidepoint(evento.pos):
                    self.estado = ESTADO_MENU
                    self.nombre_jugador = ""
                    self.experiencia = None
        
        return True
    
    def ejecutar(self):
        """Bucle principal del juego"""
        ejecutando = True
        while ejecutando:
            ejecutando = self.manejar_eventos()
            if self.estado == ESTADO_MENU: self.dibujar_menu()
            elif self.estado == ESTADO_JUGANDO: self.dibujar_jugando()
            elif self.estado == ESTADO_RESULTADOS: self.dibujar_resultados()
            pygame.display.flip()
            self.reloj.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    print("=" * 70)
    print("🦷 JUEGO DE DETECCIÓN DE CARIES EN IMÁGENES NIRI")
    print("=" * 70)
    print("\n✨ CARACTERÍSTICAS:")
    print("   ✅ Imágenes en orden aleatorio por partida")
    print("   ✅ Música de fondo (soundtrak_caries.mp3)")
    print("   ✅ Imagen de fondo (fondo_pantalla.jpg)")
    print("   ✅ Guardado automático en Excel (datos_juego_caries.xlsx)")
    print("   ✅ Ranking persistente en JSON")
    print("\n📋 ARCHIVOS NECESARIOS:")
    print("   • etiquetas_caries.json (imágenes etiquetadas)")
    print("   • imagenes/ (carpeta con imágenes)")
    print("   • fondo_pantalla.jpg (opcional)")
    print("   • soundtrak_caries.mp3 (opcional)")
    print("\n💾 INSTALACIÓN:")
    print("   pip install pygame openpyxl")
    print("\n" + "=" * 70)
    
    print("\n🔍 VERIFICANDO ARCHIVOS...")
    archivos_criticos = ['etiquetas_caries.json']
    falta_critico = False
    
    for archivo in archivos_criticos:
        if os.path.exists(archivo):
            print(f"   ✅ {archivo}")
        else:
            print(f"   ❌ {archivo} (NECESARIO)")
            falta_critico = True
    
    for archivo in ['fondo_pantalla.jpg', 'soundtrak_caries.mp3']:
        print(f"   {'✅' if os.path.exists(archivo) else '⚠️ '} {archivo} ({'encontrado' if os.path.exists(archivo) else 'opcional'})")
    
    if os.path.exists('imagenes'):
        num = len([f for f in os.listdir('imagenes') if f.endswith(('.jpg', '.jpeg', '.png'))])
        print(f"   ✅ Carpeta imagenes/ ({num} imágenes)")
    else:
        print(f"   ❌ Carpeta imagenes/ (NECESARIA)")
        falta_critico = True
    
    if falta_critico:
        print("\n⚠️  El juego se iniciará con imágenes simuladas de respaldo")
    else:
        print("\n✅ TODOS LOS ARCHIVOS ENCONTRADOS")
    
    input("\nPresiona ENTER para iniciar el juego...")
    print("\n🚀 Iniciando juego...\n")
    
    try:
        juego = JuegoDeteccionCaries()
        juego.ejecutar()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona ENTER para salir...")