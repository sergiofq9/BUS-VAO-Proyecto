import streamlit as st
from ultralytics import YOLO
import json
import re
import requests
import base64
from io import BytesIO
import cv2
import numpy as np
from PIL import Image
import streamlit as st

# --- 1. MODELO YOLO (EDGE AI) ---
@st.cache_resource
def cargar_yolo():
    return YOLO('yolov8n.pt')

def analizar_trafico(imagen_pil):
    try:
        model = cargar_yolo()
        results = model(imagen_pil, verbose=False)
        conteo = len([box for box in results[0].boxes if int(box.cls) in [2, 3, 5, 7]])
        
        if conteo < 15: nivel = "Verde"
        elif conteo < 35: nivel = "Amarillo"
        elif conteo < 55: nivel = "Naranja"
        else: nivel = "Rojo"
        
        hay_trafico = "SÍ" if conteo >= 50 else "NO"
        return nivel, conteo, hay_trafico
    except:
        return "Desconocido", 0, "No"

# ... (Tu código de YOLO para el tráfico se queda igual) ...

def analizar_panel_gemini(imagen_pil):
    """
    Analizador Local mediante Visión Artificial Clásica (OpenCV).
    Busca el patrón cromático rojo del círculo de 'Dirección Prohibida'.
    100% Offline. 0% Fallos de API.
    """
    try:
        # 1. Convertir la imagen de Streamlit (PIL) al formato de OpenCV (NumPy/BGR)
        img_cv = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
        
        # 2. Recortar la imagen (ROI - Region of Interest)
        # Solo miramos la mitad superior izquierda, que es donde está el cartel.
        # Así evitamos confundirnos con las luces traseras rojas de los coches.
        alto, ancho = img_cv.shape[:2]
        zona_panel = img_cv[0:int(alto*0.4), 0:int(ancho*0.5)]
        
        # 3. Convertir a espacio de color HSV (Ideal para detectar luces LED)
        hsv = cv2.cvtColor(zona_panel, cv2.COLOR_BGR2HSV)
        
        # 4. Definir qué es el "Rojo LED" en matemáticas
        # El rojo en HSV está en los dos extremos del cilindro de color (0-10 y 160-180)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # 5. Crear una máscara (Una imagen en blanco y negro donde lo blanco es lo rojo)
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_roja = mask1 + mask2
        
        # 6. Contar cuántos píxeles rojos hemos detectado en ese trozo de cartel
        pixeles_rojos = cv2.countNonZero(mask_roja)
        
        # CHIVATO PARA LA CONSOLA (Para que veas cómo trabaja)
        print(f"📊 OpenCV ha detectado {pixeles_rojos} píxeles rojos en el panel.")
        
        # 7. Árbol de decisión
        # Si hay una mancha roja grande (más de 300 píxeles), es el círculo prohibido.
        if pixeles_rojos > 300:
            return {"bus": False, "motos": False, "mas2": False, "cero": False, "estado": "CERRADO"}
        else:
            # Si no hay rojo, asumimos que está la flecha blanca o verde.
            return {"bus": True, "motos": True, "mas2": True, "cero": True, "estado": "ABIERTO"}
            
    except Exception as e:
        print(f"🔥 Error en OpenCV: {e}")
        return {"bus": False, "motos": False, "mas2": False, "cero": False, "estado": "DESCONOCIDO"}