"""
HERRAMIENTA DE ETIQUETADO DE CARIES EN IMÁGENES NIRI
Permite marcar manualmente las ubicaciones de caries en imágenes
y exportar las coordenadas en formato JSON compatible con el juego
"""

import pygame
import json
import os
from datetime import datetime
import sys

# ============================================================================
# INICIALIZACIÓN
# ============================================================================

pygame.init()

# Constantes
ANCHO_VENTANA = 1400
ALTO_VENTANA = 900
COLOR_BLANCO = (255, 255, 255)
COLOR_NEGRO = (0, 0, 0)
COLOR_AZUL = (59, 130, 246)
COLOR_VERDE = (34, 197, 94)
COLOR_ROJO = (239, 68, 68)
COLOR_AMARILLO = (250, 204, 21)
COLOR_GRIS = (148, 163, 184)
COLOR_FONDO = (15, 23, 42)

# ============================================================================
# CLASE PRINCIPAL
# ============================================================================

class HerramientaEtiquetado:
    """Herramienta para etiquetar caries en imágenes NIRI"""
    
    def __init__(self):
        """Inicializa la herramienta"""
        self.ventana = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("🦷 Herramienta de Etiquetado de Caries NIRI")
        
        self.reloj = pygame.time.Clock()
        
        # Fuentes
        self.fuente_titulo = pygame.font.Font(None, 48)
        self.fuente_grande = pygame.font.Font(None, 36)
        self.fuente_mediana = pygame.font.Font(None, 28)
        self.fuente_pequena = pygame.font.Font(None, 22)
        
        # Carpetas
        self.carpeta_imagenes = "imagenes_niri"  # Carpeta de entrada
        self.carpeta_salida = "imagenes_etiquetadas"  # Carpeta de salida
        self.crear_carpetas()
        
        # Imágenes
        self.imagenes = []
        self.indice_actual = 0
        self.imagen_actual = None
        self.imagen_escalada = None
        self.rect_imagen = None
        self.escala = 1.0
        
        # Polígonos
        self.puntos_poligono_actual = []  # Puntos del polígono en progreso
        self.poligonos_completados = []  # Lista de polígonos terminados
        
        # Datos etiquetados
        self.datos_etiquetados = []
        self.dificultad = "medium"  # easy, medium, hard
        
        # UI
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Cargar imágenes
        self.cargar_imagenes()
        
        print("=" * 70)
        print("🦷 HERRAMIENTA DE ETIQUETADO DE CARIES NIRI")
        print("=" * 70)
        print(f"\n📁 Carpeta de imágenes: {self.carpeta_imagenes}")
        print(f"📁 Carpeta de salida: {self.carpeta_salida}")
        print(f"✅ {len(self.imagenes)} imágenes cargadas\n")
        
        if len(self.imagenes) > 0:
            self.cargar_imagen_actual()
    
    def crear_carpetas(self):
        """Crea las carpetas necesarias si no existen"""
        if not os.path.exists(self.carpeta_imagenes):
            os.makedirs(self.carpeta_imagenes)
            print(f"📁 Carpeta creada: {self.carpeta_imagenes}")
            print(f"   ⚠️  Coloca tus imágenes NIRI en esta carpeta")
        
        if not os.path.exists(self.carpeta_salida):
            os.makedirs(self.carpeta_salida)
            print(f"📁 Carpeta creada: {self.carpeta_salida}")
    
    def cargar_imagenes(self):
        """Carga todas las imágenes de la carpeta"""
        extensiones = ('.jpg', '.jpeg', '.png', '.bmp')
        
        try:
            archivos = os.listdir(self.carpeta_imagenes)
            for archivo in archivos:
                if archivo.lower().endswith(extensiones):
                    ruta = os.path.join(self.carpeta_imagenes, archivo)
                    self.imagenes.append({
                        'nombre': archivo,
                        'ruta': ruta,
                        'etiquetada': False
                    })
        except Exception as e:
            print(f"❌ Error al cargar imágenes: {e}")
    
    def cargar_imagen_actual(self):
        """Carga la imagen actual en memoria"""
        if 0 <= self.indice_actual < len(self.imagenes):
            info = self.imagenes[self.indice_actual]
            try:
                self.imagen_actual = pygame.image.load(info['ruta'])
                self.puntos_poligono_actual = []
                self.poligonos_completados = []
                print(f"\n📷 Cargando: {info['nombre']}")
            except Exception as e:
                print(f"❌ Error al cargar imagen: {e}")
                self.imagen_actual = None
    
    def obtener_coordenadas_imagen(self, pos_mouse):
        """Convierte coordenadas de pantalla a coordenadas de imagen"""
        if not self.rect_imagen:
            return None
        
        if not self.rect_imagen.collidepoint(pos_mouse):
            return None
        
        x = (pos_mouse[0] - self.rect_imagen.left) / self.escala
        y = (pos_mouse[1] - self.rect_imagen.top) / self.escala
        
        # Asegurar que está dentro de los límites de la imagen
        if 0 <= x < self.imagen_actual.get_width() and 0 <= y < self.imagen_actual.get_height():
            return {'x': int(x), 'y': int(y)}
        return None
    
    def cerrar_poligono(self):
        """Cierra el polígono actual y lo añade a completados"""
        if len(self.puntos_poligono_actual) >= 3:
            self.poligonos_completados.append(self.puntos_poligono_actual[:])
            self.puntos_poligono_actual = []
            print(f"✅ Polígono completado. Total: {len(self.poligonos_completados)}")
    
    def deshacer_punto(self):
        """Elimina el último punto del polígono actual"""
        if len(self.puntos_poligono_actual) > 0:
            self.puntos_poligono_actual.pop()
            print(f"↶ Punto eliminado. Quedan: {len(self.puntos_poligono_actual)}")
    
    def eliminar_ultimo_poligono(self):
        """Elimina el último polígono completado"""
        if len(self.poligonos_completados) > 0:
            self.poligonos_completados.pop()
            print(f"🗑️  Polígono eliminado. Quedan: {len(self.poligonos_completados)}")
    
    def guardar_etiquetas(self):
        """Guarda las etiquetas de la imagen actual"""
        if self.indice_actual >= len(self.imagenes):
            return
        
        info = self.imagenes[self.indice_actual]
        
        # Preparar datos
        dato = {
            'imageName': info['nombre'],
            'difficulty': self.dificultad,
            'polygons': self.poligonos_completados[:],  # Copia de los polígonos
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'es_negativo': len(self.poligonos_completados) == 0
        }
        
        self.datos_etiquetados.append(dato)
        info['etiquetada'] = True
        
        # Copiar imagen a carpeta de salida
        nombre_sin_ext = os.path.splitext(info['nombre'])[0]
        extension = os.path.splitext(info['nombre'])[1]
        
        # Guardar imagen
        ruta_salida_img = os.path.join(self.carpeta_salida, info['nombre'])
        try:
            # Copiar imagen original
            import shutil
            shutil.copy2(info['ruta'], ruta_salida_img)
            print(f"💾 Imagen guardada en: {ruta_salida_img}")
        except Exception as e:
            print(f"⚠️  Error al copiar imagen: {e}")
        
        print(f"✅ Etiquetas guardadas para: {info['nombre']}")
        print(f"   Polígonos: {len(self.poligonos_completados)}")
        print(f"   Dificultad: {self.dificultad}")
        
        # Pasar a siguiente imagen
        if self.indice_actual + 1 < len(self.imagenes):
            self.indice_actual += 1
            self.cargar_imagen_actual()
        else:
            print("\n🎉 ¡Has etiquetado todas las imágenes!")
    
    def exportar_json(self):
        """Exporta todos los datos a un archivo JSON"""
        if len(self.datos_etiquetados) == 0:
            print("⚠️  No hay datos para exportar")
            return
        
        # Nombre del archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"etiquetas_caries_{timestamp}.json"
        ruta_salida = os.path.join(self.carpeta_salida, nombre_archivo)
        
        try:
            with open(ruta_salida, 'w', encoding='utf-8') as f:
                json.dump(self.datos_etiquetados, f, indent=2, ensure_ascii=False)
            
            print("\n" + "=" * 70)
            print("✅ EXPORTACIÓN EXITOSA")
            print("=" * 70)
            print(f"📄 Archivo: {ruta_salida}")
            print(f"📊 Total de imágenes etiquetadas: {len(self.datos_etiquetados)}")
            print(f"📁 Imágenes copiadas a: {self.carpeta_salida}")
            print("\n💡 Usa este archivo JSON en el juego de detección de caries")
            print("=" * 70 + "\n")
        except Exception as e:
            print(f"❌ Error al exportar JSON: {e}")
    
    def dibujar(self):
        """Dibuja toda la interfaz"""
        self.ventana.fill(COLOR_FONDO)
        
        # Panel superior
        self.dibujar_panel_superior()
        
        # Imagen con polígonos
        self.dibujar_imagen()
        
        # Panel lateral
        self.dibujar_panel_lateral()
        
        # Instrucciones en pantalla
        self.dibujar_instrucciones()
        
        pygame.display.flip()
    
    def dibujar_panel_superior(self):
        """Dibuja el panel superior con información"""
        # Título
        titulo = self.fuente_titulo.render("🦷 Etiquetado de Caries NIRI", True, COLOR_BLANCO)
        self.ventana.blit(titulo, (20, 20))
        
        # Contador de imágenes
        if len(self.imagenes) > 0:
            texto = f"Imagen {self.indice_actual + 1} de {len(self.imagenes)}"
            etiquetadas = sum(1 for img in self.imagenes if img['etiquetada'])
            texto += f" | Etiquetadas: {etiquetadas}/{len(self.imagenes)}"
        else:
            texto = "No hay imágenes en la carpeta"
        
        contador = self.fuente_mediana.render(texto, True, COLOR_GRIS)
        self.ventana.blit(contador, (20, 75))
    
    def dibujar_imagen(self):
        """Dibuja la imagen con los polígonos"""
        if not self.imagen_actual:
            # Mensaje de ayuda
            texto1 = self.fuente_grande.render("📁 Coloca tus imágenes NIRI en:", True, COLOR_AMARILLO)
            texto2 = self.fuente_mediana.render(f"    {os.path.abspath(self.carpeta_imagenes)}", True, COLOR_BLANCO)
            texto3 = self.fuente_mediana.render("Luego reinicia la herramienta", True, COLOR_GRIS)
            
            self.ventana.blit(texto1, (50, 300))
            self.ventana.blit(texto2, (50, 350))
            self.ventana.blit(texto3, (50, 400))
            return
        
        # Calcular escala para que quepa
        margen_x = 50
        margen_y = 120
        ancho_disponible = ANCHO_VENTANA - 450  # Menos panel lateral
        alto_disponible = ALTO_VENTANA - margen_y - 50
        
        escala_ancho = ancho_disponible / self.imagen_actual.get_width()
        escala_alto = alto_disponible / self.imagen_actual.get_height()
        self.escala = min(escala_ancho, escala_alto, 1.0) * self.zoom
        
        nuevo_ancho = int(self.imagen_actual.get_width() * self.escala)
        nuevo_alto = int(self.imagen_actual.get_height() * self.escala)
        
        self.imagen_escalada = pygame.transform.scale(self.imagen_actual, (nuevo_ancho, nuevo_alto))
        
        # Posición de la imagen
        x_imagen = margen_x
        y_imagen = margen_y
        
        self.rect_imagen = self.imagen_escalada.get_rect(topleft=(x_imagen, y_imagen))
        
        # Dibujar imagen
        self.ventana.blit(self.imagen_escalada, self.rect_imagen)
        
        # Borde de la imagen
        pygame.draw.rect(self.ventana, COLOR_GRIS, self.rect_imagen, 2)
        
        # Dibujar polígonos completados
        for poligono in self.poligonos_completados:
            puntos_pantalla = []
            for punto in poligono:
                x = self.rect_imagen.left + punto['x'] * self.escala
                y = self.rect_imagen.top + punto['y'] * self.escala
                puntos_pantalla.append((x, y))
            
            if len(puntos_pantalla) > 2:
                pygame.draw.polygon(self.ventana, COLOR_ROJO, puntos_pantalla, 3)
                # Puntos
                for punto in puntos_pantalla:
                    pygame.draw.circle(self.ventana, COLOR_ROJO, punto, 5)
        
        # Dibujar polígono en progreso
        if len(self.puntos_poligono_actual) > 0:
            puntos_pantalla = []
            for punto in self.puntos_poligono_actual:
                x = self.rect_imagen.left + punto['x'] * self.escala
                y = self.rect_imagen.top + punto['y'] * self.escala
                puntos_pantalla.append((x, y))
            
            # Líneas
            if len(puntos_pantalla) > 1:
                pygame.draw.lines(self.ventana, COLOR_AZUL, False, puntos_pantalla, 3)
            
            # Puntos
            for i, punto in enumerate(puntos_pantalla):
                color = COLOR_VERDE if i == 0 else COLOR_AZUL
                pygame.draw.circle(self.ventana, color, punto, 6)
    
    def dibujar_panel_lateral(self):
        """Dibuja el panel lateral con controles"""
        x_panel = ANCHO_VENTANA - 380
        y_panel = 120
        ancho_panel = 360
        
        # Fondo del panel
        pygame.draw.rect(
            self.ventana,
            (30, 41, 59),
            (x_panel, y_panel, ancho_panel, ALTO_VENTANA - y_panel - 20)
        )
        
        y_actual = y_panel + 20
        
        # Título
        titulo = self.fuente_grande.render("Controles", True, COLOR_BLANCO)
        self.ventana.blit(titulo, (x_panel + 20, y_actual))
        y_actual += 50
        
        # Estadísticas
        stats = [
            f"Puntos actuales: {len(self.puntos_poligono_actual)}",
            f"Polígonos: {len(self.poligonos_completados)}",
            f"Dificultad: {self.dificultad.upper()}"
        ]
        
        for stat in stats:
            texto = self.fuente_pequena.render(stat, True, COLOR_GRIS)
            self.ventana.blit(texto, (x_panel + 20, y_actual))
            y_actual += 30
        
        y_actual += 20
        
        # Selección de dificultad
        texto = self.fuente_mediana.render("Dificultad:", True, COLOR_BLANCO)
        self.ventana.blit(texto, (x_panel + 20, y_actual))
        y_actual += 35
        
        dificultades = [
            ('easy', 'Fácil', COLOR_VERDE),
            ('medium', 'Media', COLOR_AMARILLO),
            ('hard', 'Difícil', COLOR_ROJO)
        ]
        
        for valor, etiqueta, color in dificultades:
            color_fondo = color if self.dificultad == valor else COLOR_GRIS
            pygame.draw.rect(
                self.ventana,
                color_fondo,
                (x_panel + 20, y_actual, 100, 35)
            )
            pygame.draw.rect(
                self.ventana,
                COLOR_BLANCO if self.dificultad == valor else COLOR_GRIS,
                (x_panel + 20, y_actual, 100, 35),
                2
            )
            texto = self.fuente_pequena.render(etiqueta, True, COLOR_BLANCO)
            texto_rect = texto.get_rect(center=(x_panel + 70, y_actual + 17))
            self.ventana.blit(texto, texto_rect)
            y_actual += 45
        
        y_actual += 30
        
        # Atajos de teclado
        atajos = [
            ("CLICK", "Añadir punto"),
            ("ENTER", "Cerrar polígono"),
            ("ESPACIO", "Deshacer punto"),
            ("BACKSPACE", "Borrar polígono"),
            ("S", "Guardar y siguiente"),
            ("E", "Exportar JSON"),
            ("1/2/3", "Cambiar dificultad"),
            ("←/→", "Imagen anterior/siguiente"),
            ("ESC", "Salir")
        ]
        
        texto = self.fuente_mediana.render("Atajos:", True, COLOR_BLANCO)
        self.ventana.blit(texto, (x_panel + 20, y_actual))
        y_actual += 35
        
        for tecla, accion in atajos:
            texto_tecla = self.fuente_pequena.render(tecla, True, COLOR_AZUL)
            texto_accion = self.fuente_pequena.render(f": {accion}", True, COLOR_GRIS)
            self.ventana.blit(texto_tecla, (x_panel + 20, y_actual))
            self.ventana.blit(texto_accion, (x_panel + 100, y_actual))
            y_actual += 25
    
    def dibujar_instrucciones(self):
        """Dibuja instrucciones en la parte inferior"""
        y = ALTO_VENTANA - 30
        
        instrucciones = [
            "💡 Click en la imagen para añadir puntos | ",
            "ENTER para cerrar polígono | ",
            "S para guardar | ",
            "E para exportar JSON"
        ]
        
        texto = "".join(instrucciones)
        rendered = self.fuente_pequena.render(texto, True, COLOR_AMARILLO)
        rect = rendered.get_rect(center=(ANCHO_VENTANA // 2, y))
        self.ventana.blit(rendered, rect)
    
    def manejar_eventos(self):
        """Maneja los eventos del usuario"""
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            
            # Click del mouse
            if evento.type == pygame.MOUSEBUTTONDOWN:
                coords = self.obtener_coordenadas_imagen(evento.pos)
                if coords:
                    # Verificar si clickea cerca del primer punto para cerrar
                    if len(self.puntos_poligono_actual) > 2:
                        primer_punto = self.puntos_poligono_actual[0]
                        dist = ((coords['x'] - primer_punto['x'])**2 + 
                               (coords['y'] - primer_punto['y'])**2) ** 0.5
                        
                        if dist < 15 / self.escala:
                            self.cerrar_poligono()
                            return True
                    
                    self.puntos_poligono_actual.append(coords)
            
            # Teclas
            if evento.type == pygame.KEYDOWN:
                # ESC: Salir
                if evento.key == pygame.K_ESCAPE:
                    return False
                
                # ENTER: Cerrar polígono
                if evento.key == pygame.K_RETURN:
                    self.cerrar_poligono()
                
                # ESPACIO: Deshacer punto
                if evento.key == pygame.K_SPACE:
                    self.deshacer_punto()
                
                # BACKSPACE: Eliminar último polígono
                if evento.key == pygame.K_BACKSPACE:
                    self.eliminar_ultimo_poligono()
                
                # S: Guardar
                if evento.key == pygame.K_s:
                    self.guardar_etiquetas()
                
                # E: Exportar JSON
                if evento.key == pygame.K_e:
                    self.exportar_json()
                
                # Flechas: Navegar entre imágenes
                if evento.key == pygame.K_LEFT:
                    if self.indice_actual > 0:
                        self.indice_actual -= 1
                        self.cargar_imagen_actual()
                
                if evento.key == pygame.K_RIGHT:
                    if self.indice_actual < len(self.imagenes) - 1:
                        self.indice_actual += 1
                        self.cargar_imagen_actual()
                
                # 1, 2, 3: Cambiar dificultad
                if evento.key == pygame.K_1:
                    self.dificultad = "easy"
                    print("📊 Dificultad: FÁCIL")
                if evento.key == pygame.K_2:
                    self.dificultad = "medium"
                    print("📊 Dificultad: MEDIA")
                if evento.key == pygame.K_3:
                    self.dificultad = "hard"
                    print("📊 Dificultad: DIFÍCIL")
        
        return True
    
    def ejecutar(self):
        """Bucle principal de la aplicación"""
        ejecutando = True
        
        while ejecutando:
            ejecutando = self.manejar_eventos()
            self.dibujar()
            self.reloj.tick(60)
        
        # Al salir, preguntar si exportar
        if len(self.datos_etiquetados) > 0:
            print("\n¿Quieres exportar las etiquetas antes de salir? (S/N)")
            # Nota: En una versión más avanzada, podrías usar un diálogo gráfico
        
        pygame.quit()
        sys.exit()

# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🦷 HERRAMIENTA DE ETIQUETADO DE CARIES EN IMÁGENES NIRI")
    print("=" * 70)
    print("\n📋 INSTRUCCIONES INICIALES:")
    print("\n1. Coloca tus imágenes NIRI en la carpeta: imagenes_niri/")
    print("2. La herramienta creará automáticamente las carpetas necesarias")
    print("3. Las imágenes etiquetadas se guardarán en: imagenes_etiquetadas/")
    print("\n💡 CONTROLES:")
    print("   • Click en la imagen para añadir puntos al polígono")
    print("   • ENTER para cerrar el polígono actual")
    print("   • ESPACIO para deshacer el último punto")
    print("   • BACKSPACE para borrar el último polígono")
    print("   • S para guardar la imagen actual y pasar a la siguiente")
    print("   • E para exportar todo a JSON")
    print("   • 1/2/3 para cambiar dificultad (Fácil/Media/Difícil)")
    print("   • ←/→ para navegar entre imágenes")
    print("   • ESC para salir")
    print("\n🎯 PROCESO:")
    print("   1. Marca las caries dibujando polígonos alrededor de ellas")
    print("   2. Puedes tener múltiples polígonos por imagen")
    print("   3. Si no hay caries, simplemente presiona S sin marcar nada")
    print("   4. Al final, presiona E para exportar el JSON")
    print("\n" + "=" * 70 + "\n")
    
    input("Presiona ENTER para iniciar...")
    
    herramienta = HerramientaEtiquetado()
    herramienta.ejecutar()