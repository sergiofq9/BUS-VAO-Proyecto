import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from src.dgt_utils import descargar_foto_dgt
 
# Fíjate que hemos quitado la función que daba el ImportError
from src.processor import analizar_trafico, analizar_panel_automatico
 
st.set_page_config(page_title="BUS-VAO A-6", layout="wide", initial_sidebar_state="expanded")

# --- BLOQUE DE ESTILO CSS ---
st.markdown("""
<style>
    /* Fondo oscuro moderno */
    .stApp { background-color: #0f172a; color: #f8fafc; }
    /* Barra lateral */
    [data-testid="stSidebar"] { background-color: #1e293b; border-right: 1px solid #334155; }
    /* Títulos en azul cian */
    h1, h2, h3 { color: #38bdf8 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 10px; padding: 5px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; border-radius: 8px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8; color: #0f172a !important; font-weight: 800; }
    /* Bordes redondeados en las fotos */
    [data-testid="stImage"] img { border-radius: 12px; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.6); border: 2px solid #334155; }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    st.title("ℹ️ Información")
    
    st.markdown("### ❓ ¿Qué es el BUS-VAO?")
    st.info("Calzada reservada para Vehículos de Alta Ocupación (2 o más pasajeros), autobuses, motos y vehículos CERO emisiones.")
    
    st.markdown("---")
    st.markdown("### 🚦 Semáforo de Tráfico")
    st.success("🟢 **Verde:** Tráfico fluido.")
    st.warning("🟡 **Amarillo:** Tráfico denso.")
    st.error("🔴 **Rojo:** Atasco o retenciones.")
    
    st.markdown("---")
    st.markdown("### ⏱️ Horarios Habituales (L-V)")
    st.write("➡️ **Hacia Madrid:** De 06:00h a 11:30h")
    st.write("⬅️ **Hacia Las Rozas:** De 13:30h a 22:00h")
 
st.title("Información sobre el BUS VAO de la A-6")
 
tab_madrid, tab_rozas = st.tabs(["➡️ DIRECCIÓN MADRID", "➡️ DIRECCIÓN LAS ROZAS"])
 
def mostrar_bloque_direccion(cam_panel, diccionario_cams_trafico, tipo_panel="VETERINARIA"):
    st.subheader("🔳 Estado del Carril BUS-VAO")
    col_img, col_tags = st.columns([2, 1])
   
    img_p = descargar_foto_dgt(cam_panel)
    if img_p:
        with col_img:
            st.image(img_p, width="stretch")
        with col_tags:
            with st.spinner("🧠 Analizando panel..."):
                data = analizar_panel_automatico(img_p, tipo_panel=tipo_panel)
           
            if data['estado'] == "ABIERTO":
                st.success(f"🟢 ESTADO: {data['estado']}")
            elif data['estado'] == "CERRADO":
                st.error(f"🔴 ESTADO: {data['estado']}")
            else:
                st.warning(f"⚠️ ESTADO: {data['estado']}")
 
            st.write("---")
            st.write("**Permisos de acceso:**")
           
            def tag_logic(label, value):
                if data['estado'] == "DESCONOCIDO": st.warning(f"❔ {label} (Sin datos)")
                elif value: st.success(f"✅ {label}")
                else: st.error(f"❌ {label}")
 
            tag_logic("BUS", data['bus'])
            tag_logic("MOTOS", data['motos'])
            tag_logic("🚗 +2 OCUP", data['mas2'])
            tag_logic("🔌 CERO EMISIONES", data['cero'])
 
    st.markdown("---")
    st.subheader("🚥 Niveles de Tráfico")
   
    cols = st.columns(3)
    i = 0
    for nombre_km, url in diccionario_cams_trafico.items():
        img_t = descargar_foto_dgt(url)
        if img_t:
            nivel, count, hay_trafico = analizar_trafico(img_t)
            with cols[i % 3]:
                st.image(img_t, caption=nombre_km)
                if nivel in ["Rojo", "Negro"]: st.markdown(f"🔴 **Tráfico:** {nivel}")
                elif nivel == "Naranja": st.markdown(f"🟠 **Tráfico:** {nivel}")
                elif nivel == "Amarillo": st.markdown(f"🟡 **Tráfico:** {nivel}")
                else: st.markdown(f"🟢 **Tráfico:** {nivel}")
            i += 1
 
# --- PESTAÑA LAS ROZAS ---
with tab_rozas:
    mostrar_bloque_direccion(
        "http://infocar.dgt.es/etraffic/data/camaras/864.jpg",
        {
            "Cámara KM 31,5 - TORRELODONES": "http://infocar.dgt.es/etraffic/data/camaras/889.jpg",
            "Cámara KM 24,3 - LAS MATAS": "http://infocar.dgt.es/etraffic/data/camaras/888.jpg",
            "Cámara KM 16,1 - EL PLANTIO": "http://infocar.dgt.es/etraffic/data/camaras/873.jpg",
            "Cámara KM 13,2 - LA FLORIDA": "http://infocar.dgt.es/etraffic/data/camaras/863.jpg",
            "Cámara KM 10,1 - ARAVACA": "http://infocar.dgt.es/etraffic/data/camaras/865.jpg",
            "Cámara KM 6,9 - PUERTA DE HIERRO": "http://infocar.dgt.es/etraffic/data/camaras/1158.jpg"
        },
        "VETERINARIA"
    )
 
with tab_madrid:
    mostrar_bloque_direccion(
        "http://infocar.dgt.es/etraffic/data/camaras/879.jpg",
        {
            "Cámara KM 4,1 - C.UNIVERSITARIA": "http://infocar.dgt.es/etraffic/data/camaras/867.jpg",
            "Cámara KM 5,3 - PALACIO MONCLOA": "http://infocar.dgt.es/etraffic/data/camaras/169741.jpg",
            "Cámara KM 12,4 - POZUELO": "http://infocar.dgt.es/etraffic/data/camaras/876.jpg",
            "Cámara KM 17,2 - LAS ROZAS": "http://infocar.dgt.es/etraffic/data/camaras/893.jpg",
            "Cámara KM 22,9 - ENLACE A-6/M-50": "http://infocar.dgt.es/etraffic/data/camaras/886.jpg",
            "Cámara KM 29 - TORRELODONES": "http://infocar.dgt.es/etraffic/data/camaras/895.jpg"
        },
        "ROZAS"
    )