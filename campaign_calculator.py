import logging
logger = logging.getLogger(__name__)

# Цены делены на 3. Данные Mediascope 2024-2025 (Тюмень).
STATION_DATA = {
    "ЕВРОПА ПЛЮС": {"reach": 81.7, "price": 33.00, "aqh": 6.1, "desc": "Абсолютный лидер Тюмени с огромным отрывом. Радио №1 для активной аудитории."},
    "ДОРОЖНОЕ РАДИО": {"reach": 59.1, "price": 18.67, "aqh": 4.5, "desc": "Крупнейшая сеть вещания. 12 городов Тюменской области, ХМАО и ЯНАО в одном эфире."},
    "РЕТРО FM": {"reach": 44.5, "price": 17.00, "aqh": 3.8, "desc": "Золотой фонд мировой музыки. Невероятно лояльная аудитория со стабильным слушанием весь день."},
    "КРАСНАЯ АРМИЯ": {"reach": 30.3, "price": 16.67, "aqh": 2.2, "desc": "«Первое городское». Креативный и дерзкий голос Тюмени с уникальным локальным контентом."},
    "НОВОЕ РАДИО": {"reach": 14.5, "price": 17.67, "aqh": 1.4, "desc": "Территория суперхитов. Самые свежие новинки для молодой и драйвовой аудитории."}
}

PRICE_TIERS = {1: 1.0, 2: 0.95, 3: 0.90, 4: 0.85, 5: 0.80}

# Веса слотов (Сумма = 1.0)
TIME_SLOTS_DATA = [
    {"time": "06:00–07:00", "label": "Подъем", "weight": 0.04, "premium": False},
    {"time": "07:00–08:00", "label": "Утренний трафик", "weight": 0.12, "premium": True},
    {"time": "08:00–09:00", "label": "Пик трафика", "weight": 0.15, "premium": True},
    {"time": "09:00–10:00", "label": "Начало работы", "weight": 0.10, "premium": True},
    {"time": "10:00–11:00", "label": "Рабочий процесс", "weight": 0.07, "premium": False},
    {"time": "11:00–12:00", "label": "Офисное время", "weight": 0.06, "premium": False},
    {"time": "12:00–13:00", "label": "Обед / Пик трафика", "weight": 0.08, "premium": True},
    {"time": "13:00–14:00", "label": "Обед / Пик трафика", "weight": 0.07, "premium": True},
    {"time": "14:00–15:00", "label": "Вторая половина дня", "weight": 0.05, "premium": False},
    {"time": "15:00–16:00", "label": "Рабочий финиш", "weight": 0.06, "premium": False},
    {"time": "16:00–17:00", "label": "Конец дня", "weight": 0.07, "premium": False},
    {"time": "17:00–18:00", "label": "Вечерний трафик", "weight": 0.10, "premium": True},
    {"time": "18:00–19:00", "label": "Вечерний пик", "weight": 0.08, "premium": True},
    {"time": "19:00–20:00", "label": "Домашний вечер", "weight": 0.03, "premium": False},
    {"time": "20:00–21:00", "label": "Отдых", "weight": 0.02, "premium": False}
]

def calculate_campaign_price_and_reach(data):
    try:
        radios = data.get("selected_radios", [])
        slots = data.get("selected_time_slots", [])
        days = int(data.get("campaign_days", 1))
        duration = int(data.get("duration", 20))
        prod_option = data.get("production_option", "none")
        
        if not radios or not slots: return 0, 0, 7000, 0, 0, 0, 0, 0

        # 1. СТОИМОСТЬ ЭФИРА
        base_sec_sum = sum(STATION_DATA[r]["price"] for r in radios)
        # Скидка за количество станций
        vol_discount = PRICE_TIERS.get(len(radios), 0.8)
        
        air_cost = base_sec_sum * duration * len(slots) * days * vol_discount
        
        # Спецпредложение за 15 слотов: еще -5%
        if len(slots) == 15:
            air_cost *= 0.95

        # 2. ПРОИЗВОДСТВО
        prod_costs = {"standard": 5000, "premium": 12500, "none": 0}
        total_price = max(int(air_cost) + prod_costs.get(prod_option, 0), 7000)

        # 3. ОХВАТ (Коэффициент уникальности 0.7)
        total_st_reach = sum(STATION_DATA[r]["reach"] * 1000 for r in radios)
        slots_weight_sum = sum(TIME_SLOTS_DATA[i]["weight"] for i in slots)
        
        daily_unique = int(total_st_reach * slots_weight_sum * 0.7)
        campaign_reach = int(daily_unique * (1 + (days * 0.035)))

        # 4. КОНТАКТЫ (OTS)
        avg_aqh = sum(STATION_DATA[r]["aqh"] * 1000 for r in radios)
        total_ots = int(avg_aqh * len(slots) * days)
        
        cost_per_contact = round(total_price / total_ots, 2) if total_ots > 0 else 0

        return int(air_cost), 0, total_price, campaign_reach, daily_unique, len(radios)*len(slots), total_ots, cost_per_contact
    except Exception as e:
        logger.error(f"Calc error: {e}")
        return 0, 0, 7000, 0, 0, 0, 0, 0
