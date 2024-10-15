import streamlit as st
import requests
import os
import uuid

# Obtener la ruta del directorio donde está ubicado este archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# URLs de las APIs
API_URL_RAG = "https://llmops-arch.onrender.com/get_answer"
API_URL_DEFAULT = "https://llmops-arch.onrender.com/get_default_answer"

# Ruta del archivo CSS
CSS_PATH = os.path.join(BASE_DIR, 'frontend', 'static', 'style.css')

# Configuración de la página
st.set_page_config(page_title="UnoAfp GPT", page_icon=":robot_face:", layout="centered")

# Leer el archivo CSS
try:
    with open(CSS_PATH, "r") as css_file:
        css_content = css_file.read()
    # Inyectar el CSS en la app
    st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    st.error(f"El archivo CSS no se encontró en la ruta: {CSS_PATH}")

# Mostrar el título centrado
st.markdown('<div class="main-title" style="text-align: center;">UNO AFP GPT</div>', unsafe_allow_html=True)

# Descripción inicial
st.write("**Elige la configuración del modelo para generar la respuesta.**")

# Inicializar variables en session_state
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "RAG"

if 'history' not in st.session_state:
    st.session_state.history = []

if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

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

# Mostrar el historial de conversación
if st.session_state.history:
    # Título del historial con fondo negro y texto blanco
    st.markdown(
        '<div class="history-title">Historial de la conversación</div>',
        unsafe_allow_html=True
    )
    for entry in st.session_state.history:
        st.markdown(
            f'''
            <div class="conversation">
                <div class="user-message">
                    <strong>Usuario:</strong> {entry['question']}
                </div>
                <div class="bot-response">
                    <strong>Bot:</strong> {entry['answer']}
                </div>
            </div>
            ''',
            unsafe_allow_html=True
        )

# Crear un formulario para la entrada del usuario
with st.form(key='my_form'):
    user_input = st.text_area("", placeholder="Ingresa tu pregunta", height=150)
    submit_button = st.form_submit_button(label='Generar Respuesta')

if submit_button:
    if user_input.strip():
        with st.spinner(f'Generando respuesta con el modelo {st.session_state.selected_model}...'):
            try:
                # Seleccionar la URL según el modelo configurado
                api_url = API_URL_RAG if st.session_state.selected_model == "RAG" else API_URL_DEFAULT

                # Preparar el historial para enviar (lista de diccionarios con 'questi
