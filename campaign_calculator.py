import logging
logger = logging.getLogger(__name__)

# Цены / 3. Охват Mediascope 2024-2025.
STATION_DATA = {
    "ЕВРОПА ПЛЮС": {"reach": 81.7, "price": 33.00, "aqh": 6.1, "target": "Активные профи 25-45 лет"},
    "ДОРОЖНОЕ РАДИО": {"reach": 59.1, "price": 18.67, "aqh": 4.5, "target": "Семья и водители 30-55 лет"},
    "РЕТРО FM": {"reach": 44.5, "price": 17.00, "aqh": 3.8, "target": "Ценители хитов 35-60 лет"},
    "КРАСНАЯ АРМИЯ": {"reach": 30.3, "price": 16.67, "aqh": 2.2, "target": "Молодёжь и креатив 18-35 лет"},
    "НОВОЕ РАДИО": {"reach": 14.5, "price": 17.67, "aqh": 1.4, "target": "Драйвовая аудитория 20-40 лет"}
}

PRICE_TIERS = {1: 1.0, 2: 0.95, 3: 0.90, 4: 0.85, 5: 0.80}

TIME_SLOTS_DATA = [
    {"time": "06:00-07:00", "label": "Подъем, сборы", "weight": 0.06},
    {"time": "07:00-08:00", "label": "Утренние поездки", "weight": 0.10},
    {"time": "08:00-09:00", "label": "Пик трафика", "weight": 0.12},
    {"time": "09:00-10:00", "label": "Начало работы", "weight": 0.08},
    {"time": "10:00-11:00", "label": "Рабочий процесс", "weight": 0.07},
    {"time": "11:00-12:00", "label": "Предобеденное время", "weight": 0.06},
    {"time": "12:00-13:00", "label": "Обеденный перерыв", "weight": 0.05},
    {"time": "13:00-14:00", "label": "После обеда", "weight": 0.05},
    {"time": "14:00-15:00", "label": "Вторая половина дня", "weight": 0.05},
    {"time": "15:00-16:00", "label": "Рабочий финиш", "weight": 0.06},
    {"time": "16:00-17:00", "label": "Конец рабочего дня", "weight": 0.07},
    {"time": "17:00-18:00", "label": "Вечерние поездки", "weight": 0.10},
    {"time": "18:00-19:00", "label": "Пик трафика", "weight": 0.08},
    {"time": "19:00-20:00", "label": "Домашний вечер", "weight": 0.04},
    {"time": "20:00-21:00", "label": "Вечерний отдых", "weight": 0.04}
]

def calculate_campaign_price_and_reach(data):
    try:
        radios = data.get("selected_radios", [])
        slots = data.get("selected_time_slots", [])
        days = int(data.get("campaign_days", 1))
        duration = int(data.get("duration", 20))
        prod_option = data.get("production_option", "none")
        
        if not radios or not slots: return 0, 0, 7000, 0, 0, 0, 0, 0

        # 1. Бюджет
        base_sec = sum(STATION_DATA[r]["price"] for r in radios)
        air_cost = base_sec * duration * len(slots) * days * PRICE_TIERS.get(len(radios), 0.8)
        
        applied_discount = 0
        if len(slots) == 15:
            air_cost *= 0.95
            applied_discount = 5

        p_costs = {"standard": 5000, "vocal": 12500, "none": 0}
        total_price = max(int(air_cost) + p_costs.get(prod_option, 0), 7000)

        # 2. Охват
        st_reach_sum = sum(STATION_DATA[r]["reach"] * 1000 for r in radios)
        slot_weight_sum = sum(TIME_SLOTS_DATA[i]["weight"] for i in slots)
        daily_unique = int(st_reach_sum * slot_weight_sum * 0.7)
        total_reach = int(daily_unique * (1 + (days * 0.035)))

        # 3. OTS
        avg_aqh = sum(STATION_DATA[r]["aqh"] * 1000 for r in radios)
        total_ots = int(avg_aqh * len(slots) * days)

        return int(air_cost), applied_discount, total_price, total_reach, daily_unique, len(radios)*len(slots), total_ots, 0
    except:
        return 0, 0, 7000, 0, 0, 0, 0, 0
