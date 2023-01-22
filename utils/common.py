import json
import random
import string
import time

import utils.common as common

# read setting.json
with open("setting.json", "r") as f:
    SETTING = json.load(f)


def server_info():
    server_info = {}
    server_info["url"] = f"http://{common.SETTING['server']['ip']}:{common.SETTING['server']['port']}"
    server_info["port"] = str(common.SETTING['server']['port'])
    server_info["https_port"] = "8000"
    server_info["rtmp_port"] = "8000"
    server_info["server_protocol"] = "http"
    server_info["timestamp_now"] = time.time()
    server_info["time_now"] = time.strftime(
        "%Y-%m-%d, %H:%M:%S", time.localtime())
    server_info["timezone"] = ""
    return server_info


def gen_hash(length=32):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))
