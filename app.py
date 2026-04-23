import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from src.dgt_utils import descargar_foto_dgt
import time
import requests
# Fíjate que hemos quitado la función que daba el ImportError
from src.processor import analizar_trafico, analizar_panel_automatico
 
st.set_page_config(page_title="BUS-VAO A-6", layout="wide", initial_sidebar_state="expanded")

@st.cache_data(ttl=900) # Ahora se actualiza cada 15 minutos
def obtener_clima(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        res = requests.get(url, timeout=5).json()
        temp = res['current_weather']['temperature']
        code = res['current_weather']['weathercode']
        
        # Miramos si es de noche (entre las 22:00 y las 06:00)
        hora_actual = time.localtime().tm_hour
        es_noche = hora_actual >= 22 or hora_actual < 6
        
        alerta = ""
        if code in [0, 1]: estado = "☀️ Despejado"
        elif code in [2, 3]: estado = "⛅ Nublado"
        elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]: 
            estado = "🌧️ Lluvia"
            # Si llueve y NO es de noche, entonces sí ponemos la alerta
            if not es_noche:
                alerta = "⚠️ Posible retención por clima"
        else: estado = "🌤️ Normal"
        
        return f"{estado} ({temp}ºC)", alerta
    except:
        return "🌤️ Info no disponible", ""

