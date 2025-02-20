from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)


# Veritabanı bağlantısı
def get_db():
    conn = sqlite3.connect('water_tracking.db')
    conn.row_factory = sqlite3.Row
    return conn


# Veritabanını başlat
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS daily_intake (
                date TEXT PRIMARY KEY,
                goal INTEGER DEFAULT 0,
                intake INTEGER DEFAULT 0
            )
        ''')
        db.commit()


# Veritabanını başlatma ve geçmiş günleri kontrol etme
def update_goal_for_all_days(db, goal):
    db.execute('UPDATE daily_intake SET goal = ? WHERE goal = 0', (goal,))
    db.commit()


# Ana sayfa
@app.route('/')
def index():
    return show_day(datetime.today().strftime('%Y-%m-%d'))


# Belirli bir günün verisini göster
@app.route('/<date_param>')
def show_day(date_param):
    db = get_db()

    # Bugün veya geçmiş günlerin verisini alalım
    cur = db.execute('SELECT * FROM daily_intake WHERE date = ?', (date_param,))
    row = cur.fetchone()

    if row:
        daily_goal = row['goal']
        current_intake = row['intake']
    else:
        daily_goal, current_intake = 0, 0
        db.execute('INSERT OR IGNORE INTO daily_intake (date, goal, intake) VALUES (?, ?, ?)', (date_param, 0, 0))
        db.commit()

    update_goal_for_all_days(db, daily_goal)

    target_reached = current_intake >= daily_goal if daily_goal > 0 else False

    return render_template('index.html',
                           daily_goal=daily_goal,
                           current_intake=current_intake,
                           target_reached=target_reached,
                           today_date=date_param)


# Su miktarını artırma veya azaltma
@app.route('/update_intake', methods=['POST'])
def update_intake():
    date_param = request.form.get('date')
    action = request.form.get('action')

    db = get_db()
    cur = db.execute('SELECT * FROM daily_intake WHERE date = ?', (date_param,))
    row = cur.fetchone()

    if row:
        current_intake = row['intake']
        if action == 'increase':
            current_intake += 100
        elif action == 'decrease':
            current_intake = max(0, current_intake - 100)

        db.execute('UPDATE daily_intake SET intake = ? WHERE date = ?', (current_intake, date_param))
        db.commit()

    return redirect(url_for('show_day', date_param=date_param))


# Hedef değiştirme ekranı
@app.route('/change_goal', methods=['GET', 'POST'])
def change_goal():
    db = get_db()
    today_date = datetime.today().strftime('%Y-%m-%d')

    if request.method == 'POST':
        new_goal = int(request.form['new_goal'])

        # Bugün ve sonraki günler için hedefi güncelle
        db.execute('UPDATE daily_intake SET goal = ? WHERE date >= ?', (new_goal, today_date))
        db.commit()

        return redirect(url_for('index'))

    # Mevcut hedefi al
    cur = db.execute('SELECT goal FROM daily_intake WHERE date = ?', (today_date,))
    row = cur.fetchone()
    daily_goal = row['goal'] if row else 0

    return render_template('change_goal.html', daily_goal=daily_goal, today_date=today_date)


# Geçmiş verileri gösteren route
@app.route('/history')
def history():
    db = get_db()
    today_date = datetime.today().strftime('%Y-%m-%d')

    # Son 30 günün verilerini al (bugün dahil)
    cur = db.execute('''
        SELECT * FROM daily_intake 
        WHERE date >= date(?) AND date <= ?
        ORDER BY date DESC
        LIMIT 30
    ''', (datetime.today() - timedelta(days=29), today_date))
    rows = cur.fetchall()

    return render_template('history.html', rows=rows, today_date=today_date)

# Uygulama başlatıldığında veritabanını başlat
if __name__ == '__main__':
    init_db()
    app.run(debug=True)