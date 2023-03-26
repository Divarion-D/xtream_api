import re
import time
import config as cfg

import requests
import gzip
import shutil
import os

import utils.common as common
import utils.xmltv as xmltv
from utils.db import *

qb = QueryBuilder(DataBase(), "data.db")


class M3U_Parser:
    def __init__(self, m3u_url):
        self.m3u_url = m3u_url
        self.m3u_list = self.get_m3u_list()
        channels_lupd = common.get_setting_db("chenel_lupd")
        channels_lupd = int(channels_lupd) if channels_lupd != "" else 0
        if channels_lupd < int(time.time()) - cfg.IPTV_UPD_INTERVAL_LIST:
            # clear channels
            qb.delete("iptv_channels")
            # clear categories
            qb.delete("iptv_categories")
            self.parse_m3u()
            common.set_setting_bd("chenel_lupd", int(time.time()))

    def get_m3u_list(self):
        return requests.get(self.m3u_url).text.splitlines()

    def parse_m3u(self):
        """
        It parses an M3U file and inserts the data into a database
        """
        print("Parsing M3U file...")
        data_list = {}
        cnl = 1
        for line in self.m3u_list:
            if line.startswith("#EXTINF:"):
                cnl = 1
                data_list["stream_icon"] = (
                    re.search('tvg-logo="(.+?)"', line).group(1).strip()
                    if "tvg-logo" in line
                    else ""
                )
                data_list["name"] = (
                    re.search('tvg-name="(.+?)"', line).group(1).strip()
                    if "tvg-name" in line
                    else re.search(",(.+)", line).group(1).strip()
                )
                data_list["group_title"] = (
                    re.search('group-title="(.+?)"', line).group(1).strip()
                    if "group-title" in line
                    else ""
                )
                data_list["epg_channel_id"] = (
                    re.search('tvg-id="(.+?)"', line).group(1).strip()
                    if "tvg-id" in line
                    else ""
                )
                # data_list["tvg_shift"] = re.search('tvg-shift="(.+?)"', line).group(1) if 'tvg-shift' in line else None
                # data_list["tvg_url"] = re.search('tvg-url="(.+?)"', line).group(1) if 'tvg-url' in line else None
                # data_list["tvg_rec"] = re.search('tvg-rec="(.+?)"', line).group(1) if 'tvg-rec' in line else None
                # data_list["tvg_chno"] = re.search('tvg-chno="(.+?)"', line).group(1) if 'tvg-chno' in line else None
                # data_list["tvg_epg"] = re.search('tvg-epg="(.+?)"', line).group(1) if 'tvg-epg' in line else None
                # data_list["tvg_radio"] = re.search('tvg-radio="(.+?)"', line).group(1) if 'tvg-radio' in line else None
            elif line.startswith("#EXTGRP:"):
                data_list["group_title"] = re.search("#EXTGRP:(.+)", line).group(1)
            elif line.startswith("http"):
                data_list["url"] = line
                cnl = 0

            if cnl == 0 and data_list:
                # remove '
                data_list["name"] = data_list["name"].replace("'", "")

                print("Update:" + data_list["name"])
                if "group_title" in data_list:
                    # check if category exists
                    if (
                        not qb.select("iptv_categories")
                        .where([["category_name", "=", data_list["group_title"]]])
                        .one()
                    ):
                        qb.insert(
                            "iptv_categories",
                            {"category_name": data_list["group_title"], "parent_id": 0},
                        ).go()
                # check if channel exists
                if (
                    not qb.select("iptv_channels")
                    .where([["name", "=", data_list["name"]]])
                    .one()
                ):
                    # get category id
                    category_id = (
                        qb.select("iptv_categories")
                        .where([["category_name", "=", data_list["group_title"]]])
                        .one()["category_id"]
                    )
                    # insert channel
                    insert_id = qb.insert(
                        "iptv_channels",
                        {
                            "name": data_list["name"],
                            "stream_type": "live",
                            "direct_source": data_list["url"],
                            "stream_icon": data_list["stream_icon"],
                            "epg_channel_id": data_list["epg_channel_id"],
                            "category_id": category_id,
                        },
                    ).go()
                    # update stream_id
                    qb.update("iptv_channels", {"stream_id": insert_id - 1}).where(
                        [["channel_id", "=", insert_id]]
                    ).go()
                data_list = {}

    def get_all_categories(self):
        """
        It returns all the categories from the database
        :return: A list of all the categories in the database.
        """
        categories = qb.select("iptv_categories").all()
        return categories

    def get_all_channels(self):
        """
        It returns a list of dictionaries, each dictionary containing the following keys: num, name,
        stream_type, stream_id, stream_icon, epg_channel_id, added, category_id, tv_archive,
        direct_source, tv_archive_duration
        :return: A list of dictionaries.
        """
        data = qb.select("iptv_channels").all()

        channels = []
        for channel in data:
            channels.append(
                {
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
                    "tv_archive_duration": channel["tv_archive_duration"],
                }
            )
        return channels

    def get_channel_url(self, stream_id):
        """
        It takes a stream_id as an argument, and returns the direct_source of the channel with that
        stream_id

        :param stream_id: The stream ID of the channel you want to get the URL for
        :return: A dictionary with the key "direct_source" and the value of the channel url.
        """
        channel = (
            qb.select("iptv_channels").where([["stream_id", "=", stream_id]]).one()
        )
        return channel["direct_source"]


