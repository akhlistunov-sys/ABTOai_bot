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
