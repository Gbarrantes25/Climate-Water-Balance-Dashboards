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



pg.run()
