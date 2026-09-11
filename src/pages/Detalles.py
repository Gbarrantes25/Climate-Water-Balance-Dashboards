from pages.Inicio import cargar_datos, cargar_ciudades
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

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
                    "colorbar": {"title": "Radiación mj/m²"},
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

    crear_mapa_radiacion()

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
        df_ciudad_ag.sort_values("Temp_median", ascending=False)[["City", "Temp_median"]]
        .tail(10)
        .reset_index(drop=True)
    )

    col1, col2 = st.columns(2)

    def barras_top_radiacion():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_top_radiacion["City"],
            x=df_ciudades_top_radiacion["Radiacion"],
            orientation="h",
            marker={"color": "red"},
            opacity=0.5,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 25, "b": 25}, height=400)
        col1.markdown(
            f"<h5 style='text-align:center;'>Top 10 de Ciudades mayor Radiación Solar ({selector})</h5>",
            unsafe_allow_html=True,
        )
        col1.plotly_chart(fig)

    def barras_bottom_radiacion():
        fig = go.Figure()
        barras = go.Bar(
            y=df_ciudades_bottom_radiacion["City"],
            x=df_ciudades_bottom_radiacion["Radiacion"],
            orientation="h",
            marker={"color": "orange"},
            opacity=0.8,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 25, "b": 25}, height=400)
        col2.markdown(
            f"<h5 style='text-align:center;'>Bottom 10 Ciudades con menor Radiación Solar ({selector})</h5>",
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
                    "size": (df_ciudad_ag["Temp_median"].abs() * 1.2),
                    "color": df_ciudad_ag["Temp_median"],
                    "colorscale": "YlOrBr",
                    "colorbar": {"title": "Temperatura °C"},
                },
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "Estado: %{customdata[0]}<br>"
                    "Temperatura: %{customdata[1]:.1f} °C"
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
            marker={"color": "orange"},
            opacity=0.8,
        )
        fig.add_traces([barras])
        fig.update_layout(margin={"t": 25, "b": 25}, height=400)
        st.markdown(
            f"<h5 style='text-align:center;'>Bottom 10 de Ciudades menor Temperatura ({selector})</h5>",
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
            f"<h5 style='text-align:center;'>Top 10 de Ciudades mayor Temperatura ({selector})</h5>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(fig)

    barras_top_radiacion()
    barras_bottom_radiacion()
    st.divider()
    crear_mapa_temperatura()
    col1, col2 = st.columns(2)
    with col1:
        barras_top_temperatura()
    with col2:
        barras_bottom_temperatura()
    st.divider()


contenedor()
