from flask import Flask, request, jsonify
import requests
import os
import logging
import re
import time
from datetime import datetime

app = Flask(__name__)

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = "7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g"

class TextProcessor:
    def extract_car_info(self, text: str):
        """Извлечение информации об авто из текста"""
        text_lower = text.lower()
        
        result = {
            'brand': None,
            'model': None,
            'year': None,
            'engine': None,
            'mileage': None,
            'original_text': text
        }
        
        # Поиск марки
        brands = ['audi', 'bmw', 'mercedes', 'volkswagen', 'toyota', 'honda', 
                 'nissan', 'hyundai', 'kia', 'lexus', 'mazda', 'subaru', 'ford']
        
        for brand in brands:
            if brand in text_lower:
                result['brand'] = brand
                break
        
        # Поиск года (4 цифры между 1990-2024)
        year_pattern = r'(19[9][0-9]|20[0-2][0-4])'
        matches = re.findall(year_pattern, text_lower)
        if matches:
            result['year'] = int(matches[0])
        
        # Поиск двигателя
        engine_patterns = [r'(\d+\.\d+)', r'(\d+)l', r'v\d']
        for pattern in engine_patterns:
            match = re.search(pattern, text_lower)
            if match:
                result['engine'] = match.group(0)
                break
        
        if 'дизель' in text_lower or 'diesel' in text_lower:
            result['engine'] = 'дизель'
        elif 'бензин' in text_lower:
            result['engine'] = 'бензин'
        
        return result

class ProblemAnalyzer:
    def analyze_car_problems(self, car_info):
        """Анализ проблем автомобиля"""
        brand = car_info.get('brand', '')
        model = car_info.get('model', '')
        
        # База типичных проблем
        problems_db = {
            'bmw': {
                'common': ["Цепь ГРМ - замена 80-120к руб", "Турбина - ремонт 60-90к руб"],
                'x5': ["Пневмоподвеска - 40-70к руб", "Электроника iDrive - глюки"],
                'x3': ["Двигатель N47 - цепь ГРМ", "Топливная система"],
                '3 series': ["Свечи накала", "Тормозные диски"]
            },
            'mercedes': {
                'common': ["АКПП 7G-Tronic - мехатроник", "Пневмоподвеска Airmatic"],
                'c-class': ["Электроника COMAND", "Подушки двигателя"],
                'e-class': ["Турбокомпрессор", "Сажевый фильтр"]
            },
            'toyota': {
                'common': ["Надежная техника", "Низкая стоимость ТО"],
                'camry': ["Топливный насос", "Сцепление (механика)"],
                'rav4': ["Подвеска", "Кондиционер"]
            },
            'audi': {
                'common': ["Цепь ГРМ 2.0 TFSI", "Турбина", "Электроника MMI"],
                'a4': ["Топливный насос высокого давления"],
                'q5': ["АКПП S-tronic", "Полный привод"]
            }
        }
        
        problems = []
        
        if brand in problems_db:
            # Добавляем общие проблемы марки
            problems.extend(problems_db[brand]['common'])
            
            # Добавляем проблемы конкретной модели
            if model:
                for model_key, model_problems in problems_db[brand].items():
                    if model_key != 'common' and model in model_key:
                        problems.extend(model_problems)
        
        # Если проблем мало, добавляем общие
        if len(problems) < 3:
            problems.extend([
                "Двигатель - ТО каждые 15к км",
                "Тормоза - замена колодок 30-50к км", 
                "Подвеска - диагностика при стуках",
                "АКПП - замена масла 60к км"
            ])
        
        return {
            'car_info': car_info,
            'problems_found': len(problems),
            'problems': problems[:8],  # Ограничиваем количество
            'cost_estimation': self._estimate_costs(problems),
            'summary': f"Найдено {len(problems)} типичных проблем для {brand.upper()}"
        }
    
    def _estimate_costs(self, problems):
        """Оценка стоимости ремонта"""
        total_min = 0
        total_max = 0
        
        for problem in problems:
            if '80-120' in problem:
                total_min += 80000
                total_max += 120000
            elif '60-90' in problem:
                total_min += 60000
                total_max += 90000
            elif '40-70' in problem:
                total_min += 40000
                total_max += 70000
            else:
                total_min += 10000
                total_max += 30000
        
        return {
            'min': total_min,
            'max': total_max,
            'typical': (total_min + total_max) // 2
        }

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
        logger.info(f"Message sent to {chat_id}")
        return response.json()
    except Exception as e:
        logger.error(f"Send message error: {e}")
        return None

