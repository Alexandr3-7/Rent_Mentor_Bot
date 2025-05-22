from .vector_store import VectorStore
from .llm_service import LLMService

class RAGProcessor:
    def __init__(self):
        self.vector_store = VectorStore()
        self.llm_service = LLMService()
        print("RAGProcessor initialized.")

    def get_answer(self, user_question, k_results=3):
        print(f"RAG: Received question: {user_question}")
        relevant_chunks = self.vector_store.search(user_question, k=k_results)
        
        if not relevant_chunks:
            print("RAG: No relevant chunks found.")
            # Можно вернуть стандартный ответ или дать LLM шанс ответить без контекста (с осторожностью)
            # return "К сожалению, я не нашел релевантной информации по вашему вопросу в базе знаний."
            # Дадим LLM шанс, но он должен сам сказать, что не нашел
            return self.llm_service.generate_response(user_question, [])


        print(f"RAG: Found {len(relevant_chunks)} relevant chunks.")
        # for i, chunk in enumerate(relevant_chunks):
        #     print(f"  Chunk {i+1} source: {chunk['metadata']['source']}")

        llm_response = self.llm_service.generate_response(user_question, relevant_chunks)
        print(f"RAG: LLM response generated.")
        return llm_response

# Пример использования (для отладки)
if __name__ == '__main__':
    # Запускать из корня проекта: python core/rag_processor.py
    try:
        rag = RAGProcessor()
        # Убедитесь, что build_vector_store.py отработал
        # и в data/knowledge_base/texts/Найм/ есть файл с инфо о горничных
        test_question = "Расскажи про найм горничных" 
        answer = rag.get_answer(test_question)
        print(f"\nQuestion: {test_question}")
        print(f"Answer: {answer}")
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred in RAG processor: {e}")