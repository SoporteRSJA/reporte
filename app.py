import streamlit as st
import pandas as pd
from io import BytesIO
import os

# Configuración de la página
st.set_page_config(page_title="Filtrador Automático", page_icon="📊")

# Título
st.title("📊 Filtro por Establecimiento (Archivo Local)")

# Nombre del archivo Excel (debe estar en la misma carpeta que app.py)
ARCHIVO_EXCEL = "plano.xlsx"  # Cambia esto al nombre de tu archivo

# Verificar si el archivo existe
if not os.path.exists(ARCHIVO_EXCEL):
    st.error(f"❌ No se encontró el archivo '{ARCHIVO_EXCEL}' en la carpeta.")
else:
    # Cargar datos
    df = pd.read_excel(ARCHIVO_EXCEL)

    # 1. Selector de establecimiento
    establecimientos = df["Nombre_Establecimiento"].unique()
    establecimiento_seleccionado = st.selectbox(
        "Selecciona un establecimiento:",
        options=establecimientos
    )

    # 2. Filtrar datos
    df_filtrado = df[df["Nombre_Establecimiento"] == establecimiento_seleccionado]

    # Mostrar preview (opcional)
    st.write(f"**Datos filtrados para {establecimiento_seleccionado}:**")
    st.dataframe(df_filtrado)

    # 3. Botón de descarga
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name="Datos Filtrados")
    
    st.download_button(
        label="📥 Descargar Excel filtrado",
        data=output.getvalue(),
        file_name=f"filtrado_{establecimiento_seleccionado}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )