# LLMOps-Arch
MLOps y LLMOps Infra

# Componentes 
## Fabrica:
FDD: Fabrica de Datos
FAI: Fabrica de IA

## Tecnologia: TC
01: HDFS
02: ChromaDB

## Librerias Python: LP
01: spacy
02: nltk

## Tipo: TP
01: LLM

# Implementacion de prueba
docker build -t {USER}/{CONT_NAME}:{VERSION} .
- Ejemplo: docker build -t mgarcia92/emb:0.1 .

docker run -it --name {NAME} {USER}/{CONT_NAME}:{VERSION}
- Ejemplo: docker run -it --name emb_container mgarcia92/emb:0.1

## En el contenedor
from main import *
main()