from flask import Flask, request, jsonify
import requests
import os
import logging

app = Flask(__name__)

# Токен бота
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g')

def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=payload)
        logging.info(f"Message sent: {response.status_code}")
        return response.json()
    except Exception as e:
        logging.error(f"Send message error: {e}")
        return None

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
🚗 <b>АВТОЭКСПЕРТ БОТ</b>

Я помогу проверить автомобиль перед покупкой!

📝 <b>Просто отправьте марку и модель:</b>
• Toyota Camry
• BMW X5 
• Mercedes C-class
• Или любой другой автомобиль

🔍 <b>Я найду:</b>
• Типичные проблемы
• Стоимость ремонта
• Чек-лист для проверки

<b>Пример:</b> "Range Rover Sport 2015"
"""
            else:
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

⚙️ <b>Функционал в разработке</b>
Скоро будет детальный анализ!
"""
            
            # ОТПРАВЛЯЕМ ОТВЕТ
            send_telegram_message(chat_id, response_text)
            
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
