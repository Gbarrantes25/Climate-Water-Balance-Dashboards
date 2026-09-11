from pages.Inicio import cargar_datos, cargar_ciudades
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Título.
st.header(
    "Análisis de Clima por Estado & Ciudad", text_alignment="center", divider="gray"
)

# Inicializar estado "temporada" y "estados"
if "temporada" not in st.session_state:
    st.session_state.temporada = "Todos"
if "estados" not in st.session_state:
    st.session_state.estados = "Andaman and Nicobar Islands"
if "escala" not in st.session_state:
    st.session_state.escala = "Década"

# Cargar datos
df_extraido = cargar_datos()
df_ciudades_estados = cargar_ciudades()


# Fragmentamos el contenedor para que no recargue toda la página.
@st.fragment
def contenedor():

    # Título sidebar
    st.sidebar.markdown(
        "**Filtros**", text_alignment="center", wrap=True, unsafe_allow_html=True
    )
    # Creamos el selector de temporada.
    selector = st.sidebar.selectbox(
        "Temporada", options=["Todos", "Monzón", "Sequía"], key="temporada"
    )

    # Generar df dependiendo del filtro de tenporada (Monzón o Sequpia).
    def validar_monzon():
        if selector == "Monzón":
            df = df_extraido.loc[df_extraido["Is_Monsoon"] == True].reset_index(
                drop=True
            )
            return df
        elif selector == "Sequía":
            df = df_extraido.loc[df_extraido["Is_Monsoon"] == False].reset_index(
                drop=True
            )
            return df
        else:
            df = df_extraido.reset_index(drop=True)
            return df

    # Df acorde al filtro de la tenporada.
    df_filtro_temporada = validar_monzon()

    # Función callback para actualizar estado de sesión de ciudades.
    def actualizar_ciudades():
        st.session_state.ciudades = sorted(
            df_filtro_temporada.loc[
                df_filtro_temporada["State"] == st.session_state.estados
            ]["City"].unique()
        )

    # Estados disponibles únicos.
    estados_disponibles = sorted(df_filtro_temporada["State"].unique())

    # Multiselect de estado en columna 1.
    estados_seleccionados = st.sidebar.selectbox(
        label="Estado",
        options=estados_disponibles,
        key="estados",
        on_change=actualizar_ciudades,
        placeholder="Seleccione un estado",
        width="stretch",
    )

    # Ciudades disponibles filtrados en base al estado.
    ciudades_filtradas = sorted(
        df_filtro_temporada.loc[
            df_filtro_temporada["State"] == st.session_state.estados
        ]["City"].unique()
    )

    # Inicializar el estado de sesión de ciudades.
    if "ciudades" not in st.session_state:
        st.session_state.ciudades = ciudades_filtradas

    # Multiselect de ciudades en columna 2
    df_filtro_estado_ciudad = df_filtro_temporada.loc[
        (df_filtro_temporada["State"] == st.session_state.estados)
        & (df_filtro_temporada["City"].isin(st.session_state.ciudades))
    ].reset_index(drop=True)

    # Definiendo columnas para métricas.
    col1, col2, col3, col4 = st.columns(4)

    def metricas_vacias():
        col1.metric(
            label="Temp Min Actual",
            value=" - °C",
            icon="❄",
            border=True,
        )
        col1.metric(
            label="Temp Max Actual",
            value=" - °C",
            icon="🔥",
            border=True,
        )
        col2.metric(
            label="Temp Media Actual",
            value=" - °C",
            icon="🌡",
            border=True,
        )
        col2.metric(
            label="Radiación Solar Actual",
            value=" - mj/m²",
            icon="⛱",
            border=True,
        )
        col3.metric(
            label="Brillo solar Actual",
            value=" - ",
            icon="🌞",
            border=True,
        )
        col3.metric(
            label="Duración diurna Actual",
            value=" - ",
            icon="🧭",
            border=True,
        )
        col4.metric(
            label="Precipitación Actual",
            value=" - mm",
            icon="☔",
            border=True,
        )
        col4.metric(
            label="Límite Superávit crítico Actual",
            value=" - mm",
            icon="🌳",
            border=True,
        )
        st.divider()

    def metricas_calculadas():
        # Temp Min
        temp_min_ly = df_filtro_estado_ciudad.loc[
            df_filtro_estado_ciudad["Year"] == 2025
        ]["Temp_Min"].median()
        temp_min_actual = df_filtro_estado_ciudad.loc[
            df_filtro_estado_ciudad["Year"] == 2026
        ]["Temp_Min"].median()
        temp_min_comparativo = temp_min_actual - temp_min_ly

        # Temp Max
        temp_max_ly = df_filtro_estado_ciudad.loc[
            df_filtro_estado_ciudad["Year"] == 2025
        ]["Temp_Max"].median()
        temp_max_actual = df_filtro_estado_ciudad.loc[
            df_filtro_estado_ciudad["Year"] == 2026
        ]["Temp_Max"].median()
        temp_max_comparativo = temp_max_actual - temp_max_ly

        # Temp Media
        temp_media_ly = (
            df_filtro_estado_ciudad.loc[df_filtro_estado_ciudad["Year"] == 2025][
                "Temp_Max"
            ].median()
            + df_filtro_estado_ciudad.loc[df_filtro_estado_ciudad["Year"] == 2025][
                "Temp_Min"
            ].median()
        ) / 2
        temp_media_actual = (
            df_filtro_estado_ciudad.loc[df_filtro_estado_ciudad["Year"] == 2026][
                "Temp_Max"
            ].median()
            + df_filtro_estado_ciudad.loc[df_filtro_estado_ciudad["Year"] == 2026][
                "Temp_Min"
            ].median()
        ) / 2
        temp_media_comparativo = temp_media_actual - temp_media_ly

        # Radiación Solar
        radiacion_ly = df_filtro_estado_ciudad.loc[
            df_filtro_estado_ciudad["Year"] == 2025
        ]["Solar_Radiation"].median()
        radiacion_actual = df_filtro_estado_ciudad.loc[
            df_filtro_estado_ciudad["Year"] == 2026
        ]["Solar_Radiation"].median()
        radiacion_comparativo = radiacion_actual - radiacion_ly

        # Función para horas y minutos
        def horas_minutos(horas_decimales):
            horas = int(horas_decimales)
            minutos = int((horas_decimales - horas) * 60)
            return f"{horas} h y {minutos} m"

        # Brillo solar
        brillo_solar_ly = (
            df_filtro_estado_ciudad[df_filtro_estado_ciudad["Year"] == 2025][
                "Sunshine_sec"
            ].median()
            / 3600
        )
        brillo_solar_actual = (
            df_filtro_estado_ciudad[df_filtro_estado_ciudad["Year"] == 2026][
                "Sunshine_sec"
            ].median()
            / 3600
        )
        brillo_solar_comparativo = int((brillo_solar_actual - brillo_solar_ly) * 60)

        # Duración diurna
        diurna_ly = (
            df_filtro_estado_ciudad[df_filtro_estado_ciudad["Year"] == 2025][
                "Daylight_sec"
            ].median()
            / 3600
        )
        diurna_actual = (
            df_filtro_estado_ciudad[df_filtro_estado_ciudad["Year"] == 2026][
                "Daylight_sec"
            ].median()
            / 3600
        )
        diurna_comparativo = int((diurna_actual - diurna_ly) * 60)

        # Precipitación
        precipitacion_actual = df_filtro_estado_ciudad[
            df_filtro_estado_ciudad["Year"] == 2026
        ]["Precipitation_mm"].sum()

        # Evapotranspiración
        evapotransp_ly = df_filtro_estado_ciudad[
            df_filtro_estado_ciudad["Year"] == 2025
        ]["Ref_Evapotransp_mm"].sum()
        evapotransp_actual = df_filtro_estado_ciudad[
            df_filtro_estado_ciudad["Year"] == 2026
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

    if df_filtro_estado_ciudad.empty:
        metricas_vacias()
    else:
        metricas_calculadas()

    st.sidebar.multiselect(
        label="Ciudad",
        options=ciudades_filtradas,
        key="ciudades",
        placeholder="Seleccione una ciudad",
        wrap=True,
    )

    radio = st.sidebar.radio(
        label="Escala de tiempo",
        options=["Década", "Año", "Año-Trimestre", "Año-Mes"],
        horizontal=False,
        key="escala",
    )

    def validar_escala():
        df3 = df_filtro_estado_ciudad
        if radio == "Década":
            df3["eje_x"] = pd.to_datetime(
                (df3["Date"].dt.year // 10 * 10).astype("str") + "-01-01"
            )
            return df3
        elif radio == "Año":
            df3["eje_x"] = pd.to_datetime(df3["Date"].dt.year.astype("str") + "-01-01")
            return df3
        elif radio == "Año-Trimestre":
            df3["eje_x"] = df3["Date"].dt.to_period("Q").dt.to_timestamp()
            return df3
        else:
            df3["eje_x"] = df3["Date"].dt.to_period("M").dt.to_timestamp()
            return df3

    df_filtro_escala = validar_escala()
    df_filtro_escala_ag = (
        df_filtro_escala.groupby("eje_x")
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
            Heatwave_days=("Heatwave_Daysimple_flag", "sum"),
        )
        .reset_index()
    )
    df_filtro_escala_ag["Thermal_Amplitude"] = (
        df_filtro_escala_ag["Temp_Max"] - df_filtro_escala_ag["Temp_Min"]
    )
    df_filtro_escala_ag["Temp_Media"] = (
        df_filtro_escala_ag["Temp_Max"] + df_filtro_escala_ag["Temp_Min"]
    ) / 2
    df_filtro_escala_ag["Sunshine_hrs_median"] = round(
        (df_filtro_escala_ag["Sunshine_sec_median"] / 3600), 2
    )
    df_filtro_escala_ag["Daylight_hrs_median"] = round(
        (df_filtro_escala_ag["Daylight_sec_median"] / 3600), 2
    )

    def crear_radiacion():
        aceptable = [20] * len(df_filtro_escala_ag["eje_x"])
        fig = go.Figure()
        radiacion_min = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Solar_Radiation_min"],
            name="Mínimo mj/m²",
            line_shape="spline",
            opacity=0.2,
            line={"color": "skyblue"},
        )
        radiacion_aceptable = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=aceptable,
            name="Aceptable mj/m²",
            mode="lines",
            line={"dash": "dot", "color": "orange"},
            opacity=0.7,
        )
        radiacion_media = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Solar_Radiation_median"],
            name="Promedio mj/m²",
            mode="markers",
            line_shape="spline",
            marker={"color": "green"},
        )
        radiacion_max = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Solar_Radiation_max"],
            name="Máximo mj/m²",
            line_shape="spline",
            opacity=0.2,
            line={"color": "red"},
        )
        fig.add_traces(
            [radiacion_min, radiacion_aceptable, radiacion_media, radiacion_max]
        )
        fig.update_xaxes(
            rangeslider={"visible": True, "autorange": True},
            type="date",
            autorange=True,
        )
        fig.update_layout(
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.15,
                "xanchor": "center",
                "x": 0.5,
            },
            margin={"t": 100},
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Tendencia de Radiación Solar ({selector} 1940 - 2026)</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)
        st.divider()

    def crear_grafico_temp():
        fig = go.Figure()
        temp_min = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Temp_Min"],
            name="Mínimo °C",
            line_shape="spline",
            line={"color": "skyblue"},
            opacity=0.2,
        )
        temp_media = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Temp_Media"],
            name="Promedio °C",
            line_shape="spline",
            mode="lines+markers",
            line={"color": "green", "dash": "dot"},
        )
        temp_max = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Temp_Max"],
            name="Máximo C°",
            line_shape="spline",
            line={"color": "red"},
            opacity=0.2,
        )

        if radio == "Año-Mes":
            fig.update_xaxes(tickformat="%Y-%m")
        elif radio == "Año" or radio == "Década":
            fig.update_xaxes(tickformat="%Y")

        fig.add_traces([temp_max, temp_media, temp_min])
        fig.update_xaxes(
            rangeslider={"visible": True, "autorange": True},
            type="date",
            autorange=True,
        )
        fig.update_layout(
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.15,
                "xanchor": "center",
                "x": 0.5,
            },
            margin={"t": 100},
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Tendencia de Temperatura ({selector} 1940 - 2026)</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, key="linea_chart")
        st.divider()

    def crear_brillo_solar():
        fig = go.Figure()
        brillo_solar = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Sunshine_hrs_median"],
            name="Horas de brillo solar",
            line={"dash": "dot", "color": "green"},
            line_shape="spline",
        )
        diurno = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Daylight_hrs_median"],
            name="Horas diurnas",
            mode="lines",
            line={"color": "orange"},
            line_shape="spline",
        )
        fig.add_traces([brillo_solar, diurno])
        fig.update_xaxes(
            rangeslider={"visible": True, "autorange": True},
            type="date",
            autorange=True,
        )
        fig.update_layout(
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.15,
                "xanchor": "center",
                "x": 0.5,
            },
            margin={"t": 100},
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Tendencia de duración del día y brillo solar ({selector} 1940 - 2026)</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)
        st.divider()

    def crear_balance_hidrico():
        fig = go.Figure()
        precipitacion = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Precipitation_total"],
            name="Total precipitaciones (mm)",
            fill="tozeroy",
            fillcolor="#498ee8",
            line={"color": "#498ee8"},
            mode="lines",
        )
        evapotransp = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Ref_Evapotransp_total"],
            name="Total Evapotranspiración (mm)",
            fill="tozeroy",
            fillcolor="#a2caf3",
            line={"color": "#a2caf3"},
            mode="lines",
            opacity=0.3,
        )
        limite = go.Scatter(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Ref_Evapotransp_total"] * 1.07,
            mode="lines",
            name="Límite de Superávit Hídrico (mm)",
            line={"color": "#b4d6f8", "dash": "dot"},
        )
        fig.add_traces([limite, evapotransp, precipitacion])
        fig.update_xaxes(
            rangeslider={"visible": True, "autorange": True},
            type="date",
            autorange=True,
        )
        fig.update_layout(
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.15,
                "xanchor": "center",
                "x": 0.5,
            },
            margin={"t": 100},
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Tendencia de balance hídrico ({selector} 1940 - 2026)</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    def crear_ola_calor():
        fig = go.Figure()
        barra_ola_calor = go.Bar(
            x=df_filtro_escala_ag["eje_x"],
            y=df_filtro_escala_ag["Heatwave_days"],
            marker={
                "color": df_filtro_escala_ag["Heatwave_days"],
                "colorscale": "Oryel",
            },
            opacity=0.8,
        )
        fig.add_traces([barra_ola_calor])
        fig.update_xaxes(
            rangeslider={"visible": True, "autorange": True},
            type="date",
            autorange=True,
        )
        fig.update_layout(
            margin={"t": 40, "b": 40},bargap=0.05,barcornerradius=5
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Tendencia de días de Ola de Calor ({selector} 1940 - 2026)</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)
        st.divider()

    if not estados_seleccionados or not st.session_state.ciudades:
        st.warning("Selecciona un filtro")
    else:
        crear_radiacion()
        crear_ola_calor()
        crear_grafico_temp()
        crear_brillo_solar()
        crear_balance_hidrico()


contenedor()
