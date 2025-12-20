import os, sqlite3, io, textwrap, requests, logging
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from campaign_calculator import calculate_campaign_price_and_reach, TIME_SLOTS_DATA, STATION_DATA

app = Flask(__name__)
CORS(app)

TELEGRAM_BOT_TOKEN = '7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g'
ADMIN_TELEGRAM_ID = 174046571

# Универсальный путь к БД для Vercel/Render
DB_PATH = os.path.join(os.getcwd(), "campaigns.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            campaign_number TEXT,
            radio_stations TEXT,
            start_date TEXT, end_date TEXT, campaign_days INTEGER,
            time_slots TEXT, campaign_text TEXT, production_option TEXT,
            contact_name TEXT, company TEXT, phone TEXT, email TEXT,
            duration INTEGER, final_price INTEGER, actual_reach INTEGER,
            status TEXT DEFAULT 'active', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def create_excel_report(data):
    wb = Workbook()
    ws = wb.active
    ws.title = "Медиаплан РЗС"
    
    # Фирменный стиль РЗС
    blue_fill = PatternFill(start_color="1A237E", end_color="1A237E", fill_type="solid")
    white_bold = Font(color="FFFFFF", bold=True, size=12)
    border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    ws.merge_cells("A1:C1")
    ws["A1"] = f"МЕДИАПЛАН КАМПАНИИ {data['campaign_number']}"
    ws["A1"].fill = blue_fill
    ws["A1"].font = white_bold
    ws["A1"].alignment = Alignment(horizontal="center")

    info = [
        ["Радиостанции", data['radio_stations']],
        ["Период", f"{data['start_date']} — {data['end_date']}"],
        ["Дней", data['campaign_days']],
        ["Хронометраж", f"{data['duration']} сек."],
        ["Общий охват (чел)", data['actual_reach']],
        ["ИТОГО СУММА", f"{data['final_price']} руб."],
        ["", ""],
        ["ТЕКСТ РОЛИКА / СЦЕНАРИЙ:", ""]
    ]

    for i, (label, val) in enumerate(info, 2):
        ws.cell(row=i, column=1, value=label).font = Font(bold=True)
        ws.cell(row=i, column=2, value=val)

    # Текст ролика с переносом
    text_val = data.get('campaign_text') if data.get('campaign_text') else "Материал предоставляется заказчиком (готовый ролик)"
    wrapped = textwrap.wrap(text_val, width=70)
    start_row = 10
    for line in wrapped:
        ws.cell(row=start_row, column=1, value=line)
        ws.merge_cells(start_row=start_row, start_column=1, end_row=start_row, end_column=3)
        start_row += 1

    ws.column_dimensions['A'].width = 25
    ws.column_dimensions['B'].width = 40
    
    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

@app.route('/api/calculate', methods=['POST'])
def api_calculate():
    res = calculate_campaign_price_and_reach(request.json)
    return jsonify({"success": True, "calculation": {
        "final_price": res[2], "total_reach": res[3], "daily_coverage": res[4], "spots_per_day": res[5]
    }})

@app.route('/api/create-campaign', methods=['POST'])
def api_create():
    init_db()
    d = request.json
    c_num = f"R-{datetime.now().strftime('%H%M%S')}"
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO campaigns (user_id, campaign_number, radio_stations, start_date, end_date, campaign_days, 
        time_slots, campaign_text, production_option, contact_name, company, phone, email, duration, final_price, actual_reach)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (d.get('user_id'), c_num, ",".join(d.get('selected_radios', [])), d.get('start_date'), d.get('end_date'), 
          d.get('campaign_days'), ",".join(map(str, d.get('selected_time_slots', []))), d.get('campaign_text'),
          d.get('production_option'), d.get('contact_name'), d.get('company'), d.get('phone'), d.get('email'),
          d.get('duration'), d.get('final_price'), d.get('total_reach')))
    conn.commit()
    conn.close()

    # Уведомление в TG
    msg = f"⚡️ НОВАЯ ЗАЯВКА {c_num}\nКлиент: {d.get('contact_name')}\nКомпания: {d.get('company')}\nСумма: {d.get('final_price')} руб."
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data={"chat_id": ADMIN_TELEGRAM_ID, "text": msg})
    
    return jsonify({"success": True, "campaign_number": c_num})

@app.route('/api/user-campaigns/<int:user_id>')
def api_user_camps(user_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM campaigns WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    return jsonify({"success": True, "campaigns": [dict(r) for r in rows]})

@app.route('/api/send-excel/<camp_num>', methods=['POST'])
def api_send_excel(camp_num):
    uid = request.json.get('user_telegram_id')
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM campaigns WHERE campaign_number = ?", (camp_num,)).fetchone()
    if row:
        excel = create_excel_report(dict(row))
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", 
                      files={'document': (f'Mediaplan_{camp_num}.xlsx', excel)},
                      data={'chat_id': uid, 'caption': f'Ваш медиаплан {camp_num}'})
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Not found"})

@app.route('/api/confirmation/<camp_num>')
def api_confirm(camp_num):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM campaigns WHERE campaign_number = ?", (camp_num,)).fetchone()
    return jsonify({"success": True, "campaign": dict(row)}) if row else jsonify({"success": False})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
