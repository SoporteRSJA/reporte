import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Configuración básica
st.set_page_config(
    page_title="Filtrador GitHub",
    page_icon="📊",
    layout="centered"
)

# Título principal
st.title("🔍 Filtrador de Establecimientos")

# Obtener ID de Google Drive (para desarrollo)
FILE_ID = "1uz2NFGnv_dkRT0DdNgvQHBoGiiqwVihp"  # 👈 Reemplazar con tu ID real
DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

@st.cache_data(ttl=3600)
def descargar_datos():
    try:
        response = requests.get(DOWNLOAD_URL, timeout=30)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        st.error(f"Error de descarga: {str(e)}")
        return None

# Interfaz principal
archivo_bytes = descargar_datos()

if archivo_bytes:
    try:
        df = pd.read_excel(archivo_bytes, engine="openpyxl")
        
        if "Nombre_Establecimiento" not in df.columns:
            st.error("No se encuentra la columna 'Nombre_Establecimiento'")
        else:
            # Selector
            establecimientos = sorted(df["Nombre_Establecimiento"].unique())
            seleccion = st.selectbox("Seleccionar establecimiento:", establecimientos)
            
            # Filtrado
            df_filtrado = df[df["Nombre_Establecimiento"] == seleccion]
            st.dataframe(df_filtrado)
            
            # Descarga
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_filtrado.to_excel(writer, index=False)
            
            st.download_button(
                "Descargar resultados",
                data=output.getvalue(),
                file_name=f"filtrado_{seleccion}.xlsx"
            )
            
    except Exception as e:
        st.error(f"Error al procesar: {str(e)}")
