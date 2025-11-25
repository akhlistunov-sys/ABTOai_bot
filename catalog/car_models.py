# 📁 catalog/car_models.py
def get_car_brands():
    return [
        'Audi', 'BMW', 'Mercedes', 'Volkswagen', 'Toyota',
        'Honda', 'Nissan', 'Hyundai', 'Kia', 'Lexus',
        'Mazda', 'Mitsubishi', 'Subaru', 'Ford', 'Chevrolet',
        'Renault', 'Peugeot', 'Skoda', 'Volvo', 'Land Rover'
    ]

def get_models_by_brand(brand):
    models = {
        'Audi': ['A4', 'A6', 'Q5', 'Q7', 'A3', 'Q3'],
        'BMW': ['3 series', '5 series', 'X5', 'X3', '7 series'],
        'Mercedes': ['C-class', 'E-class', 'S-class', 'GLC', 'GLE'],
        'Toyota': ['Camry', 'Corolla', 'RAV4', 'Land Cruiser', 'Prius'],
        'Land Rover': ['Range Rover', 'Range Rover Sport', 'Discovery', 'Evoque']
    }
    return models.get(brand, ['Модель не найдена'])

def get_generations_by_model(brand, model):
    # Заглушка - в реальности полная база поколений
    return [f"{model} 2015-2018", f"{model} 2018-2021", f"{model} 2021-н.в."]
