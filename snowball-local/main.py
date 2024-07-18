# snowball-local is a local daemon-style application that will be set up in intranet
# to receive and process events from syno service.

import sqlite3
import requests
import urllib3
import json
import os
import discord

from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv("prod.env")

class BBS_Post:
    BASE_URL = "bbs.synology.inc"
    def __init__(self, post: dict) -> None:
        self.title = post["title"]
        self.brief = post["content_brief"]
        self.forum_name = post["board"]["name"]
        self.create_time = datetime.strptime(post["datetime"], "%Y-%m-%d %H:%M:%S")+timedelta(hours=8)

        # Internal used
        self.post_id = post["id"]
        self.forum_id = post["board"]["id"]
        self.url = f"https://{BBS_Post.BASE_URL}/forum/{self.forum_id}/post/{self.post_id}"

    def discord_embed(self) -> discord.Embed:
        emb = discord.Embed()
        emb.colour = discord.Colour.dark_red()
        emb.title = self.title
        emb.description = f"{self.brief}..."
        emb.url = self.url
        emb.add_field(name="Forum", value=self.forum_name, inline=True)
        emb.add_field(name="Create Time", value=self.create_time.strftime("%Y-%m-%d %H:%M:%S"), inline=True)

        return emb

class BBS:
    BASE_URL = "bbs.synology.inc"
    def __init__(self) -> None:
        # init sqlite storage
        # self.db = sqlite3.connect("bbs.db")
        pass

    def get_latest_posts(self,
                         type: str = "all",
                         limit: int = 60,
                         skip: int = 0
                        ) -> list[BBS_Post]:

        response = requests.get(
            f"https://{BBS.BASE_URL}/webapi/posts/latest?type={type}&take={limit}&skip={skip}", verify=False)
        ret = []
        for p in response.json():
            ret.append(BBS_Post(p))
        return ret

class DC_Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.none()
        super().__init__(intents=intents)

    async def on_ready(self):
        bbs = BBS()
        posts = bbs.get_latest_posts()

        print(f"Logged in as {self.user}")

        async for guild in self.fetch_guilds():
            print(f"Connected to {guild.name}")

            channels = await guild.fetch_channels()
            for channel in channels:
                if channel.name == os.getenv("BBS_REPORT_CHANNEL_NAME"):
                    print(f"Found channel {channel.name}")
                    await channel.send("", embed=posts[0].discord_embed())

def main():
    print("Starting snowball-local")

    client = DC_Client()
    client.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    # Disable SSL warning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
