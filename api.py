from typing import Union

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse, JSONResponse

import utils.common as common
import utils.iptv as iptv
import utils.user as user
from utils.db import DB
from utils.streamer import Streamer

db = DB()

db.open()
db.add_tables()


if db.get("users", "is_admin", 1) == None:
    print("Admin account not found")
    admin_username = input("Enter admin username: ")
    admin_password = input("Enter admin password: ")
    user.create_admin(admin_username, admin_password)

db.close()

iptv_data = iptv.M3U_Parser(common.SETTING["iptv"]["list_url"])

app = FastAPI()

# API XTREAM-CODES
############################################################################################################


@app.get("/player_api.php")
async def api(username: str, password: str, action: Union[str, None] = None):
    if username != None and password != None and action == None:
        user_data = user.auth(username, password)
        return {"user_info": user.user_info_xtream(user_data, username, password), "server_info": common.server_info()}

    if action != None:
        if action == "get_live_categories":
            return iptv_data.get_all_categories()
        elif action == "get_vod_categories":
            return {"live_streams": "ok"}
        elif action == "get_series_categories":
            return {"live_streams": "ok"}
        elif action == "get_live_streams":
            return iptv_data.get_all_channels()


@app.get("/live/{username}/{password}/{stream_id}.{ext}")
async def live(username: str, password: str, stream_id: str, request: Request, response: Response):
    print(request.client)
    url = iptv_data.get_channel_url(stream_id)
    response = StreamingResponse(
        Streamer.receive_stream(url), media_type="video/mp2t")
    response.set_cookie(key="channel_path", value=url)
    return response


@app.get("/live/{username}/{password}/{file_path:path}")
# A crutch for the work of an incomplete link to a list with video containers
async def live(username: str, password: str, file_path: str, request: Request):
    channel_path = request.cookies.get('channel_path')
    channel_path = channel_path.replace(channel_path.split("/")[-1], "")
    url = channel_path + file_path
    return StreamingResponse(Streamer.receive_stream(url), media_type="video/mp2t")


@app.get("/xmltv.php")
async def epg(username: str, password: str):
    file = open("epg.xml", "rb")
    return StreamingResponse(file, media_type="application/xml")

# API ADMIN
############################################################################################################

@app.get("/admin_auth")
async def admin_auth(username: str, password: str):
    status = user.auth(username, password)
    if status["error"] == 0:
        hash = common.gen_hash(20)
        db.open()
        db.update("users", "auth_hash", hash, "username='{0}'".format(username))
        db.close()
        response = JSONResponse(content={"status":200})
        response.set_cookie(key="auth", value=hash)
        return response
    else:
        return {"status":status["error_code"], "error_info":status["error_message"]}

if __name__ == "__main__":
    import utils.common as common
    ip = common.SETTING["server"]["ip"]
    port = common.SETTING["server"]["port"]
    uvicorn.run("api:app", host=ip, port=int(port), debug=True, reload=True)