class EPG_Parser:
    def __init__(self):
        self.epg = {}
        xmltv.locale = "Latin-1"
        xmltv.date_format = "%Y%m%d%H%M%S %Z"

    def _get_icon(self, icons):
        if len(icons) == 1:
            chanel_icon = icons[0]["src"]
        else:
            # if icon count is more than 1
            for icon in icons:
                chanel_icon = icon["src"]
                break
        return chanel_icon

    def parse_xml(self):
        files = cfg.IPTV_EPG_LIST_IN

        common.create_temp_folder()

        # for file in files:
        # # create epg folder
        # if not os.path.exists("./temp/epg"):
        #     os.makedirs("./temp/epg")

        # # download file
        # get_file = requests.get(file)
        # with open("./temp/epg/" + file.split("/")[-1], "wb") as f:
        #     f.write(get_file.content)
        # file = "./temp/epg/" + file.split("/")[-1]

        # # unzip file
        # new_name = common.gen_hash(5) + ".xml"
        # if file.split(".")[-1] in "gz":
        #     with gzip.open(file, "rb") as f_in:
        #         with open("./temp/epg/" + new_name, "wb") as f_out:
        #             shutil.copyfileobj(f_in, f_out)
        #     # remove arhive
        #     os.remove(file)
        #     file = "./temp/epg/" + new_name

        # parse xml
        # chanels = xmltv.read_channels(open('./temp/epg/qmqev.xml', "r"))
        # programmes = xmltv.read_programmes(open('./temp/epg/qmqev.xml', "r"))

        chanels = xmltv.read_channels(open("./temp/epg/jhija.xml", "r"))

        # get all channels name in db
        channels_db = qb.select("iptv_channels").all()

        i = 0

        for channel in chanels:
            # get channel id from db
            channel_id = None
            for channel_db in channels_db:
                for chanel_name in channel["display-name"]:
                    if chanel_name["name"] == channel_db["name"]:
                        channel_id = channel["id"]
                        # if icon count is 1
                        icon = self._get_icon(channel["icon"])
                        break
                else:
                    # Continue if the inner loop wasn't broken.
                    continue
                # Inner loop was broken, break the outer.
                break

            if channel_id:
                self.epg[i] = {}
                self.epg[i]["chanel_id"] = channel_id
                self.epg[i]["name_db"] = channel_db["name"]
                self.epg[i]["id_db"] = channel_db["channel_id"]
                self.epg[i]["icon"] = icon
                self.epg[i]["programmes"] = []
                i += 1
        print(self.epg)
