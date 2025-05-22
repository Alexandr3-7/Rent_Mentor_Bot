import os
import faiss
import pickle
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

VECTOR_STORE_DIR = "data/vector_store_cache/" # Относительно корня проекта
FAISS_INDEX_PATH = os.path.join(VECTOR_STORE_DIR, "faiss_index.idx")
METADATA_PATH = os.path.join(VECTOR_STORE_DIR, "metadata.pkl")

class VectorStore:
    def __init__(self):
        if not os.path.exists(FAISS_INDEX_PATH) or not os.path.exists(METADATA_PATH):
            raise FileNotFoundError("FAISS index or metadata not found. Please run build_vector_store.py first.")
            
        self.index = faiss.read_index(FAISS_INDEX_PATH)
        with open(METADATA_PATH, 'rb') as f:
            data = pickle.load(f)
            self.texts = data["texts"]
            self.metadata = data["metadata"]
        
        embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        print("VectorStore initialized.")

    def search(self, query_text, k=5):
        query_embedding = self.embedding_model.encode([query_text])
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for i in range(len(indices[0])):
            idx = indices[0][i]
            if idx < len(self.texts): # Проверка на выход за пределы
                 results.append({
                    "text": self.texts[idx],
                    "metadata": self.metadata[idx],
                    "distance": distances[0][i]
                })
        return results

# Пример использования (для отладки)
if __name__ == '__main__':
    # Запускать из корня проекта: python core/vector_store.py
    # Перед этим убедитесь, что build_vector_store.py отработал
    try:
        store = VectorStore()
        sample_query = "Как нанять хорошую горничную?"
        search_results = store.search(sample_query)
        print(f"Search results for '{sample_query}':")
        for res in search_results:
            print(f"  Topic: {res['metadata']['topic']}, Source: {res['metadata']['source'][:30]}..., Distance: {res['distance']:.4f}")
            # print(f"  Text: {res['text'][:100]}...") # Раскомментировать для вывода текста
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred: {e}")