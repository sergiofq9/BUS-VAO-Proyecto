import streamlit as st
import requests
from PIL import Image
from io import BytesIO
from src.dgt_utils import descargar_foto_dgt
import time
import requests
from src.processor import analizar_trafico, analizar_panel_automatico
 
st.set_page_config(page_title="BUS-VAO A-6", layout="wide", initial_sidebar_state="expanded")

@st.cache_data(ttl=3600)
def obtener_eventos_reales_madrid():
    try:
        url = "https://datos.madrid.es/egob/catalogo/206974-0-agenda-eventos-culturales-100.json"
        res = requests.get(url, timeout=10)
        datos = res.json()
        
        eventos_hoy = []
        # Filtros mucho más estrictos (evitamos atrapar teatros de barrio)
        recintos_rojo = ["wizink", "bernabéu", "bernabeu", "metropolitano", "madrid arena", "caja mágica"]
        recintos_amarillo = ["ifema", "palacio de deportes", "auditorio nacional", "teatro real", "recinto ferial"]
        
        for item in datos.get('@graph', []):
            titulo = item.get('title', '').lower()
            lugar = item.get('address', {}).get('area', {}).get('street-address', 'Madrid').lower()
            hora = item.get('dtstart', '').split('T')[-1][:5]
            
            impacto = "Bajo"
            
            for r in recintos_rojo:
                if r in lugar or r in titulo:
                    impacto = "Alto"
                    break
                    
            if impacto == "Bajo":
                for a in recintos_amarillo:
                    if a in lugar or a in titulo:
                        impacto = "Medio"
                        break
            
            # 🚨 LA CLAVE: Solo guardamos los eventos masivos, descartamos los locales (Bajo)
            if impacto in ["Alto", "Medio"]:
                eventos_hoy.append({
                    "titulo": item.get('title', ''), 
                    "lugar": item.get('address', {}).get('area', {}).get('street-address', 'Madrid'),
                    "hora": hora,
                    "impacto": impacto
                })
            
        return eventos_hoy[:5] # Máximo 5 para no hacer una lista kilométrica
    except:
        return []

@st.cache_data(ttl=300) # Se actualiza cada 5 minutos
def obtener_incidencias_a6():
    try:
        # Fuente oficial: Punto de Acceso Nacional de Información de Tráfico
        url = "https://www.dgt.es/estaticos/movilidad/incidencias-movilidad.json"
        res = requests.get(url, timeout=10).json()
        incidencias = res.get('incidencias', [])
        
        avisos = []
        for inc in incidencias:
            # Filtramos solo la A-6 en Madrid
            if inc.get('carretera') == 'A-6' and inc.get('provincia') == 'MADRID':
                tipo = inc.get('tipo', 'AVISO')
                descripcion = inc.get('descripcion', 'Sin detalles')
                pk_ini = inc.get('pk_ini', '?')
                pk_fin = inc.get('pk_fin', '?')
                
                # Asignamos un emoji según el tipo
                emoji = "⚠️"
                if "ACCIDENTE" in tipo.upper(): emoji = "💥"
                elif "OBRAS" in tipo.upper(): emoji = "🚧"
                elif "METEOROL" in tipo.upper(): emoji = "❄️"
                
                avisos.append({
                    "icono": emoji,
                    "titulo": tipo,
                    "info": f"KM {pk_ini} al {pk_fin}: {descripcion}"
                })
        return avisos
    except:
        return []

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

    st.markdown("  ")
    st.markdown("  ")

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
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    incidencias_reales = obtener_incidencias_a6()
    
    # Construimos el HTML sin triples comillas para evitar fallos de Streamlit
    html_dgt = '<div style="background:#1e293b; padding:20px; border-radius:15px; border:1px solid #334155; margin-bottom: 15px;">'
    html_dgt += '<h4 style="margin-top:0; color: #38bdf8;">🚦 Avisos DGT (A-6)</h4>'
    
    if not incidencias_reales:
        html_dgt += '<div style="background-color: rgba(74, 222, 128, 0.15); border-left: 4px solid #4ade80; padding: 10px; border-radius: 4px;"><span style="color: #4ade80; font-weight: bold; font-size: 0.9em;">✅ Sin incidencias reportadas ahora mismo.</span></div>'
    else:
        for aviso in incidencias_reales:
            html_dgt += f'<div style="background: rgba(248, 113, 113, 0.1); padding: 12px; border-radius: 10px; border-left: 5px solid #f87171; margin-bottom: 10px;"><span style="font-size: 1.2em;">{aviso["icono"]}</span> <b style="color: white;">{aviso["titulo"]}</b><br><span style="color: #cbd5e1; font-size: 0.85em;">{aviso["info"]}</span></div>'
            
    html_dgt += '</div>'
    
    st.markdown(html_dgt, unsafe_allow_html=True)

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
        <span style="color: #ffa500;">🟠 Retenciones</span><br>
        <span style="color: #f87171;">🔴 Atasco Importante</span><br>
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
 
    st.title("Información A-6: Madrid - Las Rozas")

    # --- ALERTA GLOBAL DE EVENTOS (Desplegable) ---
    eventos = obtener_eventos_reales_madrid()

    if eventos:
        # Si hay eventos, sale un recuadro que se puede desplegar
        with st.expander(f"📅 Atención: Hay {len(eventos)} eventos hoy en Madrid que pueden afectar al tráfico"):
            for ev in eventos:
                es_alto = "🔴" if ev['impacto'] == "Alto" else "🟡"
                st.markdown(f"{es_alto} **{ev['hora']} | {ev['titulo']}** 📍 *{ev['lugar']}*")
    else:
        # Si no hay eventos, sale un mensaje verde fijo muy discreto
        st.success("✅ Hoy no hay eventos multitudinarios que afecten al tráfico.")

    
