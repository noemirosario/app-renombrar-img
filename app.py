import os
import csv
from PIL import Image
import shutil

# Configuración de rutas
carpeta_entrada = r"C:\Users\Juan\Downloadsn\SIE\SIE\img"
archivo_csv = r"C:\Users\Juan\Downloads\SIE\SIE\SIE_Prueba.csv"
carpeta_salida = r"C:\Users\Juan\Downloads\SIE\SIE\Img Renombradas"

# Crear carpeta de salida
os.makedirs(carpeta_salida, exist_ok=True)

# Elegir formato de salida
formato = input("¿Deseas guardar como 'jpg' o 'psd'? ").strip().lower()
if formato not in ['jpg', 'psd']:
    raise ValueError("Formato inválido. Solo se permite 'jpg' o 'psd'.")

# Leer nombres deseados desde la columna 2 del CSV
nuevos_nombres = []
with open(archivo_csv, newline='', encoding='utf-8') as f:
    lector_csv = csv.reader(f)
    for fila in lector_csv:
        if len(fila) > 1:
            nombre_salida = fila[1].strip().replace(".psd", "")
            nuevos_nombres.append(nombre_salida)

# Listar imágenes en orden de nombre (image.jpg, image2.jpg)
imagenes_entrada = sorted(
    [f for f in os.listdir(carpeta_entrada) if f.lower().endswith(".jpg")],
    key=lambda x: int(''.join(filter(str.isdigit, x)) or 0)  # Ordenar por número
)

# Validar longitud
if len(nuevos_nombres) != len(imagenes_entrada):
    print(f"Número de imágenes ({len(imagenes_entrada)}) y nombres en CSV ({len(nuevos_nombres)}) no coinciden.")
    print("Se usará el mínimo.")
    minimo = min(len(nuevos_nombres), len(imagenes_entrada))
    nuevos_nombres = nuevos_nombres[:minimo]
    imagenes_entrada = imagenes_entrada[:minimo]

# === Renombrar imágenes ===
for i in range(len(nuevos_nombres)):
    nombre_img = imagenes_entrada[i]
    nuevo_nombre = nuevos_nombres[i]
    ruta_original = os.path.join(carpeta_entrada, nombre_img)
    ruta_salida = os.path.join(carpeta_salida, f"{nuevo_nombre}.{formato}")

    try:
        if formato == 'jpg':
            with Image.open(ruta_original) as img:
                img = img.convert("RGB")
                img.save(ruta_salida, format='JPEG')
        else:  # Solo cambiar extensión a .psd sin modificar el archivo real
            shutil.copyfile(ruta_original, ruta_salida)

        print(f"✅ {nombre_img} → {nuevo_nombre}.{formato}")
    except Exception as e:
        print(f"Error con {nombre_img}: {e}")

print("\nTodas las imágenes fueron renombradas y guardadas.")


"""
1227639,1227639.psd	image
1227640,1227640.psd	image2
1227641,1227641.psd	image3
1227638,1227638.psd	image4
947265,947265.psd	image5
1099351,1099351.psd	image6
1172417,1172417.psd	image7
179643,179643.psd	image8
1173693,1173693.psd	image9
952677,952677.psd	image10
"""