# snowball-local is a local daemon-style application that will be set up in intranet
# to receive and process events from syno service.
import urllib3
import os
import asyncio
import discord

from dotenv import load_dotenv
from bbs import BBS

class DC_Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.none()
        super().__init__(intents=intents)

    async def on_ready(self):
        bbs = BBS(self)
        await bbs.update_notify_channel()

        while True:
            await bbs.run()
            await asyncio.sleep(int(os.getenv("BBS_POLLING_INTERVAL")))

def main():
    client = DC_Client()
    client.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    # Disable SSL warning
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    # load env
    load_dotenv("conf/prod.env")

    main()
