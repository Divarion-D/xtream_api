import asyncio
import time
from concurrent.futures import ProcessPoolExecutor
from typing import Union

import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse, StreamingResponse

import config as cfg
import utils.common as common
import utils.user as user
import utils.video as video
from helper.clients import Client
from helper.db import DataBase, QueryBuilder
from helper.iptv import EPG_Parser, Help_iptv, M3U_Parser

qb = QueryBuilder(DataBase(), "data.db")
common.add_tables()

# Check if the admin account exists
if not qb.select("users").where([["is_admin", "=", 1]]).all():
    print("Admin account not found")
    admin_username = input("Enter admin username: ")
    admin_password = input("Enter admin password: ")
    user.create_admin(admin_username, admin_password)

iptv_data = M3U_Parser(cfg.IPTV_LIST_URL)
tvepg = EPG_Parser()

app = FastAPI()

CLIENT = Client()


def update():
    while True:
        time.sleep(10)
        asyncio.run(iptv_data.upd_playlist())
        asyncio.run(tvepg.upd_epg())


@app.on_event("startup")
async def on_startup():
    app.state.executor = ProcessPoolExecutor()
    app.state.loop = asyncio.get_event_loop()
    app.state.loop.run_in_executor(app.state.executor, update)


@app.on_event("shutdown")
async def on_shutdown():
    app.state.executor.shutdown()

# API XTREAM-CODES
############################################################################################################


@app.get("/player_api.php")
async def api(username: str, password: str, action: Union[str, None] = None):
    if username is not None and password is not None and action is None:
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

    if action is not None:
        user_data = user.auth(username, password)
        if user_data["error"] == 1:
            # return status code
            raise HTTPException(
                status_code=user_data["error_code"],
                detail=f"{user_data['error_message']}",
            )

        if action == "get_live_categories":
            return iptv_data.get_all_categories()
        elif action == "get_live_streams":
            return iptv_data.get_all_channels()
        elif action == "get_vod_categories":
            return video.get_films_categories()
        elif action == "get_series_categories":
            return video.get_series_categories()
        elif action == "get_vod_streams":
            return video.get_all_films()


@app.get("/live/{username}/{password}/{stream_id}.{ext}")
async def live(username: str, password: str, stream_id: str, ext: str, request: Request, response: Response):
    print("live")
    user_data = user.auth(username, password)
    if user_data["error"] == 1:
        # return status code
        raise HTTPException(
            status_code=user_data["error_code"], detail=f"{user_data['error_message']}"
        )

    stream_url = iptv_data.get_channel_url(stream_id)
    if stream_url is None:
        stream_url = CLIENT.get_client(request.client.host, str(request.client.port))
        if stream_url is not False:
            stream_url = stream_url.replace(stream_url.split("/")[-1], "")
            stream_url = stream_url + stream_id + "." + ext
            query_param = request.query_params._dict
            if query_param:
                for key, value in query_param.items():
                    stream_url += "?" + key + "=" + value
    else:
        CLIENT.remove_client()

    if stream_url is False:
        raise HTTPException(status_code=404, detail="Stream not found")

    CLIENT.add_client(request.client.host, str(request.client.port), stream_url)
    response = StreamingResponse(Help_iptv.receive_stream(stream_url), media_type="video/mp2t")
    return response


@app.get("/live/{username}/{password}/{file_path:path}")
# A crutch for the work of an incomplete link to a list with video containers
async def live_container(username: str, password: str, file_path: str, request: Request):
    print("container")
    user_data = user.auth(username, password)
    if user_data["error"] == 1:
        # return status code
        raise HTTPException(
            status_code=user_data["error_code"], detail=f"{user_data['error_message']}"
        )

    stream_url = CLIENT.get_client(request.client.host, str(request.client.port))
    stream_url = stream_url.replace(stream_url.split("/")[-1], "")
    stream_url = stream_url + file_path

    return StreamingResponse(Help_iptv.receive_stream(stream_url), media_type="video/mp2t")


@app.get("/xmltv.php")
async def epg(username: str, password: str):
    user_data = user.auth(username, password)
    if user_data["error"] == 1:
        # return status code
        raise HTTPException(
            status_code=user_data["error_code"], detail=f"{user_data['error_message']}"
        )

    file = open(cfg.IPTV_EPG_LIST_OUT, "rb")
    return StreamingResponse(file, media_type="application/xml")


# API ADMIN
############################################################################################################


@app.get("/admin_auth")
async def admin_auth(username: str, password: str):
    status = user.auth(username, password)
    if status["error"] != 0:
        return {"status": status["error_code"], "error_info": status["error_message"]}
    hash = common.gen_hash(20)
    qb.update("users", {"auth_hash": hash}).where(
        [["username", "=", username]]
    ).go()
    response = JSONResponse(content={"status": 200})
    response.set_cookie(key="auth", value=hash)
    return response


if __name__ == "__main__":
    import utils.common as common

    ip = cfg.SERVER_IP
    port = cfg.SERVER_PORT

    uvicorn.run("api:app", host=ip, port=int(port), log_level=cfg.LOG_LEVEL, reload=True)
