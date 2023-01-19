import time


def auth(username, password):
    user_info = {}
    user_info["username"] = username
    user_info["password"] = password
    user_info["message"] = "ok"
    user_info["auth"] = 1
    user_info["status"] = "Active"
    user_info["exp_date"] = "Unlimited"
    user_info["is_trial"] = "0"
    user_info["active_cons"] = "0"
    user_info["created_at"] = "0"
    user_info["max_connections"] = "1"
    user_info["allowed_output_formats"] = ["m3u8", "ts"]

    server_info = {}
    server_info["url"] = "http://192.168.0.100:8000"
    server_info["port"] = "8000"
    server_info["https_port"] = "8000"
    server_info["rtmp_port"] = "8000"
    server_info["server_protocol"] = "http"
    server_info["timestamp_now"] = time.time()
    server_info["time_now"] = time.strftime(
        "%Y-%m-%d, %H:%M:%S", time.localtime())
    server_info["timezone"] = ""

    return {"user_info": user_info, "server_info": server_info}
