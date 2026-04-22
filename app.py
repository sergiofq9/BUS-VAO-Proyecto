import streamlit as st
from src.dgt_utils import descargar_foto_dgt
from src.processor import analizar_trafico, analizar_panel_gemini

st.set_page_config(page_title="BUS-VAO A-6", layout="wide")

st.title("Información sobre el BUS VAO de la A-6")
# (Mantener el bloque de información superior igual)

tab_madrid, tab_rozas = st.tabs(["➡️ DIRECCIÓN MADRID", "➡️ DIRECCIÓN LAS ROZAS"])

def mostrar_bloque_direccion(cam_panel, diccionario_cams_trafico):
    st.subheader("🔳 Estado del Carril BUS-VAO")
    col_img, col_tags = st.columns([2, 1])
    
    img_p = descargar_foto_dgt(cam_panel)
    if img_p:
        with col_img:
            st.image(img_p, use_container_width=True)
        with col_tags:
            with st.spinner("🧠 Analizando panel..."):
                data = analizar_panel_gemini(img_p)
            
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
    # AHORA ITERAMOS SOBRE EL NOMBRE REAL Y LA URL
    i = 0
    for nombre_km, url in diccionario_cams_trafico.items():
        img_t = descargar_foto_dgt(url)
        if img_t:
            nivel, count, hay_trafico = analizar_trafico(img_t)
            with cols[i % 3]:
                # 1. TÍTULO CORREGIDO
                st.image(img_t, caption=nombre_km)
                
                # 2. DISEÑO LIMPIO SIN CAJAS NI CONTEO DE COCHES
                if nivel in ["Rojo", "Negro"]: st.markdown(f"🔴 **Tráfico:** {nivel}")
                elif nivel == "Naranja": st.markdown(f"🟠 **Tráfico:** {nivel}")
                elif nivel == "Amarillo": st.markdown(f"🟡 **Tráfico:** {nivel}")
                else: st.markdown(f"🟢 **Tráfico:** {nivel}")
                
            i += 1

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
        }
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
        }
    )