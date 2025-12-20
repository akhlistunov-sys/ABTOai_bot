import logging

logger = logging.getLogger(__name__)

# АКТУАЛЬНЫЕ ДАННЫЕ MEDIASCOPE (Тюмень, Июль 2024 - Июнь 2025)
STATION_DATA = {
    "КРАСНАЯ АРМИЯ": {"reach": 30.3, "price": 50, "share": 4.3},
    "ЕВРОПА ПЛЮС": {"reach": 81.7, "price": 99, "share": 11.5},
    "ДОРОЖНОЕ РАДИО": {"reach": 59.1, "price": 56, "share": 8.4},
    "РЕТРО FM": {"reach": 44.5, "price": 51, "share": 6.3},
    "НОВОЕ РАДИО": {"reach": 14.5, "price": 53, "share": 2.0}
}

# Коэффициенты скидок за количество станций
PRICE_TIERS = {1: 1.0, 2: 0.95, 3: 0.90, 4: 0.85, 5: 0.80}

# Временные слоты с весами охвата (согласно суточной динамике)
TIME_SLOTS_DATA = [
    {"time": "06:00-07:00", "label": "Подъем", "weight": 0.06},
    {"time": "07:00-08:00", "label": "Утренний пик", "weight": 0.12},
    {"time": "08:00-09:00", "label": "Максимум трафика", "weight": 0.15},
    {"time": "09:00-10:00", "label": "Начало дня", "weight": 0.09},
    {"time": "10:00-11:00", "label": "Работа", "weight": 0.07},
    {"time": "11:00-12:00", "label": "Работа", "weight": 0.06},
    {"time": "12:00-13:00", "label": "Обед", "weight": 0.05},
    {"time": "13:00-14:00", "label": "Обед", "weight": 0.05},
    {"time": "14:00-15:00", "label": "День", "weight": 0.05},
    {"time": "15:00-16:00", "label": "День", "weight": 0.06},
    {"time": "16:00-17:00", "label": "Завершение дня", "weight": 0.08},
    {"time": "17:00-18:00", "label": "Вечерний пик", "weight": 0.12},
    {"time": "18:00-19:00", "label": "Вечерний пик", "weight": 0.10},
    {"time": "19:00-20:00", "label": "Вечер", "weight": 0.04},
    {"time": "20:00-21:00", "label": "Отдых", "weight": 0.04}
]

PRODUCTION_OPTIONS = {
    "standard": {"price": 2000, "name": "СТАНДАРТНЫЙ РОЛИК"},
    "premium": {"price": 5000, "name": "ПРЕМИУМ РОЛИК"}
}

def format_number(num):
    return f"{num:,.0f}".replace(",", " ")

def calculate_campaign_price_and_reach(user_data):
    try:
        duration = int(user_data.get("duration", 20))
        days = int(user_data.get("campaign_days", 30))
        selected_radios = user_data.get("selected_radios", [])
        selected_slots = user_data.get("selected_time_slots", [])
        
        if not selected_radios or not selected_slots:
            return 0, 0, 7000, 0, 0, 0, 0, 0

        # 1. Расчет стоимости
        total_air_cost = 0
        num_stations = len(selected_radios)
        station_discount = PRICE_TIERS.get(num_stations, 0.8)

        for radio in selected_radios:
            station_price_sec = STATION_DATA.get(radio, {"price": 50})["price"]
            # Исправленная формула (была опечатка в переменной)
            cost_per_spot = duration * station_price_sec
            total_air_cost += cost_per_spot * len(selected_slots) * days

        total_air_cost = int(total_air_cost * station_discount)
        
        if len(selected_slots) == 15:
            total_air_cost = int(total_air_cost * 0.95) # Доп скидка за полный пакет слотов

        prod_key = user_data.get("production_option")
        prod_cost = PRODUCTION_OPTIONS.get(prod_key, {"price": 0})["price"]
        final_price = max(total_air_cost + prod_cost, 7000)

        # 2. Честный расчет охвата (Коэффициент 0.7)
        total_reach_daily_gross = 0
        for radio in selected_radios:
            base_reach = STATION_DATA.get(radio, {"reach": 0})["reach"] * 1000
            for slot_idx in selected_slots:
                if 0 <= slot_idx < len(TIME_SLOTS_DATA):
                    weight = TIME_SLOTS_DATA[slot_idx]["weight"]
                    total_reach_daily_gross += (base_reach * weight)

        # Уникальный охват (очистка от пересечений)
        unique_daily_reach = int(total_reach_daily_gross * 0.7)
        # Прогрессивный охват за период
        total_reach_period = int(unique_daily_reach * (1 + (days * 0.04))) 

        return total_air_cost + prod_cost, 0, final_price, total_reach_period, unique_daily_reach, len(selected_slots) * num_stations, 0, 0
    except Exception as e:
        logger.error(f"Calculation Error: {e}")
        return 0, 0, 7000, 0, 0, 0, 0, 0
