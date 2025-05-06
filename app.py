import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import sys
import time

# Configuración de la página
st.set_page_config(
    page_title="Filtrador de Establecimientos",
    page_icon="🏢",
    layout="centered"
)

# Título con estilo
st.markdown("""
<h1 style='text-align: center; color: #2a9d8f;'>
    🏢 Filtrador de Establecimientos desde Google Drive
</h1>
""", unsafe_allow_html=True)

# --- Configuración ---
try:
    # Intenta obtener el ID de secrets.toml (para producción)
    FILE_ID = st.secrets["1uz2NFGnv_dkRT0DdNgvQHBoGiiqwVihp"]
except:
    # Si no existe, usa un valor por defecto (para desarrollo)
    FILE_ID = "1uz2NFGnv_dkRT0DdNgvQHBoGiiqwVihp"  # 👈 ¡Reemplázalo con tu ID real!

DOWNLOAD_URL = f"https://drive.google.com/uc?export=download&id={FILE_ID}"

# --- Funciones principales ---
@st.cache_data(ttl=3600, show_spinner="Descargando datos desde Google Drive...")
def descargar_archivo():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(DOWNLOAD_URL, headers=headers, timeout=30)
        response.raise_for_status()
        return BytesIO(response.content)
    except Exception as e:
        st.error(f"🚨 Error al descargar el archivo: {str(e)}")
        return None

def procesar_archivo(archivo_bytes):
    try:
        # Lee el archivo con manejo explícito del formato
        df = pd.read_excel(
            archivo_bytes,
            engine="openpyxl",
            dtype={"Nombre_Establecimiento": "string"}
        )
        
        # Verifica columnas requeridas
        if "Nombre_Establecimiento" not in df.columns:
            st.error("El archivo no contiene la columna 'Nombre_Establecimiento'")
            return None
            
        return df
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {str(e)}")
        return None

# --- Interfaz de usuario ---
with st.spinner("Conectando con Google Drive..."):
    excel_bytes = descargar_archivo()

if excel_bytes:
    df = procesar_archivo(excel_bytes)
    
    if df is not None:
        st.success(f"✅ Datos cargados correctamente ({len(df)} registros)")
        
        # Selector de establecimiento
        establecimientos = sorted(df["Nombre_Establecimiento"].unique())
        seleccion = st.selectbox(
            "Seleccione un establecimiento:",
            options=establecimientos,
            index=0
        )
        
        # Filtrado
        df_filtrado = df[df["Nombre_Establecimiento"] == seleccion]
        
        # Mostrar resultados
        st.subheader(f"Resultados para: {seleccion}")
        st.dataframe(
            df_filtrado,
            height=300,
            use_container_width=True,
            hide_index=True
        )
        
        # Botón de descarga
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name="Datos Filtrados")
        
        st.download_button(
            label="📥 Descargar resultados en Excel",
            data=output.getvalue(),
            file_name=f"datos_filtrados_{seleccion}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# --- Sección de instrucciones ---
st.markdown("---")
with st.expander("ℹ️ Instrucciones para configurar"):
    st.markdown("""
    1. **Obtén el ID de Google Drive**:
       - Sube tu archivo Excel a Google Drive
       - Haz clic derecho → Compartir → "Cualquier persona con el enlace"
       - Copia el ID de la URL: `https://drive.google.com/file/d/[ESTE_ES_TU_ID]/view`

    2. **Configuración para producción**:
       - Crea un archivo `.streamlit/secrets.toml` en tu repositorio con:
         ```toml
         GOOGLE_DRIVE_ID = "tu_id_aquí"
         ```
    """)

# --- Footer ---
st.markdown("""
<div style='text-align: center; margin-top: 50px; color: #6c757d;'>
    <p>Desplegado con ❤️ en <a href='https://streamlit.io'>Streamlit</a></p>
</div>
""", unsafe_allow_html=True)
