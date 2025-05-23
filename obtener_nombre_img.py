import os

# Directorio donde están las imágenes
directorio = r"C:\Users\Juan\Downloads\imagenes_resultado(7)"

# Obtener solo los nombres de archivos .jpg
imagenes = [f for f in os.listdir(directorio) if f.lower().endswith('.jpg')]

print(len(imagenes))
print(imagenes)
