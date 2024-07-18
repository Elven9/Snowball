# snowball-local is a local daemon-style application that will be set up in intranet
# to receive and process events from syno service.

import sqlite3
import requests
import urllib3
import json
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv("prod.env")

class BBS_Post:
    BASE_URL = "bbs.synology.inc"
    def __init__(self, post: dict) -> None:
        self.title = post["title"]
        self.brief = post["content_brief"]
        self.forum_name = post["board"]["name"]
        self.create_time = datetime.strptime(post["datetime"], "%Y-%m-%d %H:%M:%S")

        # Internal used
        self.post_id = post["id"]
        self.forum_id = post["board"]["id"]
        self.url = f"https://{BBS_Post.BASE_URL}/forum/{self.forum_id}/post/{self.post_id}"

class BBS:
    BASE_URL = "bbs.synology.inc"
    def __init__(self) -> None:
        # init sqlite storage
        # self.db = sqlite3.connect("bbs.db")
        pass

    def get_latest_posts(self, type: str = "all", limit: int = 60, skip: int = 0):
        response = requests.get(
            f"https://{BBS.BASE_URL}/webapi/posts/latest?type={type}&take={limit}&skip={skip}", verify=False)
        ret = []
        for p in response.json():
            ret.append(BBS_Post(p))
        return ret

def dc_api(method, endpoint, data):
    # send to dc endpoints
    url = "https://discord.com/api/v10/"
    req = requests.Request(
        method=method,
        url=url + endpoint,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bot {os.getenv('DISCORD_TOKEN')}",
        }
    )
    if data:
        req.json = data
    s = requests.Session()
    prepped = s.prepare_request(req)
    return s.send(prepped)

def main():
    print("Hello from snowball-local")

    resp = dc_api("POST", f"channels/{os.getenv('BBS_REPORT_CHANNEL')}/messages", {
        "content": "Hello from snowball-local again :)"
    })
    print(resp.status_code)
    print(resp.text)

if __name__ == "__main__":
    # Disable SSL warning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
