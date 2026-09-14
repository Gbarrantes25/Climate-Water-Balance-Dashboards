from pages.Inicio import cargar_datos, cargar_ciudades
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

df_extraido = cargar_datos()
df_ciudades = cargar_ciudades()

st.header("Análisis detallado", text_alignment="center", divider="gray")


@st.fragment
def contenedor():
    st.sidebar.markdown(
        "**Filtros**", text_alignment="center", wrap=True, unsafe_allow_html=True
    )
    selector = st.sidebar.selectbox("Temporada", options=["Todos", "Monzón", "Sequía"])

    def validar_temporada():
        if selector == "Monzón":
            df = df_extraido.loc[df_extraido["Is_Monsoon"] == True]
            return df.reset_index(drop=True)
        elif selector == "Sequía":
            df = df_extraido.loc[df_extraido["Is_Monsoon"] == False]
            return df.reset_index(drop=True)
        else:
            df = df_extraido.copy()
            return df

    df_filtrado_temporada = validar_temporada()
    df_filtrado_temporada["Year"] = df_filtrado_temporada["Year"].astype("int32")

    anos_disponibles = sorted(df_filtrado_temporada["Year"].unique(), reverse=True)
    selector_anos = st.sidebar.selectbox("Años", options=anos_disponibles)
    df_filtrado_anos = df_filtrado_temporada.loc[
        df_filtrado_temporada["Year"] == selector_anos
    ].reset_index(drop=True)
    df_merge = df_filtrado_anos.merge(
        df_ciudades, how="inner", left_on=["State", "City"], right_on=["state", "city"]
    ).drop(columns=["state", "city"])
    df_ciudad_ag = (
        df_merge.groupby(["State", "City"])
        .agg(
            Radiacion=("Solar_Radiation", "median"),
            Sunshine_sec=("Sunshine_sec", "median"),
            Precipitacion=("Precipitation_mm", "sum"),
            Evapotranspiracion=("Ref_Evapotransp_mm", "sum"),
            Heatwave_day=("Heatwave_Daysimple_flag", "sum"),
            Temp_min=("Temp_Min", "median"),
            Temp_max=("Temp_Max", "median"),
            Latitud=("latitude", "median"),
            Longitud=("longitude", "median"),
        )
        .reset_index()
    )

    df_ciudad_ag["Temp_median"] = (
        df_ciudad_ag["Temp_max"] + df_ciudad_ag["Temp_min"]
    ) / 2

    df_ciudad_ag["Evapotransp_limite"] = df_ciudad_ag["Evapotranspiracion"] * 1.07

    df_ciudad_ag = df_ciudad_ag[
        (df_ciudad_ag["Latitud"].between(8, 35))
        & (df_ciudad_ag["Longitud"].between(68, 97))
    ]

    condicion_hidrico = [
        df_ciudad_ag["Precipitacion"] < df_ciudad_ag["Evapotranspiracion"],
        (df_ciudad_ag["Precipitacion"] >= df_ciudad_ag["Evapotranspiracion"])
        & (df_ciudad_ag["Precipitacion"] <= df_ciudad_ag["Evapotransp_limite"]),
        df_ciudad_ag["Precipitacion"] > df_ciudad_ag["Evapotransp_limite"],
    ]
    categoria = ["Déficit", "Superávit", "Crítico"]
    df_ciudad_ag["Balance_hidrico"] = np.select(
        condicion_hidrico, categoria, default="Otro"
    )

    mm = [
        df_ciudad_ag["Precipitacion"] - df_ciudad_ag["Evapotranspiracion"],
        df_ciudad_ag["Precipitacion"] - df_ciudad_ag["Evapotranspiracion"],
        df_ciudad_ag["Precipitacion"] - df_ciudad_ag["Evapotransp_limite"],
    ]
    df_ciudad_ag["Variance_mm"] = np.select(condicion_hidrico, mm, default=0)

    colores = ["orange", "green", "red"]
    condiciones_colores = [
        df_ciudad_ag["Balance_hidrico"] == "Déficit",
        df_ciudad_ag["Balance_hidrico"] == "Superávit",
        df_ciudad_ag["Balance_hidrico"] == "Crítico",
    ]
    matriz_colores = np.select(condiciones_colores, colores, default="white")

    df_ciudades_top_radiacion = df_ciudad_ag.sort_values("Radiacion", ascending=True)[
        ["State", "City", "Radiacion"]
    ].reset_index(drop=True)

    df_ciudades_top_temp = df_ciudad_ag.sort_values("Temp_median", ascending=True)[
        ["State", "City", "Temp_median"]
    ].reset_index(drop=True)

    df_ciudades_top_heatwave = (
        df_ciudad_ag.loc[df_ciudad_ag["Heatwave_day"] > 0]
        .sort_values("Heatwave_day", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    df_ciudad_porcentaje = (
        df_ciudad_ag.loc[
            :,
            [
                "State",
                "City",
                "Precipitacion",
                "Evapotranspiracion",
                "Variance_mm",
                "Balance_hidrico",
            ],
        ]
        .assign(
            Porcentaje_desviacion=(
                lambda x: ((x["Precipitacion"] / x["Evapotranspiracion"]) - 1) * 100
            )
        )
        .sort_values(by="Porcentaje_desviacion")
    )

    df_ciudad_porcentaje["Deficit"] = np.where(
        df_ciudad_porcentaje["Porcentaje_desviacion"] < 0,
        round(df_ciudad_porcentaje["Porcentaje_desviacion"], 1),
        np.nan,
    )
    df_ciudad_porcentaje["Superavit"] = np.where(
        (df_ciudad_porcentaje["Porcentaje_desviacion"] >= 0)
        & (df_ciudad_porcentaje["Porcentaje_desviacion"] <= 7),
        round(df_ciudad_porcentaje["Porcentaje_desviacion"], 1),
        np.nan,
    )
    df_ciudad_porcentaje["Critico"] = np.where(
        df_ciudad_porcentaje["Porcentaje_desviacion"] > 7,
        round(df_ciudad_porcentaje["Porcentaje_desviacion"], 1),
        np.nan,
    )

    def crear_mapa_radiacion():
        fig = go.Figure(
            go.Scattermap(
                lat=df_ciudad_ag["Latitud"],
                lon=df_ciudad_ag["Longitud"],
                text=df_ciudad_ag["City"],
                customdata=df_ciudad_ag[["State", "Radiacion"]],
                mode="markers",
                marker={
                    "size": (
                        df_ciudad_ag["Radiacion"]
                        / df_ciudad_ag["Radiacion"].max()
                        * 1.2
                    )
                    * 20,
                    "color": df_ciudad_ag["Radiacion"],
                    "colorscale": "YlOrBr",
                    "colorbar": {"orientation": "h"},
                },
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "<b>Estado: </b>%{customdata[0]}<br>"
                    "<b>Radiación: </b>%{customdata[1]:.1f} MJ/m²"
                    "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            height=500,
            map={"zoom": 3, "center": {"lat": 22, "lon": 80}},
            margin={"t": 25, "b": 25},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Mapa de Dispersión Geográfica de Radiación Solar ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)
        with st.popover("Hallazgos", icon="🔍"):
            st.table(
                border=True,
                data=[
                    ["Temporada", "Observación actual", "vs 2025"],
                    [
                        "Total",
                        "Hay una concentración de radiación en el centro y sur del país.",
                        "El año pasado la concentración de radiación se dió mayormente en el sur del país.",
                    ],
                    [
                        "Monzón",
                        "La concentración de radiación se da fuertemente en el norte y un poco al sur del país.",
                        "El año pasado la concrentración de radiación en el norte fue menor y con menos intensidad.",
                    ],
                    [
                        "Sequía",
                        "La parte central de India continental tiene una radiación más profunda.",
                        "El año pasado la concentración de radiaicón se dió más al oeste y sur del país.",
                    ],
                ],
                width="content",
            )

    def scatter_radiacion():
        fig = go.Figure()
        barras = go.Scatter(
            y=df_ciudades_top_radiacion["City"],
            x=df_ciudades_top_radiacion["Radiacion"],
            marker={
                "color": df_ciudades_top_radiacion["Radiacion"],
                "colorscale": "YlOrBr",
                "size": df_ciudades_top_radiacion["Radiacion"] * 0.5,
                "colorbar": {"title": "MJ/m²"},
                "showscale": True,
            },
            mode="markers+text",
            textposition="middle left",
            text=df_ciudades_top_radiacion["City"],
            textfont={"size": 9.5},
            name="Radiación Mj/m²",
            customdata=df_ciudades_top_radiacion[["State", "City", "Radiacion"]],
            hovertemplate="<b>Radiación:</b> %{customdata[2]:.2f} Mj/m²<br><b>Ciudad:</b> %{customdata[1]}<br><b>Estado:</b> %{customdata[0]}",
        )
        fig.add_vline(
            x=20,
            line_dash="dot",
            line_color="gray",
            line_width=2,
            annotation_text="Límite",
            annotation_position="top left",
        )
        fig.add_traces([barras])
        fig.update_layout(
            margin={"t": 25, "b": 25},
            height=600,
            yaxis={"title": "Ciudades", "showgrid": False, "showticklabels": False},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Ciudades Fuera del Umbral de Radiación Solar ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)
        with st.popover("Hallazgos", icon="🔍"):
            st.table(
                border=True,
                data=[
                    ["Temporada", "Actual", "vs 2025", "Observaciones"],
                    [
                        "Total",
                        "39 ciudades superaron el umbral.",
                        "4 ciudades superaron el umbral.",
                        "Este año hay 78% de ciudades superaron el límite de radiación permitida, y el año pasado solo fue solo un 8%. Es el pico más alto en la historia.",
                    ],
                    [
                        "Monzón",
                        "23 ciudades superaron el umbral.",
                        "4 ciudades superaron el umbral.",
                        "Este año solo el 46% frente al 8% (del 2025) de ciudades superaron el umbral.",
                    ],
                    [
                        "Sequía",
                        "37 ciudades superaron el umbral.",
                        "11 ciudades superaron el umbral.",
                        "Este año hubo 74% frente al 22% (2025) de ciudades que excedieron el límite.",
                    ],
                ],
                width="content",
            )

    def crear_mapa_temperatura():
        fig = go.Figure(
            go.Scattermap(
                lat=df_ciudad_ag["Latitud"],
                lon=df_ciudad_ag["Longitud"],
                text=df_ciudad_ag["City"],
                customdata=df_ciudad_ag[["State", "Temp_median"]],
                mode="markers",
                marker={
                    "size": (df_ciudad_ag["Temp_median"].abs() * 1.5),
                    "color": df_ciudad_ag["Temp_median"],
                    "colorscale": "RdYlBu_r",
                    "colorbar": {"orientation": "h"},
                },
                hovertemplate=(
                    "<b>%{text}</b><br><b>Estado: </b>%{customdata[0]}<br><b>Temperatura: </b>%{customdata[1]:.1f} °C<extra></extra>"
                ),
            )
        )
        fig.update_layout(
            height=500,
            map={
                "zoom": 2.8,
                "center": {"lat": 22, "lon": 80},
                "style": "carto-positron",
            },
            margin={"t": 25, "b": 25},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Análisis Geográfico de Temperatura Media ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    def barras_top_temperatura():
        fig = go.Figure()
        barras = go.Scatter(
            y=df_ciudades_top_temp["City"],
            x=df_ciudades_top_temp["Temp_median"],
            mode="markers+text",
            marker={
                "color": df_ciudades_top_temp["Temp_median"],
                "colorscale": "RdYlBu_r",
                "colorbar": {"title": "°C"},
                "size": 8,
                "showscale": True,
            },
            textposition="middle left",
            text=df_ciudades_top_temp["City"],
            textfont={"size": 9.5},
            name="Temperatura °C",
            customdata=df_ciudades_top_temp[["State", "City", "Temp_median"]],
            hovertemplate="<b>Temperatura:</b> %{customdata[2]:.1f} °C<br><b>Ciudad:</b> %{customdata[1]}<br><b>Estado:</b> %{customdata[0]}",
        )
        fig.add_vline(
            x=0,
            line_dash="dot",
            line_color="steelblue",
            line_width=2,
            annotation_text="Frío ",
            annotation_position="top left",
        )
        fig.add_vline(
            x=17,
            line_dash="dot",
            line_color="orange",
            line_width=2,
            annotation_text="Frío-Cálido ",
            annotation_position="top left",
        )
        fig.add_vline(
            x=25,
            line_dash="dot",
            line_color="red",
            line_width=2,
            annotation_text="Cálido ",
            annotation_position="top left",
        )
        fig.add_traces([barras])
        fig.update_layout(
            margin={"t": 25, "b": 25},
            height=600,
            yaxis={"title": "Ciudades", "showgrid": False, "showticklabels": False},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Ciudades con mayor Temperatura ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    def crear_mapa_dias_calor():
        fig = go.Figure(
            go.Scattermap(
                lat=df_ciudad_ag["Latitud"],
                lon=df_ciudad_ag["Longitud"],
                text=df_ciudad_ag["City"],
                customdata=df_ciudad_ag[["State", "Heatwave_day"]],
                mode="markers",
                marker={
                    "size": (df_ciudad_ag["Heatwave_day"].abs() * 0.8),
                    "color": df_ciudad_ag["Heatwave_day"],
                    "colorscale": "Oryel",
                    "colorbar": {"orientation": "h"},
                },
                hovertemplate=(
                    "<b>%{text}</b><br><b>Estado: </b>%{customdata[0]}<br><b>Días de Olas de Calor: </b>%{customdata[1]:.0f}<extra></extra>"
                ),
            )
        )
        fig.update_layout(
            height=500,
            map={
                "zoom": 3.2,
                "center": {"lat": 22, "lon": 80},
                "style": "carto-positron",
            },
            margin={"t": 25, "b": 25},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Análisis Geográfico de Días de Calor ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    def barras_top_dias_calor():
        fig = go.Figure()
        dias_calor = go.Bar(
            x=df_ciudades_top_heatwave["City"],
            y=df_ciudades_top_heatwave["Heatwave_day"],
            name="Días de ola de calor",
            marker={
                "colorscale": "Oryel",
                "color": df_ciudades_top_heatwave["Heatwave_day"],
            },
            opacity=0.8,
            customdata=df_ciudades_top_heatwave[["State", "Heatwave_day", "City"]],
            hovertemplate=(
                "<b>Ciudad: </b>%{customdata[2]}<br><b>Estado: </b>%{customdata[0]}<br><b>Días: </b>%{customdata[1]}<extra></extra>"
            ),
        )
        fig.update_layout(
            margin={"t": 25, "b": 25}, bargap=0.6, barcornerradius=5, autosize=True
        )
        fig.add_traces([dias_calor])
        st.markdown(
            f"<h5 style='text-align:center;'>Las 10 ciudades con más días de ola de calor ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    def histogram_temp():
        start_temp = np.floor(df_ciudad_ag["Temp_median"].min())
        end_temp = np.ceil(df_ciudad_ag["Temp_median"].max())
        size_temp = (end_temp - start_temp) / 3
        fig = go.Figure(
            go.Histogram(
                x=df_ciudad_ag["Temp_median"],
                xbins={"start": start_temp, "end": end_temp, "size": size_temp},
                marker={"color": "red"},
                autobinx=False,
                opacity=0.5,
            )
        )
        fig.update_layout(
            bargap=0.02,
            barcornerradius=5,
            height=500,
            margin={"t": 25, "b": 25},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Distribución de Ciudades por Temp ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    def histogram_radiacion():
        start_temp = np.floor(df_ciudad_ag["Radiacion"].min())
        end_temp = np.ceil(df_ciudad_ag["Radiacion"].max())
        size_temp = (end_temp - start_temp) / 3
        fig = go.Figure(
            go.Histogram(
                x=df_ciudad_ag["Radiacion"],
                xbins={"start": start_temp, "end": end_temp, "size": size_temp},
                marker={"color": "orange"},
                autobinx=False,
                opacity=0.8,
            )
        )
        fig.update_layout(
            bargap=0.02,
            barcornerradius=5,
            height=500,
            margin={"t": 25, "b": 25},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Densidad de Ciudades por Radiación ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)
        with st.popover("Hallazgos", icon="🔍"):
            st.table(
                border=True,
                data=[
                    ["Temporada", "Actual", "vs 2025", "Observaciones"],
                    [
                        "Total",
                        "33 ciudades → 21-24.9 Mj/m² y 13 de ciudades → 17-20.9 Mj/m²",
                        "15 ciudades → 18.7-21.9 Mj/m² y 34 ciudades → 15.4-18.6 Mj/m²",
                        "En el año actual hay una distribución más densa en el rango de mayor radiación, a diferencia del año pasado que se concentró en el rango intermedio (2024 también mantuvo el mismo comportamiento).",
                    ],
                    [
                        "Monzón",
                        "13 ciudades → 22-26.9 Mj/m² y 23 ciudades → 17-21.9 Mj/m²",
                        "4 ciudades → 20-23.9 Mj/m² y 18 ciudades → 16-19.9 Mj/²",
                        "El año actual hay una distribución mayor de radiación por encima de 20 Mj/m² rompiendo el patrón por debajo de 4 ciudades afectadas de los últimos 5 años.",
                    ],
                    [
                        "Sequía",
                        "35 ciudades → 21-24.9 Mj/m² y 11 ciudades → 17-20.9 Mj/m²",
                        "29 ciudades → 18.67-21.99 Mj/m² y 20 ciudades → 15.34-18.66 Mj/m²",
                        "La distribución de ciudades en el rango superior de radiación se mantiene a comparación de otros años, lo único que varía son los rangos de radiación un poco más de 2 Mj/m².",
                    ],
                ],
                width="content",
            )

    def crear_mapa_hidrico():
        fig = go.Figure(
            go.Scattermap(
                lat=df_ciudad_ag["Latitud"],
                lon=df_ciudad_ag["Longitud"],
                text=df_ciudad_ag["City"],
                customdata=df_ciudad_ag[["State", "Variance_mm", "Balance_hidrico"]],
                mode="markers",
                marker={
                    "size": 30,
                    "color": matriz_colores,
                    "sizemode": "diameter",
                },
                opacity=0.5,
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "<b>Estado Hídrico: </b>%{customdata[2]}<br>"
                    "<b>Estado: </b>%{customdata[0]}<br>"
                    "<b>Variación: </b>%{customdata[1]:.1f} mm"
                    "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            height=500,
            map={"zoom": 3, "center": {"lat": 22, "lon": 80}},
            margin={"t": 25, "b": 25},
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Mapa de Dispersión Geográfica de Balance Hídrico ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    def crear_scatter_hidrico():
        fig = go.Figure()
        deficit = go.Scatter(
            y=df_ciudad_porcentaje["City"],
            x=df_ciudad_porcentaje["Deficit"],
            name="Déficit Hídrico",
            marker={"color": "orange", "size": 7.5},
            customdata=df_ciudad_porcentaje[
                [
                    "State",
                    "City",
                    "Porcentaje_desviacion",
                    "Balance_hidrico",
                    "Precipitacion",
                    "Evapotranspiracion",
                ]
            ],
            hovertemplate="<b>Índice: </b>%{customdata[2]:.1f}%<br><b>Ciudad: </b>%{customdata[1]}</b><br><b>Estado: </b>%{customdata[0]}<br><b>Precipitación: </b>%{customdata[4]:.2f} mm<br><b>Evapotranspiración: </b>%{customdata[5]:.2f} mm",
            mode="markers+text",
            textposition="middle left",
            text=df_ciudad_porcentaje["City"],
            textfont={"size": 9.5},
        )
        superavit = go.Scatter(
            y=df_ciudad_porcentaje["City"],
            x=df_ciudad_porcentaje["Superavit"],
            name="Superávit Hídrico",
            marker={"color": "green", "size": 9},
            customdata=df_ciudad_porcentaje[
                [
                    "State",
                    "City",
                    "Porcentaje_desviacion",
                    "Balance_hidrico",
                    "Precipitacion",
                    "Evapotranspiracion",
                ]
            ],
            hovertemplate="<b>Índice: </b>%{customdata[2]:.1f}%<br><b>Ciudad: </b>%{customdata[1]}</b><br><b>Estado: </b>%{customdata[0]},<br><b>Precipitación: </b>%{customdata[4]:.2f} mm<br><b>Evapotranspiración: </b>%{customdata[5]:.2f} mm",
            mode="markers+text",
            textposition="middle left",
            text=df_ciudad_porcentaje["City"],
            textfont={"size": 9.5},
        )
        critico = go.Scatter(
            y=df_ciudad_porcentaje["City"],
            x=df_ciudad_porcentaje["Critico"],
            name="Superávit Hídrico Crítico",
            marker={"color": "red", "size": 12},
            customdata=df_ciudad_porcentaje[
                [
                    "State",
                    "City",
                    "Porcentaje_desviacion",
                    "Balance_hidrico",
                    "Precipitacion",
                    "Evapotranspiracion",
                ]
            ],
            hovertemplate="<b>Índice: </b>%{customdata[2]:.1f}%<br><b>Ciudad: </b>%{customdata[1]}</b><br><b>Estado: </b>%{customdata[0]},<br><b>Precipitación: </b>%{customdata[4]:.2f} mm<br><b>Evapotranspiración: </b>%{customdata[5]:.2f} mm",
            mode="markers+text",
            textposition="middle left",
            text=df_ciudad_porcentaje["City"],
            textfont={"size": 9.5},
        )
        fig.add_traces([deficit, superavit, critico])
        fig.add_vline(
            x=7,
            line_dash="dot",
            line_color="red",
            line_width=1,
            annotation_text=" Umbral Crítico (+7%)",
            annotation_position="top right",
        )
        fig.add_vline(
            x=0,
            line_dash="solid",
            line_color="gray",
            line_width=1,
            annotation_text="Equilibrio ",
            annotation_position="bottom left",
        )
        fig.update_layout(
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.15,
                "xanchor": "center",
                "x": 0.5,
            },
            yaxis={"title": "Ciudades", "showgrid": False, "showticklabels": False},
            height=750,
            autosize=True,
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Índice de Desviación Hídrica por Ciudad ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    st.subheader("Radiación", divider="gray", wrap=True)
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        crear_mapa_radiacion()
    with col2:
        histogram_radiacion()
    scatter_radiacion()
    st.subheader("Días de Ola de Calor", divider="gray", wrap=True)
    crear_mapa_dias_calor()
    barras_top_dias_calor()
    st.subheader("Temperatura", divider="gray", wrap=True)
    col1, col2 = st.columns([0.6, 0.4])
    with col1:
        crear_mapa_temperatura()
    with col2:
        histogram_temp()
    barras_top_temperatura()
    st.subheader("Balance Hídrico", divider="gray", wrap=True)
    crear_mapa_hidrico()
    crear_scatter_hidrico()


contenedor()
