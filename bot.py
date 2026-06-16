import discord
from discord.ext import commands
from database import Database
from cogs.plan import PlanCog

class Planbot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        super().__init__(command_prefix="!", intents=intents)

        self.db = Database()

    async def setup_hook(self):
        await self.load_extension("cogs.plan")
        guild = discord.Object(id=707177039190556683)
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync()
        events =  self.db.get_all_not_expired()
        for i in events:
          self.add_view(PlanCog.PlanView(i), message_id=i.message_id)

    async def on_ready(self):
        print(f"Bot online als {self.user}")