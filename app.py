import streamlit as st
import pandas as pd
import requests
from io import BytesIO

# Configuración de la página
st.set_page_config(
    page_title="Filtrador desde Google Drive",
    page_icon="📊",
    layout="wide"
)

# Título de la app
st.title("🔍 Filtrador de Establecimientos")

# --- Configuración ---
FILE_ID = "1uz2NFGnv_dkRT0DdNgvQHBoGiiqwVihp"  # Reemplaza con tu ID de Google Drive
# Ejemplo: Enlace "https://drive.google.com/file/d/ABC123/view" → ID = "ABC123"
# --------------------

@st.cache_data(ttl=3600)  # Cache por 1 hora
def descargar_excel():
    try:
        url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
        response = requests.get(url)
        response.raise_for_status()  # Verifica errores HTTP
        
        # Guardamos temporalmente el contenido en bytes
        return BytesIO(response.content)
        
    except Exception as e:
        st.error(f"Error al descargar: {str(e)}")
        return None

# Interfaz de usuario
with st.spinner("Descargando datos desde Google Drive..."):
    excel_bytes = descargar_excel()

if excel_bytes:
    try:
        # Lee el archivo ESPECIFICANDO el motor openpyxl
        df = pd.read_excel(
            excel_bytes,
            engine="openpyxl"  # 👈 ¡Solución al error!
        )
        
        # Verifica la columna requerida
        if "Nombre_Establecimiento" not in df.columns:
            st.error("❌ El archivo no contiene la columna 'Nombre_Establecimiento'")
        else:
            # Selector de establecimiento
            establecimientos = df["Nombre_Establecimiento"].unique()
            seleccion = st.selectbox(
                "Selecciona un establecimiento:",
                options=establecimientos
            )
            
            # Filtrado
            df_filtrado = df[df["Nombre_Establecimiento"] == seleccion]
            
            # Mostrar resultados
            st.success(f"✅ Datos cargados correctamente ({len(df_filtrado)} registros)")
            st.dataframe(df_filtrado)
            
            # Botón de descarga
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_filtrado.to_excel(writer, index=False)
            
            st.download_button(
                label="📤 Descargar Excel filtrado",
                data=output.getvalue(),
                file_name=f"filtrado_{seleccion}.xlsx"
            )
            
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        st.info("ℹ️ Verifica que el archivo sea un Excel válido (.xlsx) y no esté corrupto")
else:
    st.warning("""
    ⚠️ No se pudo cargar el archivo. Verifica:
    1. Que el ID del archivo sea correcto
    2. Que el archivo esté compartido como **"Cualquier persona con el enlace"**
    3. Que no excedas el límite de descargas de Google
    """)
