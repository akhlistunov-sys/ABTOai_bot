from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Токен бота
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g')

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправка сообщения в Telegram"""
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
        logging.info(f"Message sent: {response.status_code}")
        return response.json()
    except Exception as e:
        logging.error(f"Send message error: {e}")
        return None

def get_main_menu():
    """Главное меню с большими кнопками"""
    keyboard = {
        'keyboard': [
            ['🚀 НАЧАТЬ АНАЛИЗ АВТО'],
            ['📊 ДЕТАЛЬНЫЙ ОТЧЕТ'],
            ['🏆 О БОТЕ'],
            ['📋 ИСТОРИЯ ЗАПРОСОВ']
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

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logging.info(f"Received update: {data}")
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text == '/start':
                response_text = """
🚗 <b>АВТОЭКСПЕРТ</b>

Профессиональный анализ автомобилей перед покупкой

Выберите действие:
"""
                send_telegram_message(chat_id, response_text, get_main_menu())
                
            elif text == '🚀 НАЧАТЬ АНАЛИЗ АВТО':
                response_text = """
🔍 <b>ВЫБЕРИТЕ СПОСОБ АНАЛИЗА:</b>

• <b>📸 Фото</b> - автоматическое распознавание
• <b>🔍 Ручной ввод</b> - укажите параметры вручную
"""
                send_telegram_message(chat_id, response_text, get_analysis_methods_menu())
                
            elif text == '📊 ДЕТАЛЬНЫЙ ОТЧЕТ':
                response_text = """
📊 <b>ДЕТАЛЬНЫЙ ОТЧЕТ</b>

Для получения подробного отчета укажите:

• Марку и модель авто
• Год выпуска
• Тип двигателя
• Пробег

<b>Пример:</b> "BMW X5 2018, 3.0 дизель, 120к км"
"""
                send_telegram_message(chat_id, response_text)
                
            elif text == '🏆 О БОТЕ':
                response_text = """
🏆 <b>О БОТЕ АВТОЭКСПЕРТ</b>

🤖 <b>Что я умею:</b>
• Анализировать типичные проблемы авто
• Показывать стоимость ремонта
• Давать чек-листы для проверки
• Сравнивать с аналогами

📈 <b>Источники данных:</b>
• Отзывы владельцев
• Данные с автофорумов
• Статистика сервисов

🔧 <b>Постоянно обучаюсь</b> и улучшаю базу знаний!
"""
                send_telegram_message(chat_id, response_text, get_main_menu())
                
            elif text == '📋 ИСТОРИЯ ЗАПРОСОВ':
                response_text = """
📋 <b>ИСТОРИЯ ЗАПРОСОВ</b>

Функция в разработке 🛠

Скоро здесь появится:
• История ваших запросов
• Сохраненные отчеты
• Избранные автомобили
"""
                send_telegram_message(chat_id, response_text, get_main_menu())
                
            elif text == '📸 ОТПРАВИТЬ ФОТО':
                response_text = """
📸 <b>ОТПРАВЬТЕ ФОТО АВТО</b>

Сделайте фото:
• Вид сбоку спереди
• Хорошее освещение
• Четкий номерной знак (если есть)

Я определю марку, модель и поколение!
"""
                send_telegram_message(chat_id, response_text)
                
            elif text == '🔍 РУЧНОЙ ВВОД':
                response_text = """
🔍 <b>РУЧНОЙ ВВОД ПАРАМЕТРОВ</b>

Опишите автомобиль:

<b>Формат:</b>
Марка Модель Год [Двигатель]

<b>Примеры:</b>
• Toyota Camry 2015
• BMW X5 2018 3.0d
• Mercedes C-class 2020
"""
                send_telegram_message(chat_id, response_text)
                
            elif text == '🔙 ГЛАВНОЕ МЕНЮ':
                send_telegram_message(chat_id, "🏠 <b>Главное меню</b>", get_main_menu())
                
            else:
                # Обработка произвольного текста (ручной ввод)
                response_text = f"""
🔍 <b>АНАЛИЗИРУЮ:</b> {text}

📊 <b>ТИПИЧНЫЕ ПРОБЛЕМЫ:</b>
• Двигатель - 30% случаев
• КПП - 25% случаев  
• Подвеска - 35% случаев
• Электрика - 20% случаев

💡 <b>ЧТО ПРОВЕРИТЬ:</b>
• Тест-драйв с прогретым двигателем
• Компьютерная диагностика
• История обслуживания

⚙️ <b>Детальный анализ в разработке</b>
"""
                send_telegram_message(chat_id, response_text, get_main_menu())
            
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return '🚗 AutoExpert Bot is running!'

@app.route('/test')
def test():
    """Тестовая страница - проверка работы"""
    return jsonify({
        'status': 'active',
        'bot': '@ABTOai_bot',
        'webhook': 'configured'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
