# snowball-local is a local daemon-style application that will be set up in intranet
# to receive and process events from syno service.
import urllib3
import os
import asyncio
import discord
from discord import app_commands

from dotenv import load_dotenv
from bbs import BBS

# Need to refactor this global variable ==
# [NEED to REFACTOR]
COMMANDS_EXTRAS = {}

class App_Command():
    def __init__(self, client:discord.Client) -> None:
        self.client = client
        self.tree: app_commands.CommandTree = app_commands.CommandTree(
            client, fallback_to_global=False
        )

    async def register(self):
        async for guild in self.client.fetch_guilds():
            self.tree.add_command(subscribe_to_bbs, guild=guild)
            self.tree.add_command(unsubscribe_to_bbs, guild=guild)

            await self.tree.sync(guild=guild)

@app_commands.command(
    name="sub",
    description="Subscribe to BBS Keyword / Board",
)
@app_commands.describe(
    keyword="Keyword to subscribe",
)
async def subscribe_to_bbs(interation: discord.Interaction, keyword: str):
    global COMMANDS_EXTRAS
    bbs: BBS = COMMANDS_EXTRAS["bbs"]

    await interation.response.send_message(f"Subscribed to {keyword}", ephemeral=True)

@app_commands.command(
    name="unsub",
    description="Unsubscribe to BBS Keyword / Board",
)
@app_commands.describe(
    keyword="Keyword to unsubscribe",
)
async def unsubscribe_to_bbs(interation: discord.Interaction, keyword: str):
    global COMMANDS_EXTRAS
    bbs: BBS = COMMANDS_EXTRAS["bbs"]

    print(keyword)

    await interation.response.send_message(f"Unsbscribed to {keyword}", ephemeral=True)


class DC_Client(discord.Client):
    def __init__(self):
        # intents
        intents = discord.Intents.none()
        super().__init__(
            intents=intents,
            allowed_mentions=discord.AllowedMentions(everyone=False, roles=False, users=True),
        )

        self.bbs = BBS(self)
        self.cmd = App_Command(self)

        # [NEED to REFACTOR]
        COMMANDS_EXTRAS["bbs"] = self.bbs

    async def on_ready(self):
        await self.bbs.update_notify_channel()
        await self.cmd.register()

        while True:
            await self.bbs.run()
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
