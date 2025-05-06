import streamlit as st
import pandas as pd
import gdown
from io import BytesIO
import os

# Configuración de la página
st.set_page_config(
    page_title="Filtrador desde Google Drive",
    page_icon="📊",
    layout="wide"
)

# Título de la app
st.title("🔍 Filtrador de Establecimientos (Google Drive)")

# 1. Descargar archivo desde Google Drive (solo una vez)
@st.cache_data
def descargar_excel():
    # URL pública de tu archivo en Google Drive (reemplaza con tu enlace)
    url = "https://drive.google.com/uc?id=1uz2NFGnv_dkRT0DdNgvQHBoGiiqwVihp"  # 👈 ¡Cambiar esto!
    output = "datos_gdrive.xlsx"
    
    if not os.path.exists(output):
        gdown.download(url, output, quiet=False)
    return pd.read_excel(output)

try:
    df = descargar_excel()
    
    # 2. Verificar columna de establecimientos
    if "Nombre_Establecimiento" not in df.columns:
        st.error("El archivo no contiene la columna 'Nombre_Establecimiento'")
    else:
        # 3. Selector de establecimiento
        establecimientos = df["Nombre_Establecimiento"].unique()
        establecimiento = st.selectbox(
            "Selecciona un establecimiento:",
            options=establecimientos,
            index=0
        )

        # 4. Aplicar filtro
        df_filtrado = df[df["Nombre_Establecimiento"] == establecimiento]
        
        # Mostrar resultados
        st.subheader(f"📊 Datos para: {establecimiento}")
        st.dataframe(df_filtrado, use_container_width=True)
        
        # 5. Botón de descarga
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_filtrado.to_excel(writer, index=False)
        
        st.download_button(
            label="⬇️ Descargar Excel Filtrado",
            data=output.getvalue(),
            file_name=f"filtrado_{establecimiento}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

except Exception as e:
    st.error(f"Error al cargar el archivo: {e}")
    st.info("⚠️ Asegúrate de haber compartido el archivo en Google Drive como 'Cualquier persona con el enlace'")
