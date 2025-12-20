import os, sqlite3, io, textwrap, requests, logging
from flask import Flask, jsonify, request, send_file, send_from_directory
from flask_cors import CORS
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from campaign_calculator import calculate_campaign_price_and_reach

app = Flask(__name__)
CORS(app)

TELEGRAM_BOT_TOKEN = '7368212837:AAHqVeOYeIHpJyDXltk-b6eGMmhwdUcM45g'
ADMIN_TELEGRAM_ID = 174046571

# Для Vercel используем /tmp, так как это единственная папка с правами на запись
DB_PATH = "/tmp/campaigns.db"

def init_db():
    try:
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
    except Exception as e:
        print(f"DB Init Error: {e}")

# --- РОУТЫ ДЛЯ СТАТИКИ (ЧТОБЫ НЕ БЫЛО 404) ---

@app.route('/')
def serve_index():
    return send_from_directory('frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

# --- API ---

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

    msg = f"📋 НОВАЯ ЗАЯВКА {c_num}\nКлиент: {d.get('contact_name')}\nКомпания: {d.get('company')}\nСумма: {d.get('final_price')} руб."
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", data={"chat_id": ADMIN_TELEGRAM_ID, "text": msg})
    
    return jsonify({"success": True, "campaign_number": c_num})

@app.route('/api/user-campaigns/<int:user_id>')
def api_user_camps(user_id):
    init_db()
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
        # Функция создания Excel (встроена для компактности)
        wb = Workbook()
        ws = wb.active
        ws.title = "Медиаплан"
        ws.append(["Номер кампании", row['campaign_number']])
        ws.append(["Станции", row['radio_stations']])
        ws.append(["Сумма", row['final_price']])
        ws.append(["Текст", row['campaign_text']])
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument", 
                      files={'document': (f'Mediaplan_{camp_num}.xlsx', output)},
                      data={'chat_id': uid, 'caption': f'Ваш медиаплан {camp_num}'})
        return jsonify({"success": True})
    return jsonify({"success": False})

@app.route('/api/confirmation/<camp_num>')
def api_confirm(camp_num):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM campaigns WHERE campaign_number = ?", (camp_num,)).fetchone()
    return jsonify({"success": True, "campaign": dict(row)}) if row else jsonify({"success": False})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
