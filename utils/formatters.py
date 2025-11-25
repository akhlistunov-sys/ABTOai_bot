from typing import Dict

class ReportFormatter:
    @staticmethod
    def format_analysis_report(car_info: Dict, analysis: Dict) -> str:
        """Форматирование отчета анализа"""
        report = []
        
        # Заголовок
        car_desc = ReportFormatter._format_car_description(car_info)
        report.append(f"🔍 <b>АНАЛИЗ АВТОМОБИЛЯ:</b> {car_desc}")
        report.append("")
        
        # Сводка
        report.append(f"📊 <b>СВОДКА:</b> {analysis['summary']}")
        report.append("")
        
        # Проблемы по категориям
        report.append("⚠️ <b>ПРОБЛЕМЫ ПО КАТЕГОРИЯМ:</b>")
        for category, category_data in analysis['by_category'].items():
            if category_data['count'] > 0:
                category_name = ReportFormatter._get_category_name(category)
                report.append(f"• <b>{category_name}:</b> {category_data['count']} случаев")
                
                if category_data['common_issues']:
                    issues = ", ".join(category_data['common_issues'])
                    report.append(f"  🎯 Частые проблемы: {issues}")
                
                if category_data['typical_mileage'] != "не указан":
                    report.append(f"  🛣️ Типичный пробег: {category_data['typical_mileage']}")
        
        report.append("")
        
        # Стоимость ремонта
        costs = analysis['cost_estimation']
        report.append("💰 <b>ОРИЕНТИРОВОЧНАЯ СТОИМОСТЬ РЕМОНТА:</b>")
        report.append(f"• Типичная: {ReportFormatter._format_price(costs['typical'])} руб")
        report.append(f"• Диапазон: {ReportFormatter._format_price(costs['min'])} - {ReportFormatter._format_price(costs['max'])} руб")
        
        report.append("")
        
        # Критические проблемы
        if analysis['critical_issues']:
            report.append("🚨 <b>КРИТИЧЕСКИЕ ПРОБЛЕМЫ:</b>")
            for issue in analysis['critical_issues']:
                report.append(f"• {issue}")
            report.append("")
        
        # Советы по обслуживанию
        report.append("🔧 <b>РЕКОМЕНДАЦИИ:</b>")
        for advice in analysis['maintenance_advice']:
            report.append(f"• {advice}")
        
        report.append("")
        report.append("📈 <i>На основе анализа данных с автофорумов</i>")
        
        return "\n".join(report)
    
    @staticmethod
    def _format_car_description(car_info: Dict) -> str:
        """Форматирование описания автомобиля"""
        parts = []
        
        if car_info.get('brand'):
            parts.append(car_info['brand'].upper())
        
        if car_info.get('model'):
            parts.append(car_info['model'].upper())
        
        if car_info.get('year'):
            parts.append(str(car_info['year']))
        
        if car_info.get('engine'):
            parts.append(f"({car_info['engine']})")
        
        return " ".join(parts)
    
    @staticmethod
    def _get_category_name(category: str) -> str:
        """Получение читаемого названия категории"""
        names = {
            'engine': 'Двигатель',
            'transmission': 'Коробка передач',
            'suspension': 'Подвеска',
            'electronics': 'Электроника',
            'other': 'Другие системы'
        }
        return names.get(category, category)
    
    @staticmethod
    def _format_price(price: int) -> str:
        """Форматирование цены"""
        if price >= 100000:
            return f"{price // 1000}к"
        elif price >= 1000:
            return f"{price}"
        else:
            return str(price)
    
    @staticmethod
    def format_search_progress(car_info: Dict, current: int, total: int) -> str:
        """Форматирование прогресса поиска"""
        car_desc = ReportFormatter._format_car_description(car_info)
        return f"🔍 Ищу информацию по {car_desc}... ({current}/{total})"
    
    @staticmethod
    def format_error_message(error: str) -> str:
        """Форматирование сообщения об ошибке"""
        return f"❌ <b>Ошибка:</b> {error}\n\nПопробуйте другой запрос или обратитесь в поддержку."
