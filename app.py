from flask import Flask, jsonify
import requests
import base64

app = Flask(__name__)

# Ваш основной код бота здесь...

# Тестовый маршрут для проверки GigaChat API
@app.route('/test-gigachat')
def test_gigachat():
    client_id = "019ac4e1-9416-7c5b-8722-fd5b09d85848"
    client_secret = "d4fa8a83-8b34-42cb-b16b-1ec8bafc6a88"
    
    credentials = f"{client_id}:{client_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {'scope': 'GIGACHAT_API_PERS'}
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=10)
        
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
            
    except Exception as e:
        return jsonify({
            "status": "exception",
            "error": str(e),
            "message": "❌ Ошибка подключения к GigaChat API"
        })

if __name__ == '__main__':
    app.run(debug=True)
