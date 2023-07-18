# import utils.common as common
from utils.db import QueryBuilder, DataBase
import config as cfg

qb = QueryBuilder(DataBase(), "data.db")
provider = cfg.PROVIDER_API_URL


# Function to get all films categories from the database
def get_films_categories():
    """
    "Query the database for all films categories."

    The function is named get_films_categories() and it returns the result of a query
    :return: A list of dictionaries.
    example: [{"category_id":"4","category_name":"m123","parent_id":0}]
    """
    # Query the database for all films categories
    return qb.select("films_categories").all()


def get_series_categories():
    """
    "Query the database for all series categories."

    The function is named get_series_categories() and it returns the result of a query
    :return: A list of dictionaries.
    example: [{"category_id":"4","category_name":"m123","parent_id":0}]
    """
    # Query the database for all series categories
    return qb.select("series_categories").all()


def get_all_films():
    """
    "Query the database for all films."

    The function is named get_all_films() and it returns the result of a query
    :return: A list of dictionaries.
    """
    return [
                {
                    "num": 1,
                    "name": "\u042f \u043a\u0440\u0430\u0441\u043d\u0435\u044e",
                    "title": "\u042f \u043a\u0440\u0430\u0441\u043d\u0435\u044e",
                    "year": "",
                    "stream_type": "movie",
                    "stream_id": 4,
                    "stream_icon": "https:\/\/www.themoviedb.org\/t\/p\/w600_and_h900_bestv2\/1pCx1fyB4w0tCtuhTFfMxqhiHZa.jpg",
                    "rating": 12,
                    "rating_5based": 6,
                    "added": "1660638664",
                    "category_id": "4",
                    "category_ids": [4],
                    "container_extension": "mp4",
                    "custom_sid": "",
                    "direct_source": "http:\/\/176.124.192.118:80\/play\/DXMkxo_35hRPoig0TFWxfkASgpnTIHPuFfKUMmcmUOI",
                }
            ]
