from typing import Union

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import StreamingResponse

import utils.common as common
import utils.iptv as iptv
from utils.db import DB
from utils.streamer import Streamer

db = DB()

db.open()
db.add_tables()


iptv_data = iptv.M3U_Parser(common.SETTING["iptv"]["list_url"])

app = FastAPI()


@app.get("/player_api.php")
async def api(username: str, password: str, action: Union[str, None] = None):
    if username != None and password != None and action == None:
        return common.auth(username, password)

    if action != None:
        if action == "get_live_categories":
            return iptv_data.get_all_categories()
        elif action == "get_vod_categories":
            return {"live_streams": "ok"}
        elif action == "get_series_categories":
            return {"live_streams": "ok"}
        elif action == "get_live_streams":
            return iptv_data.get_all_channels()


@app.get("/live/{username}/{password}/{stream_id}.ts")
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


if __name__ == "__main__":
    import utils.common as common
    ip = common.SETTING["server"]["ip"]
    port = common.SETTING["server"]["port"]
    uvicorn.run("api:app", host=ip, port=int(port), debug=True, reload=True)
