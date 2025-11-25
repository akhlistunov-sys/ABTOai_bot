from flask import Flask, request, jsonify
import os
import logging

app = Flask(__name__)

# Простая заглушка для Telegram
def send_telegram_message(token, chat_id, text):
    import requests
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    requests.post(url, json=payload)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        message = update.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '')
        
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if text == '/start':
            response_text = """
🚗 <b>АВТОЭКСПЕРТ БОТ</b>

Я помогу проверить автомобиль перед покупкой!

📝 <b>Просто отправьте:</b>
• Марку и модель авто
• Или описание проблемы

🔍 <b>Я найду:</b>
• Типичные проблемы
• Стоимость ремонта
• Чек-лист для проверки

<b>Пример:</b> "Toyota Camry 2015" или "BMW X5 дизель"
            """
        else:
            response_text = f"""
🔍 <b>ИЩУ ИНФОРМАЦИЮ ПО:</b> {text}

📊 <b>ТИПИЧНЫЕ ПРОБЛЕМЫ:</b>
• Двигатель - 30% случаев
• КПП - 25% случаев  
• Подвеска - 35% случаев
• Электрика - 20% случаев

💡 <b>ЧТО ПРОВЕРИТЬ:</b>
• Тест-драйв с прогретым двигателем
• Компьютерная диагностика
• История обслуживания

🔧 <b>Бот в стадии разработки</b>
Функционал постоянно улучшается!
            """
        
        send_telegram_message(token, chat_id, response_text)
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/')
def home():
    return '🚗 AutoExpert Bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
