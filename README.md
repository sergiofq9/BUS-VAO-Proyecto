# BUS-VAO Proyecto

## Descripción

Este proyecto es una aplicación web desarrollada con Streamlit que proporciona información en tiempo real sobre el estado del carril BUS-VAO en la autopista A-6 (Madrid-Las Rozas). Utiliza visión artificial con YOLOv8 para analizar imágenes de cámaras de tráfico de la DGT (Dirección General de Tráfico) y determinar:

- El estado del carril reversible (abierto/cerrado).
- Los niveles de tráfico en diferentes puntos kilométricos.
- Información sobre los vehículos autorizados (autobuses, motos, vehículos con 2+ ocupantes, cero emisiones).

## Características

- **Monitoreo en tiempo real**: Actualización automática de imágenes desde cámaras DGT.
- **Análisis de visión artificial**: Detección automática del estado del panel indicador.
- **Conteo de vehículos**: Análisis de densidad de tráfico usando YOLOv8.
- **Interfaz intuitiva**: Diseño moderno con pestañas para ambas direcciones.
- **Información horaria**: Horarios de funcionamiento del BUS-VAO.

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
- **Botón Actualizar**: Refresca las imágenes y análisis
- **Indicadores de estado**: Verde (abierto), Rojo (cerrado), Amarillo (desconocido)

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
- **requests**: Para descargar imágenes de las cámaras DGT
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

## Aviso importante

⚠️ **Esta aplicación es solo informativa y puede cometer errores debido a condiciones de iluminación, deslumbramientos o baja visibilidad. Siempre verifica las imágenes reales de la carretera y sigue las indicaciones oficiales de la DGT.**

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo LICENSE para más detalles.

## Contribuidores

- [Sergio Fernández Quintela] - Desarrollador principal

## Contacto

Para preguntas o sugerencias, por favor abre un issue en el repositorio de GitHub.