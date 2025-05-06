import streamlit as st
import pandas as pd
import requests
from io import BytesIO
import time

# Configuración de la página
st.set_page_config(
    page_title="Filtrador desde Google Drive",
    page_icon="📊",
    layout="wide"
)

# Título de la app
st.title("🔍 Filtrador de Establecimientos (Google Drive)")

# --- Configuración importante ---
# Obtén el ID de tu archivo en Google Drive:
# Enlace de ejemplo: https://drive.google.com/file/d/1Xy3...ABC/view?usp=sharing
# El ID es: 1Xy3...ABC
FILE_ID = "1uz2NFGnv_dkRT0DdNgvQHBoGiiqwVihp"  # 👈 ¡Reemplaza esto!
# ------------------------------

@st.cache_data(ttl=3600)  # Cachea los datos por 1 hora
def descargar_archivo():
    # Genera el enlace de descarga directa
    url = f"https://drive.google.com/uc?export=download&id={FILE_ID}"
    
    try:
        # Descarga el archivo
        session = requests.Session()
        response = session.get(url, stream=True)
        
        # Verifica si la descarga fue exitosa
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            st.error(f"Error al descargar: Código {response.status_code}")
            return None
            
    except Exception as e:
        st.error(f"Error de conexión: {str(e)}")
        return None

# Muestra spinner mientras carga
with st.spinner("Descargando datos desde Google Drive..."):
    file_content = descargar_archivo()

if file_content:
    try:
        # Leer el archivo Excel
        df = pd.read_excel(file_content)
        
        # Verificar si existe la columna requerida
        if "Nombre_Establecimiento" not in df.columns:
            st.error("El archivo no contiene la columna 'Nombre_Establecimiento'")
        else:
            # Widgets de la interfaz
            st.success("¡Datos cargados correctamente!")
            st.write(f"Total de registros: {len(df)}")
            
            # Selector de establecimiento
            establecimientos = sorted(df["Nombre_Establecimiento"].unique())
            seleccion = st.selectbox(
                "Selecciona un establecimiento:",
                options=establecimientos,
                index=0
            )
            
            # Aplicar filtro
            df_filtrado = df[df["Nombre_Establecimiento"] == seleccion]
            
            # Mostrar resultados
            st.subheader(f"📊 Resultados para: {seleccion}")
            st.dataframe(df_filtrado, use_container_width=True)
            
            # Botón de descarga
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_filtrado.to_excel(writer, index=False, sheet_name="Datos Filtrados")
            
            st.download_button(
                label="⬇️ Descargar Excel Filtrado",
                data=output.getvalue(),
                file_name=f"datos_filtrados_{seleccion}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
    except Exception as e:
        st.error(f"Error al procesar el archivo: {str(e)}")
else:
    st.warning("No se pudo cargar el archivo. Verifica:")
    st.markdown("""
    1. Que el ID del archivo sea correcto
    2. Que el archivo esté compartido como **"Cualquier persona con el enlace"**
    3. Que no haya restricciones de descarga en tu cuenta de Google
    """)
