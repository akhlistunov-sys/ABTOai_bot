from flask import Flask, jsonify, request
import os
import requests
import base64
import urllib3
from dotenv import load_dotenv
import json

# Отключаем SSL предупреждения
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Функция для работы с GigaChat API
def get_gigachat_token():
    try:
        client_id = os.getenv('GIGACHAT_CLIENT_ID')
        client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        
        # Кодируем credentials
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        payload = 'scope=GIGACHAT_API_PERS'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {encoded_credentials}',
            'RqUID': '6f0b1291-c7f3-4c4a-9d6a-2d47b5d91e13'
        }
        
        response = requests.post(
            url, 
            headers=headers, 
            data=payload, 
            verify=False, 
            timeout=30
        )
        
        return response
        
    except Exception as e:
        return {"error": str(e)}

# Функция для анализа автомобиля через GigaChat
def analyze_car(car_data):
    try:
        # Сначала получаем токен
        token_response = get_gigachat_token()
        if not hasattr(token_response, 'status_code') or token_response.status_code != 200:
            return {"error": "Ошибка аутентификации GigaChat"}
        
        access_token = token_response.json().get("access_token")
        
        # УЛУЧШЕННЫЙ ПРОМПТ - КОНКРЕТНЫЙ И С СТРУКТУРОЙ
        prompt = f"""
        Ты - автоэксперт СТО с 15-летним опытом. Дай КОНКРЕТНЫЙ анализ автомобиля.

        МОДЕЛЬ: {car_data.get('brand')} {car_data.get('model')}
        ДВИГАТЕЛЬ: {car_data.get('engine')} (главный фокус!)
        КПП: {car_data.get('transmission')}  
        ПРОБЕГ: {car_data.get('mileage')} км
        ГОД: {car_data.get('year')}

        Дай ОЧЕНЬ КОНКРЕТНЫЙ отчет по этой КОНКРЕТНОЙ комплектации.
        Используй данные с Drive2.ru, Drom.ru, отзывы реальных владельцев.

        СТРУКТУРА ОТЧЕТА (ОБЯЗАТЕЛЬНО):

        🔴 КРИТИЧЕСКИЕ РИСКИ ДЛЯ ДВИГАТЕЛЯ {car_data.get('engine')}
        - Самые дорогие поломки для этого мотора
        - Пробеги, когда проявляются (например: "цепь ГРМ - 150к км")
        - Точная стоимость ремонта в рублях

        🔧 ДВИГАТЕЛЬ {car_data.get('engine')} - ДЕТАЛЬНЫЙ АНАЛИЗ
        - Ресурс до капремонта
        - Конкретные проблемы (цепь/ремень ГРМ, турбина, форсунки)
        - Пробеги для замены ключевых компонентов
        - Стоимость ремонта каждого узла

        ⚙️ КОРОБКА {car_data.get('transmission')}
        - Надежность с этим двигателем
        - Пробеги обслуживания/ремонта
        - Стоимость ремонта КПП

        🛞 ПОДВЕСКА ДЛЯ {car_data.get('brand')} {car_data.get('model')}
        - Слабые элементы и их ресурс
        - Пробеги замены (амортизаторы, сайлентблоки, ШРУСы)
        - Стоимость элементов

        ⚡ ЭЛЕКТРИКА И ЭЛЕКТРОНИКА
        - Частые сбои для этой модели
        - Проблемы с блоками управления
        - Стоимость ремонта

        🇷🇺 РОССИЙСКАЯ ЭКСПЛУАТАЦИЯ
        - Влияние климата, дорог, топлива
        - Сезонные проблемы

        📋 ЧТО ПРОВЕРИТЬ НА {car_data.get('mileage')} км
        - Конкретный чек-лист для осмотра
        - Тест-драйв: на что обратить внимание

        ТРЕБОВАНИЯ:
        - ТОЛЬКО конкретные цифры (пробеги, цены)
        - ТОЛЬКО для этой комплектации
        - Цены в рублях на 2024 год
        - Данные с российских форумов
        - Если нет точных данных - пиши "требует диагностики"
        """

        # Отправляем запрос к GigaChat
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        data = {
            "model": "GigaChat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,  # Минимум "творчества"
            "max_tokens": 3000
        }
        
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return {"error": f"Ошибка GigaChat: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

# Простой Telegram webhook обработчик
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        
        if 'message' in data:
            chat_id = data['message']['chat']['id']
            text = data['message'].get('text', '')
            
            if text == '/start':
                send_telegram_message(
                    chat_id,
                    "🚗 Добро пожаловать в ABTOai_bot!\n\n"
                    "Проанализирую любой автомобиль перед покупкой.\n\n"
                    "Отправьте данные в формате:\n"
                    "• Марка Модель Год Двигатель КПП Пробег\n\n"
                    "Пример: BMW X5 2018 3.0d Автомат 120000"
                )
            
            elif text.startswith('/analyze'):
                send_telegram_message(
                    chat_id,
                    "📝 Введите данные автомобиля:\n\n"
                    "Формат: Марка Модель Год Двигатель КПП Пробег\n"
                    "Пример: Toyota Camry 2020 2.5L Автомат 80000"
                )
            
            else:
                # Пытаемся разобрать ввод пользователя
                parts = text.split()
                if len(parts) >= 6:
                    car_data = {
                        'brand': parts[0],
                        'model': parts[1],
                        'year': parts[2],
                        'engine': parts[3],
                        'transmission': parts[4],
                        'mileage': parts[5]
                    }
                    
                    send_telegram_message(chat_id, "🔍 Анализирую автомобиль...")
                    
                    result = analyze_car(car_data)
                    
                    if "error" in result:
                        send_telegram_message(chat_id, f"❌ Ошибка: {result['error']}")
                    else:
                        # Разбиваем длинное сообщение на части
                        analysis_text = result
                        if len(analysis_text) > 4000:
                            parts = [analysis_text[i:i+4000] for i in range(0, len(analysis_text), 4000)]
                            for part in parts:
                                send_telegram_message(chat_id, part)
                        else:
                            send_telegram_message(chat_id, analysis_text)
                
                else:
                    send_telegram_message(
                        chat_id,
                        "❌ Неправильный формат. Пример:\nBMW X5 2018 3.0d Автомат 120000"
                    )
        
        return jsonify({"status": "ok"})
    
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)})

