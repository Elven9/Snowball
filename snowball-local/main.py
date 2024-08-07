# snowball-local is a local daemon-style application that will be set up in intranet
# to receive and process events from syno service.
import urllib3
import os
import asyncio
import discord
import logging

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

    bbs.add_keyword(interation.user.id, keyword)
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

    bbs.remove_keyword(interation.user.id, keyword)
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

        # Task
        self.task = None

    async def on_ready(self):
        await self.bbs.update_notify_channel()
        await self.cmd.register()

        if not self.task is None:
            self.task.cancel()

        try:
            async with asyncio.TaskGroup() as tg:
                self.task = tg.create_task(self._task_bbs())
        except asyncio.CancelledError:
            pass

    async def _task_bbs(self):
        while True:
            try:
                await self.bbs.run()
            except Exception as e:
                print(e)
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
