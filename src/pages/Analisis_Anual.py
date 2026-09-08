import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from pages.Inicio import cargar_datos

# Crear título.
st.header(
    "Análisis Interanual de Variables Climatológicas y Balance Hídrico",
    text_alignment="center",
    divider="gray",
)

# Carga de datos
df_extraido = cargar_datos()


# Fragmentamos el contenedor para que no recargue toda la página.
@st.fragment
def contenedor():

    # Titulo sidebar
    titulo_sidebar = st.sidebar.markdown(
        "**Filtros**", text_alignment="center", wrap=True, unsafe_allow_html=True
    )
    # Creamos el selector de temporada.
    selector = st.sidebar.selectbox(
        label="Temporada",
        options=["Todos", "Monzón", "Sequía"],
        key="Filtrar_Monzon",
        width="stretch",
    )

    # Generar df dependiendo del filtro de tenporada (Monzón o Sequpia).
    def validar_monzon():
        if st.session_state.Filtrar_Monzon == "Monzón":
            df = df_extraido.loc[df_extraido["Is_Monsoon"] == True].reset_index(
                drop=True
            )
            return df
        elif st.session_state.Filtrar_Monzon == "Sequía":
            df = df_extraido.loc[df_extraido["Is_Monsoon"] == False].reset_index(
                drop=True
            )
            return df
        else:
            df = df_extraido.copy()
            return df

    # Df acorde al filtro de la tenporada.
    df = validar_monzon()

    # Agrupamos df por año.
    df_ag = (
        df.groupby("Year")
        .agg(
            Temp_Min=("Temp_Min", "median"),
            Temp_Max=("Temp_Max", "median"),
            Sunshine_sec_median=("Sunshine_sec", "median"),
            Daylight_sec_median=("Daylight_sec", "median"),
            Ref_Evapotransp_total=("Ref_Evapotransp_mm", "sum"),
            Precipitation_total=("Precipitation_mm", "sum"),
            Precipitation_median=("Precipitation_mm", "median"),
            Solar_Radiation_min=("Solar_Radiation", "min"),
            Solar_Radiation_max=("Solar_Radiation", "max"),
            Solar_Radiation_median=("Solar_Radiation", "median"),
            Daylight_sec_total=("Daylight_sec", "sum"),
            Sunshine_sec_total=("Sunshine_sec", "sum"),
        )
        .reset_index()
    )

    # Creamos columnas adicionales.
    df_ag["Sunshine_hrs_median"] = round(df_ag["Sunshine_sec_median"] / 3600, 2)
    df_ag["Daylight_hrs_median"] = round(df_ag["Daylight_sec_median"] / 3600, 2)
    df_ag["Thermal_amplitude"] = round(df_ag["Temp_Max"] - df_ag["Temp_Min"], 2)
    df_ag["Temp_Media"] = round((df_ag["Temp_Max"] + df_ag["Temp_Min"]) / 2, 2)

    # Df agrupado correlación
    df_ag_corr = df_ag[
        [
            "Temp_Max",
            "Sunshine_sec_total",
            "Daylight_sec_total",
            "Ref_Evapotransp_total",
            "Solar_Radiation_median",
            "Precipitation_total",
        ]
    ].corr(numeric_only=True)

    # Valor de Irradiancia límite
    radiacion_aceptable = [20] * len(df_ag["Year"])

    # Lineplot de Irradiancia.
    fig_combinado1 = go.Figure()
    radiacion_limite = go.Scatter(
        x=df_ag["Year"],
        y=radiacion_aceptable,
        name="Aceptable mj/m²",
        line={"color": "orange"},
        opacity=0.7,
    )
    radiacion_mediana = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Solar_Radiation_median"],
        name="Promedio mj/m²",
        line={"color": "green", "dash": "dot"},
        mode="lines+markers",
        line_shape="spline",
    )
    radiacion_minima = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Solar_Radiation_min"],
        name="Mínimo mj/m²",
        line={"color": "skyblue"},
        opacity=0.5,
        line_shape="spline",
    )
    radiacion_maxima = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Solar_Radiation_max"],
        name="Máximo mj/m²",
        line={"color": "red"},
        opacity=0.5,
        line_shape="spline",
    )
    fig_combinado1.add_traces(
        [
            radiacion_maxima,
            radiacion_mediana,
            radiacion_minima,
            radiacion_limite,
        ]
    )
    fig_combinado1.update_layout(
        title=f"Análisis del comportamiento histórico de la radiación solar frente al umbral aceptable ({selector} 1940 - 2026)"
    )
    st.plotly_chart(fig_combinado1)

    # Hallazgos Radiación Solar
    with st.popover("Hallazgos", icon="🔍"):
        st.markdown(
            """
            - **Total año**:
                - En lo que va del año se ve una media histórica de radiación solar de **20.84 mj/m²**, superando el máximo histórico y el umbral aceptable de 20 mj/m².
                - Respecto al año 2025 estamos **2.87 mj/m²** por encima en la radiación promedio.
            - **Temporada monzónica**: 
                - En lo que va del año vamos con una radiación solar promedio de **19.11 mj/m²**. Si bien aún no llega al límite, está **3.11 mj/m²** por encima del año 2025.
            - **Temporada de sequía**:
                - En esta temporada hemos llegado a un máximo histórico de radiación promedio de **21.31 mj/m²** superando el umbral, y estamos **2.54 mj/m²** por encima del año 2025.
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Lineplot de Temperaturas.
    fig_combinado2 = go.Figure()
    temperatura_maxima = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Temp_Max"],
        mode="lines",
        line_shape="spline",
        name="Máximo C°",
        line={"color": "red"},
        opacity=0.5,
    )
    amplitud_termica = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Thermal_amplitude"],
        name="Amplitud Térmica C°",
        opacity=0.7,
        line_shape="spline",
        mode="markers",
        marker={
            "color": "orange",
            "size": df_ag["Thermal_amplitude"] * 1.3,
            "sizemode": "diameter",
        },
        # fill="tozeroy",
    )
    temperatura_minima = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Temp_Min"],
        mode="lines",
        line_shape="spline",
        name="Mínimo C°",
        line={"color": "skyblue"},
        opacity=0.5,
    )
    temperatura_media = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Temp_Media"],
        mode="lines",
        line_shape="spline",
        name="Media C°",
        line={"color": "green", "dash": "dot"},
    )
    fig_combinado2.add_traces(
        [temperatura_maxima, temperatura_minima, amplitud_termica, temperatura_media]
    )
    fig_combinado2.update_layout(
        title=f"Evolución histórica de las temperaturas máximas y mínimas promedio anuales ({selector} 1940 - 2026)"
    )
    st.plotly_chart(fig_combinado2)

    # Hallazgos en temperaturas
    with st.popover("Hallazgos", icon="🔍"):
        st.markdown(
            """
            - **Total año**:
                - En lo que va del año, la temperatura alcanzó una media de **27 °C** (máximo histórico). Hay una clara tendencia histórica en subida.
                - Tenemos un aumento de **0.65 °C** respecto al 2025 y **0.20 °C** respecto al 2024.
            - **Temporada monzónica**:
                - En lo que va del año hemos alcanzado un máximo histórico de **29.45 °C**. Sin duda es la tenporada con más temperatura.
                - Hay una diferencia de **1.3 °C** de temperatura respecto al año 2025.
            - **Temporada de sequía**:
                - En esta temporada también alcanzamos una temperatura promedio de **25.65 °C**, otro máximo histórico.
                - Hya una diferencia de **1.0 °C** de temperatura respecto al año 2025.
            """,
            unsafe_allow_html=True,
        )
    st.divider()

    # Lineplot de Duración día y brillo solar.
    fig_combinado3 = go.Figure()
    duracion_brillo_solar_hrs = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Sunshine_hrs_median"],
        line_shape="spline",
        name="Horas de Brillo Solar",
        mode="lines",
        line={"color": "orange"},
    )
    duracion_dia_hrs = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Daylight_hrs_median"],
        line_shape="spline",
        name="Horas diurnas",
        mode="lines",
        line={"color": "green", "dash": "dot"},
        opacity=0.85,
    )
    fig_combinado3.add_traces([duracion_brillo_solar_hrs, duracion_dia_hrs])
    fig_combinado3.update_layout(
        title=f"Comparación histórica entre el promedio diario de brillo solar y las horas diurnas ({selector} 1940 - 2026)"
    )
    st.plotly_chart(fig_combinado3)

    # Hallazgos en Brillo solar
    with st.popover("Hallazgos", icon="🔍"):
        st.markdown(
            """
            - **Total año**:
                - Hay una tendencia al alza en la duración promedio del día y el brillo solar alcanzando máximos históricos.
                - En lo que va del año se registra un promedio de **12.58 horas** diurnas y **11.25 horas de brillo solar**.
                - Hay una diferencia de **25 minutos** de luz diurna y **31 minutos** de brillo solar más respecto al año 2025.
            - **Temporada monzónica**:
                - La duración de la luz diurna promedio alcanzó un máximo histórico de **13.48 horas** y **31 minutos** más respecto al año 2025.
                - Si el brillo solar no llegó a un máximo histórico, si hubo un aumento de **1h y 39 minutos** respecto al 2025.
            - **Temporada de sequía**:
                - Se alcanzó un máximo histórico de horas diurnas promedio **12.06 horas** y **11.28 horas** de brillo solar.
                - En comparación al año 2025, el brillo solar aumentó en **27 minutos** y la luz diurna en **24 minutos**.
            """,
            unsafe_allow_html=True,
        )
    st.divider()

    # Total Evapotranspiración vs Precipitación
    superavit_critico = df_ag["Ref_Evapotransp_total"] * 1.07
    fig_combinado5 = go.Figure()

    precipitacion = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Precipitation_total"],
        marker_color="#498ee8",
        name="Total Precipitación (mm)",
        line_shape="spline",
        fill="tozeroy",
        fillcolor="#498ee8",
        opacity=0.3,
    )
    evapotransp = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Ref_Evapotransp_total"],
        marker_color="#6badef",
        line_shape="spline",
        name="Total Evapotranspiración (mm)",
        fill="tozeroy",
        fillcolor="#6badef",
        opacity=0.3,
    )
    limite = go.Scatter(
        x=df_ag["Year"],
        y=superavit_critico,
        marker_color="#b4d6f8",
        name="Límite de Superávit Hídrico (mm)",
        line_shape="spline",
        fill="tozeroy"
    )

    fig_combinado5.add_traces([evapotransp, limite, precipitacion])
    fig_combinado5.update_layout(
        # barmode="overlay",
        title=f"Balance hídrico histórico ({selector} 1940 - 2026)",
    )
    st.plotly_chart(fig_combinado5)

    # Hallazgos en Balance Hídrico
    with st.popover("Hallazgos", icon="🔍"):
        st.markdown(
            """
            - **Total año**:
                - En lo que va del año hay un déficit general hídrico por **14k mm**. Considerar que en el año 2025 llegamos al superávit hídrico y estuvimos a poco de llegar al límite.
            - **Temporada monzónica**:
                - En lo que va del año el límite del superávit hídrico es de **14.05k mm** y las precipitaciones han alcanzado **23.18k mm**, por lo que tenemos un exceso hídrico por **9.13k mm**. Podemos deducir que hay ciertas inundaciones y que momentáneamente no son tan caóticas a comparación del año 2025 (30.66k mm de desbalance).
            - **Temporada de sequía**:
                - Hay un déficit hídrico por **24k mm**, esperemos superar los **23k mm** de precipitaciones del año 2025, ya que en lo que va del año vamos con **11.95k mm**.
            """,
            unsafe_allow_html=True,
        )
    st.divider()

    # Matriz de correlación
    fig_combinado4 = go.Figure()
    mapa_correlacion = go.Heatmap(
        z=df_ag_corr.values,
        x=df_ag_corr.index,
        y=df_ag_corr.columns,
        colorscale="Blues",
        text=df_ag_corr.values.round(2),
        texttemplate="<b>%{text}</b>",
    )
    fig_combinado4.update_layout(
        xaxis={"tickangle": 270},
        title=f"Mapa de correlación climática ({selector} 1940 - 2026)",
    )
    fig_combinado4.add_traces([mapa_correlacion])
    st.plotly_chart(fig_combinado4)

    # Hallazgos en Balance Hídrico
    with st.popover("Hallazgos", icon="🔍"):
        st.markdown(
            """
            - **Total año**:
                - La precipitación tiene una correlación moderada con la duración del día.
                - La radiación solar media tiene una correlación fuerte (inversa) con la precipitación.
                - La evapotranspiración tiene una correlación fuerte con la duración del día y el brillo solar.
            - **Temporada monzónica**:
                - La precipitación tiene una correlación moderada con la duración del día.
                - La radiación solar media tiene una correlación moderada con la temperatura media, el brillo solar y la evapotranspiración.
                - La evapotranspiración tiene una fuerte correlación con el brillo solar y una moderada correlación con la luz del día.
                - La temperatura máxima tiene una correlación moderada con la radiación solar.
            - **Temporada de sequía**:
                - La radiación solar media tiene una correlación moderada (inversa) con la precipitación.
                - La evapotranspiración tiene una fuerte correlación con el brillo solar y la luz diurna.
            - Nota: 
                - Débil (0.01 - 0.29), moderada (0.30 - 0.69), fuerte (0.70 - 1.00)
            """,
            unsafe_allow_html=True,
        )


contenedor()
