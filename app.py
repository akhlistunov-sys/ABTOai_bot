from flask import Flask, jsonify
from services.gigachat_api import get_gigachat_token
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "ABTOai_bot работает! 🚗"

@app.route('/test-gigachat')
def test_gigachat():
    response = get_gigachat_token()
    
    if hasattr(response, 'status_code'):
        if response.status_code == 200:
            token = response.json().get("access_token")
            return jsonify({
                "status": "success", 
                "status_code": response.status_code,
                "token_preview": token[:50] + "..." if token else "None",
                "message": "✅ GigaChat API работает!"
            })
        else:
            return jsonify({
                "status": "error",
                "status_code": response.status_code, 
                "response": response.text,
                "message": "❌ Ошибка аутентификации"
            })
    else:
        return jsonify({
            "status": "exception",
            "error": str(response),
            "message": "❌ Ошибка подключения к GigaChat API"
        })

# 🔥 ВАЖНО: Исправленная строка для Render
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
