# BUS-VAO Proyecto

## Descripción

Este proyecto es una aplicación web desarrollada con Streamlit que proporciona información en tiempo real sobre el estado del carril BUS-VAO en la autopista A-6 (Madrid-Las Rozas). Utiliza visión artificial con YOLOv8 para analizar imágenes de cámaras de tráfico de la DGT (Dirección General de Tráfico) y determinar:

- El estado del carril reversible (abierto/cerrado).
- Los niveles de tráfico en diferentes puntos kilométricos.
- Información sobre los vehículos autorizados (autobuses, motos, vehículos con 2+ ocupantes, cero emisiones).

**Nuevas funcionalidades (v5.0.0):**
- **Información meteorológica**: Datos en tiempo real del clima en Las Rozas y Madrid, con alertas automáticas por condiciones que puedan afectar al tráfico.
- **Incidencias de tráfico**: Avisos oficiales de la DGT sobre accidentes, obras y eventos en la A-6.
- **Eventos en Madrid**: Lista de eventos culturales del día con clasificación de impacto en el tráfico.
- **Cierre nocturno automático**: El carril se considera cerrado entre las 22:00 y las 06:00 horas.

## Características

- **Monitoreo en tiempo real**: Actualización automática de imágenes desde cámaras DGT.
- **Análisis de visión artificial**: Detección automática del estado del panel indicador.
- **Conteo de vehículos**: Análisis de densidad de tráfico usando YOLOv8.
- **Interfaz intuitiva**: Diseño moderno con pestañas para ambas direcciones.
- **Información horaria**: Horarios de funcionamiento del BUS-VAO.
- **Datos meteorológicos**: Información del clima en tiempo real con alertas por lluvia.
- **Incidencias de tráfico**: Avisos oficiales de la DGT sobre eventos en la A-6.
- **Eventos culturales**: Lista de eventos en Madrid con impacto potencial en el tráfico.
- **Modo nocturno**: Cierre automático del carril entre las 22:00 y 06:00 horas.

## Instalación

### Prerrequisitos

- Python 3.11 o superior
- Entorno virtual (recomendado)

### Pasos de instalación

1. Clona el repositorio:
```bash
git clone <url-del-repositorio>
cd bus-vao-proyecto
```

2. Crea un entorno virtual:
```bash
python -m venv .venv
```

3. Activa el entorno virtual:
   - En Windows:
   ```bash
   .venv\Scripts\activate
   ```
   - En Linux/Mac:
   ```bash
   source .venv/bin/activate
   ```

4. Instala las dependencias:
```bash
pip install -r requirements.txt
```

5. Descarga el modelo YOLOv8 (incluido en el repositorio como `yolov8n.pt`)

## Uso

### Ejecutar la aplicación

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador predeterminado en `http://localhost:8501`.

### Funcionalidades de la aplicación

- **Pestaña Dirección Madrid**: Muestra el estado del carril VAO hacia Madrid
- **Pestaña Dirección Las Rozas**: Muestra el estado del carril VAO hacia Las Rozas
- **Pestaña Eventos en Madrid**: Lista de eventos culturales del día con clasificación de impacto
- **Botón Actualizar**: Refresca las imágenes y análisis
- **Indicadores de estado**: Verde (abierto), Rojo (cerrado), Amarillo (desconocido)
- **Información meteorológica**: Clima en tiempo real para Las Rozas y Madrid
- **Avisos DGT**: Incidencias oficiales en la A-6

## Estructura del proyecto

```
bus-vao-proyecto/
├── app.py                 # Aplicación principal de Streamlit
├── main.py                # Script de ejemplo simple
├── pyproject.toml         # Configuración del proyecto
├── requirements.txt       # Dependencias de Python
├── yolov8n.pt            # Modelo YOLOv8 pre-entrenado
├── README.md             # Este archivo
└── src/
    ├── __init__.py       # Inicialización del paquete
    ├── dgt_utils.py       # Utilidades para descargar y gestionar datos de cámaras DGT
    └── processor.py      # Procesamiento de imágenes con YOLO y OpenCV
```

## Dependencias

- **streamlit**: Framework web para la interfaz
- **requests**: Para descargar imágenes de las cámaras DGT y consultar APIs externas (meteorología, incidencias, eventos)
- **Pillow**: Procesamiento de imágenes
- **pandas**: Manipulación de datos
- **ultralytics**: Biblioteca YOLOv8 para detección de objetos
- **opencv-python-headless**: Procesamiento de imágenes con OpenCV
- **google-generativeai**: (Opcional, no usado en la versión actual)

## Cómo funciona

### Análisis del panel indicador

La aplicación analiza automáticamente el panel luminoso que indica si el carril VAO está abierto o cerrado. Utiliza procesamiento de color HSV para detectar:

- **Verde/Azul**: Carril abierto
- **Rojo**: Carril cerrado
- **Desconocido**: Cuando no se puede determinar el estado

### Análisis de tráfico

Utiliza YOLOv8 para contar vehículos en las imágenes de las cámaras y clasificar el nivel de tráfico:

- **Verde**: Tráfico fluido (< 12 vehículos)
- **Amarillo**: Tráfico moderado (12-34 vehículos)
- **Naranja**: Tráfico denso (35-44 vehículos)
- **Rojo**: Retenciones (45+ vehículos)

### Información meteorológica

Obtiene datos del clima en tiempo real desde la API de Open-Meteo para Las Rozas y Madrid. Genera alertas automáticas cuando hay lluvia durante el día, ya que puede causar retenciones.

### Incidencias de tráfico

Consulta la API oficial de la DGT para obtener avisos sobre accidentes, obras y otros eventos en la A-6, filtrados para la provincia de Madrid.

### Eventos culturales

Accede al portal de Datos Abiertos del Ayuntamiento de Madrid para obtener la agenda de eventos culturales del día. Clasifica el impacto potencial en el tráfico según la ubicación y tipo de evento.

### Cierre nocturno

Entre las 22:00 y las 06:00 horas, el sistema considera automáticamente el carril cerrado, independientemente del análisis de imagen.

## Aviso importante

⚠️ **Esta aplicación es solo informativa y puede cometer errores debido a condiciones de iluminación, deslumbramientos o baja visibilidad. Siempre verifica las imágenes reales de la carretera y sigue las indicaciones oficiales de la DGT.**

## Registro de cambios

### v5.0.0
- ✅ Integración de información meteorológica en tiempo real
- ✅ Avisos de incidencias de tráfico desde la DGT
- ✅ Lista de eventos culturales en Madrid con impacto en el tráfico
- ✅ Lógica automática de cierre nocturno (22:00 - 06:00)
- ✅ Nueva pestaña de eventos en la interfaz
- ✅ Mejoras en el diseño y usabilidad

### v4.0.0
- ✅ Mejoras en el análisis de tráfico
- ✅ Optimización del procesamiento de imágenes

### v2.0.0
- ✅ Implementación inicial con YOLOv8
- ✅ Análisis automático del panel indicador

### v1.0.0
- ✅ Versión básica con descarga de imágenes DGT

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## Contribuidores

- [Sergio Fernández Quintela] - Desarrollador principal

## Contacto

Para preguntas o sugerencias, por favor abre un issue en el repositorio de GitHub.