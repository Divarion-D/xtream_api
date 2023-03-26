import requests
import utils.common as common
from utils.db import *
import config as cfg

qb = QueryBuilder(DataBase(), "data.db")

def get_all_categories():
    """Retrieve all video categories from the provider API and store them in the database"""
    # Get existing genres from the database
    genres = qb.select("video_categories").all()
     # If there are no genres in the database, fetch them from the provider API
    if not genres:
        genres_data = requests.get(f"{cfg.PROVIDER_API_URL}/all_genres").json()
        for genre in genres_data:
            qb.insert("video_categories", {"name": genre["name"], "parent_id": 0}).go()
        genres = qb.select("video_categories").all()
    return genres
    