# BBS Notification
import requests
import os
import asyncio
import discord
from discord import app_commands

from datetime import datetime, timedelta
from utils import Simple_Cache
from collections import namedtuple

# Type def
BBS_Forum = namedtuple("BBS_Forum", ["id", "name"])

class BBS_Post:
    BASE_URL = "bbs.synology.inc"

    def __init__(self, post: dict) -> None:
        self.title = post["title"]
        self.brief = post["content_brief"]
        self.forum_name = post["board"]["name"]
        self.create_time = datetime.strptime(
            post["datetime"], "%Y-%m-%d %H:%M:%S")+timedelta(hours=8)

        # Internal used
        self.post_id = post["id"]
        self.forum_id = post["board"]["id"]
        self.url = f"https://{BBS_Post.BASE_URL}/forum/{
            self.forum_id}/post/{self.post_id}"

    def discord_embed(self) -> discord.Embed:
        emb = discord.Embed()
        emb.colour = discord.Colour.dark_red()
        emb.title = self.title
        emb.description = self.brief
        emb.url = self.url
        emb.add_field(name="Forum", value=self.forum_name, inline=True)
        emb.add_field(name="Create Time", value=self.create_time.strftime(
            "%Y-%m-%d %H:%M:%S"), inline=True)

        return emb


class BBS:
    BASE_URL = "bbs.synology.inc"

    def __init__(self, client: discord.Client) -> None:
        self.cache: Simple_Cache = Simple_Cache(
            os.getenv("BBS_CACHE_FILE_NAME"))
        self.client: discord.Client = client

        # Get notify channel
        self.channels: list[discord.abc.GuildChannel] = []

        # setting
        self.forum_thread_sub = [int(id) for id in os.getenv("BBS_FORUM_COMMENT_SUB").split(",")]

    async def update_notify_channel(self):
        self.channels = []
        async for guild in self.client.fetch_guilds():
            self.channels.append(discord.utils.find(
                lambda ch: ch.name == os.getenv("BBS_REPORT_CHANNEL_NAME"), await guild.fetch_channels()
            ))

    async def run(self):
        # this function will be called every 10 secs w  www
        posts = self._get_latest_posts()

        for post in posts:
            key = self._gen_forum_cache_key(post)
            if not self.cache.check_exist(key):
                self.cache.set_exist(key)
                await self._notify(post)

    async def _notify(self, post: BBS_Post):
        for ch in self.channels:
            await ch.send(embed=post.discord_embed())

    def _gen_forum_cache_key(self, post: BBS_Post) -> str:
        key = f"{post.forum_id}-{post.post_id}"
        if int(post.forum_id) in self.forum_thread_sub:
            key += f"-{post.create_time}"
        return key

    def _get_latest_posts(
        self,
        type: str = "all",
        limit: int = 5,
        skip: int = 0
    ) -> list[BBS_Post]:

        response = requests.get(
            f"https://{BBS.BASE_URL}/webapi/posts/latest?type={type}&take={limit}&skip={skip}", verify=False)
        ret = []
        for p in response.json():
            ret.append(BBS_Post(p))
        return ret
