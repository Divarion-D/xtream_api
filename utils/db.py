import sqlite3


class DB:
    def __init__(self):
        self.db = None
        self.cursor = None

    def open(self):
        try:
            self.db = sqlite3.connect("data.db")
            self.db.row_factory = self.dict_factory
            self.cursor = self.db.cursor()
        except sqlite3.Error as e:
            print("Error connecting to database!")

    def add_tables(self):
        # create table settings
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS settings ("setting_id" INTEGER PRIMARY KEY AUTOINCREMENT, "setting_name" TEXT, "setting_value" TEXT)''')
        # create table iptv_categories
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS iptv_categories ("category_id" INTEGER PRIMARY KEY AUTOINCREMENT, "category_name" TEXT, "parent_id" INTEGER)''')
        # create table iptv_channels
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS iptv_channels ("channel_id" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT, "stream_type" TEXT, "stream_id" INTEGER, "stream_icon" TEXT, "epg_channel_id" TEXT, "category_id" TEXT, "tv_archive" TEXT DEFAULT NULL, "direct_source" TEXT, "tv_archive_duration" TEXT)''')
        # create table iptv_epg
        self.cursor.execute(
            '''CREATE TABLE IF NOT EXISTS iptv_epg ("epg_id" INTEGER PRIMARY KEY AUTOINCREMENT, "channel_id" INTEGER)''')

    def insert(self, table, columns, data):
        query = "INSERT INTO {0} {1} VALUES {2};".format(table, columns, data)
        self.cursor.execute(query)
        self.db.commit()
        return self.cursor.lastrowid

    def delete(self, table, condition):
        query = "DELETE FROM {0} WHERE {1};".format(table, condition)
        self.cursor.execute(query)
        self.db.commit()

    def delete_all(self, table):
        query = "DELETE FROM {0};".format(table)
        self.cursor.execute(query)
        self.db.commit()

    def get(self, table, column, condition=None):
        if condition == None:
            query = "SELECT {0} FROM {1};".format(column, table)
        else:
            query = "SELECT {0} FROM {1} WHERE {2};".format(
                column, table, condition)
        self.cursor.execute(query)
        return self.cursor.fetchone()

    def get_all(self, table, column, condition=None):
        if condition == None:
            query = "SELECT {0} FROM {1};".format(column, table)
        else:
            query = "SELECT {0} FROM {1} WHERE {2};".format(
                column, table, condition)
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update(self, table, column, data, condition):
        query = "UPDATE {0} SET {1} = '{2}' WHERE {3};".format(
            table, column, data, condition)
        self.cursor.execute(query)
        self.db.commit()

    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def get_setting(self, setting_name):
        # check if setting exists
        if self.get("settings", "setting_name", "setting_name = '{0}'".format(setting_name)) == None:
            # setting does not exist, create it
            self.insert("settings", "(setting_name, setting_value)",
                        "('{0}', '')".format(setting_name))
        # return setting value
        return self.get("settings", "setting_value", "setting_name = '{0}'".format(setting_name))["setting_value"]

    def set_setting(self, setting_name, setting_value):
        # check if setting exists
        if self.get("settings", "setting_name", "setting_name = '{0}'".format(setting_name)) == None:
            # setting does not exist, create it
            self.insert("settings", "(setting_name, setting_value)",
                        "('{0}', '{1}')".format(setting_name, setting_value))
        else:
            # setting exists, update it
            self.cursor.execute("UPDATE settings SET setting_value = '{0}' WHERE setting_name = '{1}'".format(
                setting_value, setting_name))
            self.db.commit()

    def close(self):
        self.db.commit()
        self.db.close()