# --- AQUÍ YA VAN TUS PESTAÑAS (Solo dejas las dos de las cámaras) ---
       
    tab_madrid, tab_rozas= st.tabs(["➡️ DIRECCIÓN MADRID", "➡️ DIRECCIÓN LAS ROZAS"])

    
    
    def mostrar_bloque_direccion(cam_panel, diccionario_cams_trafico, tipo_panel="VETERINARIA"):
    # Título limpio
        st.subheader("🔳 Estado del Carril BUS-VAO")
                    
        img_p = descargar_foto_dgt(cam_panel)
        if img_p:
            c1, c2 = st.columns([2, 1])
            
            with c1: 
                # 1. ARREGLO DEL WARNING: Usamos el comando moderno que pide Streamlit
                st.image(img_p, use_container_width=True)
            
            with c2:
                # 2. BAJAR EL BLOQUE: Metemos unos espacios invisibles para empujar hacia abajo
                st.write("")
                
                data = analizar_panel_automatico(img_p, tipo_panel)
                if data['estado'] == "ABIERTO": st.success(f"🟢 {data['estado']}")
                elif data['estado'] == "CERRADO": st.error(f"🔴 {data['estado']}")
                else: st.warning(f"⚠️ {data['estado']}")
                
                st.write("---")
                
                col_a, col_b = st.columns(2)
                
                def tag_nativo(col, label, is_open):
                    if data['estado'] == "DESCONOCIDO":
                        col.info(f"❓ {label}")
                    elif is_open:
                        col.success(f"✅ {label}")
                    else:
                        col.error(f"❌ {label}")

                with col_a:
                    tag_nativo(col_a, "BUS", data.get('bus', False))
                    tag_nativo(col_a, "🚗 +2 OCUP", data.get('mas2', False))
                    
                with col_b:
                    tag_nativo(col_b, "MOTOS", data.get('motos', False))
                    tag_nativo(col_b, "🔌 CERO EMIS.", data.get('cero', False))
                
                st.write("") 
                if st.button("🔄 Actualizar", key=tipo_panel, use_container_width=True):
                    with st.spinner("🔄 Cargando..."):
                        time.sleep(1)
                        st.rerun()    
            st.markdown("---")
            st.subheader("🚥 Niveles de Tráfico")
            
            cols = st.columns(3)
        i = 0
        for nombre_km, url in diccionario_cams_trafico.items():
            img_t = descargar_foto_dgt(url)
            if img_t:
                nivel, count, hay_trafico = analizar_trafico(img_t)
                with cols[i % 3]:
                    # Usamos un contenedor para forzar que el texto vaya estrictamente debajo
                    with st.container():
                        st.image(img_t, caption=nombre_km, use_container_width=True)
                        
                        if nivel in ["Rojo", "Negro"]: 
                            st.markdown('<div style="margin-top: -15px; margin-bottom: 30px; position: relative; z-index: 2; background-color: rgba(248, 113, 113, 0.15); padding: 8px; border-radius: 6px; border-left: 4px solid #f87171;"><span style="color: #f87171; font-weight: bold;">🔴 Tráfico: Atasco Importante</span></div>', unsafe_allow_html=True)
                        elif nivel == "Naranja": 
                            st.markdown('<div style="margin-top: -15px; margin-bottom: 30px; position: relative; z-index: 2; background-color: rgba(249, 115, 22, 0.15); padding: 8px; border-radius: 6px; border-left: 4px solid #f97316;"><span style="color: #f97316; font-weight: bold;">🟠 Tráfico: Retenciones</span></div>', unsafe_allow_html=True)
                        elif nivel == "Amarillo": 
                            st.markdown('<div style="margin-top: -15px; margin-bottom: 30px; position: relative; z-index: 2; background-color: rgba(250, 204, 21, 0.15); padding: 8px; border-radius: 6px; border-left: 4px solid #facc15;"><span style="color: #facc15; font-weight: bold;">🟡 Tráfico: Denso</span></div>', unsafe_allow_html=True)
                        else: 
                            st.markdown('<div style="margin-top: -15px; margin-bottom: 30px; position: relative; z-index: 2; background-color: rgba(74, 222, 128, 0.15); padding: 8px; border-radius: 6px; border-left: 4px solid #4ade80;"><span style="color: #4ade80; font-weight: bold;">🟢 Tráfico: Fluido</span></div>', unsafe_allow_html=True)
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
    # 1. EL CSS MÁGICO QUE OBLIGA A FLOTAR A LOS WIDGETS
