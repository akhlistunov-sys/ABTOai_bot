from flask import Flask, jsonify, request
import os
import requests
import base64
import urllib3
from dotenv import load_dotenv

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
        
        # Формируем промпт для анализа авто
        prompt = f"""
        Проанализируй автомобиль и составь отчет для покупателя:

        Марка: {car_data.get('brand', 'Не указана')}
        Модель: {car_data.get('model', 'Не указана')}
        Год: {car_data.get('year', 'Не указан')}
        Двигатель: {car_data.get('engine', 'Не указан')}
        КПП: {car_data.get('transmission', 'Не указана')}
        Пробег: {car_data.get('mileage', 'Не указан')} км

        Структура отчета:
        1. КРИТИЧЕСКИЕ РИСКИ - главные проблемы этой модели
        2. ДВИГАТЕЛЬ - типичные неисправности, ресурс
        3. КПП - надежность, проблемы
        4. ПОДВЕСКА - слабые места
        5. ЭЛЕКТРИКА - частые сбои
        6. РЕКОМЕНДАЦИИ - что проверять при осмотре

        Будь конкретен, укажи пробеги и стоимость ремонта.
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
            "temperature": 0.7
        }
        
        response = requests.post(url, headers=headers, json=data, verify=False, timeout=30)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return {"error": f"Ошибка GigaChat: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

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
