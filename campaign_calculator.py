import logging
logger = logging.getLogger(__name__)

# АКТУАЛЬНЫЕ ДАННЫЕ MEDIASCOPE (Тюмень 2024-2025)
# Цены делены на 3 от исходных
STATION_DATA = {
    "КРАСНАЯ АРМИЯ": {"reach": 30.3, "price": 16.67, "aqh": 2.1},
    "ЕВРОПА ПЛЮС": {"reach": 81.7, "price": 33.00, "aqh": 5.8},
    "ДОРОЖНОЕ РАДИО": {"reach": 59.1, "price": 18.67, "aqh": 4.2},
    "РЕТРО FM": {"reach": 44.5, "price": 17.00, "aqh": 3.5},
    "НОВОЕ РАДИО": {"reach": 14.5, "price": 17.67, "aqh": 1.2}
}

PRICE_TIERS = {1: 1.0, 2: 0.95, 3: 0.90, 4: 0.85, 5: 0.80}

TIME_SLOTS_DATA = [
    {"time": "06:00-07:00", "weight": 0.06}, {"time": "07:00-08:00", "weight": 0.12},
    {"time": "08:00-09:00", "weight": 0.15}, {"time": "09:00-10:00", "weight": 0.09},
    {"time": "10:00-11:00", "weight": 0.07}, {"time": "11:00-12:00", "weight": 0.06},
    {"time": "12:00-13:00", "weight": 0.05}, {"time": "13:00-14:00", "weight": 0.05},
    {"time": "14:00-15:00", "weight": 0.05}, {"time": "15:00-16:00", "weight": 0.06},
    {"time": "16:00-17:00", "weight": 0.08}, {"time": "17:00-18:00", "weight": 0.12},
    {"time": "18:00-19:00", "weight": 0.10}, {"time": "19:00-20:00", "weight": 0.04},
    {"time": "20:00-21:00", "weight": 0.04}
]

def calculate_campaign_price_and_reach(data):
    try:
        radios = data.get("selected_radios", [])
        slots = data.get("selected_time_slots", [])
        days = int(data.get("campaign_days", 1))
        duration = int(data.get("duration", 20))
        
        if not radios or not slots: return 0, 0, 7000, 0, 0, 0, 0, 0

        # Расчет бюджета
        base_sec_total = sum(STATION_DATA[r]["price"] for r in radios)
        air_cost = int(base_sec_total * duration * len(slots) * days * PRICE_TIERS.get(len(radios), 0.8))
        
        # Скидка 5% при выборе всех 15 слотов
        if len(slots) == 15: air_cost = int(air_cost * 0.95)

        prod_costs = {"standard": 2000, "premium": 5000, "none": 0}
        total_price = max(air_cost + prod_costs.get(data.get("production_option", "none"), 0), 7000)

        # Честный охват 0.7 (Уникальные слушатели)
        daily_gross = sum(STATION_DATA[r]["reach"] * 1000 for r in radios) * sum(TIME_SLOTS_DATA[i]["weight"] for i in slots)
        unique_daily = int(daily_gross * 0.7)
        total_reach = int(unique_daily * (1 + (days * 0.035))) # Накопительный охват за период

        # Контакты (OTS)
        avg_aqh = sum(STATION_DATA[r]["aqh"] * 1000 for r in radios) / len(radios)
        total_ots = int(avg_aqh * len(radios) * len(slots) * days)

        return air_cost, 0, total_price, total_reach, unique_daily, len(radios)*len(slots), total_ots, 0
    except Exception as e:
        logger.error(f"Calc error: {e}")
        return 0, 0, 7000, 0, 0, 0, 0, 0
