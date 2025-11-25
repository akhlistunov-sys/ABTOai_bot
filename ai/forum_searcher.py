import requests
import time
import random
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ForumSearcher:
    def __init__(self):
        self.sample_problems_db = self._init_sample_problems()
    
    def _init_sample_problems(self) -> Dict:
        """Инициализация базы примеров проблем"""
        return {
            'bmw': {
                'x5': [
                    "Цепь ГРМ - замена каждые 120-150к км (80-120к руб)",
                    "Турбина - проблемы после 150к км (60-90к руб)",
                    "Пневмоподвеска - ремонт от 40к руб",
                    "Электроника iDrive - глюки после 5 лет"
                ],
                '3 series': [
                    "Двигатель N47 - цепь ГРМ (70-100к руб)",
                    "Свечи накала - замена каждые 80к км",
                    "Топливный насос - 25-40к руб"
                ]
            },
            'mercedes': {
                'c-class': [
                    "АКПП 7G-Tronic - мехатроник (45-70к руб)",
                    "Подушка двигателя - замена на 100к км",
                    "Электроника COMAND - обновления"
                ],
                'e-class': [
                    "Пневмоподвеска Airmatic - 50-80к руб",
                    "Турбокомпрессор - 80-120к руб",
                    "Сажевый фильтр - чистка 15-25к руб"
                ]
            },
            'toyota': {
                'camry': [
                    "Топливный насос - 15-25к руб",
                    "Сцепление (если механика) - 30-50к руб",
                    "Тормозные колодки - быстрый износ"
                ],
                'rav4': [
                    "Подвеска - стойки 20-35к руб",
                    "Электронный блок - редко, но дорого",
                    "Кондиционер - обслуживание каждые 2 года"
                ]
            },
            'audi': {
                'a4': [
                    "Цепь ГРМ 2.0 TFSI - 60-90к руб",
                    "Турбина - 70-110к руб",
                    "Электроника MMI - перепрошивка"
                ],
                'q5': [
                    "Двигатель 2.0 TDI - сажевый фильтр",
                    "АКПП S-tronic - мехатроник 40-70к руб",
                    "Полный привод - обслуживание"
                ]
            }
        }
    
    def search_car_problems(self, car_info: Dict) -> Dict:
        """Поиск проблем по автомобилю (упрощенная версия)"""
        brand = car_info.get('brand', '').lower()
        model = car_info.get('model', '').lower()
        
        # Имитация поиска с задержкой
        time.sleep(2)
        
        # Поиск в базе примеров
        problems = self._find_problems_in_db(brand, model)
        
        # Если не нашли, генерируем общие проблемы
        if not problems:
            problems = self._generate_general_problems(brand, model)
        
        return {
            'car_info': car_info,
            'problems_found': len(problems),
            'sources_searched': 2,  # Имитация поиска в 2 источниках
            'categorized_problems': self._categorize_problems(problems),
            'search_success': True
        }
    
    def _find_problems_in_db(self, brand: str, model: str) -> List[str]:
        """Поиск проблем в базе примеров"""
        problems = []
        
        if brand in self.sample_problems_db:
            # Ищем по точному совпадению модели
            if model in self.sample_problems_db[brand]:
                problems.extend(self.sample_problems_db[brand][model])
            
            # Добавляем общие проблемы марки
            for model_name, model_problems in self.sample_problems_db[brand].items():
                if model in model_name or model_name in model:
                    problems.extend(model_problems)
        
        return list(set(problems))  # Убираем дубли
    
    def _generate_general_problems(self, brand: str, model: str) -> List[str]:
        """Генерация общих проблем для марки"""
        general_problems = [
            "Двигатель - регулярное ТО каждые 15к км",
            "Тормозная система - замена колодок каждые 30-50к км",
            "Подвеска - диагностика при появлении стуков",
            "АКПП - замена масла каждые 60к км",
            "Электроника - проверка при покупке"
        ]
        
        brand_specific = []
        
        if brand in ['bmw', 'mercedes', 'audi']:
            brand_specific.extend([
                "Турбокомпрессор - проверка на шумы",
                "Электронные системы - диагностика сканером",
                "Премиальные опции - дорогой ремонт"
            ])
        elif brand in ['toyota', 'honda', 'nissan']:
            brand_specific.extend([
                "Надежная техника - низкая стоимость ТО",
                "Доступность запчастей - быстрый ремонт",
                "Высокий ресурс двигателя и КПП"
            ])
        
        return general_problems + brand_specific
    
    def _categorize_problems(self, problems: List[str]) -> Dict:
        """Категоризация проблем"""
        categories = {
            'engine': [],
            'transmission': [],
            'suspension': [],
            'electronics': [],
            'other': []
        }
        
        keywords = {
            'engine': ['двигатель', 'турбина', 'грм', 'цепь', 'топливный', 'насос'],
            'transmission': ['акпп', 'кпп', 'сцепление', 'мехатроник', 'масло'],
            'suspension': ['подвеска', 'стойка', 'амортизатор', 'пневмо'],
            'electronics': ['электроника', 'блок', 'команд', 'mmi', 'idrive']
        }
        
        for problem in problems:
            problem_lower = problem.lower()
            categorized = False
            
            for category, words in keywords.items():
                if any(word in problem_lower for word in words):
                    categories[category].append(problem)
                    categorized = True
                    break
            
            if not categorized:
                categories['other'].append(problem)
        
        return categories
