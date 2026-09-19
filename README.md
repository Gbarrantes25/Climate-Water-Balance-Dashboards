# Climate & Water Balance Dashboards 💻
## 📃 Descripción General
Proyecto de análisis y visualización climatológica desarrollado en Python con Streamlit y Plotly, diseñado para explorar el comportamiento histórico del clima y el balance hídrico de la India (1940-2026) a nivel país, estado y ciudad de manera interactiva.
Este proyecto transforma un dataset histórico de Kaggle en un dashboard multi-página mediante:
- 🧹 Limpieza y Transformación de Datos: imputación de nulos por mediana (año, estado, ciudad), tipado optimizado (`category`, `float32`, `boolean`) y creación de columnas derivadas (irradiancia, temperatura media, amplitud térmica, balance hídrico).
- 📈 Agrupaciones y Métricas: promedios y totales por año, década, estado y ciudad, con métricas comparativas año contra año.
- 🗺️ Visualizaciones Geográficas: mapas de dispersión (`Scattermap`) de radiación, temperatura, olas de calor y balance hídrico sobre el mapa de la India.
- 📊 Visualizaciones Estadísticas: series de tiempo, barras, histogramas, heatmap de correlación y rankings de ciudades (Top N).
- 🖱️ Filtros Interactivos: selectores de temporada (Monzón/Sequía), estado, ciudad, año y escala temporal con actualización aislada mediante `st.fragment`.

## 📊 Contenido del proyecto
- **Inicio**: presentación del proyecto, carga y limpieza del dataset, objetivos y preguntas de investigación.
- **General**: comportamiento histórico a nivel país de radiación solar, temperatura, brillo/duración del día, balance hídrico (precipitación vs. evapotranspiración) y correlación entre variables climáticas.
- **Estados & Ciudades**: mismas variables climáticas filtradas y comparadas por estado y ciudad, con escala temporal seleccionable (década/año).
- **Detalles**: análisis geoespacial y de ranking por ciudad (radiación, temperatura, días de ola de calor y balance hídrico), con hallazgos y conclusiones por temporada.

## 🛠️ Herramientas y Tecnologías Utilizadas
- Desarrollo y Visualización: Python, Streamlit, Plotly.
- Librerías:
  - `pandas` y `numpy` para manipulación, limpieza y agregación de datos.
  - `plotly` (`graph_objects`) para gráficos interactivos y mapas.
  - `matplotlib` y `seaborn` para apoyo en análisis estadístico.
  - `streamlit` para el dashboard interactivo multi-página.
- Fuente de Datos: dataset histórico climatológico de la India obtenido de Kaggle, almacenado en formato `.parquet`.
- Gestor de Entorno: UV.
- Lenguaje: Python 3.12+.

## ⚙️ Configuración del Entorno
- Software Necesario: Python 3.12+ y las librerías `streamlit`, `pandas`, `numpy`, `plotly`, `matplotlib` y `seaborn`.
- Instalación:
  - Clonar el repositorio.
  - Instalar dependencias con UV: `uv sync`.
  - Ejecutar el proyecto: `streamlit run app.py`.

## 📂 Estructura del Repositorio
<code>.
  ├── app.py                       # Configuración de página y enrutamiento (navegación)
  ├── README.md                    # Este archivo
  ├── uv.lock                      # Gestor de paquetes del proyecto
  ├── pyproject.toml               # Gestor y configuración de dependencias
  └── src/
      ├── assets/
      │   └── logo.svg              # Logo del dashboard
      ├── data/
      │   ├── ClimaHistorico.parquet   # Dataset histórico climatológico
      │   └── Estados.parquet          # Dataset de estados y ciudades
      └── pages/
          ├── Inicio.py               # Carga, limpieza y presentación del proyecto
          ├── General.py              # Análisis general a nivel país
          ├── Estados_Ciudades.py     # Análisis por estado y ciudad
          └── Detalles.py             # Análisis geoespacial y ranking por ciudad
</code>

## ✅ Características Principales
- Enrutamiento multi-página con `st.navigation` y `st.Page`, incluyendo enlace externo a la documentación en GitHub.
- Optimización de Rendimiento:
  - `@st.cache_data` para evitar recalcular la carga y limpieza del dataset en cada interacción.
  - `@st.fragment` para que cada sección con filtros se actualice de forma aislada, sin recargar todo el dashboard.
- Filtros por temporada (Monzón/Sequía), estado, ciudad, año y escala temporal (década/año).
- Mapas geográficos interactivos (`Scattermap`) de radiación, temperatura, olas de calor y balance hídrico sobre la India.
- Comparativos año contra año mediante métricas (`st.metric`) para temperatura, radiación y balance hídrico.
- Hallazgos y conclusiones contextualizadas por temporada en cada sección de análisis.

## 🖼️ Vistas Previas del proyecto
<details>
  <summary>Dashboard</summary>
    <!-- Agregar aquí las capturas de pantalla del dashboard -->
</details>

## 👤 Autor
- Giancarlo Barrantes
- Lima, Perú
- [Linkedin](https://www.linkedin.com/in/gb25/)