# Функция для отправки сообщений в Telegram
def send_telegram_message(chat_id, text):
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

# Установка webhook для Telegram
@app.route('/set-webhook', methods=['GET'])
def set_webhook():
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

# Маршруты Flask
@app.route('/')
def home():
    return "🚗 ABTOai_bot работает! Используйте /test-gigachat для проверки API"

@app.route('/test-gigachat')
def test_gigachat():
    response = get_gigachat_token()
    
    if hasattr(response, 'status_code'):
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            return jsonify({
                "status": "success",
                "status_code": response.status_code,
                "token_preview": token[:50] + "..." if token else "None",
                "expires_in": token_data.get("expires_in"),
                "message": "✅ GigaChat API работает!"
            })
        else:
            return jsonify({
                "status": "error",
                "status_code": response.status_code,
                "response": response.text,
                "message": "❌ Ошибка аутентификации в GigaChat"
            })
    else:
        return jsonify({
            "status": "exception",
            "error": str(response),
            "message": "❌ Ошибка подключения к GigaChat API"
        })

@app.route('/analyze-car', methods=['POST'])
def analyze_car_route():
    try:
        car_data = request.json
        result = analyze_car(car_data)
        
        if "error" in result:
            return jsonify({"status": "error", "message": result["error"]})
        else:
            return jsonify({"status": "success", "analysis": result})
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/debug-env')
def debug_env():
    return jsonify({
        "client_id": os.getenv('GIGACHAT_CLIENT_ID', 'NOT_FOUND'),
        "client_secret": os.getenv('GIGACHAT_CLIENT_SECRET', 'NOT_FOUND'),
        "bot_token": os.getenv('BOT_TOKEN', 'NOT_FOUND')
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy", "service": "ABTOai_bot"})

# Запуск для Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
