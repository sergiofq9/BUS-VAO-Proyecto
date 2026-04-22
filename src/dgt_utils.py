import requests
from PIL import Image
from io import BytesIO

# Diccionario de cámaras (Nombres sincronizados)
CAMS_A6_VAO = {
    "A-6 km 18.2 (Las Rozas)": "https://infocar.dgt.es/idioma/es/informacion-trafico/camaras/ficheros/6.18.2.jpg",
    "A-6 km 10.6 (Pozuelo)": "https://infocar.dgt.es/idioma/es/informacion-trafico/camaras/ficheros/6.10.6.jpg",
    "A-6 km 6.5 (Puerta de Hierro)": "https://infocar.dgt.es/idioma/es/informacion-trafico/camaras/ficheros/6.6.5.jpg"
}

def descargar_foto_dgt(url):
    """Descarga la imagen de la DGT saltándose los bloqueos básicos."""
    # Cabeceras más completas para simular un navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://infocar.dgt.es/ece/',
        'Accept': 'image/avif,image/webp,image/apng,image/*,*/*;q=0.8'
    }
    try:
        # Añadimos verify=False por si los certificados de la DGT dan problemas
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status() # Lanza error si no es un 200 OK
        return Image.open(BytesIO(response.content))
    except Exception as e:
        # Ahora lo imprimimos en la terminal para poder leer el error exacto
        print(f"⚠️ Error DGT en {url}: {e}")
        return None