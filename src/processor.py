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
import datetime

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
        elif conteo < 45: 
            nivel = "Naranja"
        else: 
            nivel = "Rojo"
        
        hay_trafico = "SÍ" if conteo >= 35 else "NO"
        return nivel, conteo, hay_trafico
    except:
        return "Desconocido", 0, "No"

def analizar_panel_automatico(imagen_pil, tipo_panel="VETERINARIA"):
    try:
        # --- EL PARCHE: LÓGICA DE HORARIO ---
        hora_actual = datetime.datetime.now().hour
        # Si son las 22, 23, 0, 1, 2, 3, 4 o 5, el VAO está cerrado.
        if hora_actual >= 22 or hora_actual < 6:
            return {"estado": "CERRADO", "bus": False, "motos": False, "mas2": False, "cero": False}
        # ------------------------------------

        # Si estamos en horario de apertura, entonces sí, miramos la foto
        img = cv2.cvtColor(np.array(imagen_pil), cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        alto, ancho = img.shape[:2]

        if tipo_panel == "VETERINARIA":
            panel_hsv = hsv[int(alto*0.28):int(alto*0.42), int(ancho*0.40):int(ancho*0.60)]
            m_roja = cv2.inRange(panel_hsv, np.array([0, 100, 150]), np.array([10, 255, 255]))
            m_verde = cv2.inRange(panel_hsv, np.array([40, 70, 120]), np.array([90, 255, 255]))
            m_azul = cv2.inRange(panel_hsv, np.array([90, 100, 130]), np.array([140, 255, 255]))
            
            if cv2.countNonZero(m_verde) > 10: return {"estado": "ABIERTO", "bus": True, "motos": True, "mas2": True, "cero": True}
            if cv2.countNonZero(m_roja) > 10: return {"estado": "CERRADO", "bus": False, "motos": False, "mas2": False, "cero": False}
            if cv2.countNonZero(m_azul) > 10: return {"estado": "ABIERTO", "bus": True, "motos": True, "mas2": True, "cero": True}
        else:
            panel_hsv = hsv[int(alto*0.10):int(alto*0.45), int(ancho*0.15):int(ancho*0.85)]
            m_roja = cv2.inRange(panel_hsv, np.array([0, 100, 130]), np.array([10, 255, 255]))
            m_azul = cv2.inRange(panel_hsv, np.array([90, 100, 130]), np.array([140, 255, 255]))
            
            if cv2.countNonZero(m_roja) > 15: return {"estado": "CERRADO", "bus": False, "motos": False, "mas2": False, "cero": False}
            if cv2.countNonZero(m_azul) > 15: return {"estado": "ABIERTO", "bus": True, "motos": True, "mas2": True, "cero": True}

        return {"estado": "DESCONOCIDO", "bus": False, "motos": False, "mas2": False, "cero": False}
    except:
        return {"estado": "ERROR", "bus": False, "motos": False, "mas2": False, "cero": False}