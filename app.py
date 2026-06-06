import streamlit as st
import os
import sys
import tempfile

# 1. Configurar la ruta para que Streamlit encuentre tu paquete local
# Obtenemos la ruta absoluta de la raíz del repositorio
repo_root = os.path.dirname(os.path.abspath(__file__))
# Añadimos 'compylatex/src' al sys.path para que 'import compylatex' funcione
package_src_path = os.path.join(repo_root, "compylatex", "src")
if package_src_path not in sys.path:
    sys.path.insert(0, package_src_path)

try:
    from compylatex.executor import compylatex
except ImportError as e:
    st.error(f"Error al importar compylatex: {e}. Revisa la estructura de carpetas.")
    st.stop()

st.set_page_config(page_title="ComPyLaTex Web")

st.title("Procesador ComPyLaTex")
st.markdown("""
Esta aplicación procesa archivos LaTeX ejecutando los algoritmos y cálculos 
definidos en sus etiquetas.
""")

uploaded_file = st.file_uploader("Sube tu archivo .tex", type=["tex"])

if uploaded_file is not None:
    st.success(f"Archivo cargado: {uploaded_file.name}")
    
    if st.button("Ejecutar compylatex"):
        with st.spinner("Procesando ecuaciones y algoritmos..."):
            try:
                # Creamos un directorio temporal para trabajar de forma segura
                with tempfile.TemporaryDirectory() as tmpdir:
                    input_path = os.path.join(tmpdir, "input.tex")
                    output_path = os.path.join(tmpdir, "output.tex")
                    
                    # Guardamos el contenido subido al archivo temporal
                    with open(input_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Ejecutamos tu función principal
                    # Nota: compylatex lee de input_path y escribe en output_path
                    compylatex(input_path, output_path)
                    
                    # Leemos el resultado para ofrecer la descarga
                    with open(output_path, "rb") as f:
                        result_data = f.read()
                    
                    st.success("¡Procesamiento completado!")
                    
                    # Botón para descargar el resultado
                    st.download_button(
                        label="Descargar resultado .tex",
                        data=result_data,
                        file_name=f"procesado_{uploaded_file.name}",
                        mime="text/x-tex"
                    )
                    
            except Exception as e:
                st.error(f"Ocurrió un error durante el procesamiento: {e}")
