import streamlit as st
import os
import csv
import io
import zipfile
from PIL import Image
import cv2
import numpy as np
from psd_tools import PSDImage  # <-- NUEVO: necesario para manejar PSD

# === Configuración inicial ===
st.title("🖼️ Renombrar y Procesar Imágenes (JPG/PSD)")

ancho_cm, alto_cm, dpi = 22, 23, 300
ancho_px = int((ancho_cm / 2.54) * dpi)
alto_px = int((alto_cm / 2.54) * dpi)
margen_cm = 1
margen_px = int((margen_cm / 2.54) * dpi)  # convierte cm a pixeles
ancho_disp = ancho_px - 2 * margen_px
alto_disp = alto_px - 2 * margen_px


# === Formato de entrada ===
formato_entrada = st.selectbox("Formato de las imágenes que vas a subir", ["jpg", "psd"])
imagenes = st.file_uploader(f"Sube las imágenes originales (*.{formato_entrada})", type=[formato_entrada], accept_multiple_files=True)

# === Subida de CSV ===
archivo_csv = st.file_uploader("Sube el CSV con nuevos nombres", type=["csv"])

# === Formato de salida ===
formato_salida = st.selectbox("Formato de salida", ["jpg", "psd"])

# === Preguntar qué desea hacer ===
accion = st.radio("¿Qué deseas hacer?", ["Solo renombrar imágenes", "Renombrar y procesar (recorte, fondo blanco, etc.)"])

# === Función para procesar PSD ===
def cargar_psd_como_pil(file):
    psd = PSDImage.open(file)
    composed = psd.composite()
    return composed.convert("RGB")

# === Función de procesamiento ===
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

    # Margen deseado en cm → px
    margen_cm = 0.3
    margen_px = int((margen_cm / 2.54) * dpi)
    ancho_disp = ancho_px - 2 * margen_px
    alto_disp = alto_px - 2 * margen_px

    # Escalado respetando el borde
    factor_escala = min(ancho_disp / w, alto_disp / h)
    nuevo_ancho = int(w * factor_escala)
    nuevo_alto = int(h * factor_escala)

    zapato_escalado = cv2.resize(zapato, (nuevo_ancho, nuevo_alto), interpolation=cv2.INTER_LINEAR)

    # Canvas blanco
    canvas = np.ones((alto_px, ancho_px, 3), dtype=np.uint8) * 255

    offset_x = (ancho_px - nuevo_ancho) // 2
    offset_y = (alto_px - nuevo_alto) // 2

    canvas[offset_y:offset_y + nuevo_alto, offset_x:offset_x + nuevo_ancho] = zapato_escalado

    imagen_final = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    return imagen_final

# === Botón de ejecución ===
if st.button("Ejecutar"):
    if not imagenes or not archivo_csv:
        st.error("⚠️ Sube imágenes y el archivo CSV.")
    else:
        nuevos_nombres = []
        archivo_csv.seek(0)
        lector_csv = csv.reader(archivo_csv.read().decode("utf-8").splitlines())

        next(lector_csv, None)  # <-- Esto salta la primera fila

        for fila in lector_csv:
            if len(fila) > 1:
                nombre_salida = fila[1].strip().replace(".psd", "").replace(".jpg", "")
                nuevos_nombres.append(nombre_salida)

        if len(nuevos_nombres) != len(imagenes):
            st.warning(f"⚠️ Atención: {len(imagenes)} imágenes pero {len(nuevos_nombres)} nombres en CSV. Se usará el mínimo.")

        minimo = min(len(nuevos_nombres), len(imagenes))

        # === Crear ZIP con resultados ===
        buffer_zip = io.BytesIO()
        with zipfile.ZipFile(buffer_zip, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(minimo):
                imagen_file = imagenes[i]
                nombre_final = nuevos_nombres[i]

                try:
                    if formato_entrada == "psd":
                        imagen_pil = cargar_psd_como_pil(imagen_file)
                    else:
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

                # Guardar como JPG siempre (PSD se exporta como JPG renombrado)
                img_buffer = io.BytesIO()
                img_resultado.save(img_buffer, format="JPEG", dpi=(dpi, dpi))
                img_buffer.seek(0)

                ext = "psd" if formato_salida == "psd" else "jpg"
                zip_file.writestr(f"{nombre_final}.{ext}", img_buffer.read())

                st.success(f"✅ Guardado: {nombre_final}.{ext}")

        st.download_button("📥 Descargar ZIP", data=buffer_zip.getvalue(), file_name="imagenes_resultado.zip")

        st.balloons()
        st.success("🎉 Proceso completado.")
