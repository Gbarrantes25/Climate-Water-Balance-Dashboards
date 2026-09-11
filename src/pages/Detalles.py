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

    condicion_deficit = [
        df_ciudad_ag["Precipitacion"] < df_ciudad_ag["Evapotranspiracion"]
    ]
    operacion_deficit = [
        df_ciudad_ag["Precipitacion"] - df_ciudad_ag["Evapotranspiracion"]
    ]

    condicion_superavit = [
        (df_ciudad_ag["Precipitacion"] >= df_ciudad_ag["Evapotranspiracion"])
        & (df_ciudad_ag["Precipitacion"] <= df_ciudad_ag["Evapotransp_limite"])
    ]
    operacion_superavit = [
        df_ciudad_ag["Precipitacion"] - df_ciudad_ag["Evapotranspiracion"]
    ]

    condicion_critica = [
        df_ciudad_ag["Precipitacion"] > df_ciudad_ag["Evapotransp_limite"]
    ]
    operacion_critica = [
        df_ciudad_ag["Precipitacion"] - df_ciudad_ag["Evapotransp_limite"]
    ]

    df_ciudad_ag["Deficit_hidrico"] = np.select(
        condicion_deficit, operacion_deficit, default=0
    )
    df_ciudad_ag["Superavit_hidrico"] = np.select(
        condicion_superavit, operacion_superavit, default=-1
    )
    df_ciudad_ag["Superavit_critico_hidrico"] = np.select(
        condicion_critica, operacion_critica, default=0
    )

    df_ciudad_ag = df_ciudad_ag[
        (df_ciudad_ag["Latitud"].between(8, 35))
        & (df_ciudad_ag["Longitud"].between(68, 97))
    ]

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
                        * 1.5
                    )
                    * 20,
                    "color": df_ciudad_ag["Radiacion"],
                    "colorscale": "YlOrBr",
                    "colorbar": {"orientation": "h"},
                },
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Estado: %{customdata[0]}<br>"
                    "Radiación: %{customdata[1]:.1f} MJ/m²"
                    "<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            height=500,
            map={"zoom": 3.2, "center": {"lat": 22, "lon": 80}},
            margin={"t": 25, "b": 25},
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Análisis Geográfico de Radiación Solar ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    df_ciudades_top_radiacion = (
        df_ciudad_ag.sort_values("Radiacion", ascending=True)[["City", "Radiacion"]]
        .tail(10)
        .reset_index(drop=True)
    )

    df_ciudades_bottom_radiacion = (
        df_ciudad_ag.sort_values("Radiacion", ascending=False)[["City", "Radiacion"]]
        .tail(10)
        .reset_index(drop=True)
    )

    df_ciudades_top_temp = (
        df_ciudad_ag.sort_values("Temp_median", ascending=True)[["City", "Temp_median"]]
        .tail(10)
        .reset_index(drop=True)
    )

    df_ciudades_bottom_temp = (
        df_ciudad_ag.sort_values("Temp_median", ascending=False)[
            ["City", "Temp_median"]
        ]
        .tail(10)
        .reset_index(drop=True)
    )

    df_ciudades_top_heatwave = (
        df_ciudad_ag.loc[df_ciudad_ag["Heatwave_day"] > 0]
        .sort_values("Heatwave_day", ascending=False)
        .head(10)
        .reset_index(drop=True)
    )

    def barras_top_radiacion():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_top_radiacion["City"],
            x=df_ciudades_top_radiacion["Radiacion"],
            orientation="h",
            marker={
                "color": df_ciudades_top_radiacion["Radiacion"],
                "colorscale": [[0.0, "#FF8000"], [0.5, "#FF0000"], [1, "#750000"]],
            },
            # opacity=0.5,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 25, "b": 25}, height=400)
        col1.markdown(
            f"<h5 style='text-align:center;'>10 Ciudades con mayor Radiación Solar ({selector})</h5>",
            unsafe_allow_html=True,
        )
        col1.plotly_chart(fig)

    def barras_bottom_radiacion():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_bottom_radiacion["City"],
            x=df_ciudades_bottom_radiacion["Radiacion"],
            orientation="h",
            marker={
                "color": df_ciudades_bottom_radiacion["Radiacion"],
                "colorscale": [[0.0, "#FFF52E"], [0.5, "#FFCC8A"], [1, "#FF940A"]],
            },
            opacity=0.8,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 25, "b": 25}, height=400)
        col2.markdown(
            f"<h5 style='text-align:center;'>10 Ciudades con menor Radiación Solar ({selector})</h5>",
            unsafe_allow_html=True,
        )
        col2.plotly_chart(fig)

    def crear_mapa_temperatura():
        fig = go.Figure(
            go.Scattermap(
                lat=df_ciudad_ag["Latitud"],
                lon=df_ciudad_ag["Longitud"],
                text=df_ciudad_ag["City"],
                customdata=df_ciudad_ag[["State", "Temp_median"]],
                mode="markers",
                marker={
                    "size": (df_ciudad_ag["Temp_median"].abs() * 1.35),
                    "color": df_ciudad_ag["Temp_median"],
                    "colorscale": "RdYlBu_r",
                    "colorbar": {"orientation": "h"},
                },
                hovertemplate=(
                    "<b>%{text}</b><br>Estado: %{customdata[0]}<br>Temperatura: %{customdata[1]:.1f} °C<extra></extra>"
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
        )
        st.markdown(
            f"<h5 style='text-align:center;'>Análisis Geográfico de Temperatura Media ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig, use_container_width=True)

    def barras_bottom_temperatura():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_bottom_temp["City"],
            x=df_ciudades_bottom_temp["Temp_median"],
            orientation="h",
            marker={
                "color": df_ciudades_bottom_temp["Temp_median"],
                "colorscale": "RdYlBu_r",
            },
            opacity=0.8,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 25, "b": 25}, height=400)
        st.markdown(
            f"<h5 style='text-align:center;'>10 Ciudades con menor Temperatura ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    def barras_top_temperatura():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_top_temp["City"],
            x=df_ciudades_top_temp["Temp_median"],
            orientation="h",
            marker={"color": "red"},
            opacity=0.5,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 25, "b": 25}, height=400)
        st.markdown(
            f"<h5 style='text-align:center;'>10 Ciudades con mayor Temperatura ({selector})</h5>",
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
                    "size": (df_ciudad_ag["Heatwave_day"].abs() * 1.1),
                    "color": df_ciudad_ag["Heatwave_day"],
                    "colorscale": "Oryel",
                    "colorbar": {"orientation": "h"},
                },
                hovertemplate=(
                    "<b>%{text}</b><br>Estado: %{customdata[0]}<br>Días de Olas de Calor: %{customdata[1]:.0f}<extra></extra>"
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
                "Ciudad: %{customdata[2]}<br>Estado: %{customdata[0]}<br>Días %{customdata[1]}<extra></extra>"
            ),
        )
        fig.update_layout(margin={"t": 25, "b": 25})
        fig.add_traces([dias_calor])
        fig.update_layout(autosize=True)
        st.markdown(
            f"<h5 style='text-align:center;'>Las 10 ciudades con más días de ola de calor ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    df_ciudades_top_deficit = (
        df_ciudad_ag.loc[df_ciudad_ag["Deficit_hidrico"] < 0]
        .sort_values("Deficit_hidrico", ascending=False)
        .tail(10)
        .reset_index(drop=True)
    )

    df_ciudades_top_critico = (
        df_ciudad_ag.sort_values("Superavit_critico_hidrico", ascending=True)
        .tail(10)
        .reset_index(drop=True)
    )

    df_ciudades_top_balance = (
        df_ciudad_ag.loc[df_ciudad_ag["Superavit_hidrico"] > 0]
        .sort_values("Superavit_hidrico", ascending=True)
        .tail(10)
        .reset_index(drop=True)
    )

    def barras_deficit():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_top_deficit["City"],
            x=df_ciudades_top_deficit["Deficit_hidrico"].abs(),
            orientation="h",
            marker={"color": "orange"},
            name="Déficit Hídrico",
            customdata=df_ciudades_top_deficit[["State", "City", "Deficit_hidrico"]],
            hovertemplate="Valor: %{customdata[2]:.2f}<br>Ciudad: %{customdata[1]}<br>Estado: %{customdata[0]}",
            opacity=0.7,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 15}, height=400)
        st.markdown(
            f"<h5 style='text-align:center;'>Las 10 ciudades con mayor déficit hídrico ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    def barras_critico():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_top_critico["City"],
            x=df_ciudades_top_critico["Superavit_critico_hidrico"],
            orientation="h",
            marker={"color": "#2F7FDA"},
            name="Superávit Crítico",
            customdata=df_ciudades_top_critico[
                ["State", "City", "Superavit_critico_hidrico"]
            ],
            hovertemplate="Valor: %{customdata[2]:.2f}<br>Ciudad: %{customdata[1]}<br>Estado: %{customdata[0]}",
            opacity=0.7,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 15}, height=400)
        st.markdown(
            f"<h5 style='text-align:center;'>Las 10 ciudades con mayor superávit hídrico crítico ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    def barras_superavit():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_top_balance["City"],
            x=df_ciudades_top_balance["Superavit_hidrico"],
            orientation="h",
            marker={"color": "#369B4F"},
            name="Superávit Hídrico",
            customdata=df_ciudades_top_balance[["State", "City", "Superavit_hidrico"]],
            hovertemplate="Valor: %{customdata[2]:.2f}<br>Ciudad: %{customdata[1]}<br>Estado: %{customdata[0]}",
            opacity=0.7,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 15}, height=400)
        st.markdown(
            f"<h5 style='text-align:center;'>Las ciudades con mayor balance hídrico ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    crear_mapa_radiacion()
    col1, col2 = st.columns(2)
    with col1:
        barras_top_radiacion()
    with col2:
        barras_bottom_radiacion()
    st.divider()
    st.divider()
    crear_mapa_dias_calor()
    barras_top_dias_calor()
    st.divider()
    st.divider()
    crear_mapa_temperatura()
    col1, col2 = st.columns(2)
    with col1:
        barras_top_temperatura()
    with col2:
        barras_bottom_temperatura()
    st.divider()
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        barras_deficit()
    with col2:
        barras_critico()
    with col3:
        if df_ciudades_top_balance.empty:
            st.write("")
        else:
            barras_superavit()


contenedor()
