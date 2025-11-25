# 📁 app.py
from flask import Flask, request, jsonify
import telegram
from bot.telegram_handler import process_message
import os
import logging

app = Flask(__name__)
bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))
logging.basicConfig(level=logging.INFO)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        process_message(bot, update)
        return jsonify({'status': 'ok'})
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/health', methods=['GET'])
def health():
    return 'Bot is running'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
