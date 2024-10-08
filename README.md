# LLMOps-Arch
MLOps y LLMOps Infra

# Componentes 
## Fabrica:
- fdd: Fabrica de Datos
- fai: Fabrica de IA

## Capa
- stg: Stage
- uni: Universal

## Pipeline
- fet: Feature
- tra: Entrenamiento
- inf: Inferencia

OBS: Se le agrega correlativo para "n" proyectos

## Tecnologia: TC
- 01: HDFS
- 02: ChromaDB

## Librerias Python: LP
- 01: spacy
- 02: nltk

## Tipo: TP
- 01: LLM

## Ejemplo de flujo de trabajo
fai_stg01_tp01_01
- fai: Fabrica de IA
- uni: universal (correlativo 01)
- tp: LLM (Le he agregado este detalle como ejemplo de arquitectura LLM)
- 01: Correlativo de proceso

# Estructura datos
- En carpeta raiz
mkdir -p datos/raw
- Mover archivos .pdf, .json... a carpeta datos/raw
mkdir -p datos/universal

# Implementaciones

## Local: Consola
### Ingesta a BBDD Vector -> Chroma
- En carpeta raiz
cd fai_universal_tp01/fai_uni01_tp01_01
python3 main.py

### Inferencia
- Consola 1: Inicializacion de la API del LLM (En carpeta raiz)

cd fai_inference_tp01/fai_inf01_tp01_01
python3 main.py 

- Consola 2: Inicializacion sevicio de streamlit (En carpeta raiz)

cd fai_inference_tp01/fai_inf01_tp01_01/frontend
streamlit run main_streamlit.py