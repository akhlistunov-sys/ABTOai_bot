import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def get_gigachat_token():
    try:
        client_id = os.getenv('GIGACHAT_CLIENT_ID')
        client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        
        print(f"Client ID: {client_id}")  # Для дебага
        print(f"Client Secret: {client_secret}")  # Для дебага
        
        if not client_id or not client_secret:
            return {"error": "Missing credentials"}
        
        credentials = f"{client_id}:{client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        payload = {'scope': 'GIGACHAT_API_PERS'}
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': f'Basic {encoded_credentials}'
        }
        
        response = requests.post(url, headers=headers, data=payload, verify=False, timeout=30)
        print(f"Response status: {response.status_code}")  # Для дебага
        print(f"Response text: {response.text}")  # Для дебага
        
        return response
        
    except Exception as e:
        print(f"Exception: {str(e)}")  # Для дебага
        return {"error": str(e)}
