import streamlit as st
from pathlib import Path

raiz = Path(__file__).resolve().parent
dir_logo = (raiz / "src" /"assets" / "logo.svg").as_posix()
dir_inicio = str(raiz / "src" / "pages" / "Inicio.py")
dir_anual = str(raiz / "src" / "pages" / "Analisis_Anual.py")
dir_ciudades = str(raiz / "src" / "pages" / "Estados_Ciudades.py")

# Configurando página
st.set_page_config(
    page_title="Análisis Histórico Climatológico",
    page_icon=dir_logo,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Enrutamiento
logo = st.logo(image=dir_logo, size="large")
inicio = st.Page(dir_inicio, title="Inicio", default=True)
anual = st.Page(dir_anual, title="Análisis Anual")
ciudades = st.Page(dir_ciudades, title="Estados & Ciudades")
documentacion = st.Page("https://github.com/Gbarrantes25", title="Documentación")

pg = st.navigation(
    [inicio, anual, ciudades, documentacion],
    position="top",
)

if pg.title == "Inicio":
    st.markdown(
        """
        <style>
            /* Elimina el contenedor del sidebar por completo */
            section[data-testid="stSidebar"] {
                display: none !important;
                width: 0px !important;
            }
            
            /* Oculta el botón flotante superior izquierdo (flecha <<) */
            button[data-testid="stSidebarCollapseButton"] {
                display: none !important;
            }
            
            /* Fuerza a que el bloque principal use el 100% real sin padding izquierdo residual */
            .stMainBlockContainer {
                max-width: 100% !important;
                padding-left: 5rem !important; /* Ajusta según prefieras el margen de tu diseño */
                padding-right: 5rem !important;
            }
            
            /* Ajusta la raíz de la app multipágina para remover el split layout */
            div[data-testid="stAppViewBlockContainer"] {
                width: 100% !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

pg.run()
