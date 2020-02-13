from flask import Flask, render_template, url_for, request, redirect, json, session
from flask_socketio import SocketIO, emit
import pymysql
import time
from add_log import add_log
from get_messages import get_messages

app = Flask(__name__)
socketio = SocketIO(app)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

users = []


@app.route("/signup", methods=['GET'])
def signup():
    return render_template('signup.html')


@app.route("/search_pair", methods=['POST'])
def search_pair():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    if not username:
        return json.dumps({"status": "error", "message": "Введите имя"})
    if not email:
        return json.dumps({"status": "error", "message": "Введите email"})
    if not password:
        return json.dumps({"status": "error", "message": "Введите пароль"})

    connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")
    try:
        with connection.cursor() as cursor:
            sql = "SELECT name FROM users WHERE name=%s"
            pair_name = cursor.execute(sql, username)

            sql = "SELECT email FROM users WHERE email=%s"
            pair_email = cursor.execute(sql, email)

    finally:
        connection.close()

    if not pair_name and not pair_email:
        return json.dumps({"status": "OK"})
    elif pair_name:
        return json.dumps({"status": "error", "message": "Имя занято"})
    else:
        return json.dumps({"status": "error", "message": "E-mail занят"})


@app.route("/add_user", methods=['POST'])
def add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO users (id, name, email, passwd) VALUES (NULL, %s, %s, %s)"
            cursor.execute(sql, (username, email, password))
            connection.commit()
    finally:
        connection.close()

    session["username"] = username.lower()
    session["email"] = email
    session["password"] = password
    session["first_message_in_db"] = 0

    users.append(session["username"])

    add_log("new_user", session['username'])

    return json.dumps({"status": "OK"})


@app.route("/login", methods=['GET'])
def login():
    return render_template('login.html')


@app.route("/check", methods=['POST'])
def check():
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users:
        return json.dumps({"status": "error", "message": "Пользователь уже в сети"})

    connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list", )
    try:
        with connection.cursor() as cursor:
            sql = "SELECT email FROM users WHERE name=%s AND passwd=%s"
            answer = cursor.execute(sql, (username, password))
            email = cursor.fetchone()
    finally:
        connection.close()
    if answer:
        session["username"] = username.lower()
        session["password"] = password
        session["email"] = email[0]
        session["first_message_in_db"] = 0
        session.modified = True
        users.append(session["username"])
        add_log("login", session['username'])

        return json.dumps({"status": "OK"})
    return json.dumps({"status": "error", "message": "Неверный логин или пороль"})


@app.route("/exit", methods=['GET'])
def exit():
    users.remove(session["username"])
    session.pop("username", None)
    session.pop("email", None)
    session.pop("password", None)
    session.pop("first_message_in_db", None)
    return redirect(url_for('login'))


@app.route("/", methods=['GET'])
def main():
    if "username" in session:
        return render_template("messenger.html", messages=get_messages(session))
    return redirect(url_for('login'))


@app.route("/messenger", methods=['GET'])
def messenger():
    if "username" in session:
        return render_template('messenger.html', messages=get_messages(session))
    return redirect(url_for('login'))


@app.route("/userpage", methods=['GET'])
def user_page():
    if "username" in session:
        return render_template("user_page.html", session=session)
    return redirect(url_for('login'))


@app.route("/change_name", methods=['GET'])
def change_name():
    if "username" in session:
        return render_template("change_name.html")
    return redirect(url_for('login'))


@app.route("/cn", methods=['POST'])
def cn():

    new_name = request.form.get("username").lower()

    if new_name:

        connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")

        try:
            with connection.cursor() as cursor:

                sql = "SELECT email FROM users WHERE name=%s"
                answer = cursor.execute(sql, new_name)

                if answer:
                    return json.dumps({"status": "error", "message": "Имя занято"})

                else:
                    sql = "UPDATE users SET name = %s WHERE email=%s"
                    cursor.execute(sql, (new_name, session['email']))
                    connection.commit()

                    past_name = session['username']
                    add_log("rename", session['username'], new_name)
                    users.remove(session["username"])
                    session["username"] = new_name
                    session.modified = True
                    users.append(session["username"])

                    return json.dumps({"status": "OK", "past_name": past_name, "new_name": session['username']})
        finally:
            connection.close()
    else:
        return json.dumps({"status": "error", "message": "Заполните поле"})


@app.route("/change_email", methods=['GET'])
def change_email():
    if "username" in session:
        return render_template("change_email.html")
    return redirect(url_for('login'))


@app.route("/ce", methods=['POST'])
def ce():

    new_email = request.form.get("email")

    if new_email:

        connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")

        try:
            with connection.cursor() as cursor:
                sql = "SELECT name FROM users WHERE email=%s"
                answer = cursor.execute(sql, new_email)

                if answer:
                    return json.dumps({"status": "error", "message": "E-mail занят"})
                else:
                    sql = "UPDATE users SET email = %s WHERE name=%s"
                    cursor.execute(sql, (new_email, session['username']))
                    connection.commit()

                    session["email"] = new_email
                    session.modified = True

                    return json.dumps({"status": "OK"})
        finally:
            connection.close()
    else:
        return json.dumps({"status": "error", "message": "Заполните поле"})


@app.route("/change_pass", methods=['GET'])
def change_pass():
    if "username" in session:
        return render_template("change_pass.html")
    return redirect(url_for('login'))


@app.route("/cp", methods=['POST'])
def cp():
    new_pass = request.form.get("password")

    if new_pass and new_pass != session['password']:

        connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")

        try:
            with connection.cursor() as cursor:
                sql = "UPDATE users SET passwd = %s WHERE name=%s"
                cursor.execute(sql, (new_pass, session['username']))
                connection.commit()

                session["password"] = new_pass
                session.modified = True
                return json.dumps({"status": "OK"})

        finally:
            connection.close()

    elif new_pass == session['password']:
        return json.dumps({"status": "error", "message": "Вы ввели старый пароль"})
    else:
        return json.dumps({"status": "error", "message": "Заполните поле"})


@app.route("/dlt", methods=['GET'])
def dlt_user():
    if "username" in session:

        connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")

        try:
            with connection.cursor() as cursor:
                sql = "DELETE FROM users WHERE name=%s"
                cursor.execute(sql, session["username"])
                connection.commit()
        finally:
            connection.close()

        add_log("dlt", session['username'])
        return redirect(url_for('exit'))

    return redirect(url_for('login'))


@socketio.on('add_message')
def add_message(message_data):
    if message_data['code'] == 1:
        message = {"message": message_data['data'], "name": "system", "time": time.ctime()[10:16]}
    else:
        message = {"message": message_data['data'], "name": session['username'], "time": time.ctime()[10:16]}

    connection = pymysql.connect("127.0.0.1", "root", "1234", "messages")
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO message (id, tag, message, time) VALUES (NULL, %s, %s, %s)"
            cursor.execute(sql, (message['name'], message['message'], message['time']))
            connection.commit()
    finally:
        connection.close()
    emit('update', message, broadcast=True)


@socketio.on('clear_db')
def clear():

    connection = pymysql.connect("127.0.0.1", "root", "1234", "messages")
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id FROM message"
            id = cursor.execute(sql)
    finally:
        connection.close()

    connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")
    try:
        with connection.cursor() as cursor:
            sql = "UPDATE users SET first_message_in_db = %s WHERE name=%s"
            cursor.execute(sql, (int(id), session['username']))
            connection.commit()

    finally:
        connection.close()

    emit('clear_field', " ", broadcast=False)


if __name__ == "__main__":
    socketio.run(app)

# IT'S NOT A BUG IT'S A FEATURE
