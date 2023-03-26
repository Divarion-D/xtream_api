import string
import unittest

import config as cfg  # assuming cfg is imported
import utils.common as common

server_info_data = common.server_info()


class TestServerInfo(unittest.TestCase):
    def test_url(self):
        self.assertEqual(
            server_info_data["url"], f"http://{cfg.SERVER_IP}:{cfg.SERVER_PORT}"
        )

    def test_port(self):
        self.assertEqual(server_info_data["port"], str(cfg.SERVER_PORT))

    def test_https_port(self):
        self.assertEqual(server_info_data["https_port"], "8000")

    def test_rtmp_port(self):
        self.assertEqual(server_info_data["rtmp_port"], "8000")

    def test_server_protocol(self):
        self.assertEqual(server_info_data["server_protocol"], "http")

    def test_timestamp_now(self):
        self.assertIsInstance(server_info_data["timestamp_now"], float)

    def test_time_now(self):
        self.assertIsInstance(server_info_data["time_now"], str)

    def test_timezone(self):
        self.assertEqual(server_info_data["timezone"], "")


class TestGenHash(unittest.TestCase):
    def test_default_length(self):
        self.assertEqual(len(common.gen_hash()), 32)

    def test_custom_length(self):
        self.assertEqual(len(common.gen_hash(16)), 16)
        self.assertEqual(len(common.gen_hash(8)), 8)

    def test_lowercase_letters_only(self):
        for char in common.gen_hash():
            self.assertIn(char, string.ascii_lowercase)


if __name__ == "__main__":
    unittest.main()
