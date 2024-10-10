import streamlit as st
import requests
import os

API_URL_RAG = "http://127.0.0.1:8000/get_answer"  # URL para el modelo RAG
API_URL_DEFAULT = "http://127.0.0.1:8000/get_default_answer"  # URL para el modelo por defecto
CSS_PATH = "static/style.css"

# Definir estilos en Streamlit
st.set_page_config(page_title="UnoAfp GPT", page_icon=">", layout="centered")

# Leer el archivo CSS
with open(CSS_PATH, "r") as css_file:
    css_content = css_file.read()

# Inyectar el CSS en la app de Streamlit
st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

# Título estilizado
st.markdown('<div class="main-title">UnoAfp GPT ></div>', unsafe_allow_html=True)

st.write("**Ingresa una pregunta y elige el modelo para obtener la respuesta.**")

# Input para la pregunta del usuario
userInput = st.text_area("Pregunta:", height=100, help="Escribe tu pregunta aquí", key="userInput")

# Opciones de modelo: RAG (con contexto) o Default (sin contexto)
model_option = st.radio("Elige el modelo:", ("RAG (Con Contexto)", "Default (Sin Contexto)"))

# Botón para obtener respuesta
if st.button("Obtener Respuesta"):
    if userInput.strip():
        with st.spinner('Generando respuesta...'):
            try:
                # Seleccionar la URL según la opción de modelo elegida
                if model_option == "RAG (Con Contexto)":
                    api_url = API_URL_RAG
                else:
                    api_url = API_URL_DEFAULT
                
                # Hacer una solicitud POST a la API
                response = requests.post(api_url, json={"question": userInput})
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Mostrar la respuesta con estilo
                    st.markdown(f'<div class="answer-box"><strong>Respuesta:</strong><br>{data.get("answer", "No se obtuvo respuesta.")}</div>', unsafe_allow_html=True)
                    
                    # Mostrar el contexto solo si se eligió el modelo RAG
                    if model_option == "RAG (Con Contexto)":
                        st.markdown(f'<div class="context-box"><strong>Contexto Utilizado:</strong><br>{data.get("context", "No se obtuvo contexto.")}</div>', unsafe_allow_html=True)
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
