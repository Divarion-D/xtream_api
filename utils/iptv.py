import datetime
import gzip
import os
import re
import time
import urllib.request
import aiohttp

import requests

import config as cfg
import utils.common as common
import utils.xmltv as xmltv
from utils.db import *

qb = QueryBuilder(DataBase(), "data.db")


class M3U_Parser:
    def __init__(self, m3u_url):
        self.m3u_url = m3u_url
        self.m3u_list = self._get_m3u_list()
        channels_lupd = common.get_setting_db("chenel_lupd")
        channels_lupd = int(channels_lupd) if channels_lupd != "" else 0
        if channels_lupd < int(time.time()) - cfg.IPTV_UPD_INTERVAL_LIST:
            # clear channels
            qb.delete("iptv_channels")
            # clear categories
            qb.delete("iptv_categories")
            self.parse_m3u()
            common.set_setting_bd("chenel_lupd", int(time.time()))

    def _get_m3u_list(self):
        """
        It takes a URL, makes a request to that URL, and returns the response as a list of strings
        :return: A list of strings
        """
        timeout = 30
        try:
            request = requests.get(self.m3u_url, timeout=timeout)
            if request.status_code == 200:
                return request.text.splitlines()
            else:
                print("Error get m3u list")
                return []
        except requests.exceptions.Timeout:
            print("Playlist request timeout")
            return []
        except requests.exceptions.RequestException as e:
            print(e)
            return []
            
    def _get_m3u_list_key(self, line, list, flag):
        """
        It takes a line from a m3u file, checks if it starts with #EXTINF: or #EXTGRP: or http, and if
        it does, it extracts the relevant information from the line and returns it in a dictionary
        
        :param line: The line of the m3u file
        :param list: This is the list that will be returned
        :param flag: This is a flag that is used to check if the line starts with #EXTINF:
        :return: The flag and the list.
        """
        # Check if the line starts with #EXTINF:
        if line.startswith("#EXTINF:"):
            flag = 1
            # Get the stream icon
            list["stream_icon"] = (
                re.search('tvg-logo="(.+?)"', line)[1].strip()
                if "tvg-logo" in line
                else ""
            )
            # Get the name
            list["name"] = (
                re.search('tvg-name="(.+?)"', line)[1].strip()
                if "tvg-name" in line
                else re.search(",(.+)", line)[1].strip()
            )
            # Get the group title
            list["group_title"] = (
                re.search('group-title="(.+?)"', line)[1].strip()
                if "group-title" in line
                else ""
            )
            # Get the epg channel id
            list["epg_channel_id"] = (
                re.search('tvg-id="(.+?)"', line)[1].strip()
                if "tvg-id" in line
                else ""
            )
            # Uncomment the following lines to get the other values
            # list["tvg_shift"] = re.search('tvg-shift="(.+?)"', line).group(1) if 'tvg-shift' in line else None
            # list["tvg_url"] = re.search('tvg-url="(.+?)"', line).group(1) if 'tvg-url' in line else None
            # list["tvg_rec"] = re.search('tvg-rec="(.+?)"', line).group(1) if 'tvg-rec' in line else None
            # list["tvg_chno"] = re.search('tvg-chno="(.+?)"', line).group(1) if 'tvg-chno' in line else None
            # list["tvg_epg"] = re.search('tvg-epg="(.+?)"', line).group(1) if 'tvg-epg' in line else None
            # list["tvg_radio"] = re.search('tvg-radio="(.+?)"', line).group(1) if 'tvg-radio' in line else None
        # Check if the line starts with #EXTGRP:
        elif line.startswith("#EXTGRP:"):
            list["group_title"] = re.search("#EXTGRP:(.+)", line)[1]
        # Check if the line starts with http
        elif line.startswith("http"):
            list["url"] = line
            flag = 0
        return flag, list

    def parse_m3u(self):
        """
        It parses an M3U file and inserts the data into a database
        """
        print("Parsing M3U file...")
        data_list = {}
        flag = 1
        for line in self.m3u_list:
            flag, data_list = self._get_m3u_list_key(line, data_list, flag)
            if flag == 0 and data_list:
                # remove '
                data_list["name"] = data_list["name"].replace("'", "")
                print("Update:" + data_list["name"])
                # check if category exists
                if "group_title" in data_list and (
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
        return qb.select("iptv_categories").all()

    def get_all_channels(self):
        """
        It returns a list of dictionaries, each dictionary containing the following keys: num, name,
        stream_type, stream_id, stream_icon, epg_channel_id, added, category_id, tv_archive,
        direct_source, tv_archive_duration
        :return: A list of dictionaries.
        """
        data = qb.select("iptv_channels").all()

        return [
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
            for channel in data
        ]

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
        self.epg_channel = []
        self.epg_channel_id = []
        self.epg_program = []
        xmltv.locale = "Latin-1"
        xmltv.date_format = "%Y%m%d%H%M%S %Z"

    def _get_icon(self, icons=None):
        """
        It returns the first icon in the list of icons.
        
        :param icons: This is a list of dictionaries. Each dictionary contains the src key, which is the URL
        of the icon
        :return: A list of dictionaries.
        """
        if not icons:
            return None
        chanel_icon = icons[0]["src"]
        # if icon count is more than 1
        if len(icons) > 1:
            for icon in icons:
                chanel_icon = icon["src"]
                break
        return chanel_icon
    
    def download_epg(self, files):
        """
        Downloads epg files from given list of URLs
        
        :param files: A list of URLs to download the EPG files from
        :return: A list of file paths to the downloaded epg files.
        """
        """Downloads epg files from given list of URLs"""
        opener=urllib.request.build_opener()
        opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
        urllib.request.install_opener(opener)

        epg_file = []
        # Create epg folder if it doesn't exist
        if not os.path.exists(os.path.join("./temp/epg")):
            os.makedirs(os.path.join("./temp/epg"))
        for file in files:
            # Download file
            print(f"Downloading EPG file: {file}")
            urllib.request.urlretrieve(file, os.path.join("./temp/epg", os.path.basename(file)))
            file = os.path.join("./temp/epg", os.path.basename(file))
            # Unzip file if it is a .gz archive
            if file.split(".")[-1] == "gz":
                print(f"Unzipping EPG file: {file}")
                new_name = common.gen_hash(5) + ".xml"
                with gzip.open(file, "rb") as f_in:
                    with open(os.path.join("./temp/epg", new_name), "wb") as f_out:
                        f_out.write(f_in.read())
                # Remove arhive
                os.remove(file)
                epg_file.append(os.path.join("./temp/epg", new_name))
        return epg_file

    def parse_channel(self, channel, channels_db):
        """
        It takes a channel from the XMLTV file and a list of channels from the database, and returns the
        channel name, channel ID, channel database entry, and channel icon
        
        :param channel: The channel to parse
        :param channels_db: A list of dictionaries containing the channel name and ID
        :return: The name, id, channel_db, and icon are being returned.
        """
        for channel_db in channels_db:
            for chanel_name in channel["display-name"]:
                if chanel_name["name"] == channel_db["name"]:
                    # Return the channel name, id, db and icon
                    return chanel_name, channel["id"], channel_db, self._get_icon(channel["icon"])
        # If no match is found, return None
        return None, None, None, None
        
    def parse_programme(self, programmes):
        """
        The function iterates through each programme in the list of programmes and checks if the channel
        of the programme is in the list of epg_channel_ids. If it is, the programme is appended to the
        list of epg_programmes
        
        :param programmes: This is the list of programmes that we are iterating through
        """
        # Iterate through each programme in the list of programmes
        for programme in programmes:
            # Check if the channel of the programme is in the list of epg_channel_ids
            if programme["channel"] in self.epg_channel_id:
                # Append the programme to the list of epg_programmes
                self.epg_program.append(programme)

    def write_epg(self):
        """
        It writes the EPG data to a file.
        """
        # Generate date formatt "20030811003608 -0300"
        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S %Z")
        # Create an XMLTV writer object
        w = xmltv.Writer(
            encoding="us-ascii",
            date=date,
            # source_info_url="http://www.funktronics.ca/python-xmltv",
            # source_info_name="Funktronics",
            # generator_info_name="python-xmltv",
            # generator_info_url="http://www.funktronics.ca/python-xmltv",
        )
        # Add channels to the writer
        for c in self.epg_channel:
            w.addChannel(c)
        # Add programs to the writer
        for p in self.epg_program:
            w.addProgramme(p)
        # Write the XMLTV file
        w.write(cfg.IPTV_EPG_LIST_OUT, pretty_print=True)

    def parse_xml(self):
        """
        It downloads the EPG files, parses them, and writes the output to a new file.
        """
        # Create a temporary folder
        common.create_temp_folder()
        # Get the list of EPG files to be parsed
        files = self.download_epg(cfg.IPTV_EPG_LIST_IN)
        #files = ["./temp/epg/fnkuo.xml"]
        # Get all channels from the database
        channels_db = qb.select("iptv_channels").all()
        # Iterate through each file
        for file in files:
            print(f"Parsing EPG file: {file}")
            # Read the channels and programmes from the file
            chanels = xmltv.read_channels(open(file, "r"))
            programmes = xmltv.read_programmes(open(file, "r"))
            print("Parsing channels...")
            # Iterate through each channel
            for channel in chanels:
                # Parse the channel
                chanel_name, channel_id, channel_db, icon = self.parse_channel(channel, channels_db)
                # If the channel is valid
                if channel_id:
                    # Remove the data from the channels_db
                    channels_db.remove(channel_db)
                    # Update the channel in the database
                    qb.update("iptv_channels", {"epg_channel_id": channel_id, "stream_icon": icon}).where([["name", "=", chanel_name["name"]]]).go()
                    # Append the channel to the epg_channel list
                    self.epg_channel.append(channel)
                    # Append the channel_id to the epg_channel_id list
                    self.epg_channel_id.append(channel_id)
            print("Parsing programmes...")
            # Parse the programmes
            self.parse_programme(programmes)
            # Remove epg files
            os.remove(os.path.join("./temp/epg", os.path.basename(file)))
        print("Writing XML file...")
        # Write the EPG file
        self.write_epg()


class Help_iptv:
    @staticmethod
    async def receive_stream(url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                async for dataBytes in response.content.iter_chunked(1024):
                    yield dataBytes