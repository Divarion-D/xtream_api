import requests
import utils.common as common
from utils.db import *
import config as cfg

qb = QueryBuilder(DataBase(), "data.db")

def get_all_categories():
    genres = qb.select("video_categories").all()
    if not genres:
        genres_data = requests.get(cfg.PROVIDER_API_URL + "/all_genres").json()
        for genre in genres_data:
            qb.insert("video_categories", {"name": genre["name"], "parent_id": 0}).go()
        genres = qb.select("video_categories").all()
    return genres
    