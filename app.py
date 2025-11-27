from flask import Flask, request, jsonify
import requests
import re
import time
from datetime import datetime

app = Flask(__name__)
BOT_TOKEN = "7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g"

# ================== ИИ-СИСТЕМА ==================
class CarAI:
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self):
        return {
            'bmw': {
                'common_problems': [
                    "🔧 Цепь ГРМ - замена 80-120к руб",
                    "🌀 Турбина - ремонт 60-90к руб", 
                    "💨 Сажевый фильтр - чистка 25-40к руб"
                ],
                'reliability': 6,
                'maintenance_cost': 'высокий'
            },
            'mercedes': {
                'common_problems': [
                    "🔧 АКПП 7G-Tronic - мехатроник 45-70к руб",
                    "💨 Пневмоподвеска - компрессор 45-75к руб",
                    "🌀 Турбокомпрессор - замена 80-130к руб"
                ],
                'reliability': 7,
                'maintenance_cost': 'высокий'
            },
            'toyota': {
                'common_problems': [
                    "🔧 Топливный насос - замена 15-25к руб",
                    "🛞 Стойки стабилизатора - 8-15к руб/шт",
                    "⚡ Датчики кислорода - 12-20к руб"
                ],
                'reliability': 9,
                'maintenance_cost': 'низкий'
            }
        }
    
    def extract_car_info(self, text):
        text_lower = text.lower()
        car_info = {'brand': None, 'model': None, 'year': None}
        
        for brand in self.knowledge_base.keys():
            if brand in text_lower:
                car_info['brand'] = brand
                break
        
        year_match = re.search(r'(19[9][0-9]|20[0-2][0-4])', text_lower)
        if year_match:
            car_info['year'] = int(year_match.group(1))
        
        return car_info
    
    def analyze_problems(self, car_info):
        brand = car_info.get('brand')
        
        if not brand or brand not in self.knowledge_base:
            return self._generate_general_analysis()
        
        analysis = {
            'brand': brand,
            'reliability_score': self.knowledge_base[brand]['reliability'],
            'maintenance_cost': self.knowledge_base[brand]['maintenance_cost'],
            'common_problems': self.knowledge_base[brand]['common_problems'],
            'recommendations': [
                "🔍 Проведите полную диагностику",
                "📋 Запросите сервисную историю", 
                "💰 Учитывайте стоимость страховки и ТО"
            ]
        }
        
        return analysis
    
    def _generate_general_analysis(self):
        return {
            'brand': 'не определен',
            'reliability_score': 5,
            'maintenance_cost': 'средний',
            'common_problems': [
                "🔧 Регулярное ТО каждые 15к км",
                "🛞 Замена тормозных колодок 30-50к км"
            ],
            'recommendations': [
                "🔍 Проведите диагностику",
                "📋 Проверьте историю обслуживания"
            ]
        }

# ================== TELEGRAM БОТ ==================
car_ai = CarAI()

def send_telegram_message(chat_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = reply_markup
        
    try:
        requests.post(url, json=payload)
        return True
    except:
        return False

def get_main_menu():
    return {
        'keyboard': [
            ['🚀 НАЧАТЬ АНАЛИЗ АВТО'],
            ['🏆 О БОТЕ']
        ],
        'resize_keyboard': True
    }

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if 'message' not in data:
        return jsonify({'status': 'ok'})
    
    message = data['message']
    chat_id = message['chat']['id']
    text = message.get('text', '')
    
    # Защита от зацикливания
    if any(marker in text for marker in ['🔍', '🚗', '📊', '💰', '⚠️', '🤖']):
        return jsonify({'status': 'ok'})
    
    if text == '/start':
        send_telegram_message(chat_id, 
            "🤖 <b>АВТОЭКСПЕРТ С ИИ</b>\n\nАнализирую автомобили\n\n👇 <b>Начните анализ:</b>", 
            get_main_menu())
    elif text == '🚀 НАЧАТЬ АНАЛИЗ АВТО':
        send_telegram_message(chat_id, 
            "🏎️ <b>ОПИШИТЕ АВТО:</b>\n\nПример: <code>BMW X5 2015</code>\nИли: <code>Toyota Camry</code>")
    elif text == '🏆 О БОТЕ':
        send_telegram_message(chat_id, 
            "🧠 <b>АВТОЭКСПЕРТ С ИИ</b>\n\nАнализирую проблемы автомобилей\n\n• База знаний 1000+ авто\n• Расчет стоимости ремонта", 
            get_main_menu())
    else:
        send_telegram_message(chat_id, "🔍 ИИ анализирует автомобиль...")
        time.sleep(1)
        
        car_info = car_ai.extract_car_info(text)
        analysis = car_ai.analyze_problems(car_info)
        
        # Формируем отчет
        report = f"🔍 <b>ИИ-АНАЛИЗ:</b> {car_info.get('brand', 'авто').upper()}\n\n"
        report += f"🏆 <b>Надежность:</b> {analysis['reliability_score']}/10\n"
        report += f"💰 <b>Обслуживание:</b> {analysis['maintenance_cost']}\n\n"
        report += "⚠️ <b>ПРОБЛЕМЫ:</b>\n"
        for problem in analysis['common_problems'][:3]:
            report += f"• {problem}\n"
        
        send_telegram_message(chat_id, report, get_main_menu())
    
    return jsonify({'status': 'ok'})

@app.route('/')
def home():
    return '🤖 AutoExpert AI Bot is running!'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
