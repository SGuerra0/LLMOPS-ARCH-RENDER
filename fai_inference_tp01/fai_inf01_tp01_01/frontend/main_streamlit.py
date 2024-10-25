import streamlit as st
import requests
import os
import uuid
import streamlit.components.v1 as components
import base64

# Configuración de URLs de API desde el primer código
API_URL_RAG = "https://llmops-arch-api.onrender.com/get_answer"
API_URL_DEFAULT = "https://llmops-arch-api.onrender.com/get_default_answer"
CSS_PATH = "static/style.css"
LOGO_PATH = "static/unoafp_logo.png"

# Configuración de la página
st.set_page_config(page_title="UNO AFP GPT", page_icon=":robot_face:", layout="wide")

# Leer e inyectar CSS
with open(CSS_PATH, "r") as css_file:
    css_content = css_file.read()
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

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

# Crear columnas: izquierda (opciones) y derecha (formulario y logo)
left_col, right_col = st.columns([1, 2], gap="large")

with left_col:
    st.subheader("Configuración del Modelo")

    # Botones verticales
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

    st.write(f"**Configuración seleccionada:** {st.session_state.selected_model}")
    temperature = st.slider("Temperatura del modelo", 0.0, 1.0, 0.6, 0.1)

    model_name = st.selectbox("Selecciona un modelo", list(model_options.keys()), index=0)
    model_option = model_options[model_name]

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
    # Mostrar el logo
    def get_base64_image(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    logo_base64 = get_base64_image(LOGO_PATH)
    st.markdown(f'<div style="display: flex; justify-content: center;"><img src="data:image/png;base64,{logo_base64}" style="width:180px;"/></div>', unsafe_allow_html=True)

    # Formulario para ingresar preguntas
    with st.form("input_form"):
        user_input = st.text_area("", placeholder="Ingresa tu pregunta", height=150)
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

# Pie de página
st.markdown('<div class="footer">Desarrollado por Platwave | 2024</div>', unsafe_allow_html=True)
