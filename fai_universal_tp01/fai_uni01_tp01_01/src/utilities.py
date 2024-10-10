import os
from langchain.schema import Document
import chromadb
import json
import glob
import pypdfium2
import uuid
import spacy

# Cargar el modelo de SpaCy para español
nlp = spacy.load('es_core_news_sm')

def normalize_text_preserve_entities(text):
    """
    Normaliza el texto preservando la capitalización de entidades nombradas (personas, organizaciones, etc.).
    """
    # Procesar el texto con SpaCy
    doc = nlp(text)
    
    normalized_tokens = []
    for token in doc:
        # Si es una entidad nombrada, no convertir a minúsculas
        if token.ent_type_:
            normalized_tokens.append(token.text)  # Mantener la capitalización original
        else:
            normalized_tokens.append(token.text.lower())  # Convertir a minúsculas
    
    return " ".join(normalized_tokens)

def extract_metadata(text, source):
    """
    Extrae entidades nombradas y fechas automáticamente utilizando SpaCy como metadatos.
    """
    doc = nlp(text)
    metadata = {
        "source": source,
        "persons": [],
        "organizations": [],
        "locations": [],
        "dates": []
    }

    for ent in doc.ents:
        if ent.label_ == "PER":
            metadata["persons"].append(ent.text)
        elif ent.label_ == "ORG":
            metadata["organizations"].append(ent.text)
        elif ent.label_ in ["LOC", "GPE"]:
            metadata["locations"].append(ent.text)
        elif ent.label_ == "DATE":
            metadata["dates"].append(ent.text)

    return metadata

# Funciones para cargar y procesar documentos
def load_documents():
    # Cargar documentos PDF usando pypdfium2
    pdf_files = glob.glob(os.path.join(os.getenv("DATA_PATH"), "*.pdf"))
    pdf_documents = []
    for pdf_file in pdf_files:
        pdf_text = extract_text_from_pdf(pdf_file)
        if pdf_text.strip():
            metadata = extract_metadata(pdf_text, pdf_file)
            pdf_documents.append(Document(page_content=pdf_text, metadata=metadata))
        else:
            print(f"No se extrajo texto del archivo PDF: {pdf_file}")

    # Cargar documentos JSON y extraer el contenido de input y output
    json_files = glob.glob(os.path.join(os.getenv("DATA_PATH"), "*.json"))
    json_documents = []
    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as file:
            try:
                data = json.load(file)
                # Extraer el texto de 'input' y 'output'
                text = extract_text_from_json(data)
                if text.strip():
                    metadata = extract_metadata(text, json_file)
                    json_documents.append(Document(page_content=text, metadata=metadata))
                else:
                    print(f"No se extrajo texto del archivo JSON: {json_file}")
            except json.JSONDecodeError:
                print(f"Error al decodificar JSON del archivo: {json_file}")

    documents = pdf_documents + json_documents
    print(f"Cargados {len(pdf_documents)} documentos PDF y {len(json_documents)} documentos JSON.")
    return documents

def extract_text_from_json(data):
    """
    Extrae los valores de 'input' como titulos y 'output' como contenido.
    """
    if isinstance(data, list):  # Asumimos que los registros estan en una lista
        documents = []
        for item in data:
            if "input" in item and "output" in item:
                input_text = item.get("input", "")
                output_text = item.get("output", "")
                # Combina el input como titulo y el output como contenido
                full_text = f"Titulo: {input_text}\n\nContenido: {output_text}"
                # Normalizar el texto extraido preservando entidades
                normalized_text = normalize_text_preserve_entities(full_text)
                documents.append(normalized_text)
        return "\n".join(documents)
    else:
        return ""

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_document = pypdfium2.PdfDocument(pdf_file)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            page_text = page.get_textpage().get_text_range()
            if page_text:
                # Normalizar el texto extraido preservando entidades
                normalized_text = normalize_text_preserve_entities(page_text)
                text += normalized_text + "\n"
            else:
                print(f"No se extrajo texto de la pagina {page_num} del archivo PDF: {pdf_file}")
        pdf_document.close()
    except Exception as e:
        print(f"Error al abrir el archivo PDF: {pdf_file}. Error: {e}")
    return text

def split_text(documents, nlp, max_chunk_size=1000):
    """
    Divide los documentos en chunks semanticos utilizando SpaCy.
    """
    chunks = []
    for doc in documents:
        text = doc.page_content
        spacy_doc = nlp(text)
        sentences = [sent.text.strip() for sent in spacy_doc.sents]

        current_chunk = ''
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length <= max_chunk_size:
                current_chunk += sentence + ' '
                current_length += sentence_length
            else:
                # Agregar el chunk actual a la lista de chunks
                chunks.append(Document(page_content=current_chunk.strip(), metadata=doc.metadata))
                # Iniciar un nuevo chunk
                current_chunk = sentence + ' '
                current_length = sentence_length

        # Agregar el ultimo chunk
        if current_chunk:
            chunks.append(Document(page_content=current_chunk.strip(), metadata=doc.metadata))

    print(f"Divididos {len(documents)} documentos en {len(chunks)} chunks.")
    return chunks

def save_to_chroma(chunks, chroma_client, embedding_model):
    # Preparar datos
    texts = [chunk.page_content for chunk in chunks if chunk.page_content.strip()]
    metadatas = [chunk.metadata for chunk in chunks if chunk.page_content.strip()]
    ids = [str(uuid.uuid4()) for _ in range(len(texts))]

    # Crear o obtener la coleccion
    if os.getenv("DB_NAME") in [collection.name for collection in chroma_client.list_collections()]:
        collection = chroma_client.get_collection(name=os.getenv("DB_NAME"))
    else:
        collection = chroma_client.create_collection(name=os.getenv("DB_NAME"))

    # Procesar en lotes
    BATCH_SIZE = 200
    def batch(iterable, size):
        for i in range(0, len(iterable), size):
            yield iterable[i:i + size]

    for texts_batch, metadatas_batch, ids_batch in zip(batch(texts, BATCH_SIZE), batch(metadatas, BATCH_SIZE), batch(ids, BATCH_SIZE)):
        embeddings_batch = embedding_model.embed_documents(texts_batch)
        collection.upsert(
            documents=texts_batch,
            metadatas=metadatas_batch,
            ids=ids_batch,
            embeddings=embeddings_batch
        )

    # Configura el cliente para que persista la base de datos en la ruta especificada
    client = chromadb.PersistentClient(path=os.getenv("CHROMA_PATH"))

    print(f"Guardados {len(texts)} chunks en la coleccion.")
