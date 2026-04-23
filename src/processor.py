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
        
        # Umbrales ajustados al alza para absorber los coches del carril contrario
        if conteo < 12: 
            nivel = "Verde"
        elif conteo < 35: 
            nivel = "Amarillo"
        elif conteo < 50: 
            nivel = "Naranja"
        else: 
            nivel = "Rojo"
        
        hay_trafico = "SÍ" if conteo >= 35 else "NO"
        return nivel, conteo, hay_trafico
    except:
        return "Desconocido", 0, "No"

def analizar_panel_automatico(imagen_pil, tipo_panel="VETERINARIA"):
    try:
        img = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        alto, ancho = img.shape[:2]

        if tipo_panel == "VETERINARIA":
            # 1. Recorte mucho más ceñido a la pantalla negra (esquivamos el puente)
            panel_hsv = hsv[int(alto*0.28):int(alto*0.42), int(ancho*0.40):int(ancho*0.60)]
            
            # 2. Rojo estricto (brillo 160) para no pillar reflejos de pintura
            mask_roja1 = cv2.inRange(panel_hsv, np.array([0, 100, 160]), np.array([20, 255, 255]))
            mask_roja2 = cv2.inRange(panel_hsv, np.array([160, 100, 160]), np.array([180, 255, 255]))
            total_rojo = cv2.countNonZero(mask_roja1 + mask_roja2)

            # 3. Azul normal
            mask_azul = cv2.inRange(panel_hsv, np.array([90, 100, 140]), np.array([140, 255, 255]))
            total_azul = cv2.countNonZero(mask_azul)

            # 4. Verde PERMISIVO (bajamos brillo a 130 y saturación a 80) para el atardecer
            mask_verde = cv2.inRange(panel_hsv, np.array([40, 80, 130]), np.array([90, 255, 255]))
            total_verde = cv2.countNonZero(mask_verde)

            if total_verde > 15:
                return {"estado": "ABIERTO", "bus": True, "motos": True, "mas2": True, "cero": True}
            elif total_rojo > 15 and total_azul < 15:
                return {"estado": "CERRADO", "bus": False, "motos": False, "mas2": False, "cero": False}
            elif total_azul > 15:
                return {"estado": "ABIERTO", "bus": True, "motos": True, "mas2": True, "cero": True}
            else:
                return {"estado": "DESCONOCIDO", "bus": False, "motos": False, "mas2": False, "cero": False}

        else:
            # Lógica ROZAS (Se queda exactamente igual que antes, que funcionaba bien)
            panel_hsv = hsv[int(alto*0.10):int(alto*0.45), int(ancho*0.15):int(ancho*0.85)]
            brillo_min = 140

            mask_roja1 = cv2.inRange(panel_hsv, np.array([0, 100, brillo_min]), np.array([30, 255, 255]))
            mask_roja2 = cv2.inRange(panel_hsv, np.array([160, 100, brillo_min]), np.array([180, 255, 255]))
            total_rojo = cv2.countNonZero(mask_roja1 + mask_roja2)

            mask_azul = cv2.inRange(panel_hsv, np.array([90, 100, brillo_min]), np.array([140, 255, 255]))
            total_azul = cv2.countNonZero(mask_azul)

            if total_rojo > 20:
                return {"estado": "CERRADO", "bus": False, "motos": False, "mas2": False, "cero": False}
            elif total_azul > 20:
                return {"estado": "ABIERTO", "bus": True, "motos": True, "mas2": True, "cero": True}
            else:
                return {"estado": "DESCONOCIDO", "bus": False, "motos": False, "mas2": False, "cero": False}

    except Exception:
        return {"estado": "DESCONOCIDO", "bus": False, "motos": False, "mas2": False, "cero": False}