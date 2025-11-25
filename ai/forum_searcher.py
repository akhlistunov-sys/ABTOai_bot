import requests
import time
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class ForumSearcher:
    def __init__(self):
        self.search_templates = {
            'drive2': 'https://www.drive2.ru/search/?text={query}',
            'drom': 'https://www.drom.ru/forum/search/?q={query}',
        }
    
    def search_car_problems(self, car_info: Dict) -> Dict:
        """Поиск проблем по автомобилю на форумах"""
        queries = self._generate_search_queries(car_info)
        results = {}
        
        for source, template in self.search_templates.items():
            try:
                source_results = self._search_source(queries, template, source)
                results[source] = source_results
                time.sleep(1)  # Задержка между запросами
            except Exception as e:
                logger.error(f"Ошибка поиска в {source}: {e}")
                results[source] = []
        
        return self._analyze_results(results, car_info)
    
    def _generate_search_queries(self, car_info: Dict) -> List[str]:
        """Генерация поисковых запросов"""
        brand = car_info.get('brand', '')
        model = car_info.get('model', '')
        year = car_info.get('year', '')
        engine = car_info.get('engine', '')
        
        queries = []
        
        # Основные запросы
        base_query = f"{brand} {model}"
        if year:
            base_query += f" {year}"
        if engine:
            base_query += f" {engine}"
        
        queries.extend([
            f"{base_query} проблемы",
            f"{base_query} неисправности",
            f"{base_query} отзывы",
            f"{base_query} что ломается",
            f"{base_query} ремонт",
        ])
        
        return queries
    
    def _search_source(self, queries: List[str], template: str, source: str) -> List[Dict]:
        """Поиск в конкретном источнике"""
        results = []
        
        for query in queries[:2]:  # Ограничиваем количество запросов
            try:
                # Имитация реального поиска
                simulated_data = self._simulate_forum_search(query, source)
                results.extend(simulated_data)
            except Exception as e:
                logger.error(f"Ошибка запроса {query} в {source}: {e}")
        
        return results
    
    def _simulate_forum_search(self, query: str, source: str) -> List[Dict]:
        """Имитация поиска на форумах (заглушка)"""
        # В реальности здесь будет парсинг форумов
        # Сейчас возвращаем тестовые данные
        
        time.sleep(0.5)  # Имитация задержки
        
        sample_problems = [
            {
                'title': f'Проблемы с двигателем {query}',
                'content': 'Часто ломается цепь ГРМ после 100к км',
                'source': source,
                'date': '2024-01-15',
                'relevance': 0.8
            },
            {
                'title': f'Неисправности коробки {query}',
                'content': 'Мехатроник выходит из строя на 150к км',
                'source': source,
                'date': '2024-01-10',
                'relevance': 0.7
            },
            {
                'title': f'Отзыв владельца {query}',
                'content': 'Подвеска стучит после 80к км, дорогой ремонт',
                'source': source,
                'date': '2024-01-05',
                'relevance': 0.6
            }
        ]
        
        return sample_problems
    
    def _analyze_results(self, results: Dict, car_info: Dict) -> Dict:
        """Анализ результатов поиска"""
        all_problems = []
        for source_problems in results.values():
            all_problems.extend(source_problems)
        
        # Группировка проблем по категориям
        categorized = self._categorize_problems(all_problems)
        
        return {
            'car_info': car_info,
            'problems_found': len(all_problems),
            'sources_searched': len(results),
            'categorized_problems': categorized,
            'raw_results': all_problems[:10]  # Ограничиваем вывод
        }
    
    def _categorize_problems(self, problems: List[Dict]) -> Dict:
        """Категоризация проблем"""
        categories = {
            'engine': [],
            'transmission': [],
            'suspension': [],
            'electronics': [],
            'other': []
        }
        
        keywords = {
            'engine': ['двигатель', 'мотор', 'турбина', 'грм', 'цепь', 'ремень'],
            'transmission': ['коробка', 'акпп', 'мкпп', 'мехатроник', 'сцепление'],
            'suspension': ['подвеска', 'амортизатор', 'стойка', 'пружина', 'шаровой'],
            'electronics': ['электроника', 'блок', 'датчик', 'проводка', 'мультимедиа']
        }
        
        for problem in problems:
            content = f"{problem['title']} {problem['content']}".lower()
            categorized = False
            
            for category, words in keywords.items():
                if any(word in content for word in words):
                    categories[category].append(problem)
                    categorized = True
                    break
            
            if not categorized:
                categories['other'].append(problem)
        
        return categories
