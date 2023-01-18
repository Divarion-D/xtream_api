from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import time
import uvicorn
import json
import iptv
from db import DB
import common
from typing import Union
from utils.streamer import Streamer

db = DB()

db.open()
db.add_tables()

# read setting.json
with open("setting.json", "r") as f:
    setting = json.load(f)

iptv_data = iptv.M3U_Parser(setting["iptv"]["list_url"])

app = FastAPI()

@app.get("/player_api.php")
async def api(username: str, password: str, action: Union[str, None] = None):
    if username != None and password != None and action == None:
        return common.auth(username, password)

    if action != None:
        if action == "get_live_categories":
            return iptv_data.get_all_categories()
        elif action == "get_vod_categories":
            return {"live_streams": setting["live_streams"]}
        elif action == "get_series_categories":
            return {"live_streams": setting["live_streams"]}
        elif action == "get_live_streams":
            return iptv_data.get_all_channels()

@app.get("/live/{username}/{password}/{stream_id}.ts")
async def live(username: str, password: str, stream_id: str, request: Request):

    url = iptv_data.get_channel_url(stream_id)
    return StreamingResponse(Streamer.receive_stream(url), media_type="video/mp2t")

if __name__ == "__main__":
    ip = input("Enter ip (default: 127.0.1.1): ")
    port = input("Enter port (default: 8000): ")
    if ip == "":
        ip = "192.168.1.1"
    if port == "":
        port = "8000"
    uvicorn.run("api:app", host=ip, port=int(port), debug=True, reload=True)
