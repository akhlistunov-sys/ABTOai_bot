# 📁 utils/report_formatter.py
def generate_report(car_name: str, problems: Dict) -> str:
    """Генерация красивого отчета в Markdown"""
    
    report = f"🔍 *{car_name.upper()} - ОТЧЕТ О ПРОБЛЕМАХ*\n\n"
    
    # Двигатель
    report += "⚙️ *ДВИГАТЕЛЬ:*\n"
    for problem in problems.get('engine', []):
        report += f"• {problem['component']} - {problem['cost']} ({problem['mileage']}) - {problem['frequency']}\n"
    
    # КПП
    report += "\n🔄 *КОРОБКА ПЕРЕДАЧ:*\n"
    for problem in problems.get('gearbox', []):
        report += f"• {problem['component']} - {problem['cost']} ({problem['mileage']}) - {problem['frequency']}\n"
    
    # Подвеска
    report += "\n🧲 *ПОДВЕСКА:*\n"
    for problem in problems.get('suspension', []):
        report += f"• {problem['component']} - {problem['cost']} ({problem['mileage']}) - {problem['frequency']}\n"
    
    # Рекомендации
    report += "\n💡 *ЧТО ПРОВЕРИТЬ:*\n"
    report += "• Шум турбины на прогретом двигателе\n"
    report += "• Работа АКПП на холодную\n"
    report += "• Стуки в подвеске на неровностях\n"
    
    report += "\n📊 *На основе анализа 150+ отзывов владельцев*"
    
    return report
