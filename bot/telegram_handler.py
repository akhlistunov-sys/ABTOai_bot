# 📁 bot/telegram_handler.py
import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from catalog.car_models import get_car_brands, get_models_by_brand, get_generations_by_model
from utils.report_formatter import generate_report
from api.forum_searcher import search_car_problems

def process_message(bot, update):
    try:
        if 'message' in update:
            message = update['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if 'photo' in message:
                # Обработка фото
                handle_photo(bot, chat_id, message['photo'][-1]['file_id'])
            elif text == '/start':
                show_main_menu(bot, chat_id)
            elif text.startswith('brand_'):
                handle_brand_selection(bot, chat_id, text)
            elif text.startswith('model_'):
                handle_model_selection(bot, chat_id, text)
            elif text.startswith('generation_'):
                handle_generation_selection(bot, chat_id, text)
            else:
                handle_text_message(bot, chat_id, text)
                
    except Exception as e:
        logging.error(f"Process message error: {e}")

def show_main_menu(bot, chat_id):
    keyboard = [
        ['📸 Отправить фото авто'],
        ['🔍 Найти по марке'],
        ['❓ Помощь']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.send_message(
        chat_id=chat_id,
        text="Выберите способ поиска:",
        reply_markup=reply_markup
    )

def handle_photo(bot, chat_id, file_id):
    # Заглушка для распознавания фото
    bot.send_message(chat_id, "📸 Фото получено. Определяю автомобиль...")
    
    # Имитация распознавания - в реальности здесь будет CV модель
    car_brands = get_car_brands()
    keyboard = [[brand] for brand in car_brands[:5]]  # Первые 5 марок
    keyboard.append(['🎯 Уточнить вручную'])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.send_message(
        chat_id=chat_id,
        text="Похоже на одну из этих марок. Выберите или уточните:",
        reply_markup=reply_markup
    )

def handle_brand_selection(bot, chat_id, brand):
    brand_name = brand.replace('brand_', '')
    models = get_models_by_brand(brand_name)
    
    keyboard = [[model] for model in models[:8]]  # Первые 8 моделей
    keyboard.append(['🔙 Назад'])
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    bot.send_message(
        chat_id=chat_id,
        text=f"Выберите модель {brand_name}:",
        reply_markup=reply_markup
    )

def handle_text_message(bot, chat_id, text):
    if text == '📸 Отправить фото авто':
        bot.send_message(chat_id, "Сделайте фото автомобила (вид сбоку спереди)")
    elif text == '🔍 Найти по марке':
        show_brand_selection(bot, chat_id)
    elif text == '❓ Помощь':
        show_help(bot, chat_id)
    else:
        # Попытка найти автомобиль по тексту
        search_car_by_text(bot, chat_id, text)

def show_brand_selection(bot, chat_id):
    car_brands = get_car_brands()
    keyboard = [car_brands[i:i+2] for i in range(0, len(car_brands), 2)]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    bot.send_message(
        chat_id=chat_id,
        text="Выберите марку автомобиля:",
        reply_markup=reply_markup
    )

def search_car_by_text(bot, chat_id, text):
    # Заглушка для поиска по тексту
    bot.send_message(chat_id, f"🔍 Ищу информацию по '{text}'...")
    
    # Имитация поиска проблем
    problems = search_car_problems(text)
    report = generate_report(text, problems)
    
    bot.send_message(
        chat_id=chat_id,
        text=report,
        parse_mode='Markdown'
    )

def show_help(bot, chat_id):
    help_text = """
🤖 *КАК РАБОТАЕТ БОТ:*

1. *Отправьте фото* авто - я определю марку и модель
2. *Выберите из списка* марку если фото нет
3. *Получите отчет* с проблемами и стоимостью ремонта

📊 *ЧТО В ОТЧЕТЕ:*
• Проблемы по пробегу
• Стоимость ремонта
• Чек-лист для проверки
• Рейтинги надежности

💡 *Совет:* Для точного отчета укажите двигатель и год выпуска
"""
    bot.send_message(chat_id, help_text, parse_mode='Markdown')
