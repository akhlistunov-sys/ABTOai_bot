from flask import Flask, jsonify, request
import os
import requests
import base64
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Функция для работы с GigaChat API
def get_gigachat_token():
    try:
        client_id = os.getenv('GIGACHAT_CLIENT_ID')
        client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        
        print(f"🔑 Client ID: {client_id}")
        print(f"🔑 Client Secret: {client_secret}")
        
        # Кодируем credentials
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        print(f"🔐 Encoded credentials: {encoded_credentials}")
        
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        payload = 'scope=GIGACHAT_API_PERS'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {encoded_credentials}',
            'RqUID': '6f0b1291-c7f3-4c4a-9d6a-2d47b5d91e13'  # Добавляем RqUID
        }
        
        print("🔄 Sending request to GigaChat...")
        response = requests.post(
            url, 
            headers=headers, 
            data=payload, 
            verify=False, 
            timeout=30
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        print(f"📡 Response text: {response.text}")
        
        return response
        
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return {"error": str(e)}

# Маршруты Flask
@app.route('/')
def home():
    return "🚗 ABTOai_bot работает! Используйте /test-gigachat для проверки API"

@app.route('/test-gigachat')
def test_gigachat():
    print("🚀 Starting GigaChat test...")
    response = get_gigachat_token()
    
    # Логируем в консоль Render
    print(f"🎯 Final response type: {type(response)}")
    
    if hasattr(response, 'status_code'):
        print(f"📊 Status code: {response.status_code}")
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

# 🔥 ВАЖНО: Исправленная строка для Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
