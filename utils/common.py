import json
import random
import string
import time

import utils.common as common
from utils.db import *

qb = QueryBuilder(DataBase(), 'data.db')

# read setting.json
with open("setting.json", "r") as f:
    SETTING = json.load(f)


def add_tables():
    # create table settings
    qb.reset()  # reset query builder
    qb.query(
        '''CREATE TABLE IF NOT EXISTS settings ("setting_id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "value" TEXT)'''
    )
    # create table iptv_categories
    qb.reset()  # reset query builder
    qb.query(
        '''CREATE TABLE IF NOT EXISTS iptv_categories ("category_id" INTEGER PRIMARY KEY AUTOINCREMENT, "category_name" TEXT, "parent_id" INTEGER)'''
    )
    # create table iptv_channels
    qb.reset()  # reset query builder
    qb.query(
        '''CREATE TABLE IF NOT EXISTS iptv_channels ("channel_id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "stream_type" TEXT, "stream_id" INTEGER, "stream_icon" TEXT, "epg_channel_id" TEXT, "category_id" TEXT, "tv_archive" TEXT DEFAULT NULL, "direct_source" TEXT, "tv_archive_duration" TEXT)'''
    )
    # create table iptv_epg
    qb.reset()  # reset query builder
    qb.query(
        '''CREATE TABLE IF NOT EXISTS iptv_epg ("epg_id" INTEGER PRIMARY KEY AUTOINCREMENT, "channel_id" INTEGER)'''
    )
    # create table users
    qb.reset()  # reset query builder
    qb.query(
        '''CREATE TABLE IF NOT EXISTS users ("user_id" INTEGER PRIMARY KEY AUTOINCREMENT, "username" TEXT, "password" TEXT, "email" TEXT, "is_admin" INTEGER DEFAULT 0, "is_trial" INTEGER DEFAULT 0, "status" TEXT, "exp_date" TEXT, "max_connections" INTEGER DEFAULT 1, "created_at" INTEGER DEFAULT 0, "active_cons" INTEGER DEFAULT 0, "allowed_output_formats" TEXT, "auth_hash" TEXT)'''
    )


def server_info():
    server_info = {}
    server_info[
        "url"] = f"http://{common.SETTING['server']['ip']}:{common.SETTING['server']['port']}"
    server_info["port"] = str(common.SETTING['server']['port'])
    server_info["https_port"] = "8000"
    server_info["rtmp_port"] = "8000"
    server_info["server_protocol"] = "http"
    server_info["timestamp_now"] = time.time()
    server_info["time_now"] = time.strftime("%Y-%m-%d, %H:%M:%S",
                                            time.localtime())
    server_info["timezone"] = ""
    return server_info


def gen_hash(length=32):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def get_setting_db(name):
    data = qb.select('settings').where([['name', '=', name]]).one()
    if data:
        return data['value']
    else:
        qb.insert('settings', {'name': name, 'value': ''}).go()
        return ''


def set_setting_bd(name, value):
    qb.update('settings', {'value': value}).where([['name', '=', name]]).go()
