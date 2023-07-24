import random
import string
import time
import os

import config as cfg
from helper.db import QueryBuilder, DataBase

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
    # create table films_categories
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS films_categories ("category_id" INTEGER PRIMARY KEY AUTOINCREMENT, "category_name" TEXT, "parent_id" INTEGER)"""
    )
    # create table series_categories
    qb.reset()  # reset query builder
    qb.query(
        """CREATE TABLE IF NOT EXISTS series_categories ("category_id" INTEGER PRIMARY KEY AUTOINCREMENT, "category_name" TEXT, "parent_id" INTEGER)"""
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


def random_user_agent():
    user_agent_pool = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Opera/9.80 (Windows NT 6.1; U; zh-cn) Presto/2.9.168 Version/11.50",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; InfoPath.3)",
        "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; GTB7.0)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1)",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; ) AppleWebKit/534.12 (KHTML, like Gecko) Maxthon/3.0 Safari/534.12",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E; SE 2.X MetaSr 1.0)",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.3 (KHTML, like Gecko) Chrome/6.0.472.33 Safari/534.3 SE 2.X MetaSr 1.0",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E)",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/13.0.782.41 Safari/535.1 QQBrowser/6.9.11079.201",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.1; WOW64; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; .NET4.0E) QQBrowser/6.9.11079.201",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    ]
    return random.choice(user_agent_pool)