# --- BLOQUE DE ESTILO CSS ---
st.markdown("""
<style>
    /* Fondo oscuro moderno en toda la app */
    .stApp, .main { background-color: #0f172a; color: #f8fafc; }
    
    /* Eliminar el hueco blanco superior */
    header {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    /* Barra lateral estilo y scroll unificado */
    [data-testid="stSidebar"] { 
        background-color: #1e293b; 
        border-right: 1px solid #334155; 
    }
    
    /* Forzar que el scroll sea global (menos independiente) */
    .stApp > header { background-color: transparent; }
    
    /* Títulos en azul cian */
    h1, h2, h3 { color: #38bdf8 !important; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* Pestañas (Tabs) */
    .stTabs [data-baseweb="tab-list"] { background-color: #1e293b; border-radius: 10px; padding: 5px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.3); }
    .stTabs [data-baseweb="tab"] { color: #94a3b8; border-radius: 8px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #38bdf8; color: white !important; font-weight: 800; }
    
    /* Bordes redondeados en las fotos */
    [data-testid="stImage"] img { border-radius: 12px; box-shadow: 0 8px 16px -4px rgba(0,0,0,0.6); border: 2px solid #334155; }
    
    /* Textos blancos justificados en alertas y sidebar */
    .stAlert p, [data-testid="stSidebar"] p, [data-testid="stSidebar"] div { color: white !important; text-align: justify; }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (SIDEBAR) ---
col_lateral, col_principal = st.columns([1, 3], gap="large")
with col_lateral:
    clima_rozas, alerta_roz = obtener_clima(40.49, -3.87)
    clima_madrid, alerta_mad = obtener_clima(40.41, -3.70)
    
    alerta_html = ""
    if alerta_roz or alerta_mad:
        alerta_html = f'<div style="background-color: rgba(248, 113, 113, 0.2); border-left: 4px solid #f87171; padding: 8px; margin-top: 15px; border-radius: 4px;"><span style="color: #f87171; font-size: 0.85em; font-weight: bold;">{alerta_roz or alerta_mad}</span></div>'

    st.markdown(f"""
<div style="background:#1e293b; padding:20px; border-radius:15px; border:1px solid #334155; margin-bottom: 15px;">
    <h4 style="margin-top:0; color: #38bdf8;">☁️ Meteorología</h4>
    <div style="display: flex; justify-content: space-between; margin-bottom: 8px; border-bottom: 1px solid #334155; padding-bottom: 5px;">
        <span style="color: #94a3b8; font-size: 0.9em;">Las Rozas:</span>
        <span style="color: white; font-weight: bold; font-size: 0.95em;">{clima_rozas}</span>
    </div>
    <div style="display: flex; justify-content: space-between;">
        <span style="color: #94a3b8; font-size: 0.9em;">Madrid:</span>
        <span style="color: white; font-weight: bold; font-size: 0.95em;">{clima_madrid}</span>
    </div>
    {alerta_html}
</div>
""", unsafe_allow_html=True)
    st.markdown("""
<style>
    /* Esto arregla el botón para que sea azul con letras negras legibles */
    div.stButton > button {
        background-color: #38bdf8 !important;
        color: #0f172a !important;
        font-weight: bold !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px !important;
    }
    div.stButton > button:hover {
        background-color: #0ea5e9 !important;
        color: white !important;
    }
</style>

<div style="background-color: #1e293b; padding: 25px; border-radius: 15px; border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-top: 15px;">
    <h3 style="color: #38bdf8; margin-top: 0;">ℹ️ Información</h3>
    <p style="color: #94a3b8; font-size: 0.9em; text-align: justify;">
        <strong>¿Qué es el BUS-VAO?</strong><br>
        Calzada reversible en la A-6 reservada para autobuses, motos, vehículos con 2 o más ocupantes y etiqueta CERO emisiones (cuando lo indique el cartel luminoso en las entradas).
    </p>
    <hr style="border-color: #334155; margin: 15px 0;">
    <h4 style="color: #38bdf8; margin-bottom: 10px;">🚥 Tráfico</h4>
    <div style="background-color: #0f172a; padding: 10px; border-radius: 8px;">
        <span style="color: #4ade80;">🟢 Fluido</span><br>
        <span style="color: #facc15;">🟡 Denso</span><br>
        <span style="color: #f87171;">🔴 Retenciones</span>
    </div>
    <hr style="border-color: #334155; margin: 15px 0;">
    <h4 style="color: #38bdf8; margin-bottom: 10px;">⏱️ Horarios (L-V)</h4>
    <div style="background-color: #0f172a; padding: 10px; border-radius: 8px; font-size: 0.9em;">
        <p style="margin: 0; color: #f8fafc;">➡️ <b>Hacia Madrid:</b><br><span style="color: #94a3b8;">06:00h - 11:30h</span></p>
        <p style="margin: 0; color: #f8fafc;">➡️ <b>Cambio de Sentido:</b><br><span style="color: #94a3b8;">11:30h - 13:30h</span></p>
        <p style="margin: 10px 0 0 0; color: #f8fafc;">⬅️ <b>Hacia Las Rozas:</b><br><span style="color: #94a3b8;">13:30h - 22:00h</span></p>
    </div>
</div>
""", unsafe_allow_html=True)
with col_principal:
 
    st.title("Información sobre el BUS VAO de la A-6")
    
    tab_madrid, tab_rozas = st.tabs(["➡️ DIRECCIÓN MADRID", "➡️ DIRECCIÓN LAS ROZAS"])
    
    def mostrar_bloque_direccion(cam_panel, diccionario_cams_trafico, tipo_panel="VETERINARIA"):
        t_col1, t_col2 = st.columns([4, 1])
        with t_col1: st.subheader("🔳 Estado del Carril BUS-VAO")
        with t_col2: 
            if st.button("🔄 Actualizar", key=tipo_panel):
                with st.spinner("🔄 Cargando..."):
                    time.sleep(1) # Esto hace que el usuario vea la animación
                    st.rerun()
        img_p = descargar_foto_dgt(cam_panel)
        if img_p:
            c1, c2 = st.columns([2, 1])
            with c1: st.image(img_p, width="stretch")
            with c2:
                data = analizar_panel_automatico(img_p, tipo_panel)
                if data['estado'] == "ABIERTO": st.success(f"🟢 {data['estado']}")
                elif data['estado'] == "CERRADO": st.error(f"🔴 {data['estado']}")
                else: st.warning(f"⚠️ {data['estado']}")
                
                st.write("---")
                def tag(l, v):
                    if data['estado'] == "DESCONOCIDO": st.info(f"❓ {l}")
                    else: st.write(f"{'✅' if v else '❌'} {l}")
                tag("BUS", data['bus']); tag("MOTOS", data['motos'])
                tag("🚗 +2 OCUP", data['mas2']); tag("🔌 CERO", data['cero'])
    
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
        st.markdown("---")
    st.caption("⚠️ **Aviso:** Este sistema de visión artificial puede cometer errores por deslumbramientos o baja visibilidad. Presta atención siempre a las imágenes de la carretera.")