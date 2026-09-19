# Climate & Water Balance Dashboards 💻
## 📃 Descripción General
Proyecto de análisis y visualización de rendimiento académico desarrollado en Python con Streamlit, diseñado para explorar el desempeño de alumnos por curso, aula y periodo de manera interactiva.
Este proyecto transforma un modelo de datos dimensional (calendario, alumnos, cursos y notas) en un dashboard visual mediante:
- 📊 Modelo Dimensional: Tablas de dimensión y hechos generadas y relacionadas por claves.
- 🧹 Limpieza de Datos: Tratamiento de valores nulos y normalización de columnas.
- 📈 Agrupaciones y Pivotes: Promedios por curso, por alumno y tablas pivote.
- 🎨 Visualizaciones: Histograma, boxplot, violinplot, heatmap, lineplot, barplot, regplot y countplot.
- 🖱️ Filtros Interactivos: Multiselectores por aula con actualización aislada mediante `st.fragment`.

## 📊 Contenido del proyecto
- Sección de Tablas de Dimensión y Hechos: modelo de datos base (calendario, alumnos, cursos, notas).
- Sección de Limpieza de Datos: imputación de nulos y renombrado de columnas.
- Sección de Agrupaciones: promedios por curso y por alumno-curso.
- Sección de Join y Pivote: unión de tablas y tabla pivote alumno x curso.
- Secciones de Visualización (6 a 12): distribución de notas, comparativos por curso, mapa de calor, evolución temporal, ranking, relación nota-edad y aprobados vs desaprobados.

## 🛠️ Herramientas y Tecnologías Utilizadas
- Desarrollo y Visualización: Python, Streamlit.
- Librerías: 
  - `pandas` y `numpy` para manipulación y generación de datos.
  - `matplotlib` y `seaborn` para visualización estadística.
  - `streamlit` para el dashboard interactivo.
- Fuente de Datos: Datos sintéticos generados con semilla fija (`np.random.seed`) para reproducibilidad.
- Lenguaje: Python 3.

## ⚙️ Configuración del Entorno
- Software Necesario: Python 3.10+ y las librerías `streamlit`, `pandas`, `numpy`, `matplotlib` y `seaborn`.
- Instalación:
  - Clonar el repositorio.
  - Instalar dependencias: `pip install streamlit pandas numpy matplotlib seaborn`.
  - Ejecutar el proyecto: `streamlit run Analisis.py`.

## 📂 Estructura del Repositorio
<code>.
  ├── Analisis.py          # Script principal del dashboard en Streamlit
  ├── .python-version      # Versión de python del proyecto
  ├── README.md            # Este archivo
  ├── uv.lock              # Gestor de paquetes del proyecto
  ├── src/
  ├   └── mi_proyecto/
  ├       └── __init__.py  # Puerta de entrada del proyecto
  └── pyproject.toml       # Gestor y configuración de dependencias
</code>

## ✅ Características Principales
- Modelo Dimensional: Tablas de calendario, alumnos, cursos y hechos (notas) relacionadas por Id.
- Optimización de Rendimiento:
  - `@st.cache_data` para evitar recalcular la generación y el merge de datos en cada interacción.
  - `@st.fragment` para que cada gráfico con filtro se actualice de forma aislada, sin recargar todo el dashboard.
- Visualizaciones interactivas filtradas por aula: histograma, lineplot y countplot.
- Documentación embebida: cada sección muestra su propio código fuente con `inspect.getsource()`.

## 🖼️ Vistas Previas del proyecto
<details>
  <summary>Dashboard</summary>
    <img width="1300" height="958" alt="image" src="https://github.com/user-attachments/assets/96720cad-fe68-40bf-ab9d-2361c6f01d62" />
    <img width="1368" height="1079" alt="image" src="https://github.com/user-attachments/assets/6d58778a-c468-4f77-b680-8ee42cd5a99c" />
</details>

## 👤 Autor
- Giancarlo Barrantes
- Lima, Perú
- [Linkedin](https://www.linkedin.com/in/gb25/)