# =========================================================
# BOTONES FLOTANTES (CALCULADORA Y SUGERENCIAS)
# =========================================================

# 1. CSS de Francotirador (Solo mueve nuestros botones)
st.markdown("""
<style>
    /* Escondemos las marcas para que no se vean en la pantalla */
    .marca-izq, .marca-der { display: none; }

    /* Forzamos al elemento que va justo DESPUÉS de la marca izquierda a ir a la esquina */
    div[data-testid="stVerticalBlock"] > div:has(.marca-izq) + div {
        position: fixed !important;
        bottom: 20px !important;
        left: 20px !important;
        z-index: 99999 !important;
    }
    /* Diseño del botón rectangular (Calculadora) */
    div[data-testid="stVerticalBlock"] > div:has(.marca-izq) + div button {
        border-radius: 10px !important;
        background-color: #1e293b !important;
        border: 2px solid #38bdf8 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5) !important;
        font-weight: bold !important;
    }

    /* Forzamos al elemento que va justo DESPUÉS de la marca derecha a ir a la esquina */
    div[data-testid="stVerticalBlock"] > div:has(.marca-der) + div {
        position: fixed !important;
        bottom: 20px !important;
        right: 20px !important;
        z-index: 99999 !important;
    }
    /* Diseño del botón circular (Asistente Sugerencias) */
    div[data-testid="stVerticalBlock"] > div:has(.marca-der) + div button {
        border-radius: 50% !important;
        width: 65px !important;
        height: 65px !important;
        font-size: 30px !important;
        background-color: #1e293b !important;
        border: 2px solid #38bdf8 !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.5) !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
</style>
""", unsafe_allow_html=True)


