from flask import Flask, request
import telegram
import os
import logging

app = Flask(__name__)
bot = telegram.Bot(token=os.getenv('TELEGRAM_BOT_TOKEN'))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    chat_id = update['message']['chat']['id']
    text = update['message'].get('text', '')
    
    if text == '/start':
        bot.send_message(chat_id=chat_id, text="🚗 Бот запущен! Отправьте марку автомобиля для анализа")
    else:
        bot.send_message(chat_id=chat_id, text=f"🔍 Ищу информацию по '{text}'...")
        # Заглушка - здесь будет реальный поиск
        report = f"""
🔍 *{text.upper()} - ОТЧЕТ*

⚙️ *ТИПИЧНЫЕ ПРОБЛЕМЫ:*
• Двигатель - 30% случаев
• КПП - 25% случаев  
• Подвеска - 35% случаев

💡 *ЧТО ПРОВЕРИТЬ:*
• Тест-драйв с прогретым двигателем
• Диагностика на СТО
• Проверка истории обслуживания

*Бот в стадии разработки*
"""
        bot.send_message(chat_id=chat_id, text=report, parse_mode='Markdown')
    
    return 'ok'

@app.route('/')
def home():
    return 'Bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
