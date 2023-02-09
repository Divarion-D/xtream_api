import bcrypt
from utils.db import *

qb = QueryBuilder(DataBase(), 'data.db')


def create_admin(username: str, password: str):
    hash_pwd = bcrypt.hashpw(password.encode('utf-8'),
                             bcrypt.gensalt())  # hash password
    qb.insert("users", {
        'username': username,
        'password': hash_pwd.decode('utf-8'),
        'is_admin': 1
    }).go()


def auth(username: str, password: str):
    user = qb.select("users").where([["username", "=", username]]).one()
    if user == None:
        return {
            "error": 1,
            "error_code": 401,
            "error_message": "Username not found"
        }
    else:
        # check password
        if bcrypt.checkpw(password.encode('utf-8'),
                          user["password"].encode('utf-8')):
            return {"error": 0, "user_info": user}
        else:
            return {
                "error": 1,
                "error_code": 402,
                "error_message": "Wrong password"
            }


def user_info_xtream(data, username, password):
    data = data['user_info']

    user_info = {}
    user_info["username"] = username
    user_info["password"] = password
    user_info["message"] = "ok"
    user_info["auth"] = 1
    user_info["status"] = "Active"
    user_info["exp_date"] = "Unlimited"
    user_info["is_trial"] = data["is_trial"]
    user_info["active_cons"] = data["active_cons"]
    user_info["created_at"] = data["active_cons"]
    user_info["max_connections"] = data["max_connections"]
    user_info["allowed_output_formats"] = ["m3u8", "ts"]

    return user_info
