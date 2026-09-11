import streamlit as st
import pandas as pd
from pathlib import Path

# Título
st.header(
    "Proyecto Climatológico y Balance Hídrico (India)", text_alignment="center", divider="gray"
)

# Carpeta raíz
src_dir = Path(__file__).resolve().parent.parent

ruta = (src_dir / "data" / "ClimaHistorico.parquet").as_posix()


# Cargando y limpiando dataframe
@st.cache_data
def cargar_datos():
    df_raw = pd.read_parquet(
        ruta,
        columns=[
            "city",
            "state",
            "date",
            "year",
            "decade",
            "month",
            "temp_min_c",
            "temp_max_c",
            "solar_radiation_mj_m2",
            "sunshine_duration_sec",
            "daylight_duration_sec",
            "is_monsoon_season",
            "precipitation_mm",
            "rain_mm",
            "reference_evapotranspiration_mm",
            "heatwave_day_simple_flag",
        ],
    )

    # Limpieza de datos nulos
    df_raw["temp_min_c"] = df_raw["temp_min_c"].fillna(
        df_raw.groupby(["year", "state", "city"])["temp_min_c"].transform("median")
    )
    df_raw["solar_radiation_mj_m2"] = df_raw["solar_radiation_mj_m2"].fillna(
        df_raw.groupby(["year", "state", "city"])["solar_radiation_mj_m2"].transform(
            "median"
        )
    )
    df_raw["sunshine_duration_sec"] = df_raw["sunshine_duration_sec"].fillna(
        df_raw.groupby(["year", "state", "city"])["sunshine_duration_sec"].transform(
            "median"
        )
    )

    # Cambiando tipo de dato
    df_raw["state"] = df_raw["state"].astype("category")
    df_raw["city"] = df_raw["city"].astype("category")
    df_raw["year"] = df_raw["year"].astype("category")
    df_raw["month"] = df_raw["month"].astype("category")
    df_raw["temp_max_c"] = df_raw["temp_max_c"].astype("float32")
    df_raw["temp_min_c"] = df_raw["temp_min_c"].astype("float32")
    df_raw["solar_radiation_mj_m2"] = df_raw["solar_radiation_mj_m2"].astype("float32")
    df_raw["date"] = df_raw["date"].astype("datetime64[us]")
    df_raw["sunshine_duration_sec"] = df_raw["sunshine_duration_sec"].astype("float32")
    df_raw["daylight_duration_sec"] = df_raw["daylight_duration_sec"].astype("float32")
    df_raw["decade"] = df_raw["decade"].astype("category")
    df_raw["precipitation_mm"] = df_raw["precipitation_mm"].fillna(0).astype("float32")
    df_raw["rain_mm"] = df_raw["rain_mm"].fillna(0).astype("float32")
    df_raw["reference_evapotranspiration_mm"] = (
        df_raw["reference_evapotranspiration_mm"].fillna(0).astype("float32")
    )
    df_raw["is_monsoon_season"] = df_raw["is_monsoon_season"].astype("boolean")
    df_raw["heatwave_day_simple_flag"] = df_raw["heatwave_day_simple_flag"].astype("boolean")

    # Creando nueva columna de Irradiación
    df_raw["Irradiance_wm2"] = round(
        (df_raw["solar_radiation_mj_m2"] * 1000000) / df_raw["daylight_duration_sec"], 2
    )
    df_raw = df_raw.sort_values("date").reset_index(drop=True)

    # Renombrando columnas
    df = df_raw.rename(
        columns={
            "city": "City",
            "state": "State",
            "date": "Date",
            "year": "Year",
            "decade": "Decade",
            "month": "Month",
            "temp_max_c": "Temp_Max",
            "temp_min_c": "Temp_Min",
            "solar_radiation_mj_m2": "Solar_Radiation",
            "sunshine_duration_sec": "Sunshine_sec",
            "daylight_duration_sec": "Daylight_sec",
            "is_monsoon_season": "Is_Monsoon",
            "precipitation_mm": "Precipitation_mm",
            "rain_mm": "Rain_mm",
            "reference_evapotranspiration_mm": "Ref_Evapotransp_mm",
            "heatwave_day_simple_flag": "Heatwave_Daysimple_flag",
        }
    ).reset_index(drop=True)
    return df


# Mostrar df limpio
df = cargar_datos()

@st.cache_data
def cargar_ciudades():
    # Carpeta raíz
    src_dir = Path(__file__).resolve().parent.parent
    ruta = (src_dir / "data" / "Estados.parquet").as_posix()
    df = (
        pd.read_parquet(ruta)
        .sort_values("state")
        .drop_duplicates()
        .reset_index(drop=True)
    )
    return df


df_ciudades_estados = cargar_ciudades()

# Preguntas del proyecto
st.markdown(
    """
            <h4> 1. ¿Qué es?</h4>
            <p>Es un dashboard climatológico que usa un dataset de Kaggle que nos ayudará a visualizar la información histórica de la temperatura y radiación en el país de la India desde el año 1940 hasta el 2026
            .</p>
            <h4>2. ¿Cómo lo hice?</h4>
            <p>El proyecto se creó con las siguientes tecnologías:</p>
            <ul>
                <li><span style='font-weight:600;'>Python v.3.12</span>: Núcleo fundamental en el desarrollo.</li>
                <li><span style='font-weight:600;'>UV</span>: Entorno ultra rápido de Python.</li>
                <li><span style='font-weight:600;'>Visual Studio Code</span>: Editor de código con el mejor autocompletado que hay (pylance).</li>
                <li><span style='font-weight:600;'>Pandas</span>: Librería por excelencia para manipulación y limpieza de datos.</li>
                <li><span style='font-weight:600;'>Numpy</span>: Para cálculos más eficientes.</li>
                <li><span style='font-weight:600;'>Plotly</span>: Gráficos interactivos para web.</li>
                <li><span style='font-weight:600;'>Streamlit</span>: Para aportar interactividad en la información de los gráficos con slicers.</li>
                <li><span style='font-weight:600;'>Streamlit Community Cloud</span>: Nube Saas para despliegue de proyecto.</li>
            </ul>
            <br>
            <p style='font-weight:800;'>Flujo: Extracción → Transformación y Carga → Filtro y Manipulación → Paginación de contenido → Visualización → Exportar a Github → Despliegue en nube</p>
            <br>
            <p style='font-weight:600; text-decoration: underline;'>Daframe (primeros 20 registros)</p>
            """,
    unsafe_allow_html=True,
)
st.dataframe(df.head(20), "stretch")
st.markdown(
    """
            <h4>3. ¿Cuál es el objetivo?</h4>
            <p>Es poder medir de manera ágil el impacto histórico de la temperatura y la radiación solar (mj/m2) en los estados y ciudades de la India, para que posteriormente los encargados de la salud y ambiente de dicho país decidan las mejores estrategias en favor de sus ciudadanos.</p>
            """,
    unsafe_allow_html=True,
)