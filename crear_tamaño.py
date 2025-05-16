from PIL import Image

# === Parámetros de tamaño final en cm ===
ancho_cm = 22
alto_cm = 23
dpi = 300

# === Convertir a píxeles ===
ancho_px = int((ancho_cm / 2.54) * dpi)  # ≈ 2598
alto_px = int((alto_cm / 2.54) * dpi)    # ≈ 2717

# === Rutas ===
ruta_original = r"C:\Users\Juan\Downloads\SIE\SIE\img\image6.jpg"
ruta_salida = r"C:\Users\Juan\Downloads\SIE\SIE\img\6.jpg"

# === Abrir imagen ===
imagen = Image.open(ruta_original).convert("RGB")

# === Redimensionar imagen al tamaño final (sin mantener proporción) ===
imagen_redimensionada = imagen.resize((ancho_px, alto_px), Image.LANCZOS)

# === Guardar ===
imagen_redimensionada.save(ruta_salida)
print("✅ Imagen ajustada: el zapato ocupa TODO el ancho y alto de 22cm x 23cm (puede haber distorsión).")