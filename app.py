from flask import Flask, jsonify, request, session
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from services.gigachat_api import GigaChatAPI

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'abtoai-secret-key-2024')

# Инициализация GigaChat API
gigachat = GigaChatAPI()

# База данных пользовательских сессий
user_sessions = {}

def send_telegram_message(chat_id, text):
    """Отправка сообщения в Telegram"""
    try:
        bot_token = os.getenv('BOT_TOKEN')
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Telegram send error: {str(e)}")
        return {"error": str(e)}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработчик входящих сообщений от Telegram"""
    try:
        data = request.get_json()
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            
            # Инициализация сессии пользователя
            if chat_id not in user_sessions:
                user_sessions[chat_id] = {
                    'step': 'brand',
                    'car_data': {},
                    'created_at': datetime.now().isoformat()
                }
            
            session = user_sessions[chat_id]
            
            if text == '/start':
                send_telegram_message(chat_id, 
                    "🚗 Добро пожаловать в ABTOai_bot!\n\n"
                    "Я помогу проанализировать автомобиль перед покупкой.\n\n"
                    "Введите марку автомобиля:"
                )
                session['step'] = 'brand'
                session['car_data'] = {}
                
            elif text == '/reset':
                session['step'] = 'brand'
                session['car_data'] = {}
                send_telegram_message(chat_id, "🔄 Сессия сброшена. Введите марку автомобиля:")
                
            elif session['step'] == 'brand':
                session['car_data']['brand'] = text
                session['step'] = 'model'
                send_telegram_message(chat_id, 
                    f"✅ Марка: {text}\n\n"
                    f"Теперь введите модель автомобиля:"
                )
                
            elif session['step'] == 'model':
                session['car_data']['model'] = text
                brand = session['car_data']['brand']
                model = text
                
                # Получаем варианты от GigaChat
                send_telegram_message(chat_id, 
                    f"✅ {brand} {model}\n\n"
                    f"🔍 Ищу доступные варианты..."
                )
                
                variants = gigachat.get_car_variants(brand, model)
                
                if "error" in variants:
                    send_telegram_message(chat_id, 
                        f"❌ Не удалось получить данные.\n\n"
                        f"Введите поколение вручную (например: F15, G30):"
                    )
                    session['step'] = 'generation_manual'
                else:
                    # Формируем сообщение с вариантами
                    response_text = f"✅ Найдены варианты для {brand} {model}:\n\n"
                    
                    if 'generations' in variants:
                        response_text += "📅 ПОКОЛЕНИЯ:\n"
                        for gen in variants['generations'][:5]:  # Первые 5
                            response_text += f"• {gen.get('name', '')} ({gen.get('years', '')})\n"
                    
                    if 'engines' in variants:
                        response_text += "\n🔧 ДВИГАТЕЛИ:\n"
                        for engine in variants['engines'][:5]:
                            response_text += f"• {engine.get('name', '')} ({engine.get('power', '')})\n"
                    
                    response_text += "\nВведите поколение автомобиля:"
                    
                    send_telegram_message(chat_id, response_text)
                    session['step'] = 'generation'
                    session['variants'] = variants
                    
            elif session['step'] in ['generation', 'generation_manual']:
                session['car_data']['generation'] = text
                session['step'] = 'engine'
                
                # Получаем двигатели из вариантов или просим ввести
                if 'variants' in session and 'engines' in session['variants']:
                    engines_text = "Выберите двигатель:\n"
                    for engine in session['variants']['engines'][:8]:
                        engines_text += f"• {engine.get('name', '')}\n"
                    engines_text += "\nИли введите свой вариант:"
                else:
                    engines_text = "Введите двигатель (например: 2.0d, 3.0i):"
                
                send_telegram_message(chat_id, engines_text)
                
            elif session['step'] == 'engine':
                session['car_data']['engine'] = text
                session['step'] = 'transmission'
                
                # Получаем КПП из вариантов или просим ввести
                if 'variants' in session and 'transmissions' in session['variants']:
                    trans_text = "Выберите коробку передач:\n"
                    for trans in session['variants']['transmissions'][:5]:
                        trans_text += f"• {trans.get('name', '')}\n"
                    trans_text += "\nИли введите свою КПП:"
                else:
                    trans_text = "Введите коробку передач (например: Автомат, Механика):"
                
                send_telegram_message(chat_id, trans_text)
                
            elif session['step'] == 'transmission':
                session['car_data']['transmission'] = text
                session['step'] = 'mileage'
                send_telegram_message(chat_id, 
                    "Введите пробег автомобиля (в км):\n"
                    "Пример: 120000"
                )
                
            elif session['step'] == 'mileage':
                try:
                    mileage = int(text)
                    session['car_data']['mileage'] = mileage
                    session['step'] = 'analyzing'
                    
                    # Начинаем анализ
                    car_data = session['car_data']
                    send_telegram_message(chat_id, 
                        f"🔍 Анализирую автомобиль:\n"
                        f"• {car_data['brand']} {car_data['model']}\n"
                        f"• Поколение: {car_data.get('generation', 'не указано')}\n"
                        f"• Двигатель: {car_data['engine']}\n"
                        f"• КПП: {car_data['transmission']}\n"
                        f"• Пробег: {car_data['mileage']} км\n\n"
                        f"Подождите 15-20 секунд..."
                    )
                    
                    # Запрашиваем анализ у GigaChat
                    analysis_result = gigachat.analyze_car(car_data)
                    
                    if "error" in analysis_result:
                        send_telegram_message(chat_id, 
                            f"❌ Ошибка анализа: {analysis_result['error']}\n\n"
                            f"Попробуйте снова /start"
                        )
                    else:
                        # Разбиваем длинное сообщение на части
                        analysis_text = analysis_result
                        if len(analysis_text) > 4000:
                            parts = [analysis_text[i:i+4000] for i in range(0, len(analysis_text), 4000)]
                            for i, part in enumerate(parts):
                                send_telegram_message(chat_id, part)
                                if i < len(parts) - 1:
                                    time.sleep(1)  # Пауза между сообщениями
                        else:
                            send_telegram_message(chat_id, analysis_text)
                        
                        # Предлагаем новый анализ
                        send_telegram_message(chat_id,
                            "\n\n🔄 Хотите проанализировать другой автомобиль?\n"
                            "Используйте /start"
                        )
                    
                    # Очищаем сессию
                    del user_sessions[chat_id]
                    
                except ValueError:
                    send_telegram_message(chat_id, 
                        "❌ Пробег должен быть числом.\n"
                        "Введите пробег в км (например: 120000):"
                    )
        
        return jsonify({"status": "ok"})
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

@app.route('/set-webhook', methods=['GET'])
def set_webhook():
    """Установка webhook для Telegram"""
    try:
        bot_token = os.getenv('BOT_TOKEN')
        webhook_url = f"https://abtoai-bot.onrender.com/webhook"
        
        url = f"https://api.telegram.org/bot{bot_token}/setWebhook"
        payload = {
            'url': webhook_url
        }
        response = requests.post(url, json=payload)
        
        return jsonify({
            "status": "success", 
            "webhook_set": response.json()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Тестовые маршруты
@app.route('/')
def home():
    return "🚗 ABTOai_bot работает! Webhook: /set-webhook"

@app.route('/test-gigachat')
def test_gigachat():
    """Тест GigaChat API"""
    variants = gigachat.get_car_variants("BMW", "X5")
    return jsonify({
        "status": "success",
        "variants": variants
    })

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "service": "ABTOai_bot",
        "timestamp": datetime.now().isoformat()
    })

# Запуск для Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
