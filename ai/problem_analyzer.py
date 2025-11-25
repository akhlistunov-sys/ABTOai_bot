from typing import Dict, List
import re

class ProblemAnalyzer:
    def __init__(self):
        self.cost_patterns = {
            'руб': r'(\d+[\s\d]*)\s*руб',
            'тыс': r'(\d+)\s*тыс',
            '₽': r'(\d+[\s\d]*)\s*₽'
        }
        
        self.mileage_patterns = {
            'к_км': r'(\d+)\s*к\s*км',
            'тыс_км': r'(\d+)\s*тыс',
            'km': r'(\d+)\s*km'
        }
    
    def analyze_problems(self, search_results: Dict) -> Dict:
        """Анализ и структурирование проблем"""
        categorized = search_results['categorized_problems']
        
        analysis = {
            'summary': self._generate_summary(categorized),
            'by_category': {},
            'cost_estimation': self._estimate_costs(categorized),
            'critical_issues': self._find_critical_issues(categorized),
            'maintenance_advice': self._generate_maintenance_advice(categorized)
        }
        
        for category, problems in categorized.items():
            if problems:
                analysis['by_category'][category] = {
                    'count': len(problems),
                    'common_issues': self._extract_common_issues(problems, category),
                    'frequency': self._calculate_frequency(problems, len(problems)),
                    'typical_mileage': self._extract_typical_mileage(problems)
                }
        
        return analysis
    
    def _generate_summary(self, categorized: Dict) -> str:
        """Генерация сводки по проблемам"""
        total_problems = sum(len(problems) for problems in categorized.values())
        
        if total_problems == 0:
            return "Информация по проблемам не найдена"
        
        # Находим самую частую категорию
        main_category = max(categorized.items(), key=lambda x: len(x[1]))[0]
        main_count = len(categorized[main_category])
        
        category_names = {
            'engine': 'двигатель',
            'transmission': 'коробка передач',
            'suspension': 'подвеска',
            'electronics': 'электроника',
            'other': 'другие системы'
        }
        
        return (f"Найдено {total_problems} упоминаний проблем. "
                f"Основные проблемы связаны с {category_names.get(main_category, main_category)} "
                f"({main_count} случаев).")
    
    def _extract_common_issues(self, problems: List[Dict], category: str) -> List[str]:
        """Извлечение наиболее частых проблем в категории"""
        issue_keywords = self._get_category_keywords(category)
        issue_counts = {}
        
        for problem in problems:
            content = f"{problem['title']} {problem['content']}".lower()
            
            for keyword in issue_keywords:
                if keyword in content:
                    issue_counts[keyword] = issue_counts.get(keyword, 0) + 1
        
        # Сортируем по частоте и возвращаем топ-3
        common_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [issue[0] for issue in common_issues]
    
    def _get_category_keywords(self, category: str) -> List[str]:
        """Ключевые слова для каждой категории"""
        keywords = {
            'engine': ['цепь грм', 'турбина', 'сальник', 'клапан', 'форсунка', 'тнвд', 'egr'],
            'transmission': ['мехатроник', 'сцепление', 'соленоид', 'фрикцион', 'переключение'],
            'suspension': ['стойка', 'амортизатор', 'шаровой', 'сайлентблок', 'пружина', 'стабилизатор'],
            'electronics': ['датчик', 'блок управления', 'проводка', 'дисплей', 'камера', 'радар'],
            'other': ['тормоз', 'рулевой', 'кондиционер', 'печка', 'сиденье']
        }
        return keywords.get(category, [])
    
    def _calculate_frequency(self, problems: List[Dict], total_count: int) -> str:
        """Расчет частоты проблем"""
        if total_count == 0:
            return "редко"
        
        problem_count = len(problems)
        ratio = problem_count / total_count if total_count > 0 else 0
        
        if ratio > 0.7:
            return "очень часто"
        elif ratio > 0.5:
            return "часто"
        elif ratio > 0.3:
            return "периодически"
        else:
            return "редко"
    
    def _extract_typical_mileage(self, problems: List[Dict]) -> str:
        """Извлечение типичного пробега для проблем"""
        mileages = []
        
        for problem in problems:
            content = f"{problem['title']} {problem['content']}"
            mileage = self._extract_mileage_from_text(content)
            if mileage:
                mileages.append(mileage)
        
        if not mileages:
            return "не указан"
        
        # Возвращаем наиболее частый пробег
        typical = max(set(mileages), key=mileages.count)
        return typical
    
    def _extract_mileage_from_text(self, text: str) -> str:
        """Извлечение пробега из текста"""
        for pattern_name, pattern in self.mileage_patterns.items():
            match = re.search(pattern, text.lower())
            if match:
                mileage = match.group(1)
                if pattern_name == 'тыс_км':
                    return f"{mileage} тыс км"
                elif pattern_name == 'к_км':
                    return f"{mileage}к км"
                else:
                    return f"{mileage} km"
        return ""
    
    def _estimate_costs(self, categorized: Dict) -> Dict:
        """Оценка стоимости ремонта"""
        cost_ranges = {
            'engine': {'min': 30000, 'max': 150000, 'typical': 80000},
            'transmission': {'min': 20000, 'max': 120000, 'typical': 60000},
            'suspension': {'min': 10000, 'max': 60000, 'typical': 30000},
            'electronics': {'min': 5000, 'max': 80000, 'typical': 25000},
            'other': {'min': 5000, 'max': 50000, 'typical': 15000}
        }
        
        total_min = 0
        total_max = 0
        total_typical = 0
        
        for category, problems in categorized.items():
            if problems and category in cost_ranges:
                total_min += cost_ranges[category]['min']
                total_max += cost_ranges[category]['max']
                total_typical += cost_ranges[category]['typical']
        
        return {
            'min': total_min,
            'max': total_max,
            'typical': total_typical,
            'ranges': cost_ranges
        }
    
    def _find_critical_issues(self, categorized: Dict) -> List[str]:
        """Поиск критических проблем"""
        critical_keywords = [
            'аварийный', 'опасный', 'неуправляемый', 'пожар', 'взрыв',
            'отказ тормозов', 'отказ руля', 'заклинило'
        ]
        
        critical_issues = []
        
        for category, problems in categorized.items():
            for problem in problems:
                content = f"{problem['title']} {problem['content']}".lower()
                if any(keyword in content for keyword in critical_keywords):
                    critical_issues.append(problem['title'])
        
        return critical_issues[:3]  # Ограничиваем количество
    
    def _generate_maintenance_advice(self, categorized: Dict) -> List[str]:
        """Генерация советов по обслуживанию"""
        advice = []
        
        if categorized.get('engine'):
            advice.append("Регулярно меняйте масло и фильтры")
        
        if categorized.get('transmission'):
            advice.append("Своевременно обслуживайте коробку передач")
        
        if categorized.get('suspension'):
            advice.append("Проверяйте подвеску при появлении стуков")
        
        if categorized.get('electronics'):
            advice.append("Диагностируйте электронику при появлении ошибок")
        
        if not advice:
            advice.append("Следуйте регламенту технического обслуживания")
        
        return advice
