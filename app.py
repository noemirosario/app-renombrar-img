import streamlit as st
import os
import csv
import io
import zipfile
from PIL import Image
import cv2
import numpy as np

st.title("🖼️ Renombrar y Procesar Imágenes (solo JPG)")

# Parámetros de impresión y márgenes
ancho_cm, alto_cm, dpi = 22, 23, 300
ancho_px = int((ancho_cm / 2.54) * dpi)
alto_px = int((alto_cm / 2.54) * dpi)
margen_cm = 0.3
margen_px = int((margen_cm / 2.54) * dpi)
ancho_disp = ancho_px - 2 * margen_px
alto_disp = alto_px - 2 * margen_px

# Entradas del usuario
imagenes = st.file_uploader("Sube las imágenes originales (.jpg)", type=["jpg"], accept_multiple_files=True)
archivo_csv = st.file_uploader("Sube el CSV con nuevos nombres", type=["csv"])
accion = st.radio("¿Qué deseas hacer?", ["Solo renombrar imágenes", "Renombrar y procesar (recorte, fondo blanco, etc.)"])

img_inicio = st.number_input("Imagen inicial a procesar", min_value=1)
img_fin = st.number_input("Imagen final a procesar", min_value=img_inicio)

# Ajuste para lectura de CSV
fila_inicio_excel = img_inicio + 1
fila_fin_excel = img_fin + 1

def procesar_imagen(imagen_pil):
    imagen = cv2.cvtColor(np.array(imagen_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, mascara = cv2.threshold(gris, 240, 255, cv2.THRESH_BINARY_INV)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contornos:
        return None
    c = max(contornos, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)
    zapato = imagen[y:y + h, x:x + w]
    margen_px = int((0.3 / 2.54) * dpi)
    ancho_disp = ancho_px - 2 * margen_px
    alto_disp = alto_px - 2 * margen_px
    factor_escala = min(ancho_disp / w, alto_disp / h)
    nuevo_ancho = int(w * factor_escala)
    nuevo_alto = int(h * factor_escala)
    zapato_escalado = cv2.resize(zapato, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LINEAR)
    canvas = np.ones((alto_px, ancho_px, 3), dtype=np.uint8) * 255
    offset_x = (ancho_px - nuevo_ancho) // 2
    offset_y = (alto_px - nuevo_alto) // 2
    canvas[offset_y:offset_y + nuevo_alto, offset_x:offset_x + nuevo_ancho] = zapato_escalado
    return Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))

if st.button("Ejecutar"):
    if not imagenes or not archivo_csv:
        st.error("⚠️ Sube imágenes y el archivo CSV.")
    else:
        archivo_csv.seek(0)
        lector_csv = list(csv.reader(archivo_csv.read().decode("utf-8").splitlines()))
        datos_csv = lector_csv[1:]  # Omitimos encabezado

        # Diccionario imagen_num -> archivo de imagen
        imagen_dict = {}
        for img in imagenes:
            nombre = os.path.splitext(img.name)[0]
            num = ''.join(filter(str.isdigit, nombre))  # extrae el número como string
            if num.isdigit():
                imagen_dict[int(num)] = img

        # Filtrar imágenes dentro del rango especificado
        numeros_validos = [n for n in imagen_dict if img_inicio <= n <= img_fin]
        numeros_validos.sort()  # asegurar orden ascendente
        sub_imagenes = [imagen_dict[n] for n in numeros_validos]

        # Obtener nuevos nombres desde el CSV
        nuevos_nombres = []
        for n in numeros_validos:
            indice_csv = n
            if 0 <= indice_csv - 1 < len(datos_csv):
                fila = datos_csv[indice_csv - 1]
                if len(fila) > 1:
                    nombre_salida = os.path.splitext(fila[1].strip())[0]
                    nuevos_nombres.append(nombre_salida)

        if len(nuevos_nombres) != len(sub_imagenes):
            st.warning(f"⚠️ Atención: {len(sub_imagenes)} imágenes pero {len(nuevos_nombres)} nombres. Se usará el mínimo.")
        
        minimo = min(len(nuevos_nombres), len(sub_imagenes))
        buffer_zip = io.BytesIO()

        with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(minimo):
                imagen_file = sub_imagenes[i]
                nombre_final = nuevos_nombres[i]

                try:
                    imagen_pil = Image.open(imagen_file).convert("RGB")
                except Exception as e:
                    st.error(f"❌ Error cargando {imagen_file.name}: {e}")
                    continue

                if accion == "Renombrar y procesar (recorte, fondo blanco, etc.)":
                    img_resultado = procesar_imagen(imagen_pil)
                    if img_resultado is None:
                        st.error(f"❌ No se pudo procesar: {imagen_file.name}")
                        continue
                else:
                    img_resultado = imagen_pil

                img_buffer = io.BytesIO()
                img_resultado.save(img_buffer, format="JPEG", quality=95)
                img_buffer.seek(0)
                zip_file.writestr(f"{nombre_final}.jpg", img_buffer.read())
                st.success(f"✅ Guardado: {nombre_final}.jpg")

        st.download_button("📥 Descargar ZIP", data=buffer_zip.getvalue(), file_name="imagenes_resultado.zip")
        st.balloons()
        st.success("🎉 Proceso completado.")
