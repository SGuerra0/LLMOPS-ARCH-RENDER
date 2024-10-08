import streamlit as st
import requests
import os

API_URL = "http://127.0.0.1:8000/get_answer"
CSS_PATH="static/style.css"

# Definir estilos en Streamlit
st.set_page_config(page_title="UnoAfp GPT", page_icon=">", layout="centered")

# Read the CSS file content
with open(CSS_PATH, "r") as css_file:
    css_content = css_file.read()

# Inject the CSS into your Streamlit app
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Titulo estilizado
st.markdown('<div class="main-title">UnoAfp GPT ></div>', unsafe_allow_html=True)

st.write("**Ingresa una pregunta y el modelo proporcionara una respuesta basada en el contexto recuperado.**")


# Input form
userInput = st.text_area("Pregunta:", height=100, help="Escribe tu pregunta aqui", key="userInput")

# Boton para obtener respuesta
if st.button("Obtener Respuesta"):
    if userInput.strip():
        with st.spinner('Generando respuesta...'):
            try:
                # Hacer una solicitud POST a la API
                response = requests.post(API_URL, json={"question": userInput})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Mostrar la respuesta con estilo
                    st.markdown(f'<div class="answer-box"><strong>Respuesta:</strong><br>{data.get("answer", "No se obtuvo respuesta.")}</div>', unsafe_allow_html=True)
                    
                    # Mostrar el contexto con estilo
                    st.markdown(f'<div class="context-box"><strong>Contexto Utilizado:</strong><br>{data.get("context", "No se obtuvo contexto.")}</div>', unsafe_allow_html=True)
                else:
                    error_detail = response.json().get('detail', 'Error desconocido.')
                    st.error(f"Error {response.status_code}: {error_detail}")
            
            except requests.exceptions.ConnectionError:
                st.error("No se pudo conectar con la API. Asegurate de que el backend esta corriendo.")
            except Exception as e:
                st.error(f"Ocurrio un error: {e}")
    else:
        st.warning("Por favor, ingresa una pregunta valida.")

# Pie de pagina
st.markdown('<div class="footer">Desarrollado por Platwave | 2024</div>', unsafe_allow_html=True)