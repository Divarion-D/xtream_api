import unittest
from unittest.mock import Mock
from unittest.mock import patch

import requests

import config as cfg  # assuming cfg is imported
import utils.iptv as iptv

m3u_obj = iptv.M3U_Parser("https://raw.githubusercontent.com/Divarion-D/xtream_api/master/tests/test.m3u")
epg_obj = iptv.EPG_Parser()

####################### M3U #######################

class TestGetM3uListKey(unittest.TestCase):
    def test_starts_with_extinf(self):
        line = "#EXTINF:-1 tvg-logo=\"http://example.com/logo.png\" group-title=\"Group Title\" tvg-id=\"123\" tvg-name=\"Channel Name\",Channel Name"
        expected_output = (1, {'stream_icon': 'http://example.com/logo.png', 'name': 'Channel Name', 'group_title': 'Group Title', 'epg_channel_id': '123'})
        list = {}
        flag = 0

        result = m3u_obj._get_m3u_list_key(line, list, flag)
        print(result)

        self.assertEqual(result, expected_output)

    def test_starts_with_extgrp(self):
        line = "#EXTGRP:Group Title"
        expected_output = (0, {'group_title': 'Group Title'})
        list = {}
        flag = 0

        result = m3u_obj._get_m3u_list_key(line, list, flag)

        self.assertEqual(result, expected_output)

    def test_starts_with_http(self):
        line = "http://example.com/live/channel1.m3u8"
        expected_output = (0, {'url': 'http://example.com/live/channel1.m3u8'})
        list = {}
        flag = 1

        result = m3u_obj._get_m3u_list_key(line, list, flag)

        self.assertEqual(result, expected_output)

class TestM3uList(unittest.TestCase):

    @patch('requests.get')
    def test_get_m3u_list_success(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'channel1\nchannel2\nchannel3\n'
        
        result = m3u_obj._get_m3u_list()
        
        self.assertEqual(result, ['channel1', 'channel2', 'channel3'])
    
    @patch('requests.get')
    def test_get_m3u_list_timeout(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout
        
        result = m3u_obj._get_m3u_list()
        
        self.assertEqual(result, [])

    @patch('requests.get')
    def test_get_m3u_list_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException('Test error')
        
        result = m3u_obj._get_m3u_list()
        
        self.assertEqual(result, [])

####################### EPG #######################

class TestGetIcon(unittest.TestCase):
    def test_single_icon(self):
        self.assertEqual(epg_obj._get_icon([{"src": "icon1.png"}]), "icon1.png")

    def test_multiple_icons(self):
        self.assertEqual(epg_obj._get_icon([{"src": "icon1.png"}, {"src": "icon2.png"}]), "icon1.png")

    def test_empty_icons(self):
        self.assertEqual(epg_obj._get_icon([]), None)


if __name__ == '__main__':
    unittest.main()