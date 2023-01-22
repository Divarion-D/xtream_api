import re
import time

import requests

import utils.common as common
from utils.db import DB

db = DB()


class M3U_Parser():
    def __init__(self, m3u_url):
        self.m3u_url = m3u_url
        self.m3u_list = self.get_m3u_list()
        db.open()
        channels_lupd = db.get_setting("chenel_lupd")
        channels_lupd = int(channels_lupd) if channels_lupd != '' else 0
        if channels_lupd < int(time.time()) - common.SETTING["iptv"]["upd_interval_list"]:
            # clear channels
            db.delete_all("iptv_channels")
            # clear categories
            db.delete_all("iptv_categories")
            self.parse_m3u()
            db.set_setting("chenel_lupd", int(time.time()))
        db.close()

    def get_m3u_list(self):
        return requests.get(self.m3u_url).text.splitlines()

    def parse_m3u(self):
        print("Parsing M3U file...")
        data_list = {}
        cnl = 1
        for line in self.m3u_list:
            if line.startswith('#EXTINF:'):
                cnl = 1
                data_list["stream_icon"] = re.search(
                    'tvg-logo="(.+?)"', line).group(1).strip() if 'tvg-logo' in line else ""
                data_list["name"] = re.search('tvg-name="(.+?)"', line).group(
                    1).strip() if 'tvg-name' in line else re.search(',(.+)', line).group(1).strip()
                data_list["group_title"] = re.search(
                    'group-title="(.+?)"', line).group(1).strip() if 'group-title' in line else ""
                data_list["epg_channel_id"] = re.search(
                    'tvg-id="(.+?)"', line).group(1).strip() if 'tvg-id' in line else ""
                #data_list["tvg_shift"] = re.search('tvg-shift="(.+?)"', line).group(1) if 'tvg-shift' in line else None
                #data_list["tvg_url"] = re.search('tvg-url="(.+?)"', line).group(1) if 'tvg-url' in line else None
                #data_list["tvg_rec"] = re.search('tvg-rec="(.+?)"', line).group(1) if 'tvg-rec' in line else None
                #data_list["tvg_chno"] = re.search('tvg-chno="(.+?)"', line).group(1) if 'tvg-chno' in line else None
                #data_list["tvg_epg"] = re.search('tvg-epg="(.+?)"', line).group(1) if 'tvg-epg' in line else None
                #data_list["tvg_radio"] = re.search('tvg-radio="(.+?)"', line).group(1) if 'tvg-radio' in line else None
            elif line.startswith('#EXTGRP:'):
                data_list["group_title"] = re.search(
                    '#EXTGRP:(.+)', line).group(1)
            elif line.startswith('http'):
                data_list["url"] = line
                cnl = 0

            if cnl == 0 and data_list:
                # remove '
                data_list["name"] = data_list["name"].replace("'", "")

                print("Update:" + data_list["name"])
                if "group_title" in data_list:
                    if not db.get("iptv_categories", "category_name", "category_name = '{0}'".format(data_list["group_title"])):
                        db.insert("iptv_categories", ("category_name",
                                  "parent_id"), (data_list["group_title"], 0))

                if not db.get("iptv_channels", "name", "name = '{0}'".format(data_list["name"])):
                    category_id = db.get("iptv_categories", "category_id", "category_name = '{0}'".format(
                        data_list["group_title"]))["category_id"]
                    insert_id = db.insert("iptv_channels", ("name", "stream_type", "direct_source", "stream_icon", "epg_channel_id", "category_id"), (
                        data_list["name"], "live", data_list["url"], data_list["stream_icon"], data_list["epg_channel_id"], category_id))
                    db.update("iptv_channels", "stream_id", insert_id -
                              1, "channel_id = {0}".format(insert_id))
                data_list = {}

    def get_all_categories(self):
        db.open()
        categories = db.get_all("iptv_categories", "*")
        db.close()
        return categories

    def get_all_channels(self):
        db.open()
        data = db.get_all("iptv_channels", "*")
        db.close()

        channels = []
        for channel in data:
            channels.append({
                "num": channel["channel_id"],
                "name": channel["name"],
                "stream_type": channel["stream_type"],
                "stream_id": channel["stream_id"],
                "stream_icon": channel["stream_icon"],
                "epg_channel_id": channel["epg_channel_id"],
                "added": None,
                "category_id": channel["category_id"],
                "tv_archive": channel["tv_archive"],
                "direct_source": channel["direct_source"],
                "tv_archive_duration": channel["tv_archive_duration"]
            })
        return channels

    def get_channel_url(self, stream_id):
        db.open()
        channel = db.get("iptv_channels", "direct_source",
                         "stream_id = {0}".format(stream_id))
        db.close()
        return channel["direct_source"]
