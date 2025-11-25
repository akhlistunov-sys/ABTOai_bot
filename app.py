from flask import Flask, request, jsonify
import logging
from ai.text_processor import TextProcessor
from ai.car_identifier import CarIdentifier
from ai.forum_searcher import ForumSearcher
from ai.problem_analyzer import ProblemAnalyzer
from utils.formatters import ReportFormatter
from utils.logger import setup_logger

# Настройка логгера
logger = setup_logger()

app = Flask(__name__)

# Инициализация компонентов ИИ
text_processor = TextProcessor()
car_identifier = CarIdentifier()
forum_searcher = ForumSearcher()
problem_analyzer = ProblemAnalyzer()

# Токен бота
BOT_TOKEN = "7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g"

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправка сообщения в Telegram"""
    import requests
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    try:
        response = requests.post(url, json=payload)
        logger.info(f"Message sent to {chat_id}")
        return response.json()
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return None

def get_main_menu():
    """Главное меню"""
    keyboard = {
        'keyboard': [
            ['🚀 НАЧАТЬ АНАЛИЗ АВТО'],
            ['📊 ДЕТАЛЬНЫЙ ОТЧЕТ'],
            ['🏆 О БОТЕ', '📋 ИСТОРИЯ']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    return keyboard

def get_analysis_methods_menu():
    """Меню выбора метода анализа"""
    keyboard = {
        'keyboard': [
            ['📸 ОТПРАВИТЬ ФОТО'],
            ['🔍 РУЧНОЙ ВВОД'],
            ['🔙 ГЛАВНОЕ МЕНЮ']
        ],
        'resize_keyboard': True,
        'one_time_keyboard': False
    }
    return keyboard

def process_car_analysis(chat_id, text):
    """Обработка анализа автомобиля"""
    try:
        # Шаг 1: Идентификация авто
        progress_msg = send_telegram_message(chat_id, "🔍 Определяю параметры авто...")
        
        car_info = car_identifier.identify_car(text)
        logger.info(f"Car identified: {car_info}")
        
        if not car_info.get('brand'):
            send_telegram_message(chat_id, 
                "❌ Не удалось определить марку авто. Пожалуйста, укажите четче:\n\n"
                "Пример: <code>BMW X5 2015 дизель</code>\n"
                "Или: <code>Toyota Camry 2018</code>")
            return
        
        # Шаг 2: Поиск на форумах
        send_telegram_message(chat_id, 
            f"📊 Ищу информацию по {car_info['brand'].upper()} {car_info.get('model', '').upper()}...")
        
        search_results = forum_searcher.search_car_problems(car_info)
        
        # Шаг 3: Анализ проблем
        send_telegram_message(chat_id, "🔧 Анализирую найденные данные...")
        
        analysis = problem_analyzer.analyze_problems(search_results)
        
        # Шаг 4: Формирование отчета
        report = ReportFormatter.format_analysis_report(car_info, analysis)
        
        send_telegram_message(chat_id, report, get_main_menu())
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        error_msg = ReportFormatter.format_error_message(str(e))
        send_telegram_message(chat_id, error_msg, get_main_menu())

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука от Telegram"""
    try:
        data = request.get_json()
        logger.info(f"Received update: {data}")
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            # Обработка команд
            if text == '/start':
                welcome_text = """
🎯 <b>АВТОЭКСПЕРТ С ИСКУССТВЕННЫМ ИНТЕЛЛЕКТОМ</b>

🤖 Я анализирую автомобили с помощью ИИ:
• Ищу проблемы на форумах
• Анализирую отзывы владельцев  
• Рассчитываю стоимость ремонта
• Даю рекомендации

👇 <b>Начните анализ авто:</b>
"""
                send_telegram_message(chat_id, welcome_text, get_main_menu())
                
            elif text == '🚀 НАЧАТЬ АНАЛИЗ АВТО':
                methods_text = """
🔍 <b>ВЫБЕРИТЕ СПОСОБ АНАЛИЗА:</b>

📸 <b>Фото авто</b> - автоматическое распознавание
🔍 <b>Ручной ввод</b> - укажите параметры вручную

👇 Выберите вариант:
"""
                send_telegram_message(chat_id, methods_text, get_analysis_methods_menu())
                
            elif text == '🔍 РУЧНОЙ ВВОД':
                input_text = """
🏎️ <b>ОПИШИТЕ АВТОМОБИЛЬ:</b>

Укажите в свободной форме:
• Марку и модель
• Год выпуска
• Двигатель (если знаете)

<b>Примеры:</b>
• <code>BMW X5 2015 дизель</code>
• <code>Toyota Camry 2018 2.5</code>  
• <code>Mercedes C-class 2020</code>

📝 Напишите описание авто:
"""
                send_telegram_message(chat_id, input_text)
                
            elif text == '📊 ДЕТАЛЬНЫЙ ОТЧЕТ':
                report_text = """
📊 <b>ДЕТАЛЬНЫЙ ОТЧЕТ</b>

Для подробного анализа укажите:

🚗 <b>Марка и модель</b>
📅 <b>Год выпуска</b>
⚙️ <b>Двигатель</b> (если знаете)
🛣️ <b>Пробег</b> (если известен)

<b>Формат:</b>
<code>Марка Модель Год [Двигатель] [Пробег]</code>

📝 Напишите данные об авто:
"""
                send_telegram_message(chat_id, report_text)
                
            elif text == '🏆 О БОТЕ':
                about_text = """
🏆 <b>АВТОЭКСПЕРТ С ИИ</b>

🤖 <b>Технологии:</b>
• Искусственный интеллект
• Компьютерное зрение
• Обработка естественного языка
• Анализ больших данных

🔧 <b>Возможности:</b>
• Поиск проблем на Drive2, Drom
• Анализ сотен отзывов
• Расчет стоимости ремонта
• Рекомендации по проверке

📈 <b>База знаний:</b>
• 1000+ моделей автомобилей
• Реальные отзывы владельцев
• Актуальные цены на запчасти
"""
                send_telegram_message(chat_id, about_text, get_main_menu())
                
            elif text == '📋 ИСТОРИЯ':
                history_text = """
📋 <b>ИСТОРИЯ ЗАПРОСОВ</b>

🛠 <b>Функция в разработке</b>

Скоро здесь появится:
• История ваших запросов
• Сохраненные отчеты  
• Сравнительные анализы

📅 <b>Следите за обновлениями!</b>
"""
                send_telegram_message(chat_id, history_text, get_main_menu())
                
            elif text == '🔙 ГЛАВНОЕ МЕНЮ':
                send_telegram_message(chat_id, "🏠 <b>Главное меню</b>", get_main_menu())
                
            elif text == '📸 ОТПРАВИТЬ ФОТО':
                photo_text = """
📸 <b>ОТПРАВЬТЕ ФОТО АВТО</b>

🖼️ <b>Рекомендации:</b>
• Вид сбоку спереди
• Хорошее освещение
• Четкий автомобиль в кадре

📱 Сделайте фото и отправьте его в этот чат!

<b>Или используйте ручной ввод:</b>
"""
                send_telegram_message(chat_id, photo_text, get_analysis_methods_menu())
                
            else:
                # Обработка произвольного текста - запуск анализа
                process_car_analysis(chat_id, text)
            
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return '🚗 AutoExpert AI Bot is running!'

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'ai_components': {
            'text_processor': 'active',
            'car_identifier': 'active', 
            'forum_searcher': 'active',
            'problem_analyzer': 'active'
        }
    })

if __name__ == '__main__':
    logger.info("🚀 Starting AutoExpert AI Bot...")
    app.run(host='0.0.0.0', port=5000, debug=False)
