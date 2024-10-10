import streamlit as st
import requests
import os
# URLs de las APIs
API_URL_RAG = "http://127.0.0.1:8000/get_answer"  
API_URL_DEFAULT = "http://127.0.0.1:8000/get_default_answer"  
CSS_PATH = "static/style.css"  # Ruta del CSS

# Configuración de la página
st.set_page_config(page_title="UnoAfp GPT", page_icon=":robot_face:", layout="centered")

# Leer el archivo CSS
with open(CSS_PATH, "r") as css_file:
    css_content = css_file.read()

# Inyectar el CSS en la app
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Cargar el logo y alinearlo con el título en la misma fila
logo_path = "static/unoafp_logo.png"
col1, col2 = st.columns([1, 4])
with col1:
    st.image(logo_path, width=100)
with col2:
    st.markdown('<div class="main-title">UNO AFP GPT</div>', unsafe_allow_html=True)

# Descripción inicial
st.write("**Elige la configuración del modelo para generar la respuesta.**")

# Inicializar el modelo seleccionado con un valor predeterminado
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "RAG"

# Crear columnas para los botones de configuración, centrados en la pantalla
config_col1, config_col2, _ = st.columns([1, 1, 2])
with config_col1:
    if st.button("RAG", use_container_width=True):
        st.session_state.selected_model = "RAG"  # Actualizar el modelo seleccionado

with config_col2:
    if st.button("DEFAULT", use_container_width=True):
        st.session_state.selected_model = "Default"  # Actualizar el modelo seleccionado

# Mostrar el modelo seleccionado centrado
st.markdown(f'<div class="model-selection" style="text-align:center; font-weight:bold;">Modelo seleccionado: {st.session_state.selected_model}</div>', unsafe_allow_html=True)
# Agregar un slider para seleccionar la temperatura del modelo
st.write("**Ajusta la temperatura del modelo (entre 0 y 1):**")
temperature = st.slider("Temperatura del modelo", min_value=0.0, max_value=1.0, value=0.6, step=0.1)

# Diccionario que mapea los nombres de los modelos a sus rutas
model_options = {
    "Firefunction v2": "accounts/fireworks/models/firefunction-v2",
    "LLaMA 8B": "accounts/fireworks/models/llama-v3p1-8b-instruct",
    "LLaMA 70B": "accounts/fireworks/models/llama-v3p1-70b-instruct"
}

# Agregar un selectbox para seleccionar el modelo
st.write("**Selecciona el modelo a utilizar:**")
model_name = st.selectbox("Modelos disponibles", list(model_options.keys()))

# Obtener la ruta del modelo seleccionado
model_option = model_options[model_name]
# Input para la pregunta del usuario
userInput = st.text_area("", placeholder="Ingresa tu pregunta", height=150, key="userInput")

# Crear botón "Generar Respuesta"
if st.button("Generar Respuesta", use_container_width=True):
    if userInput.strip():
        with st.spinner(f'Generando respuesta con el modelo {st.session_state.selected_model}...'):
            try:
                # Seleccionar la URL según el modelo configurado
                api_url = API_URL_RAG if st.session_state.selected_model == "RAG" else API_URL_DEFAULT
                
                # Hacer una solicitud POST a la API seleccionada
                response = requests.post(api_url, json={"question": userInput, "temperature": temperature, "model": model_option})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Mostrar la respuesta **debajo** del área de texto, centrada y con estilo
                    st.markdown(
                        f'''
                        <div class="answer-container" style="text-align:left;">
                            <div class="answer-box" style="background-color: #1f1f1f; color: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
                                <strong>Respuesta:</strong><br>{data.get("answer", "No se obtuvo respuesta.")}
                            </div>
                        </div>
                        ''',
                        unsafe_allow_html=True
                    )
                    
                    # Mostrar el contexto si es el modelo RAG
                    if st.session_state.selected_model == "RAG":
                        st.markdown(
                            f'''
                            <div class="context-container" style="text-align:left;">
                                <div class="context-box" style="background-color: #333333; color: white; padding: 15px; border-radius: 5px; margin: 10px 0;">
                                    <strong>Contexto Utilizado:</strong><br>{data.get("context", "No se obtuvo contexto.")}
                                </div>
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )
                else:
                    error_detail = response.json().get('detail', 'Error desconocido.')
                    st.error(f"Error {response.status_code}: {error_detail}")
            
            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar con la API. Asegúrate de que el backend está corriendo.")
            except Exception as e:
                st.error(f"Ocurrió un error: {e}")
    else:
        st.warning("Por favor, ingresa una pregunta válida.")

# Pie de página
st.markdown('<div class="footer">Desarrollado por Platwave | 2024</div>', unsafe_allow_html=True)
