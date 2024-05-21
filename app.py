import os
import sqlite3

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = 'your_secret_key'
DB_NAME = 'mydb.db'
LOGFILE = 'error.log'


def error_log(error: str) -> None:
    error = error + '\n'
    if not os.path.exists(LOGFILE):
        with open('error.log', 'w') as f:
            f.write(error)
    else:
        with open('error.log', 'a', encoding='utf-8') as f:
            f.write(error)


def get_all_user() -> list:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('Select iid, idno, pwd from member')
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return result


def get_user_data() -> list:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 設置 row_factory
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM member WHERE iid = ?", (session['userid'],))
    user = cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()
    return user


def edit_user_data(nm, birth, blood, phone, email, idno, pwd, iid) -> None:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 設置 row_factory
    cursor = conn.cursor()
    cursor.execute(
        "Update member set nm = ?, birth = ?, blood = ?, phone = ?, email = ?, idno = ?, pwd = ? WHERE iid = ?",
        (nm, birth, blood, phone, email, idno, pwd, iid),
    )
    conn.commit()
    cursor.close()
    conn.close()


@app.route('/')
def index():
    try:
        if 'userid' not in session:
            return redirect(url_for('login'))
        else:
            user = get_user_data()
            if user is None:
                raise Exception('Account 不存在')
            else:
                return render_template(
                    'index.html',
                    nm=user['nm'],
                    birth=user['birth'],
                    blood=user['blood'],
                    phone=user['phone'],
                    email=user['email'],
                    idno=user['idno'],
                    pwd=user['pwd'],
                )
    except Exception as e:
        error_log(f"有錯誤產生，錯誤訊息為：{e}")
        return render_template('error.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'GET':
            return render_template('login.html', error='')
        elif request.method == 'POST':
            userid = request.form.get('userid')
            password = request.form.get('pwd')
            correct_login = False
            user = get_all_user()
            for i in user:
                if i[1] == userid and i[2] == password:
                    correct_login = True
                if correct_login:
                    session['userid'] = i[0]
                    break
            if correct_login:
                return redirect(url_for('index'))
            return render_template('login.html', error="請輸入正確的帳號密碼")
    except Exception as e:
        error_log(f"有錯誤產生，錯誤訊息為：{e}")
        return render_template('error.html')


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    try:
        if 'userid' not in session:
            return redirect(url_for('login'))
        else:
            if request.method == 'GET':
                user = get_user_data()
                return render_template(
                    'edit.html',
                    nm=user['nm'],
                    birth=user['birth'],
                    blood=user['blood'],
                    phone=user['phone'],
                    email=user['email'],
                    idno=user['idno'],
                    pwd=user['pwd'],
                )
            elif request.method == "POST":
                name = request.form.get('nms')
                birth = request.form.get('births')
                blood = request.form.get('bloods')
                phone = request.form.get('phones')
                email = request.form.get('emails')
                userid = request.form.get('idnos')
                pwd = request.form.get('pwds')
                edit_user_data(
                    nm=name,
                    birth=birth,
                    blood=blood,
                    phone=phone,
                    email=email,
                    idno=userid,
                    pwd=pwd,
                    iid=session['userid'],
                )
                return redirect(url_for('index'))
    except Exception as e:
        error_log(f"有錯誤產生，錯誤訊息為：{e}")
        return render_template('error.html')


@app.route('/logout')
def logout():
    try:
        session.pop('userid', None)
        return redirect(url_for('index'))
    except Exception as e:
        error_log(f"有錯誤產生，錯誤訊息為：{e}")
        return render_template('error.html')
