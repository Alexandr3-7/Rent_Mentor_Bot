import os
from aiogram import Router, F, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from .keyboards import main_menu_keyboard, template_topics_keyboard
from core.rag_processor import RAGProcessor # Относительный импорт

router = Router()
rag_processor = RAGProcessor() # Инициализируем один раз

TEMPLATES_DIR = "data/knowledge_base/templates/" # Относительно корня

# Состояния для запроса шаблонов
class TemplateRequest(StatesGroup):
    waiting_for_topic = State()
    waiting_for_keywords = State()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! 👋 Я твой бот-наставник по посуточной аренде.\n"
        "Ты можешь выбрать тему из меню ниже или задать мне вопрос текстом.",
        reply_markup=main_menu_keyboard()
    )

@router.callback_query(F.data == "back_to_main_menu")
async def cq_back_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Чем могу помочь?",
        reply_markup=main_menu_keyboard()
    )
    await callback.answer()

# Обработка выбора темы из главного меню
@router.callback_query(F.data.startswith("topic_"))
async def cq_topic_selected(callback: types.CallbackQuery):
    topic_name = callback.data.split("_")[1].capitalize()
    # Можно сразу дать какой-то общий ответ по теме или предложить задать вопрос
    # Для примера, просто подтвердим выбор и предложим задать вопрос
    await callback.message.answer(
        f"Выбрана тема: {topic_name}. Задайте свой вопрос по этой теме."
    )
    await callback.answer() # Закрыть "часики" на кнопке

# --- Обработка запроса шаблонов ---
@router.callback_query(F.data == "request_template_start")
async def cq_request_template_start(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(TemplateRequest.waiting_for_keywords) # Сразу на ввод ключевых слов
    # await state.set_state(TemplateRequest.waiting_for_topic) # Если хотим сначала выбор темы
    # await callback.message.edit_text(
    #     "По какой теме вам нужен шаблон?",
    #     reply_markup=template_topics_keyboard()
    # )
    await callback.message.edit_text(
        "Пожалуйста, напишите ключевые слова для поиска шаблона (например, 'вакансия менеджер' или 'чек-лист горничная')."
    )
    await callback.answer()

# @router.callback_query(TemplateRequest.waiting_for_topic, F.data.startswith("template_topic_"))
# async def cq_template_topic_selected(callback: types.CallbackQuery, state: FSMContext):
#     topic_name = callback.data.split("_")[-1] # последние слово после template_topic_
#     await state.update_data(selected_topic=topic_name)
#     await state.set_state(TemplateRequest.waiting_for_keywords)
#     await callback.message.edit_text(
#         f"Тема: {topic_name.capitalize()}. Теперь введите ключевые слова для поиска шаблона (например, 'вакансия', 'регламент')."
#     )
#     await callback.answer()

@router.message(TemplateRequest.waiting_for_keywords)
async def process_template_keywords(message: types.Message, state: FSMContext):
    # data = await state.get_data()
    # topic = data.get("selected_topic") # если был выбор темы
    keywords = message.text.lower().split()
    await state.clear()

    found_files = []
    # Упрощенный поиск: ищем в названиях файлов по всем темам (или в конкретной, если был выбор)
    # search_path = os.path.join(TEMPLATES_DIR, topic) if topic else TEMPLATES_DIR
    search_path = TEMPLATES_DIR

    for root, _, files in os.walk(search_path):
        for file_name in files:
            # Ищем все ключевые слова в имени файла
            if all(keyword in file_name.lower() for keyword in keywords):
                found_files.append(os.path.join(root, file_name))
    
    if found_files:
        await message.answer(f"Нашел следующие шаблоны по вашему запросу ({message.text}):")
        for file_path in found_files:
            try:
                doc = types.FSInputFile(file_path)
                await message.answer_document(doc)
            except Exception as e:
                await message.answer(f"Не удалось отправить файл {os.path.basename(file_path)}: {e}")
        # Предложить вернуться в меню
        await message.answer("Хотите что-то еще?", reply_markup=main_menu_keyboard())
    else:
        await message.answer(
            f"К сожалению, не нашел шаблонов по запросу '{message.text}'. "
            "Попробуйте другие ключевые слова или проверьте наличие шаблонов в базе.",
            reply_markup=main_menu_keyboard()
        )


# Обработка свободного текстового вопроса
@router.message(F.text)
async def handle_text_question(message: types.Message):
    user_question = message.text
    
    # Простая проверка на запрос шаблона по ключевым словам
    # (можно улучшить, например, через NLP классификацию интента)
    template_keywords = ["шаблон", "чек-лист", "регламент", "документ", "инструкция", "вакансия"]
    if any(keyword in user_question.lower() for keyword in template_keywords):
        # Перенаправляем на логику поиска шаблонов
        # Это дублирует немного FSM, но упрощает для простого текстового запроса
        keywords_for_search = user_question.lower()
        for tk in template_keywords: # уберем сами ключевые слова из запроса
            keywords_for_search = keywords_for_search.replace(tk, "")
        keywords_for_search = keywords_for_search.strip().split()

        if not keywords_for_search:
            await message.answer("Пожалуйста, уточните, какой именно шаблон вам нужен (например, 'шаблон вакансии менеджера').", reply_markup=main_menu_keyboard())
            return

        # Процедура поиска файлов, аналогичная той, что в FSM
        found_files = []
        for root, _, files in os.walk(TEMPLATES_DIR):
            for file_name in files:
                if all(keyword in file_name.lower() for keyword in keywords_for_search):
                    found_files.append(os.path.join(root, file_name))
        
        if found_files:
            await message.answer(f"Похоже, вы ищете шаблон. Нашел следующее по запросу '{user_question}':")
            for file_path in found_files:
                try:
                    doc = types.FSInputFile(file_path)
                    await message.answer_document(doc)
                except Exception as e:
                    await message.answer(f"Не удалось отправить файл {os.path.basename(file_path)}: {e}")
            await message.answer("Если это не то, что вы искали, или у вас есть другой вопрос, пожалуйста, задайте его.", reply_markup=main_menu_keyboard())
            return
        else:
            await message.answer(f"Я понял, что вы ищете шаблон, но не смог найти подходящий по запросу '{user_question}'. Попробуйте переформулировать или выберите опцию 'Запросить шаблон' в меню.", reply_markup=main_menu_keyboard())
            return


    # Если не запрос шаблона, то это вопрос к RAG
    await message.answer("Получил ваш вопрос, сейчас подумаю... 🤔")
    
    # Используем run_in_executor для неблокирующего вызова RAG
    # так как RAG может быть ресурсоемким
    loop = asyncio.get_event_loop()
    try:
        # Это важно, так как rag_processor.get_answer() - синхронная и блокирующая функция
        # Если она будет асинхронной внутри, то это не нужно.
        # Но sentence-transformers и faiss по умолчанию синхронные.
        answer = await loop.run_in_executor(None, rag_processor.get_answer, user_question)
    except Exception as e:
        print(f"Error during RAG processing: {e}")
        answer = "Произошла внутренняя ошибка при обработке вашего запроса. Пожалуйста, попробуйте позже."

    await message.answer(answer, reply_markup=main_menu_keyboard())