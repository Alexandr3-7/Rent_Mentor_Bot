import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables.")
        self.client = OpenAI(api_key=self.api_key)
        self.model_name = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")

    def generate_response(self, user_question, context_chunks):
        context_str = "\n\n".join([chunk["text"] for chunk in context_chunks])
        
        system_prompt = """Ты — дружелюбный и опытный наставник по бизнесу посуточной аренды.
Твоя задача — помочь ученику, отвечая на его вопросы просто, понятно и структурированно.
Используй только информацию из предоставленного ниже КОНТЕКСТА.
Если в КОНТЕКСТЕ нет ответа на вопрос, честно скажи, что не можешь ответить на основе имеющихся материалов, и предложи ученику переформулировать вопрос или выбрать другую тему.
Не придумывай информацию от себя.
Отвечай развернуто, объясняй сложные моменты простыми словами. Можешь использовать списки, если это уместно.
"""

        user_prompt_template = f"""КОНТЕКСТ:
---
{context_str}
---

ВОПРОС УЧЕНИКА: {user_question}

ТВОЙ ОТВЕТ НАСТАВНИКА:"""

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt_template}
                ],
                temperature=0.7, # Немного креативности, но не слишком
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "Извините, произошла ошибка при попытке сгенерировать ответ. Пожалуйста, попробуйте позже."

# Пример использования (для отладки)
if __name__ == '__main__':
    # Запускать из корня проекта: python core/llm_service.py
    llm = LLMService()
    # Моделируем контекст
    mock_context = [
        {"text": "Для найма горничной важно проверить рекомендации."},
        {"text": "Обучение горничной должно включать стандарты уборки."}
    ]
    question = "Что важно при найме горничной?"
    answer = llm.generate_response(question, mock_context)
    print(f"Question: {question}")
    print(f"Answer: {answer}")