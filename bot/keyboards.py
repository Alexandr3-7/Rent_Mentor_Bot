from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Темы могут быть загружены динамически, например, из названий папок в data/knowledge_base/texts/
AVAILABLE_TOPICS = ["Найм", "Продажи", "Финансы", "Управление", "Горничные"] # Дополните или загружайте динамически

def main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton(text=topic, callback_data=f"topic_{topic.lower()}")] for topic in AVAILABLE_TOPICS
    ]
    # Можно добавить кнопку для запроса шаблона
    buttons.append([InlineKeyboardButton(text="📄 Запросить шаблон", callback_data="request_template_start")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

def template_topics_keyboard():
    # Предполагаем, что темы для шаблонов те же, что и для текстов
    buttons = [
        [InlineKeyboardButton(text=topic, callback_data=f"template_topic_{topic.lower()}")] for topic in AVAILABLE_TOPICS
    ]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back_to_main_menu")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard