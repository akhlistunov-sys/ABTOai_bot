from typing import Dict, List, Optional

class CarDatabase:
    def __init__(self):
        self.database = self._initialize_database()
    
    def _initialize_database(self) -> Dict:
        """Инициализация базы данных автомобилей"""
        return {
            'audi': {
                'models': ['a3', 'a4', 'a5', 'a6', 'a8', 'q3', 'q5', 'q7', 'q8'],
                'common_engines': ['1.4', '1.8', '2.0', '3.0', '4.2'],
                'problematic': ['a4 b8 2008-2011 - проблемы с цепью ГРМ']
            },
            'bmw': {
                'models': ['1 series', '2 series', '3 series', '4 series', '5 series', 
                          '6 series', '7 series', 'x1', 'x2', 'x3', 'x4', 'x5', 'x6', 'x7'],
                'common_engines': ['2.0', '3.0', '4.4', '6.0'],
                'problematic': ['n47 двигатель - цепь ГРМ', 'n63 двигатель - перегрев']
            },
            'mercedes': {
                'models': ['a-class', 'b-class', 'c-class', 'e-class', 's-class',
                          'glc', 'gle', 'gls', 'gla', 'glb'],
                'common_engines': ['1.6', '2.0', '3.0', '4.0', '5.5', '6.0'],
                'problematic': ['om651 двигатель - проблемы с турбиной']
            },
            'toyota': {
                'models': ['camry', 'corolla', 'rav4', 'land cruiser', 'prado', 
                          'highlander', 'avensis', 'auris', 'prius'],
                'common_engines': ['1.6', '1.8', '2.0', '2.5', '3.5', '4.0'],
                'problematic': ['1zz-fe - расход масла']
            },
            'volkswagen': {
                'models': ['golf', 'passat', 'polo', 'tiguan', 'touareg', 'jetta'],
                'common_engines': ['1.4', '1.6', '2.0', '3.0', '3.6'],
                'problematic': ['dsg7 - проблемы с мехатроником']
            }
        }
    
    def get_brand_info(self, brand: str) -> Optional[Dict]:
        """Получение информации о марке"""
        return self.database.get(brand.lower())
    
    def validate_model(self, brand: str, model: str) -> bool:
        """Проверка существования модели у марки"""
        brand_info = self.get_brand_info(brand)
        if not brand_info:
            return False
        return model.lower() in brand_info['models']
    
    def get_common_problems(self, brand: str, model: str = None) -> List[str]:
        """Получение типичных проблем для марки/модели"""
        brand_info = self.get_brand_info(brand)
        if not brand_info:
            return []
        
        problems = brand_info.get('problematic', [])
        
        if model:
            # Фильтруем проблемы по модели
            model_problems = [p for p in problems if model.lower() in p.lower()]
            return model_problems
        
        return problems
    
    def get_common_engines(self, brand: str) -> List[str]:
        """Получение типичных двигателей для марки"""
        brand_info = self.get_brand_info(brand)
        if not brand_info:
            return []
        return brand_info.get('common_engines', [])
    
    def search_brand(self, query: str) -> List[str]:
        """Поиск марки по запросу"""
        query = query.lower()
        matches = []
        
        for brand in self.database.keys():
            if query in brand:
                matches.append(brand)
        
        return matches
    
    def get_all_brands(self) -> List[str]:
        """Получение всех марок"""
        return list(self.database.keys())
