import cv2
import numpy as np
from PIL import Image

# === Parámetros de tamaño final en cm ===
ancho_cm = 22
alto_cm = 23
dpi = 300

# === Convertir a píxeles ===
ancho_px = int((ancho_cm / 2.54) * dpi)  # ≈ 2598
alto_px = int((alto_cm / 2.54) * dpi)    # ≈ 2717

# === Rutas ===
ruta_original = r"C:\Users\Juan\Downloads\SIE\SIE\image2.jpg"
ruta_salida = r"C:\Users\Juan\Downloads\SIE\SIE\imageEDIT2.jpg"

# === Leer imagen con OpenCV ===
imagen = cv2.imread(ruta_original)

# === Convertir a escala de grises para detectar zapato ===
gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
_, mascara = cv2.threshold(gris, 240, 255, cv2.THRESH_BINARY_INV)

# === Detectar contornos ===
contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
c = max(contornos, key=cv2.contourArea)
x, y, w, h = cv2.boundingRect(c)

# === Recortar solo el zapato ===
zapato = imagen[y:y+h, x:x+w]

# === Escalar el zapato para que cubra todo el ancho del canvas final ===
factor_escala = ancho_px / w
nuevo_ancho = ancho_px
nuevo_alto = int(h * factor_escala)
zapato_escalado = cv2.resize(zapato, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LINEAR)

# === Crear canvas blanco del tamaño final ===
canvas = np.ones((alto_px, ancho_px, 3), dtype=np.uint8) * 255

# === Centrar zapato verticalmente en el canvas ===
offset_y = (alto_px - nuevo_alto) // 2

# === Si el zapato es más alto que el canvas, recortar ===
if offset_y < 0:
    zapato_escalado = zapato_escalado[-offset_y : -offset_y + alto_px, :]
    offset_y = 0

# === Pegar zapato en el canvas ===
canvas[offset_y:offset_y+zapato_escalado.shape[0], 0:nuevo_ancho] = zapato_escalado

# === Convertir a PIL y guardar ===
imagen_final = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
imagen_final.save(ruta_salida, dpi=(dpi, dpi))

print("✅ Imagen generada con el zapato cubriendo TODO el ancho en 22cm x 23cm sin deformar.")
