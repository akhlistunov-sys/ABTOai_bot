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
        contact_name TEXT, company TEXT, phone TEXT, email TEXT,
        duration INTEGER, final_price INTEGER, actual_reach INTEGER, ots INTEGER)""")
    conn.close()

def create_pro_excel(row):
    wb = Workbook()
    ws = wb.active
    ws.title = "Медиаплан РЗС"
    blue = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
    ws.merge_cells("A1:C1")
    ws["A1"] = f"МЕДИАПЛАН РЗС ТЮМЕНЬ #{row['campaign_number']}"
    ws["A1"].fill = blue; ws["A1"].font = Font(color="FFFFFF", bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center")
    
    headers = [
        ("Радиостанции", row['radio_stations']),
        ("Период", f"{row['start_date']} - {row['end_date']} ({row['campaign_days']} дн.)"),
        ("Хронометраж", f"{row['duration']} сек."),
        ("Рекламных контактов", f"{row.get('ots', 0):,}"),
        ("ИТОГО К ОПЛАТЕ", f"{row['final_price']:,} руб.")
    ]
    for r_idx, (k, v) in enumerate(headers, 3):
        ws.cell(row=r_idx, column=1, value=k).font = Font(bold=True)
        ws.cell(row=r_idx, column=2, value=v)
    
    ws["A9"] = "ТЕКСТ / СЦЕНАРИЙ:"; ws["A9"].font = Font(bold=True)
    txt = row['campaign_text'] if row['campaign_text'] else "Предоставляется заказчиком"
    for i, line in enumerate(textwrap.wrap(txt, 70), 10): ws.cell(row=i, column=1, value=line)
    
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
        "final_price": res[2], "total_reach": res[3], "daily_coverage": res[4], "spots_per_day": res[5], "ots": res[6]
    }})

@app.route('/api/create-campaign', methods=['POST'])
def create():
    init_db(); d = request.json; c_num = f"R-{datetime.now().strftime('%H%M%S')}"
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""INSERT INTO campaigns (user_id, campaign_number, radio_stations, start_date, end_date, 
        campaign_days, time_slots, campaign_text, production_option, contact_name, company, phone, email, 
        duration, final_price, actual_reach, ots) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d.get('user_id'), c_num, ",".join(d.get('selected_radios')), d.get('start_date'), d.get('end_date'), 
         d.get('campaign_days'), ",".join(map(str, d.get('selected_time_slots'))), d.get('campaign_text'), 
         d.get('production_option'), d.get('contact_name'), d.get('company'), d.get('phone'), d.get('email'), 
         d.get('duration'), d.get('final_price'), d.get('total_reach'), d.get('ots')))
    conn.commit(); conn.close()
    
    # Авто-отправка Excel клиенту и админу
    row_dict = d.copy(); row_dict['campaign_number'] = c_num
    excel = create_pro_excel(row_dict)
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", 
        files={'document': (f'Mediaplan_{c_num}.xlsx', excel)}, 
        data={'chat_id': d.get('user_id'), 'caption': f'Ваш медиаплан {c_num} готов!'})
    
    return jsonify({"success":True, "campaign_number": c_num})

@app.route('/api/user-campaigns/<int:user_id>')
def history(user_id):
    init_db(); conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM campaigns WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    return jsonify({"success":True, "campaigns": [dict(r) for r in rows]})

@app.route('/api/confirmation/<num>')
def conf(num):
    init_db(); conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM campaigns WHERE campaign_number = ?", (num,)).fetchone()
    return jsonify({"success":True, "campaign": dict(row)}) if row else jsonify({"success":False})

if __name__ == '__main__': init_db(); app.run(host='0.0.0.0', port=5000)
