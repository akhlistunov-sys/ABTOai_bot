import os, sqlite3, io, textwrap, requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from campaign_calculator import calculate_campaign_price_and_reach

app = Flask(__name__)
CORS(app)

TELEGRAM_BOT_TOKEN = '7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g'
ADMIN_TELEGRAM_ID = 174046571
DB_PATH = "/tmp/campaigns.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, campaign_number TEXT,
        radio_stations TEXT, start_date TEXT, end_date TEXT, campaign_days INTEGER,
        time_slots TEXT, campaign_text TEXT, production_option TEXT,
        contact_name TEXT, company TEXT, phone TEXT,
        duration INTEGER, final_price INTEGER, actual_reach INTEGER, ots INTEGER,
        cost_per_contact REAL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

def create_excel(row):
    wb = Workbook(); ws = wb.active; ws.title = "Медиаплан РЗС"
    blue = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
    ws.merge_cells("A1:C1")
    ws["A1"] = f"МЕДИАПЛАН РЕКЛАМНОЙ КАМПАНИИ #{row['campaign_number']}"
    ws["A1"].fill = blue; ws["A1"].font = Font(color="FFFFFF", bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center")
    
    data = [
        ("Радиостанции", row['radio_stations']),
        ("Период размещения", f"{row['start_date']} - {row['end_date']} ({row['campaign_days']} дн.)"),
        ("Хронометраж", f"{row['duration']} сек."),
        ("Рекламные контакты (OTS)", f"{row.get('ots', 0):,}"),
        ("Общий охват (период)", f"{row['actual_reach']:,} чел."),
        ("Стоимость 1 контакта", f"{row.get('cost_per_contact', 0)} руб."),
        ("ИТОГО К ОПЛАТЕ", f"{row['final_price']:,} руб.")
    ]
    for r_idx, (k, v) in enumerate(data, 3):
        ws.cell(row=r_idx, column=1, value=k).font = Font(bold=True)
        ws.cell(row=r_idx, column=2, value=v)
    
    ws["A11"] = "ТЕКСТ / СЦЕНАРИЙ РОЛИКА:"; ws["A11"].font = Font(bold=True, color="1A237E")
    txt = row.get('campaign_text') or "Материал заказчика"
    for i, line in enumerate(textwrap.wrap(txt, 70), 12):
        ws.cell(row=i, column=1, value=line)

    ws["A20"] = "Ваш менеджер: Александра Васильева"; ws["A21"] = "Телефон: +7 (3452) 68-82-12"
    
    out = io.BytesIO(); wb.save(out); out.seek(0)
    return out

@app.route('/')
def index(): return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def static_files(path): return send_from_directory('frontend', path)

@app.route('/api/calculate', methods=['POST'])
def calc():
    res = calculate_campaign_price_and_reach(request.json)
    return jsonify({"success":True, "calculation": {
        "final_price": res[2], "total_reach": res[3], "daily_coverage": res[4], "spots": res[5], "ots": res[6], "cpc": res[7]
    }})

@app.route('/api/create-campaign', methods=['POST'])
def create():
    init_db(); d = request.json; c_num = f"R-{datetime.now().strftime('%H%M%S')}"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""INSERT INTO campaigns (user_id, campaign_number, radio_stations, start_date, end_date, 
        campaign_days, time_slots, campaign_text, production_option, contact_name, company, phone, 
        duration, final_price, actual_reach, ots, cost_per_contact) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d.get('user_id'), c_num, ",".join(d.get('selected_radios')), d.get('start_date'), d.get('end_date'), 
         d.get('campaign_days'), ",".join(map(str, d.get('selected_time_slots'))), d.get('campaign_text'), 
         d.get('production_option'), d.get('contact_name'), d.get('company'), d.get('phone'), 
         d.get('duration'), d.get('final_price'), d.get('total_reach'), d.get('ots'), d.get('cpc')))
    conn.commit(); conn.close()
    
    # Отправка Excel
    try:
        excel = create_excel(d); excel.name = f"Mediaplan_{c_num}.xlsx"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", 
            files={'document': (excel.name, excel)}, data={'chat_id': d.get('user_id'), 'caption': f'Ваш медиаплан {c_num} готов!'})
    except: pass
    
    return jsonify({"success":True, "campaign_number": c_num})

@app.route('/api/user-campaigns/<int:user_id>')
def history(user_id):
    init_db(); conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM campaigns WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    return jsonify({"success":True, "campaigns": [dict(r) for r in rows]})

@app.route('/api/send-excel/<num>', methods=['POST'])
def send_ex(num):
    uid = request.json.get('user_telegram_id')
    conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM campaigns WHERE campaign_number = ?", (num,)).fetchone()
    if row:
        excel = create_excel(dict(row)); excel.name = f"Mediaplan_{num}.xlsx"
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", 
            files={'document': (excel.name, excel)}, data={'chat_id': uid})
        return jsonify({"success":True})
    return jsonify({"success":False})

if __name__ == '__main__': init_db(); app.run(host='0.0.0.0', port=5000)
