import streamlit as st
import os
import csv
import io
import zipfile
from PIL import Image
import cv2
import numpy as np

# === Configuración inicial ===
st.title("🖼️ Renombrar y Procesar Imágenes (JPG/PSD)")

ancho_cm, alto_cm, dpi = 22, 23, 300
ancho_px = int((ancho_cm / 2.54) * dpi)
alto_px = int((alto_cm / 2.54) * dpi)

# === Subida de archivos ===
imagenes = st.file_uploader("Sube las imágenes originales (.jpg)", type=["jpg"], accept_multiple_files=True)
archivo_csv = st.file_uploader("Sube el CSV con nuevos nombres", type=["csv"])

formato = st.selectbox("Formato de salida", ["jpg", "psd"])

# === Preguntar qué desea hacer ===
accion = st.radio("¿Qué deseas hacer?", ["Solo renombrar imágenes", "Renombrar y procesar (recorte, fondo blanco, etc.)"])

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
    factor_escala = ancho_px / w
    nuevo_alto = int(h * factor_escala)
    zapato_escalado = cv2.resize(zapato, (ancho_px, nuevo_alto), interpolation=cv2.INTER_LINEAR)

    canvas = np.ones((alto_px, ancho_px, 3), dtype=np.uint8) * 255
    offset_y = (alto_px - nuevo_alto) // 2

    if offset_y < 0:
        zapato_escalado = zapato_escalado[-offset_y: -offset_y + alto_px, :]
        offset_y = 0

    canvas[offset_y:offset_y + zapato_escalado.shape[0], 0:ancho_px] = zapato_escalado

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

                imagen_pil = Image.open(imagen_file)

                if accion == "Renombrar y procesar (recorte, fondo blanco, etc.)":
                    img_resultado = procesar_imagen(imagen_pil)
                    if img_resultado is None:
                        st.error(f"❌ No se pudo procesar: {imagen_file.name}")
                        continue
                else:
                    # Solo renombrar (sin procesar)
                    img_resultado = imagen_pil.convert("RGB")

                # Guardar como JPG siempre, cambiar extensión si es PSD
                img_buffer = io.BytesIO()
                img_resultado.save(img_buffer, format="JPEG", dpi=(dpi, dpi))
                img_buffer.seek(0)

                ext = "psd" if formato == "psd" else "jpg"
                zip_file.writestr(f"{nombre_final}.{ext}", img_buffer.read())

                st.success(f"✅ Guardado: {nombre_final}.{ext}")

        st.download_button("📥 Descargar ZIP", data=buffer_zip.getvalue(), file_name="imagenes_resultado.zip")

        st.balloons()
        st.success("🎉 Proceso completado.")
