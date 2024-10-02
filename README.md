# LLMOps-Arch
MLOps y LLMOps Infra

# Componentes 
## Fabrica:
- FDD: Fabrica de Datos
- FAI: Fabrica de IA

## Capa
- STG: Stage
- UNI: Universal

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
FAI-STG01-TP01-01
- FAI: Fabrica de IA
- STG: Stage (correlativo 01)
- TP: LLM (Le he agregado este detalle como ejemplo de arquitectura LLM)
- 01: Correlativo de proceso

FAI-STG01-TP01-02
- Continuacion de proceso, lo estoy afinando. Le quise agregar este "job" para la evaluacion del embedding.

# Implementacion de prueba
docker build -t {USER}/{CONT_NAME}:{VERSION} .
- Ejemplo: docker build -t mgarcia92/emb:0.1 .

docker run -it --name {NAME} {USER}/{CONT_NAME}:{VERSION}
- Ejemplo: docker run -it --name emb_container mgarcia92/emb:0.1

## En el contenedor
from main import *
main()