def get_main_menu():
    """Главное меню"""
    return {
        'keyboard': [
            ['🚀 НАЧАТЬ АНАЛИЗ АВТО'],
            ['📊 ДЕТАЛЬНЫЙ ОТЧЕТ'],
            ['🏆 О БОТЕ', '📋 ИСТОРИЯ']
        ],
        'resize_keyboard': True
    }

def format_report(car_info, analysis):
    """Форматирование отчета"""
    brand = car_info.get('brand', '').upper()
    model = car_info.get('model', '').upper()
    year = car_info.get('year', '')
    
    report = []
    report.append(f"🔍 <b>АНАЛИЗ АВТОМОБИЛЯ:</b> {brand} {model} {year}")
    report.append("")
    report.append(f"📊 <b>СВОДКА:</b> {analysis['summary']}")
    report.append("")
    
    report.append("⚠️ <b>ТИПИЧНЫЕ ПРОБЛЕМЫ:</b>")
    for i, problem in enumerate(analysis['problems'][:6], 1):
        report.append(f"{i}. {problem}")
    
    report.append("")
    report.append("💰 <b>ОРИЕНТИРОВОЧНАЯ СТОИМОСТЬ РЕМОНТА:</b>")
    costs = analysis['cost_estimation']
    report.append(f"• Типичная: {costs['typical']:,} руб".replace(',', ' '))
    report.append(f"• Диапазон: {costs['min']:,} - {costs['max']:,} руб".replace(',', ' '))
    
    report.append("")
    report.append("🔧 <b>РЕКОМЕНДАЦИИ:</b>")
    report.append("• Проведите полную диагностику перед покупкой")
    report.append("• Проверьте историю обслуживания")
    report.append("• Учитывайте стоимость страховки и ТО")
    
    report.append("")
    report.append("📈 <i>На основе анализа типичных проблем</i>")
    
    return "\n".join(report)

# Инициализация компонентов
text_processor = TextProcessor()
problem_analyzer = ProblemAnalyzer()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик вебхука от Telegram"""
    try:
        data = request.get_json()
        
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text == '/start':
                welcome = "🎯 <b>АВТОЭКСПЕРТ</b>\n\nАнализирую автомобили перед покупкой\n\n👇 <b>Выберите действие:</b>"
                send_telegram_message(chat_id, welcome, get_main_menu())
                
            elif text == '🚀 НАЧАТЬ АНАЛИЗ АВТО':
                response = "🏎️ <b>ОПИШИТЕ АВТОМОБИЛЬ:</b>\n\nПример: <code>BMW X5 2015 дизель</code>\nИли: <code>Toyota Camry 2018</code>"
                send_telegram_message(chat_id, response)
                
            elif text in ['📊 ДЕТАЛЬНЫЙ ОТЧЕТ', '🔍 РУЧНОЙ ВВОД']:
                response = "📝 <b>ВВЕДИТЕ ДАННЫЕ АВТО:</b>\n\nФормат: Марка Модель Год [Двигатель]\n\nПример: <code>BMW X5 2015 3.0d</code>"
                send_telegram_message(chat_id, response)
                
            elif text == '🏆 О БОТЕ':
                about = "🤖 <b>АВТОЭКСПЕРТ</b>\n\nАнализирую типичные проблемы автомобилей\n\n• Поиск общих неисправностей\n• Расчет стоимости ремонта\n• Рекомендации по проверке"
                send_telegram_message(chat_id, about, get_main_menu())
                
            elif text == '📋 ИСТОРИЯ':
                history = "📋 <b>ИСТОРИЯ ЗАПРОСОВ</b>\n\nФункция в разработке 🛠"
                send_telegram_message(chat_id, history, get_main_menu())
                
            else:
                # Анализ автомобиля
                send_telegram_message(chat_id, "🔍 Анализирую автомобиль...")
                time.sleep(1)
                
                car_info = text_processor.extract_car_info(text)
                analysis = problem_analyzer.analyze_car_problems(car_info)
                report = format_report(car_info, analysis)
                
                send_telegram_message(chat_id, report, get_main_menu())
            
        return jsonify({'status': 'ok'})
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'status': 'error'}), 500

@app.route('/')
def home():
    return '🚗 AutoExpert Bot is running!'

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    logger.info("🚀 Starting AutoExpert Bot...")
    app.run(host='0.0.0.0', port=5000, debug=False)
