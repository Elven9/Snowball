# snowball-local is a local daemon-style application that will be set up in intranet
# to receive and process events from syno service.

import sqlite3
import requests
import urllib3
from datetime import datetime
from collections import namedtuple

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

def main():
    print("Hello from snowball-local")
    # Send a request to snowball-remote
    bbs = BBS()
    posts = bbs.get_latest_posts()
    for post in posts:
        print(f"{post.title} in {post.forum_name} at {post.create_time}")

if __name__ == "__main__":
    # Disable SSL warning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
