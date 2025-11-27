import requests
import base64
import os
from dotenv import load_dotenv

load_dotenv()

def get_gigachat_token():
    client_id = os.getenv('GIGACHAT_CLIENT_ID')
    client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
    
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
        return response
    except Exception as e:
        return {"error": str(e)}
