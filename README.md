# Skynet
MLOps Infra

docker build -t {USER}/{CONT_NAME}:{VERSION} .
- Ejemplo: docker build -t mgarcia92/emb:0.1 .

docker run -it --name {NAME} {USER}/{CONT_NAME}:{VERSION}
- Ejemplo: docker run -it --name emb_container mgarcia92/emb:0.1

# En el contenedor
from main import *
main()