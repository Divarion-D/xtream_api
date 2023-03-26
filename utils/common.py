import random
import string
import time
import os

import config as cfg
import utils.common as common
from utils.db import *

qb = QueryBuilder(DataBase(), "data.db")


def add_tables():
    # create table settings
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS settings ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "value" TEXT)"""
    )
    # create table iptv_categories
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS iptv_categories ("category_id" INTEGER PRIMARY KEY AUTOINCREMENT, "category_name" TEXT, "parent_id" INTEGER)"""
    )
    # create table iptv_channels
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS iptv_channels ("channel_id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "stream_type" TEXT, "stream_id" INTEGER, "stream_icon" TEXT, "epg_channel_id" TEXT, "category_id" TEXT, "tv_archive" TEXT DEFAULT NULL, "direct_source" TEXT, "tv_archive_duration" TEXT)"""
    )
    # create table iptv_epg
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS iptv_epg ("epg_id" INTEGER PRIMARY KEY AUTOINCREMENT, "channel_id" INTEGER)"""
    )
    # create table users
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS users ("user_id" INTEGER PRIMARY KEY AUTOINCREMENT, "username" TEXT, "password" TEXT, "email" TEXT, "is_admin" INTEGER DEFAULT 0, "is_trial" INTEGER DEFAULT 0, "status" TEXT, "exp_date" TEXT, "max_connections" INTEGER DEFAULT 1, "created_at" INTEGER DEFAULT 0, "active_cons" INTEGER DEFAULT 0, "allowed_output_formats" TEXT, "auth_hash" TEXT)"""
    )
    # create table video_categories
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS video_categories ("id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "parent_id" INTEGER)"""
    )


def server_info():
    server_info = {
        "url": f"http://{cfg.SERVER_IP}:{cfg.SERVER_PORT}",
        "port": str(cfg.SERVER_PORT),
        "https_port": "8000",
        "rtmp_port": "8000",
        "server_protocol": "http",
        "timestamp_now": time.time(),
    }
    server_info["time_now"] = time.strftime("%Y-%m-%d, %H:%M:%S", time.localtime())
    server_info["timezone"] = ""
    return server_info


def gen_hash(length=32):
    """
    It generates a random string of length 32, using only lowercase letters

    :param length: The length of the hash, defaults to 32 (optional)
    :return: A string of random lowercase letters of length 32.
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def get_setting_db(name):
    if data := qb.select("settings").where([["name", "=", name]]).one():
        return data["value"]
    qb.insert("settings", {"name": name, "value": ""}).go()
    return ""


def set_setting_bd(name, value):
    qb.update("settings", {"value": value}).where([["name", "=", name]]).go()

def create_temp_folder():
    if not os.path.exists("./temp"):
        os.makedirs("./temp")