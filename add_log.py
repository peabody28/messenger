import time


def add_log(code, username, new_name=None):
    if code == "new_user":
        f = open("logs.txt", "a")
        text = "NEW_USER: " + username + "   "
        f.write(text + (50 - len(text)) * " " + time.ctime()[4:] + "\n")
        f.close()
    elif code == "login":
        f = open("logs.txt", "a")
        text = username + " LOGIN "
        f.write(text + (50 - len(text)) * " " + time.ctime()[4:] + "\n")
        f.close()
    elif code == "dlt":
        f = open("logs.txt", "a")
        text = username + " DELETED "
        f.write(text + (50 - len(text)) * " " + time.ctime()[4:] + "\n")
        f.close()
    else:
        f = open("logs.txt", "a")
        text = username + " CHANGE NAME TO " + new_name
        f.write(text + (50 - len(text)) * " " + time.ctime()[4:] + "\n")
        f.close()
