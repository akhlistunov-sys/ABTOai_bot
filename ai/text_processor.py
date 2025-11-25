import re
from typing import Dict, List, Optional

class TextProcessor:
    def __init__(self):
        self.brands = self._load_brands()
        self.models_pattern = self._load_models_pattern()
    
    def _load_brands(self) -> List[str]:
        """Загрузка списка марок авто"""
        return [
            'audi', 'bmw', 'mercedes', 'volkswagen', 'toyota',
            'honda', 'nissan', 'hyundai', 'kia', 'lexus',
            'mazda', 'mitsubishi', 'subaru', 'ford', 'chevrolet',
            'renault', 'peugeot', 'skoda', 'volvo', 'land rover',
            'range rover', 'porsche', 'volvo', 'jeep'
        ]
    
    def _load_models_pattern(self) -> Dict[str, List[str]]:
        """Паттерны для моделей"""
        return {
            'bmw': ['x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7', 'series', 'm3', 'm5'],
            'mercedes': ['a-class', 'c-class', 'e-class', 's-class', 'glc', 'gle', 'gls'],
            'toyota': ['camry', 'corolla', 'rav4', 'land cruiser', 'prado', 'prius'],
            'audi': ['a3', 'a4', 'a5', 'a6', 'a8', 'q3', 'q5', 'q7', 'q8']
        }
    
    def extract_car_info(self, text: str) -> Dict[str, Optional[str]]:
        """Извлечение информации об авто из текста"""
        text_lower = text.lower()
        
        result = {
            'brand': None,
            'model': None,
            'year': None,
            'engine': None,
            'mileage': None,
            'original_text': text
        }
        
        # Поиск марки
        result['brand'] = self._extract_brand(text_lower)
        
        # Поиск модели
        if result['brand']:
            result['model'] = self._extract_model(text_lower, result['brand'])
        
        # Поиск года (4 цифры между 1990-2024)
        result['year'] = self._extract_year(text_lower)
        
        # Поиск двигателя
        result['engine'] = self._extract_engine(text_lower)
        
        # Поиск пробега
        result['mileage'] = self._extract_mileage(text_lower)
        
        return result
    
    def _extract_brand(self, text: str) -> Optional[str]:
        """Извлечение марки авто"""
        for brand in self.brands:
            if brand in text:
                return brand
        return None
    
    def _extract_model(self, text: str, brand: str) -> Optional[str]:
        """Извлечение модели авто"""
        if brand in self.models_pattern:
            for model in self.models_pattern[brand]:
                if model in text:
                    return model
        
        # Поиск по паттерну "марка модель"
        pattern = rf'{brand}\s+(\w+)'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Извлечение года выпуска"""
        year_pattern = r'(19[9][0-9]|20[0-2][0-4])'
        matches = re.findall(year_pattern, text)
        if matches:
            return int(matches[0])
        return None
    
    def _extract_engine(self, text: str) -> Optional[str]:
        """Извлечение информации о двигателе"""
        # Паттерны для двигателей
        engine_patterns = [
            r'(\d+\.\d+)',  # 2.0, 3.0 и т.д.
            r'(\d+)l',      # 2l, 3l
            r'(\d+)\s*л',   # 2 л, 3 л
            r'v\d',         # v6, v8
        ]
        
        for pattern in engine_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        # Проверка типа топлива
        if 'дизель' in text or 'diesel' in text or 'диз' in text:
            return 'дизель'
        elif 'бензин' in text or 'petrol' in text:
            return 'бензин'
        elif 'гибрид' in text or 'hybrid' in text:
            return 'гибрид'
        
        return None
    
    def _extract_mileage(self, text: str) -> Optional[str]:
        """Извлечение пробега"""
        mileage_patterns = [
            r'(\d+)\s*к\s*км',      # 100к км
            r'(\d+)\s*тыс',         # 100 тыс
            r'(\d+)\s*km',          # 100000 km
        ]
        
        for pattern in mileage_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        
        return None
