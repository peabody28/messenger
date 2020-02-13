import pymysql


def get_messages(session):

    connection = pymysql.connect("127.0.0.1", "root", "1234", "users_list")

    try:
        with connection.cursor() as cursor:
            sql = "SELECT first_message_in_db FROM users WHERE name=%s"
            cursor.execute(sql, session['username'])
            begin = cursor.fetchone()[0]

    finally:
        connection.close()

    messages = []

    connection = pymysql.connect("127.0.0.1", "root", "1234", "messages")
    try:
        with connection:
            cursor = connection.cursor()
            sql = "SELECT id FROM message"
            id = cursor.execute(sql)

            for i in range(begin, id):
                sql = "SELECT * FROM message WHERE id=%s"
                cursor.execute(sql, i + 1)
                answer = cursor.fetchall()[0]

                messages.append({"message": answer[1],
                                 "name": answer[2],
                                 "time": answer[3]})
    finally:
        connection.close()
    return messages
