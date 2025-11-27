import requests
import base64

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

response = requests.post(url, headers=headers, data=payload, verify=False)

print("Status:", response.status_code)
if response.status_code == 200:
    token = response.json().get("access_token")
    print("✅ УСПЕХ! Token:", token[:50] + "...")
else:
    print("❌ Ошибка:", response.text)
