import cv2
import numpy as np
from PIL import Image

def quitar_sombra_precisa(imagen_pil):
    # Convertir PIL a OpenCV
    imagen = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)

    # Convertir a escala de grises
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)

    # Detectar píxeles más oscuros que un umbral, pero solo en la zona inferior
    altura = gris.shape[0]
    mascara_sombra = np.zeros_like(gris)
    region_inferior = gris[int(altura * 0.6):, :]
    _, sombra = cv2.threshold(region_inferior, 180, 255, cv2.THRESH_BINARY_INV)
    mascara_sombra[int(altura * 0.6):, :] = sombra

    # Suavizar la máscara
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    mascara_limpia = cv2.morphologyEx(mascara_sombra, cv2.MORPH_OPEN, kernel)
    mascara_limpia = cv2.GaussianBlur(mascara_limpia, (11, 11), 0)

    # Aplicar máscara: reemplazar sombra con blanco
    imagen[mascara_limpia > 0] = [255, 255, 255]

    return Image.fromarray(cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB))

# === PRUEBA LOCAL ===
if __name__ == "__main__":
    ruta = r"C:\Users\Juan\Downloads\image8.psd"    # reemplaza si usas otra imagen
    original = Image.open(ruta)
    resultado = quitar_sombra_precisa(original)
    resultado.save(r"C:\Users\Juan\Downloads\image8.jpg", dpi=(300, 300))
    print("✅ Imagen sin sombra guardada como sin_sombra.jpg")
