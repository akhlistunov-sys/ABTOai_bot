from typing import Dict, Optional
from .text_processor import TextProcessor

class CarIdentifier:
    def __init__(self):
        self.text_processor = TextProcessor()
        self.car_database = self._init_car_database()
    
    def _init_car_database(self) -> Dict:
        """Инициализация базы данных авто"""
        return {
            'bmw': {
                'x5': {'generations': ['E53', 'E70', 'F15', 'G05'], 'years': [2000, 2006, 2013, 2018]},
                'x3': {'generations': ['E83', 'F25', 'G01'], 'years': [2003, 2010, 2017]},
                '3 series': {'generations': ['E46', 'E90', 'F30', 'G20'], 'years': [1998, 2005, 2011, 2019]}
            },
            'mercedes': {
                'c-class': {'generations': ['W203', 'W204', 'W205'], 'years': [2000, 2007, 2014]},
                'e-class': {'generations': ['W211', 'W212', 'W213'], 'years': [2002, 2009, 2016]},
                'gle': {'generations': ['W166', 'V167'], 'years': [2011, 2018]}
            },
            'toyota': {
                'camry': {'generations': ['XV30', 'XV40', 'XV50', 'XV70'], 'years': [2001, 2006, 2011, 2017]},
                'rav4': {'generations': ['XA30', 'XA40', 'XA50'], 'years': [2005, 2012, 2018]}
            }
        }
    
    def identify_car(self, text: str) -> Dict:
        """Идентификация автомобиля по тексту"""
        car_info = self.text_processor.extract_car_info(text)
        
        if car_info['brand'] and car_info['model']:
            generation = self._find_generation(car_info)
            car_info['generation'] = generation
        
        return car_info
    
    def _find_generation(self, car_info: Dict) -> Optional[str]:
        """Определение поколения авто"""
        brand = car_info['brand']
        model = car_info['model']
        year = car_info['year']
        
        if brand in self.car_database and model in self.car_database[brand]:
            generations = self.car_database[brand][model]
            
            if year:
                for i, gen_year in enumerate(generations['years']):
                    if year >= gen_year:
                        if i + 1 < len(generations['years']) and year < generations['years'][i + 1]:
                            return generations['generations'][i]
                        elif i == len(generations['years']) - 1:
                            return generations['generations'][i]
            
            # Если год не указан, возвращаем последнее поколение
            return generations['generations'][-1]
        
        return None
    
    def validate_car_info(self, car_info: Dict) -> bool:
        """Проверка корректности информации об авто"""
        if not car_info['brand']:
            return False
        
        # Проверка существования модели в базе
        if car_info['brand'] in self.car_database:
            if car_info['model']:
                return car_info['model'] in self.car_database[car_info['brand']]
            return True  # Марка есть, модели может не быть в базе
        
        return True  # Разрешаем любые марки
