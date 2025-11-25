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

Я помогу проверить автомобиль перед покупкой
