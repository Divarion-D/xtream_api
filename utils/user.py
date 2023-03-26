import bcrypt

from utils.db import *

qb = QueryBuilder(DataBase(), "data.db")


def create_admin(username: str, password: str):
    hash_pwd = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt()
    )  # hash password
    qb.insert(
        "users",
        {"username": username, "password": hash_pwd.decode("utf-8"), "is_admin": 1},
    ).go()


def auth(username: str, password: str):
    user = qb.select("users").where([["username", "=", username]]).one()
    if user is None:
        return {"error": 1, "error_code": 401, "error_message": "Username not found"}
    # check password
    if bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return {"error": 0, "user_info": user}
    else:
        return {"error": 1, "error_code": 402, "error_message": "Wrong password"}


def user_info_xtream(data, username, password):
    data = data["user_info"]

    return {
        "username": username,
        "password": password,
        "message": "ok",
        "auth": 1,
        "status": "Active",
        "exp_date": "Unlimited",
        "is_trial": data["is_trial"],
        "active_cons": data["active_cons"],
        "created_at": data["active_cons"],
        "max_connections": data["max_connections"],
        "allowed_output_formats": ["m3u8", "ts"],
    }