# 2. BOTÓN IZQUIERDO (Calculadora Moderna)
st.markdown('<span class="marca-izq"></span>', unsafe_allow_html=True)
with st.popover("⏱️ Estimación de tu tiempo"):
    
    st.markdown("""
    <style>
        @keyframes bajaTitulo { 0% { opacity: 0; transform: translateY(-20px); } 100% { opacity: 1; transform: translateY(0); } }
        @keyframes subeCont { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
        
        .tit-anim { animation: bajaTitulo 0.5s ease-out forwards; color: #38bdf8; text-align: center; margin: 0 0 15px 0; font-size: 1.5em; font-weight: bold;}
        .stSelectbox, div[data-testid="stMetric"] { animation: subeCont 0.6s ease-out forwards; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="tit-anim">Calculadora de Ruta</div>', unsafe_allow_html=True)
    
    # Diccionario con puntos kilométricos para poder calcular cualquier ruta
    puntos = {
        "Atocha / Centro (Madrid)": -5,
        "Moncloa (Madrid)": 0,
        "Ciudad Universitaria": 2,
        "Aravaca (KM 10)": 10,
        "Majadahonda (KM 14)": 14,
        "Las Rozas (KM 18)": 18,
        "Torrelodones (KM 29)": 29,
        "Collado Villalba (KM 40)": 40,
        "Guadarrama (KM 47)": 47
    }
    
    lugares = list(puntos.keys())
    
    # Ahora el usuario puede elegir cualquier combinación (ida o vuelta)
    origen = st.selectbox("📍 Origen:", lugares, index=7) # Villalba por defecto
    destino = st.selectbox("🎯 Destino:", lugares, index=1) # Moncloa por defecto
    
    # LÓGICA REALISTA DE TIEMPOS
    dist_total = abs(puntos[origen] - puntos[destino])
    
    if dist_total == 0:
        st.warning("El origen y el destino son el mismo.")
    else:
        # Velocidades medias realistas ajustadas (Villalba-Moncloa sale a ~34 min en normal)
        vel_normal = 70  # km/h con tráfico denso pero fluido
        vel_vao = 100    # km/h carril despejado
        
        # Penalización de semáforos si se cruza el centro de Madrid
        penalizacion_ciudad = 12 if ("Centro" in origen or "Centro" in destino) else 0
        
        # Cálculo: (Distancia / Velocidad) * 60 minutos
        t_normal = int((dist_total / vel_normal) * 60) + penalizacion_ciudad
        t_vao = int((dist_total / vel_vao) * 60) + penalizacion_ciudad
        
        ahorro = t_normal - t_vao
        
        # Corrección por si el viaje es muy corto
        if ahorro < 0 or dist_total <= 5: 
            t_vao = t_normal
            ahorro = 0
            
        c1, c2 = st.columns(2)
        with c1:
            st.metric("🚗 Carril Normal", f"{t_normal} min")
        with c2:
            delta_color = "normal" if ahorro > 0 else "off"
            st.metric("🚌 BUS-VAO", f"{t_vao} min", delta=f"-{ahorro} min" if ahorro > 0 else "0 min", delta_color=delta_color)
# 3. BOTÓN DERECHO (Sugerencias circular)
# 1. Inicializamos la "memoria" (Pon esto justo encima del botón derecho)
if "sug_texto" not in st.session_state:
    st.session_state.sug_texto = ""
if "sug_enviada" not in st.session_state:
    st.session_state.sug_enviada = False

# 2. Función que se ejecuta al darle al botón
def limpiar_y_enviar():
    if st.session_state.sug_texto.strip() != "":
        st.session_state.sug_enviada = True
        st.session_state.sug_texto = "" # Esto es lo que vacía la caja

# 3. BOTÓN DERECHO (Sugerencias)
st.markdown('<span class="marca-der"></span>', unsafe_allow_html=True)
with st.popover("👩🏻‍💼"):
    st.write("### 💬 Sugerencias")
    
    # La caja de texto ahora está atada a la "memoria" con key="sug_texto"
    st.text_area("Ayúdanos a mejorar la App:", key="sug_texto")
    
    # El botón llama a la función de arriba antes de recargar la página
    st.button("Enviar", on_click=limpiar_y_enviar)
    
    # Mensaje de éxito con colores forzados para que se lea siempre
    if st.session_state.sug_enviada:
        st.markdown("""
        <div style="background-color: #d1fae5; color: #065f46; padding: 10px; border-radius: 5px; font-weight: bold; text-align: center; margin-top: 10px;">
            ✅ Sugerencia registrada. ¡Gracias!
        </div>
        """, unsafe_allow_html=True)