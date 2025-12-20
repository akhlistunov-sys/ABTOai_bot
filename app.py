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
DB_PATH = "/tmp/campaigns.db" if os.environ.get('VERCEL') else "campaigns.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, campaign_number TEXT,
        radio_stations TEXT, start_date TEXT, end_date TEXT, campaign_days INTEGER,
        time_slots TEXT, campaign_text TEXT, production_option TEXT,
        contact_name TEXT, company TEXT, phone TEXT, email TEXT,
        duration INTEGER, final_price INTEGER, actual_reach INTEGER, ots INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    conn.commit()
    conn.close()

def create_pro_excel(row):
    wb = Workbook()
    ws = wb.active
    ws.title = "Медиаплан РЗС"
    blue = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
    
    ws.merge_cells("A1:C1")
    ws["A1"] = f"МЕДИАПЛАН РЗС ТЮМЕНЬ #{row['campaign_number']}"
    ws["A1"].fill = blue
    ws["A1"].font = Font(color="FFFFFF", bold=True, size=14)
    ws["A1"].alignment = Alignment(horizontal="center")
    
    data = [
        ("Радиостанции", row['radio_stations']),
        ("Период кампании", f"{row['start_date']} - {row['end_date']} ({row['campaign_days']} дн.)"),
        ("Хронометраж", f"{row['duration']} сек."),
        ("Суточный охват", f"{int(row['actual_reach'] * 0.7)} чел."),
        ("Общий охват (период)", f"{row['actual_reach']} чел."),
        ("Всего рекламных контактов", f"{row.get('ots', 0):,}"),
        ("ИТОГО К ОПЛАТЕ", f"{row['final_price']:,} руб.")
    ]
    
    for r_idx, (k, v) in enumerate(data, 3):
        ws.cell(row=r_idx, column=1, value=k).font = Font(bold=True)
        ws.cell(row=r_idx, column=1).border = border
        ws.cell(row=r_idx, column=2, value=v).border = border

    ws["A11"] = "СЦЕНАРИЙ / ТЕКСТ РОЛИКА:"; ws["A11"].font = Font(bold=True)
    txt = row['campaign_text'] if row['campaign_text'] else "Материал предоставляется заказчиком (готовый файл)"
    for i, line in enumerate(textwrap.wrap(txt, 70), 12):
        ws.cell(row=i, column=1, value=line)
    
    ws.column_dimensions['A'].width = 30; ws.column_dimensions['B'].width = 45
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
    
    msg = f"✅ ЗАЯВКА {c_num}\nКлиент: {d.get('contact_name')}\nСумма: {d.get('final_price')}р\nКонтактов: {d.get('ots')}"
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data={"chat_id": ADMIN_TELEGRAM_ID, "text": msg})
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
        excel = create_pro_excel(dict(row))
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", 
            files={'document': (f'Mediaplan_{num}.xlsx', excel)}, 
            data={'chat_id': uid, 'caption': f'Ваш профессиональный медиаплан {num}'})
        return jsonify({"success":True})
    return jsonify({"success":False})

@app.route('/api/confirmation/<num>')
def conf(num):
    init_db(); conn = sqlite3.connect(DB_PATH); conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM campaigns WHERE campaign_number = ?", (num,)).fetchone()
    return jsonify({"success":True, "campaign": dict(row)}) if row else jsonify({"success":False})

if __name__ == '__main__': init_db(); app.run(host='0.0.0.0', port=5000)
