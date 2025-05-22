import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter # Можно использовать и свой простой сплиттер
from dotenv import load_dotenv

load_dotenv()

TEXTS_DIR = "../data/knowledge_base/texts/"
VECTOR_STORE_DIR = "../data/vector_store_cache/"
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "faiss_index.idx")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.pkl")

# Убедимся, что директория для векторного хранилища существует
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

def load_documents(base_path):
    docs = []
    for root, _, files in os.walk(base_path):
        for file_name in files:
            if file_name.endswith(".txt"):
                file_path = os.path.join(root, file_name)
                topic = os.path.basename(root) # Получаем название папки как тему
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                        docs.append({"text": text, "source": file_path, "topic": topic})
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return docs

def main():
    print("Loading documents...")
    documents = load_documents(TEXTS_DIR)
    if not documents:
        print("No documents found. Exiting.")
        return

    print(f"Loaded {len(documents)} documents.")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Размер чанка (в символах)
        chunk_overlap=200 # Перекрытие между чанками
    )
    
    all_chunks_text = []
    metadata = []
    
    for doc_idx, doc in enumerate(documents):
        chunks = text_splitter.split_text(doc["text"])
        for chunk_idx, chunk_text in enumerate(chunks):
            all_chunks_text.append(chunk_text)
            metadata.append({
                "source": doc["source"],
                "topic": doc["topic"],
                "chunk_id": f"doc{doc_idx}_chunk{chunk_idx}" 
            })

    if not all_chunks_text:
        print("No text chunks generated. Exiting.")
        return
        
    print(f"Generated {len(all_chunks_text)} chunks.")

    print("Loading embedding model...")
    # Используем SentenceTransformer для локальных эмбеддингов
    # Если используете OpenAI, нужно будет адаптировать под их API
    embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    model = SentenceTransformer(embedding_model_name)

    print("Generating embeddings...")
    embeddings = model.encode(all_chunks_text, show_progress_bar=True)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension) # L2-норма (евклидово расстояние)
    index.add(embeddings)

    print(f"FAISS index created with {index.ntotal} vectors.")

    print(f"Saving FAISS index to {FAISS_INDEX_PATH}")
    faiss.write_index(index, FAISS_INDEX_PATH)

    print(f"Saving metadata to {METADATA_PATH}")
    with open(METADATA_PATH, 'wb') as f:
        pickle.dump({"texts": all_chunks_text, "metadata": metadata}, f)

    print("Vector store built successfully!")

if __name__ == "__main__":
    main()