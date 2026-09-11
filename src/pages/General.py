import pandas as pd
import numpy as np
import plotly.graph_objects as go
import streamlit as st
from pages.Inicio import cargar_datos

# Crear título.
st.header(
    "Análisis General de Variables Climatológicas y Balance Hídrico",
    text_alignment="center",
    divider="gray",
)

# Carga de datos
df_extraido = cargar_datos()


# Fragmentamos el contenedor para que no recargue toda la página.
@st.fragment
def contenedor():

    # Titulo sidebar
    st.sidebar.markdown(
        "**Filtros**", text_alignment="center", wrap=True, unsafe_allow_html=True
    )
    # Creamos el selector de temporada.
    selector = st.sidebar.selectbox(
        label="Temporada",
        options=["Todos", "Monzón", "Sequía"],
        key="Filtrar_Monzon_General",
        width="stretch",
    )

    # Generar df dependiendo del filtro de tenporada (Monzón o Sequpia).
    def validar_monzon():
        if st.session_state.Filtrar_Monzon_General == "Monzón":
            df = df_extraido.loc[df_extraido["Is_Monsoon"] == True].reset_index(
                drop=True
            )
            return df
        elif st.session_state.Filtrar_Monzon_General == "Sequía":
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

    col1, col2, col3, col4 = st.columns(4)
    def metricas_calculadas():
            # Temp Min
            temp_min_ly = df.loc[
                df["Year"] == 2025
            ]["Temp_Min"].median()
            temp_min_actual = df.loc[
                df["Year"] == 2026
            ]["Temp_Min"].median()
            temp_min_comparativo = temp_min_actual - temp_min_ly
    
            # Temp Max
            temp_max_ly = df.loc[
                df["Year"] == 2025
            ]["Temp_Max"].median()
            temp_max_actual = df.loc[
                df["Year"] == 2026
            ]["Temp_Max"].median()
            temp_max_comparativo = temp_max_actual - temp_max_ly
    
            # Temp Media
            temp_media_ly = (
                df.loc[df["Year"] == 2025][
                    "Temp_Max"
                ].median()
                + df.loc[df["Year"] == 2025][
                    "Temp_Min"
                ].median()
            ) / 2
            temp_media_actual = (
                df.loc[df["Year"] == 2026][
                    "Temp_Max"
                ].median()
                + df.loc[df["Year"] == 2026][
                    "Temp_Min"
                ].median()
            ) / 2
            temp_media_comparativo = temp_media_actual - temp_media_ly
    
            # Radiación Solar
            radiacion_ly = df.loc[
                df["Year"] == 2025
            ]["Solar_Radiation"].median()
            radiacion_actual = df.loc[
                df["Year"] == 2026
            ]["Solar_Radiation"].median()
            radiacion_comparativo = radiacion_actual - radiacion_ly
    
            # Función para horas y minutos
            def horas_minutos(horas_decimales):
                horas = int(horas_decimales)
                minutos = int((horas_decimales - horas) * 60)
                return f"{horas} h y {minutos} m"
    
            # Brillo solar
            brillo_solar_ly = (
                df[df["Year"] == 2025][
                    "Sunshine_sec"
                ].median()
                / 3600
            )
            brillo_solar_actual = (
                df[df["Year"] == 2026][
                    "Sunshine_sec"
                ].median()
                / 3600
            )
            brillo_solar_comparativo = int((brillo_solar_actual - brillo_solar_ly) * 60)
    
            # Duración diurna
            diurna_ly = (
                df[df["Year"] == 2025][
                    "Daylight_sec"
                ].median()
                / 3600
            )
            diurna_actual = (
                df[df["Year"] == 2026][
                    "Daylight_sec"
                ].median()
                / 3600
            )
            diurna_comparativo = int((diurna_actual - diurna_ly) * 60)
    
            # Precipitación
            precipitacion_actual = df[
                df["Year"] == 2026
            ]["Precipitation_mm"].sum()
    
            # Evapotranspiración
            evapotransp_ly = df[
                df["Year"] == 2025
            ]["Ref_Evapotransp_mm"].sum()
            evapotransp_actual = df[
                df["Year"] == 2026
            ]["Ref_Evapotransp_mm"].sum()
    
            # Balance hídrico
            balance_hidrico_normal = precipitacion_actual - evapotransp_actual
    
            def balance_hidrico(precipitacion, evapotranspiracion):
                if precipitacion < evapotranspiracion:
                    return "Décifit hídrico"
                elif precipitacion <= (evapotranspiracion * 1.07):
                    return "Superávit hídrico"
                else:
                    return "Superávit crítico"
    
            if (
                balance_hidrico(precipitacion_actual, evapotransp_actual)
                == "Décifit hídrico"
            ):
                actual = "down"
                color = "orange"
            elif (
                balance_hidrico(precipitacion_actual, evapotransp_actual)
                == "Superávit hídrico"
            ):
                actual = "up"
                color = "green"
            else:
                actual = "up"
                color = "red"
    
            col1.metric(
                label="Temp Min Actual",
                value=f"{temp_min_actual:.1f} °C",
                icon="❄",
                border=True,
                delta_description=f"vs 2025 ({temp_min_ly:.1f} °C)",
                delta=f"{temp_min_comparativo:.1f} °C",
            )
            col1.metric(
                label="Temp Max Actual",
                value=f"{temp_max_actual:.1f} °C",
                icon="🔥",
                border=True,
                delta_description=f"vs 2025 ({temp_max_ly:.1f} °C)",
                delta=f"{temp_max_comparativo:.1f} °C",
            )
            col2.metric(
                label="Temp Media Actual",
                value=f"{temp_media_actual:.1f} °C",
                icon="🌡",
                border=True,
                delta_description=f"vs 2025 ({temp_media_ly:.1f} °C)",
                delta=f"{temp_media_comparativo:.1f} °C",
            )
            col2.metric(
                label="Radiación Solar Actual",
                value=f"{radiacion_actual:.1f} mj/m²",
                icon="⛱",
                border=True,
                delta_description=f"vs 2025 ({radiacion_ly:.1f} mj/m²)",
                delta=f"{radiacion_comparativo:.1f} mj/m²",
            )
            col3.metric(
                label="Brillo solar Actual",
                value=horas_minutos(brillo_solar_actual),
                delta=f"{brillo_solar_comparativo} minutos",
                delta_description=f"vs 2025 ({horas_minutos(brillo_solar_ly)})",
                icon="🌞",
                border=True,
            )
            col3.metric(
                label="Duración diurna Actual",
                value=horas_minutos(diurna_actual),
                delta=f"{diurna_comparativo} minutos",
                delta_description=f"vs 2025 ({horas_minutos(diurna_ly)})",
                icon="🧭",
                border=True,
            )
            col4.metric(
                label="Precipitación Actual",
                value=f"{precipitacion_actual:.1f} mm",
                delta=f"{balance_hidrico_normal:.1f} mm",
                delta_description=f"{balance_hidrico(precipitacion_actual, evapotransp_actual)}",
                delta_arrow=actual,
                delta_color=color,
                icon="☔",
                border=True,
            )
            col4.metric(
                label="Límite Superávit crítico Actual",
                value=f"{evapotransp_actual * 1.07:.1f} mm",
                delta=f"{evapotransp_actual * 1.07 - evapotransp_ly * 1.07:.1f} mm",
                delta_description=f"vs 2025 ({evapotransp_ly * 1.07:.1f} mm)",
                delta_arrow="off",
                icon="🌳",
                border=True,
                delta_color="gray",
            )
            st.divider()

    metricas_calculadas()

    # Valor de Irradiancia límite
    radiacion_aceptable = [20] * len(df_ag["Year"])

    # Lineplot de Radiación.
    fig_combinado1 = go.Figure()
    radiacion_limite = go.Scatter(
        x=df_ag["Year"],
        y=radiacion_aceptable,
        name="Aceptable mj/m²",
        line={"color": "orange", "dash": "dot"},
        opacity=0.7,
    )
    radiacion_mediana = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Solar_Radiation_median"],
        name="Promedio mj/m²",
        line={"color": "green", "dash": "dot"},
        mode="markers",
        marker={
            "size": df_ag["Solar_Radiation_median"],
            "sizemode": "diameter",
            "sizeref": 2.7,
        },
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
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.15,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"t": 100, "b": 40, "l": 40, "r": 40},
        autosize=True,
    )
    st.markdown(
        f"<h5 style='text-align:center;'>Análisis del comportamiento histórico de la radiación solar frente al umbral aceptable ({selector} 1940 - 2026)</h5>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_combinado1, use_container_width=True)

    # Hallazgos Radiación Solar
    with st.popover("Hallazgos", icon="🔍"):
        st.table(
            [
                [
                    "Temporada",
                    "Año Actual",
                    "Año pasado",
                    "vs Año pasado",
                    "Observaciones",
                ],
                [
                    "Total",
                    "20.84 mj/m²",
                    "17.97 mj/m²",
                    "+2.87 mj/m²",
                    "Se alcanzó el máximo histórico en radiación solar y superamos el umbral límite de 20 mj/m².",
                ],
                [
                    "Monzón",
                    "19.11 mj/m²",
                    "16.0 mj/m²",
                    "+3.11 mj/m²",
                    "Hay una variación porcentual nunca antes vista de 19.43% respecto al 2025.",
                ],
                [
                    "Sequía",
                    "21.31 mj/m²",
                    "18.77 m2/m²",
                    "+2.54 mj/m²",
                    "Hay una variación porcentual nunca antes vista de 13.53% respecto al 2025. Es la variación más alta en su historia.",
                ],
            ],
            width="content",
            border=True,
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
        mode="markers",
        line_shape="spline",
        name="Media C°",
        line={"color": "green", "dash": "dot"},
    )
    fig_combinado2.add_traces(
        [temperatura_maxima, temperatura_minima, amplitud_termica, temperatura_media]
    )
    fig_combinado2.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.15,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"t": 100, "b": 40, "l": 40, "r": 40},
        autosize=True,
    )
    st.markdown(
        f"<h5 style='text-align:center;'>Evolución histórica de las temperaturas máximas y mínimas promedio anuales ({selector} 1940 - 2026)</h5>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_combinado2)

    # Hallazgos en temperaturas
    with st.popover("Hallazgos", icon="🔍"):
        st.table(
            [
                [
                    "Temporada",
                    "Año Actual",
                    "Año pasado",
                    "vs Año pasado",
                    "Observaciones",
                ],
                [
                    "Total",
                    "27.0 °C",
                    "26.35 °C",
                    "+0.65 °C",
                    "Hay una clara tendencia histórica en ascenso. No habíamos experimentado un aumento de temperatura así desde el año 1954-1953 (+0.60 °C).",
                ],
                [
                    "Monzón",
                    "29.45 °C",
                    "28.15 °C",
                    "+1.3 °C",
                    "La temperatura actual logró un máximo histórico, y un fuerte incremento no visto desde 1987-1986 (+1.1 °C).",
                ],
                [
                    "Sequía",
                    "25.65 °C",
                    "24.65 °C",
                    "+1.0 °C",
                    "Otro máximo histórico alcanzado. No se veía un incremento así desde 1969-1968 (+0.95 °C).",
                ],
            ],
            width="content",
            border=True,
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
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.15,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"t": 100, "b": 40, "l": 40, "r": 40},
        autosize=True,
    )
    st.markdown(
        f"<h5 style='text-align:center;'>Comparación histórica entre el promedio diario de brillo solar y las horas diurnas ({selector} 1940 - 2026)</h5>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_combinado3)

    # Hallazgos en Brillo solar
    with st.popover("Hallazgos", icon="🔍"):
        st.table(
            [
                [
                    "Temporada",
                    "Año Actual",
                    "Año pasado",
                    "vs Año pasado",
                    "Observaciones",
                ],
                [
                    "Total",
                    "12.58 hrs diurnas",
                    "12.16 hrs diurnas",
                    "+25 minutos",
                    "Alcanzamos el máximo histórico, ya que por lo general las horas del día rondaban en un promedio de 12.16 hrs.",
                ],
                [
                    "Total",
                    "11.25 hrs de brillo solar",
                    "10.72 hrs de brillo solar",
                    "+31 minutos",
                    "Otro máximo histórico alcanzado.",
                ],
                [
                    "Monzón",
                    "13.48 hrs diurnas",
                    "12.96 hrs diurnas",
                    "+31 minutos",
                    "",
                ],
                [
                    "Monzón",
                    "11.11 hrs de brillo solar",
                    "9.45 hrs de brillo solar",
                    "+1h y 39 minutos",
                    "Se alcanzó un incremento histórico.",
                ],
                [
                    "Sequía",
                    "11.28 hrs de brillo solar",
                    "10.88 hrs de brillo solar",
                    "+27 minutos",
                    "Se alcanzó un máximo histórico en la duración del brillo solar.",
                ],
                [
                    "Sequía",
                    "12.06 hrs diurnas",
                    "11.61 hrs diurnas",
                    "+24 minutos",
                    "Las horas diurnas eran estables (11.61 hrs) hasta el 2026.",
                ],
            ],
            width="content",
            border=True,
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
        fill="tozeroy",
        fillcolor="#498ee8",
        opacity=0.3,
    )
    evapotransp = go.Scatter(
        x=df_ag["Year"],
        y=df_ag["Ref_Evapotransp_total"],
        marker_color="#a2caf3",
        name="Total Evapotranspiración (mm)",
        fill="tozeroy",
        fillcolor="#a2caf3",
        opacity=0.3,
    )
    limite = go.Scatter(
        x=df_ag["Year"],
        y=superavit_critico,
        marker_color="#b4d6f8",
        name="Límite de Superávit Hídrico (mm)",
        line={"dash": "dot"},
    )

    fig_combinado5.add_traces([limite,evapotransp, precipitacion])
    fig_combinado5.update_layout(
        legend={
            "orientation": "h",
            "yanchor": "bottom",
            "y": 1.15,
            "xanchor": "center",
            "x": 0.5,
        },
        margin={"t": 100, "b": 40, "l": 40, "r": 40},
        autosize=True,
    )
    st.markdown(
        f"<h5 style='text-align:center;'>Balance hídrico histórico ({selector} 1940 - 2026)</h5>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_combinado5)

    # Hallazgos en Balance Hídrico
    with st.popover("Hallazgos", icon="🔍"):
        st.table(
            [
                [
                    "Temporada",
                    "Precipitación Actual",
                    "Evapotranspiración Actual",
                    "Estado Actual",
                    "Precipitación año pasado",
                    "Estado año pasado",
                    "Observaciones",
                ],
                [
                    "Total",
                    "35.13k mm",
                    "52.82k mm",
                    "Décifit hídrico",
                    "77.98k mm",
                    "Superávit hídrico",
                    "En lo que va del año tenemos un déficit hídrico por 17.69k mm.",
                ],
                [
                    "Monzón",
                    "23.18k mm",
                    "13.13k mm",
                    "Superávit crítico",
                    "54.21k mm",
                    "Superávit crítico",
                    "Actualmente hay un excedente hídrico por 10.05k mm, lo que puede a conllevar a inundaciones.",
                ],
                [
                    "Sequía",
                    "11.95k mm",
                    "36.23k mm",
                    "Déficit hídrico",
                    "23.76k mm",
                    "Déficit hídrico",
                    "En lo que va del año tenemos un déficit hídrico por 24.28k mm. Es posible que la sequía de este año esté muy potenciada.",
                ],
            ],
            border=True,
            width="content",
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
    fig_combinado4.add_traces([mapa_correlacion])
    fig_combinado4.update_layout(xaxis={"tickangle": 270}, margin={"t": 20})
    st.markdown(
        f"<h5 style='text-align:center;'>Mapa de correlación climática ({selector} 1940 - 2026)</h5>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig_combinado4)

    # Hallazgos en Balance Hídrico
    with st.popover("Hallazgos", icon="🔍"):
        st.table(
            [
                ["Temporada", "Variables", "Nivel de correlación"],
                ["Total", "Precipitación → Duración del día", "Moderada"],
                ["Total", "Radiación solar → Precipitación", "Fuerte (inversa)"],
                ["Total", "Evapotranspiración → Duración del día", "Fuerte"],
                ["Total", "Evapotranspiración → Brillo solar", "Fuerte"],
                ["Monzón","Precipitación → Duración del día","Moderada"],
                ["Monzón","Radiación solar → Temperatura media","Moderada"],
                ["Monzón","Radiación solar → Brillo solar","Moderada"],
                ["Monzón","Radiación solar → Evapotranspiración","Moderada"],
                ["Monzón","Temperatura máxima → Radiación solar","Moderada"],
                ["Sequía","Radiación solar → Precipitación","Moderada (inversa)"],
                ["Sequía","Evapotranspiración → Brillo solar","Fuerte"]
            ],
            border=True,
            width="content",
        )

contenedor()
