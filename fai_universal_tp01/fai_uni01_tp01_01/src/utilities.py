import os
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import json
import glob
import pypdfium2
import uuid

def load_documents():
    # Cargar documentos PDF y JSON
    pdf_files = glob.glob(os.path.join(os.getenv("DATA_PATH"), "*.pdf"))
    json_files = glob.glob(os.path.join(os.getenv("DATA_PATH"), "*.json"))

    documents = []
    for pdf_file in pdf_files:
        pdf_text = extract_text_from_pdf(pdf_file)
        if pdf_text.strip():
            documents.append(Document(page_content=pdf_text, metadata={"source": pdf_file}))

    for json_file in json_files:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            text = extract_text_from_json(data)
            if text.strip():
                documents.append(Document(page_content=text, metadata={"source": json_file}))

    return documents

def extract_text_from_pdf(pdf_file):
    text = ""
    try:
        pdf_document = pypdfium2.PdfDocument(pdf_file)
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text += page.get_textpage().get_text_range() + "\n"
        pdf_document.close()
    except Exception as e:
        print(f"Error al abrir PDF: {pdf_file}. Error: {e}")
    return text

def extract_text_from_json(data):
    documents = []
    if isinstance(data, list):
        for item in data:
            input_text = item.get("input", "")
            output_text = item.get("output", "")
            full_text = f"Título: {input_text}\n\nContenido: {output_text}"
            documents.append(full_text)
    return "\n".join(documents)

def organize_documents_in_tree(documents):
    tree = {}
    for doc in documents:
        source = doc.metadata["source"]
        category = source.split('/')[-1].split('_')[0]  # Categorizar por nombre de archivo
        if category not in tree:
            tree[category] = []
        tree[category].append(doc)
    return tree

def split_documents_in_chunks(document_tree, chunk_size=1000):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
    chunks = []
    for category, docs in document_tree.items():
        for doc in docs:
            doc_chunks = text_splitter.split_text(doc.page_content)
            chunks.extend([Document(page_content=chunk, metadata=doc.metadata) for chunk in doc_chunks])
    return chunks

def save_to_chroma(chunks, chroma_client, embedding_model):
    texts = [chunk.page_content for chunk in chunks if chunk.page_content.strip()]
    metadatas = [chunk.metadata for chunk in chunks if chunk.page_content.strip()]
    ids = [str(uuid.uuid4()) for _ in range(len(texts))]

    collection_name = os.getenv("DB_NAME")
    if collection_name in [col.name for col in chroma_client.list_collections()]:
        collection = chroma_client.get_collection(name=collection_name)
    else:
        collection = chroma_client.create_collection(name=collection_name)

    BATCH_SIZE = 200
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i + BATCH_SIZE]
        batch_metadatas = metadatas[i:i + BATCH_SIZE]
        batch_ids = ids[i:i + BATCH_SIZE]
        embeddings = embedding_model.embed_documents(batch_texts)

        collection.upsert(
            documents=batch_texts,
            metadatas=batch_metadatas,
            ids=batch_ids,
            embeddings=embeddings
        )

    print(f"Guardados {len(texts)} chunks en la colección {collection_name}.")