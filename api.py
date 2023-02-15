from typing import Union

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

import utils.common as common
import utils.iptv as iptv
import utils.user as user
import utils.video as video
from utils.db import *
from utils.streamer import Streamer
import config as cfg

qb = QueryBuilder(DataBase(), "data.db")
common.add_tables()

# Check if the admin account exists
if not qb.select("users").where([["is_admin", "=", 1]]).all():
    print("Admin account not found")
    admin_username = input("Enter admin username: ")
    admin_password = input("Enter admin password: ")
    user.create_admin(admin_username, admin_password)

iptv_data = iptv.M3U_Parser(cfg.IPTV_LIST_URL)

app = FastAPI()

# API XTREAM-CODES
############################################################################################################


@app.get("/player_api.php")
async def api(username: str, password: str, action: Union[str, None] = None):
    if username != None and password != None and action == None:
        user_data = user.auth(username, password)
        if user_data["error"] == 1:
            # return status code 401
            raise HTTPException(
                status_code=user_data["error_code"],
                detail=f"{user_data['error_message']}",
            )
        return {
            "user_info": user.user_info_xtream(user_data, username, password),
            "server_info": common.server_info(),
        }

    if action != None:
        user_data = user.auth(username, password)
        if user_data["error"] == 1:
            # return status code
            raise HTTPException(
                status_code=user_data["error_code"],
                detail=f"{user_data['error_message']}",
            )

        if action == "get_live_categories":
            return iptv_data.get_all_categories()
        elif action == "get_vod_categories":
            return video.get_all_categories()
        elif action == "get_series_categories":
            return {"live_streams": "ok"}
        elif action == "get_live_streams":
            return iptv_data.get_all_channels()
        elif action == "get_vod_streams":
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


@app.get("/live/{username}/{password}/{stream_id}.{ext}")
async def live(
    username: str, password: str, stream_id: str, request: Request, response: Response
):
    user_data = user.auth(username, password)
    if user_data["error"] == 1:
        # return status code
        raise HTTPException(
            status_code=user_data["error_code"], detail=f"{user_data['error_message']}"
        )

    url = iptv_data.get_channel_url(stream_id)
    response = StreamingResponse(Streamer.receive_stream(url), media_type="video/mp2t")
    response.set_cookie(key="channel_path", value=url)
    return response


@app.get("/live/{username}/{password}/{file_path:path}")
# A crutch for the work of an incomplete link to a list with video containers
async def live(username: str, password: str, file_path: str, request: Request):
    user_data = user.auth(username, password)
    if user_data["error"] == 1:
        # return status code
        raise HTTPException(
            status_code=user_data["error_code"], detail=f"{user_data['error_message']}"
        )

    channel_path = request.cookies.get("channel_path")
    channel_path = channel_path.replace(channel_path.split("/")[-1], "")
    url = channel_path + file_path
    return StreamingResponse(Streamer.receive_stream(url), media_type="video/mp2t")


@app.get("/xmltv.php")
async def epg(username: str, password: str):
    user_data = user.auth(username, password)
    if user_data["error"] == 1:
        # return status code
        raise HTTPException(
            status_code=user_data["error_code"], detail=f"{user_data['error_message']}"
        )

    file = open("epg.xml", "rb")
    return StreamingResponse(file, media_type="application/xml")


# API ADMIN
############################################################################################################


@app.get("/admin_auth")
async def admin_auth(username: str, password: str):
    status = user.auth(username, password)
    if status["error"] == 0:
        hash = common.gen_hash(20)
        qb.update("users", {"auth_hash": hash}).where(
            [["username", "=", username]]
        ).go()
        response = JSONResponse(content={"status": 200})
        response.set_cookie(key="auth", value=hash)
        return response
    else:
        return {"status": status["error_code"], "error_info": status["error_message"]}


if __name__ == "__main__":
    import utils.common as common

    ip = cfg.SERVER_IP
    port = cfg.SERVER_PORT
    uvicorn.run("api:app", host=ip, port=int(port), debug=True, reload=True)
