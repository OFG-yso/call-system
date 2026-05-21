from flask import Flask, request, render_template_string, redirect, session
import sqlite3, smtplib, os
from email.mime.text import MIMEText

app = Flask(__name__)
app.secret_key = "change-this-secret"
ADMIN_PASSWORD = "kwansei1889"
EMAIL = "ofg@kgjh.jp"
APP_PASSWORD = "zilf hzgk cssv steb"
DB = "queue.db"


def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS queue (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        called INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()


def send_mail(to, num):
    msg = MIMEText(f"受付番号{num}番のお客様\n\n順番になりましたので受付へお越しください。\n\n※このメールは自動送信です。返信不可")
    msg['Subject'] = '順番になりました'
    msg['From'] = '受付システム（返信不可）'
    msg['To'] = to

    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(EMAIL, APP_PASSWORD)
    s.sendmail(EMAIL, [to], msg.as_string())
    s.quit()


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute('INSERT INTO queue (email) VALUES (?)', (email,))
        num = c.lastrowid
        conn.commit()
        conn.close()
        return f'受付完了。あなたの番号は {num} 番です。'
    return '''<form method="post">メール:<input name="email"><button>受付</button></form>'''


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST' and 'pw' in request.form:
        if request.form['pw'] == ADMIN_PASSWORD:
            session['ok'] = True
    if not session.get('ok'):
        return '<form method="post">PW:<input type="password" name="pw"><button>ログイン</button></form>'

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT * FROM queue WHERE called=0 ORDER BY id')
    rows = c.fetchall()
    conn.close()

    html = '<h1>待機</h1>'
    for r in rows:
        html += f'{r[0]} {r[1]} <a href="/call/{r[0]}">呼ぶ</a><br>'
    return html


@app.route('/call/<int:num>')
def call(num):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute('SELECT email FROM queue WHERE id=?', (num,))
    email = c.fetchone()[0]
    send_mail(email, num)
    c.execute('UPDATE queue SET called=1 WHERE id=?', (num,))
    conn.commit()
    conn.close()
    return redirect('/admin')


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
