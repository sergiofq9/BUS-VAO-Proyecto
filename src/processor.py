import google.generativeai as genai
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
        if conteo < 25: 
            nivel = "Verde"
        elif conteo < 50: 
            nivel = "Amarillo"
        elif conteo < 65: 
            nivel = "Naranja"
        else: 
            nivel = "Rojo"
        
        hay_trafico = "SÍ" if conteo >= 50 else "NO"
        return nivel, conteo, hay_trafico
    except:
        return "Desconocido", 0, "No"
    
llave = st.secrets["GEMINI_API_KEY"]

# 1. Configura tu llave
genai.configure(api_key=llave)

@st.cache_data(ttl=600) 
def analizar_busvao_con_ia(_imagen_pil, tipo_panel): # <-- Añadimos el guion bajo aquí
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        prompt = f"""
        Analiza el panel del BUS-VAO para la dirección: {tipo_panel}.
        Responde SOLO una palabra: 'ABIERTO', 'CERRADO' o 'DESCONOCIDO'.
        """

        # Usamos el nombre con el guion bajo dentro también
        resultado = model.generate_content([prompt, _imagen_pil])
        
        respuesta_texto = resultado.text.strip().upper()
        
        # Simplificamos la respuesta para tu app.py
        estado_final = "ABIERTO" if "ABIERTO" in respuesta_texto else "CERRADO"
        if "DESCONOCIDO" in respuesta_texto: estado_final = "DESCONOCIDO"
        
        return {"estado": estado_final}

    except Exception as e:
        if "429" in str(e):
            return {"estado": "ERROR", "detalle": "Cuota agotada. Espera un poco."}
        return {"estado": "ERROR", "detalle": str(e)}
    try:
        # Seleccionamos el modelo
        model = genai.GenerativeModel('gemini-3.1-flash-image-preview')

        # Usamos el 'tipo_panel' para darle una instrucción más precisa a la IA
        prompt = f"""
        Analiza esta imagen de la A-6. Te estás centrando en el panel del BUS-VAO 
        para la dirección: {tipo_panel}.
        
        Dime si el carril está ABIERTO para esa dirección, CERRADO, o si está 
        abierto para la dirección CONTRARIA.
        
        Responde SOLO con una de estas opciones: 'MADRID', 'LAS ROZAS', 'CERRADO'.
        """

        # Le pasamos la imagen (que ya es un objeto PIL) y el prompt
        resultado = model.generate_content([prompt, _imagen_pil])
        
        return resultado.text.strip().upper()

    except Exception as e:
        return f"ERROR_IA: {str(e)}"    

# --- PRUEBA RÁPIDA ---
# Cámara del km 7.5 de la A-6 (Puente de San Fernando)
url_ejemplo = "https://infocar.dgt.es/idioma/es/camaras/madrid/camara.do?id=128" 
# Nota: Tendrás que buscar la URL directa del .jpg de la cámara