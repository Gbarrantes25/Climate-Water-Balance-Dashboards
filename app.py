import streamlit as st
from pathlib import Path

raiz = Path(__file__).resolve().parent
dir_logo = (raiz / "src" / "assets" / "logo.svg").as_posix()
dir_inicio = str(raiz / "src" / "pages" / "Inicio.py")
dir_anual = str(raiz / "src" / "pages" / "General.py")
dir_ciudades = str(raiz / "src" / "pages" / "Estados_Ciudades.py")
dir_detalles = str(raiz / "src" / "pages" / "Detalles.py")

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
general = st.Page(dir_anual, title="General")
ciudades = st.Page(dir_ciudades, title="Estados & Ciudades")
detalles = st.Page(dir_detalles, title="Detalles")
documentacion = st.Page("https://github.com/Gbarrantes25/Climate-Water-Balance-Dashboards", title="Documentación")

pg = st.navigation(
    [inicio, general, ciudades, detalles, documentacion],
    position="top",
)


pg.run()
