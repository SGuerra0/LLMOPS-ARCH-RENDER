import streamlit as st
import requests
import os
import uuid
import streamlit.components.v1 as components
import base64
from PIL import Image

# Configuración de URLs de API
API_URL_RAG = "https://llmops-arch-render.onrender.com/get_answer"
API_URL_DEFAULT = "https://llmops-arch-render.onrender.com/get_default_answer"
CSS_PATH = "static/style.css"
BANNER_PATH = "static/afpuno1.png"  # Banner que ahora estará arriba de todo, en formato wide y más pequeño
PLATWAVE_LOGO_PATH = "static/platwave iso.png"
ROBOT_PATH = "static/robot.png"  # Ruta de la imagen robot.png

# Configuración de la página
st.set_page_config(page_title="UNO AFP GPT", page_icon=":robot_face:", layout="wide")

# Ocultar barra superior de Streamlit y ajustar márgenes
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            .block-container {padding-top: 0px !important; padding-bottom: 0px !important;}
            .css-18e3th9 {padding-top: 0px !important;} /* Ajuste adicional específico de Streamlit */
            .stButton>button {
                background-color: #bd2ea9;
                color: white;
                font-weight: bold;
                border-radius: 5px;
                border: none;
                padding: 0.5em 1em;
            }
            .stButton>button:hover {
                background-color: #a0248e; /* color un poco más oscuro para hover */
            }
            /* Estilo para el banner con altura reducida al 70% */
            .banner-image {
                width: 100%;
                height: 45%; 
                object-fit: cover;
            }
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Leer e inyectar CSS
with open(CSS_PATH, "r") as css_file:
    css_content = css_file.read()
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Mostrar el banner con altura reducida al 70%
st.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="data:image/png;base64,{base64.b64encode(open(BANNER_PATH, "rb").read()).decode()}" 
             class="banner-image" />
    </div>
    """,
    unsafe_allow_html=True
)

# Inicializar variables en session_state
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "Base de datos especializada"
if 'history' not in st.session_state:
    st.session_state.history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Opciones de modelos
model_options = {
    "LLaMA 70B": "accounts/fireworks/models/llama-v3p1-70b-instruct",
    "Firefunction v2": "accounts/fireworks/models/firefunction-v2",
    "LLaMA 8B": "accounts/fireworks/models/llama-v3p1-8b-instruct"
}

# Crear columnas: izquierda (opciones) y derecha (formulario)
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    # Subheader con imagen al extremo derecho
    header_col1, header_col2 = st.columns([8, 1])
    with header_col1:
        st.subheader("Configuración del Modelo")
    with header_col2:
        st.image(ROBOT_PATH, width=85)  # Ajuste del tamaño de la imagen
    
    st.write(f"**Configuración seleccionada:** {st.session_state.selected_model}")

    # Botones para configuración del modelo
    if st.button("Base de datos especializada"):
        st.session_state.selected_model = "Base de datos especializada"
    st.write("")
    if st.button("Default"):
        st.session_state.selected_model = "Default"
    st.write("")
    if st.button("Borrar Memoria"):
        st.session_state.history.clear()
        st.session_state.session_id = str(uuid.uuid4())
        st.success("¡Memoria borrada!")

    # Slider de temperatura y selección de modelo
    temperature = st.slider("Temperatura del modelo", 0.0, 1.0, 0.6, 0.1)
    model_name = st.selectbox("Selecciona un modelo", list(model_options.keys()), index=0)
    model_option = model_options[model_name]

    # Historial de preguntas y respuestas
    st.subheader("Historial")
    if st.session_state.history:
        history_entries = ""
        for entry in reversed(st.session_state.history):
            history_entries += f'''
            <div class="history-entry">
                <p><strong>Pregunta:</strong><br>{entry['question']}</p>
                <p><strong>Respuesta:</strong><br>{entry['answer']}</p>
            </div>
            '''
        history_html = f'<div class="history-panel">{history_entries}</div>'
        components.html(f"<style>{css_content}</style>{history_html}", height=420, scrolling=False)
    else:
        st.write("El historial está vacío.")

with right_col:
    # Formulario para ingresar preguntas
    with st.form("input_form"):
        user_input = st.text_area("", placeholder="Ingresa tu pregunta", height=150)
        
        # Usar columnas dentro del formulario para alinear el botón aún más a la derecha
        col1, col2 = st.columns([5, 1])  # Ajuste para empujar el botón más a la derecha
        with col1:
            pass  # Espacio en blanco para alinear
        with col2:
            submit = st.form_submit_button("Generar Respuesta")

    if submit and user_input.strip():
        with st.spinner(f'Generando respuesta con {st.session_state.selected_model}...'):
            try:
                api_url = API_URL_RAG if st.session_state.selected_model == "Base de datos especializada" else API_URL_DEFAULT
                payload = {
                    "question": user_input,
                    "temperature": temperature,
                    "model": model_option,
                    "session_id": st.session_state.session_id,
                    "history": st.session_state.history,
                }
                response = requests.post(api_url, json=payload)
                data = response.json()

                st.session_state.history.append({
                    'question': user_input,
                    'answer': data.get("answer", "No se obtuvo respuesta.")
                })

                answer_html = f'''
                <div class="current-answer">
                    <p><strong>Respuesta:</strong><br>{data.get('answer', 'No se obtuvo respuesta.')}</p>
                    {'<p><strong>Contexto:</strong><br>' + data.get('context', '') + '</p>' if data.get('context') else ''}
                </div>
                '''
                components.html(f"<style>{css_content}</style>{answer_html}", height=500, scrolling=True)
            except Exception as e:
                st.error(f"Error: {e}")
    elif submit:
        st.warning("Por favor, ingresa una pregunta válida.")

# Pie de página con logo de Platwave en la esquina inferior derecha
st.markdown(f'''
    <div class="footer-logo">
        <img src="data:image/png;base64,{base64.b64encode(open(PLATWAVE_LOGO_PATH, "rb").read()).decode()}" />
    </div>
''', unsafe_allow_html=True)
