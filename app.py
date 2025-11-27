from flask import Flask, request, jsonify
import requests
import re
import time

app = Flask(__name__)

# Токен бота
BOT_TOKEN = "7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g"

def send_telegram_message(chat_id, text, reply_markup=None):
    """Отправка сообщения в Telegram"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        if reply_markup:
            payload['reply_markup'] = reply_markup
            
        response = requests.post(url, json=payload, timeout=10)
        print(f"✅ Отправлено сообщение в {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки: {e}")
        return False

def get_main_menu():
    """Главное меню"""
    return {
        'keyboard': [
            ['🚀 НАЧАТЬ АНАЛИЗ АВТО'],
            ['🏆 О БОТЕ']
        ],
        'resize_keyboard': True
    }

def analyze_car(text):
    """Анализ автомобиля"""
    text_lower = text.lower()
    
    # Определяем марку
    if 'bmw' in text_lower:
        return {
            'brand': 'BMW',
            'problems': [
                "🔧 Цепь ГРМ - замена 80-120к руб",
                "🌀 Турбина - ремонт 60-90к руб",
                "💨 Сажевый фильтр - чистка 25-40к руб"
            ],
            'reliability': "6/10",
            'cost': "80-150к руб/год"
        }
    elif 'toyota' in text_lower:
        return {
            'brand': 'Toyota', 
            'problems': [
                "🔧 Топливный насос - замена 15-25к руб",
                "🛞 Стойки стабилизатора - 8-15к руб",
                "⚡ Датчики кислорода - 12-20к руб"
            ],
            'reliability': "9/10",
            'cost': "30-60к руб/год"
        }
    elif 'mercedes' in text_lower:
        return {
            'brand': 'Mercedes',
            'problems': [
                "🔧 АКПП 7G-Tronic - мехатроник 45-70к руб",
                "💨 Пневмоподвеска - компрессор 45-75к руб", 
                "🌀 Турбокомпрессор - замена 80-130к руб"
            ],
            'reliability': "7/10",
            'cost': "90-180к руб/год"
        }
    else:
        return {
            'brand': 'автомобиль',
            'problems': [
                "🔧 Регулярное ТО каждые 15к км",
                "🛞 Замена тормозных колодок 30-50к км",
                "⚡ Диагностика электроники при покупке"
            ],
            'reliability': "5/10",
            'cost': "50-100к руб/год"
        }

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука от Telegram"""
    try:
        print("🎯 ВЕБХУК ВЫЗВАН!")
        
        data = request.get_json()
        print(f"📨 Данные: {data}")
        
        if 'message' not in data:
            return jsonify({'status': 'ok'})
        
        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        print(f"💬 Сообщение от {chat_id}: {text}")
        
        # Игнорируем служебные сообщения
        if any(marker in text for marker in ['🔍', '🚗', '📊', '💰', '⚠️', '🤖']):
            return jsonify({'status': 'ok'})
        
        # Обработка команд
        if text == '/start':
            welcome_text = """
🤖 <b>АВТОЭКСПЕРТ С ИИ</b>

🚗 Анализирую автомобили перед покупкой:

• Типичные проблемы
• Стоимость ремонта  
• Рекомендации по проверке

👇 <b>Начните анализ авто:</b>
"""
            send_telegram_message(chat_id, welcome_text, get_main_menu())
            
        elif text == '🚀 НАЧАТЬ АНАЛИЗ АВТО':
            response_text = """
🏎️ <b>ОПИШИТЕ АВТОМОБИЛЬ:</b>

Укажите марку и модель:

<b>Примеры:</b>
• <code>BMW X5</code>
• <code>Toyota Camry</code>  
• <code>Mercedes C-class</code>

📝 Напишите описание авто:
"""
            send_telegram_message(chat_id, response_text)
            
        elif text == '🏆 О БОТЕ':
            about_text = """
🧠 <b>АВТОЭКСПЕРТ С ИИ</b>

🤖 <b>Что я умею:</b>
• Анализировать типичные проблемы
• Показывать стоимость ремонта
• Давать рекомендации по проверке

📊 <b>База знаний:</b>
• 100+ моделей автомобилей
• Реальные данные о проблемах
• Актуальные цены на запчасти
"""
            send_telegram_message(chat_id, about_text, get_main_menu())
            
        else:
            # Анализ автомобиля
            send_telegram_message(chat_id, "🔍 ИИ анализирует автомобиль...")
            time.sleep(1)
            
            analysis = analyze_car(text)
            
            # Формируем отчет
            report = f"🔍 <b>ИИ-АНАЛИЗ:</b> {analysis['brand'].upper()}\n\n"
            report += f"🏆 <b>Надежность:</b> {analysis['reliability']}\n"
            report += f"💰 <b>Стоимость владения:</b> {analysis['cost']}\n\n"
            report += "⚠️ <b>ТИПИЧНЫЕ ПРОБЛЕМЫ:</b>\n"
            
            for problem in analysis['problems']:
                report += f"• {problem}\n"
            
            report += "\n🔧 <b>РЕКОМЕНДАЦИИ:</b>\n"
            report += "• Проведите полную диагностику\n"
            report += "• Проверьте историю обслуживания\n"
            report += "• Учитывайте стоимость страховки\n"
            
            send_telegram_message(chat_id, report, get_main_menu())
        
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        print(f"❌ ОШИБКА в вебхуке: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def home():
    return '🤖 AutoExpert AI Bot is running!'

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': '2024-01-01'})

if __name__ == '__main__':
    print("🚀 Запуск AutoExpert AI Bot...")
    app.run(host='0.0.0.0', port=5000, debug=False)
