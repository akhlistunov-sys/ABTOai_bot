import os
import requests
import base64
import json
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class GigaChatAPI:
    def __init__(self):
        self.client_id = os.getenv('GIGACHAT_CLIENT_ID')
        self.client_secret = os.getenv('GIGACHAT_CLIENT_SECRET')
        self.cache_file = 'data/car_cache.json'
        self.cache_days = int(os.getenv('CACHE_DAYS', 7))
        self.timeout = int(os.getenv('REQUEST_TIMEOUT', 30))
        
        # Создаем директории если нет
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)
        
        # Загружаем кэш
        self.cache = self.load_cache()
    
    def load_cache(self):
        """Загружаем кэш из файла"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log_error(f"Cache load error: {str(e)}")
        return {}
    
    def save_cache(self):
        """Сохраняем кэш в файл"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log_error(f"Cache save error: {str(e)}")
    
    def log_error(self, message):
        """Логирование ошибок"""
        try:
            with open('logs/app.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] {message}\n")
        except:
            pass
    
    def get_access_token(self):
        """Получаем access token для GigaChat"""
        try:
            credentials = f"{self.client_id}:{self.client_secret}"
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
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                self.log_error(f"Token error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.log_error(f"Token exception: {str(e)}")
            return None
    
    def ask_gigachat(self, prompt):
        """Отправляем запрос к GigaChat"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return {"error": "Ошибка аутентификации GigaChat"}
            
            url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            data = {
                "model": "GigaChat",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                url, 
                headers=headers, 
                json=data, 
                verify=False, 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                self.log_error(f"GigaChat API error: {response.status_code} - {response.text}")
                return {"error": f"Ошибка GigaChat: {response.status_code}"}
                
        except Exception as e:
            self.log_error(f"GigaChat exception: {str(e)}")
            return {"error": str(e)}
    
    def get_car_variants(self, brand, model):
        """Получаем варианты поколений, двигателей, КПП для авто"""
        cache_key = f"{brand}_{model}".lower().replace(" ", "_")
        
        # Проверяем кэш
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            
            # Если кэш свежий (меньше cache_days дней)
            if datetime.now() - cache_time < timedelta(days=self.cache_days):
                return cached_data['data']
        
        # Запрашиваем у GigaChat
        prompt = f"""
        Какие поколения, двигатели и коробки передач были у {brand} {model}?
        
        Ответь в формате JSON:
        {{
            "generations": [
                {{"name": "F15", "years": "2013-2018"}},
                {{"name": "G05", "years": "2018-2023"}}
            ],
            "engines": [
                {{"name": "2.0d", "power": "190 л.с."}},
                {{"name": "3.0d", "power": "249 л.с."}}
            ],
            "transmissions": [
                {{"name": "Автомат 8-ступ", "type": "автомат"}},
                {{"name": "Автомат xDrive", "type": "автомат"}}
            ]
        }}
        
        Только факты, без пояснений.
        """
        
        result = self.ask_gigachat(prompt)
        
        if "error" in result:
            return result
        
        # Пытаемся распарсить JSON ответ
        try:
            # Ищем JSON в ответе
            import re
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                # Если не JSON, возвращаем как есть
                data = {"raw_response": result}
            
            # Сохраняем в кэш
            self.cache[cache_key] = {
                "timestamp": datetime.now().isoformat(),
                "data": data
            }
            self.save_cache()
            
            return data
            
        except Exception as e:
            self.log_error(f"JSON parse error: {str(e)}")
            return {"raw_response": result}
    
    def analyze_car(self, car_data):
        """Анализ автомобиля - основной запрос"""
        prompt = f"""
        Ты — автоэксперт с 15-летним опытом. Проанализируй автомобиль и составь сбалансированный отчет.

        МОДЕЛЬ: {car_data.get('brand')} {car_data.get('model')} {car_data.get('year')}
        ДВИГАТЕЛЬ: {car_data.get('engine')} 
        КОРОБКА: {car_data.get('transmission')}
        ПРОБЕГ: {car_data.get('mileage')} км

        Используй данные с Drive2.ru, Drom.ru, otoba.ru, отзывы реальных владельцев.

        СТРУКТУРА ОТЧЕТА (ОБЯЗАТЕЛЬНО):

        🚗 ОБЩАЯ ОЦЕНКА
        [Краткая характеристика автомобиля]
        [Общий вердикт для данного пробега]

        🔧 ДВИГАТЕЛЬ {car_data.get('engine')}
        ✅ Надежность: [Оценка]
        📝 Описание: [Характеристика мотора]
        ⚠️ Основные нюансы:
        • [Конкретные особенности, пробеги ремонта, цены]
        • [Типичные поломки для этого двигателя]
        • [Ресурс и рекомендации по обслуживанию]

        ⚙️ КОРОБКА {car_data.get('transmission')}  
        ✅ Надежность: [Оценка]
        📝 Описание: [Характеристика КПП]
        ⚠️ Основные нюансы:
        • [Особенности типа КПП (вариатор/робот/автомат)]
        • [Пробеги обслуживания и ремонта]
        • [Слабые места и стоимость восстановления]

        🛞 ПОДВЕСКА
        ✅ Надежность: [Оценка]
        📝 Описание: [Тип подвески и поведение]
        ⚠️ Основные нюансы:
        • [Ресурс элементов, пробеги замены]
        • [Влияние российских дорог]
        • [Стоимость обслуживания]

        ⚡ ЭЛЕКТРИКА
        ✅ Надежность: [Оценка]  
        📝 Описание: [Общая оценка электроники]
        ⚠️ Основные нюансы:
        • [Частые сбои и проблемы]
        • [Блоки управления, датчики]
        • [Стоимость диагностики и ремонта]

        📋 ДЛЯ ПРОБЕГА {car_data.get('mileage')} км
        [Конкретные рекомендации по осмотру]
        [Что должно быть уже заменено]
        [Что ожидать в ближайшем будущем]

        ТРЕБОВАНИЯ:
        - Будь объективен: указывай и плюсы и минусы
        - Только конкретные цифры: пробеги, цены в рублях
        - Акцент на ОСНОВНЫЕ НЮАНСЫ каждого узла
        - Данные с российских форумов и отзывов
        """
        
        return self.ask_gigachat(prompt)
