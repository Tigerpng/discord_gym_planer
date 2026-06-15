import discord
from discord import app_commands
from discord.ext import commands
from typing import List
import datetime as dt
from models.event import *

WEEKDAYS = [
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag"
]


# ----------------------------
# Utils
# ----------------------------
def parse_list(value: str) -> List[str]:
    return value.split(",") if value else []


def validate_date(date: str) -> bool:
    try:
      year =  dt.datetime.today().year
      date =  date + "." + str(year)
      day = dt.datetime.strptime(date ,'%d.%m.%Y')
      return True
    except:
        return False

def validate_time(time: str) -> bool:
    try:
        h, m = map(int, time.split(":"))
        return 0 <= h <= 23 and 0 <= m <= 59
    except:
        return False


# ----------------------------
# Core Renderer (NO STATE)
# ----------------------------
class PlanRenderer:
    @staticmethod
    def build(event):

        participants = [
            p.name
            for p in event.participants()
        ]

        drivers = [
            p.name
            for p in event.participants()
            if p.driver
        ]

        embed = discord.Embed(
            title=f"📅 Termin für {WEEKDAYS[event.date.weekday()]}",
            description=(
                f"**Zeit:** {event.time.strftime('%H:%M')} Uhr\n"
                f"**Datum:** {event.date.strftime('%d.%m.%Y')}"
            ),
            color=0x00AAFF
        )

        embed.add_field(
            name="👍 Teilnehmer:",
            value="\n".join(participants) if participants else "-",
            inline=False
        )

        embed.add_field(
            name="🚗 Fahrer:",
            value="\n".join(drivers) if drivers else "-",
            inline=False
        )

        return embed


# ----------------------------
# Cog
# ----------------------------
class PlanCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ---------------- Slash Command ----------------
    @app_commands.command(name="plan", description="Erstellt Termin")
    async def plan(self, interaction: discord.Interaction, date: str, time: str):

        if not validate_date(date):
            return await interaction.response.send_message("❌ Datum falsch (dd.mm)", ephemeral=True)

        if not validate_time(time):
            return await interaction.response.send_message("❌ Zeit falsch (HH:MM)", ephemeral=True)

        year =  dt.datetime.today().year
        date =  date + "." + str(year)
        new_date = dt.datetime.strptime(date ,'%d.%m.%Y')

        new_time = dt.datetime.strptime(time ,'%H:%M')

        event = self.bot.db.create_event(interaction.channel_id, new_date, new_time)

        embed = PlanRenderer.build(event)

        view = self.PlanView(event)

        msg = await interaction.channel.send(embed=embed, view=view)

        self.bot.db.update_message(event.id, msg.id)

        await interaction.response.send_message("✅ erstellt", ephemeral=True)

    # ---------------- PERSISTENT VIEW ----------------
    class PlanView(discord.ui.View):
        def __init__(self, event):
            super().__init__(timeout=None)
            self.event_id = event.id

        # ---------------- Resolver ----------------
        def get_data(self, bot):
            return bot.db.get_event(self.event_id)

        def save(self, bot, participants, drivers):
            bot.db.update(self.event_id, participants, drivers)

        async def refresh(self, interaction):
        
            bot = interaction.client

            event = self.get_data(bot)

            await interaction.response.edit_message(
                embed=PlanRenderer.build(event),
                view=self
            )

        # ---------------- BUTTONS ----------------

        @discord.ui.button(
            emoji="👍",
            style=discord.ButtonStyle.success,
            custom_id="plan:join"
        )
        async def join(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):

            bot = interaction.client

            bot.db.join_event(
                self.event_id,
                interaction.user.name
            )

            await self.refresh(interaction)


        @discord.ui.button(
            emoji="🚗",
            style=discord.ButtonStyle.primary,
            custom_id="plan:driver"
        )
        async def driver(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):

            bot = interaction.client

            bot.db.toggle_driver(
                self.event_id,
                interaction.user.name
            )

            await self.refresh(interaction)

        @discord.ui.button(
            emoji="👎",
            style=discord.ButtonStyle.danger,
            custom_id="plan:decline"
        )
        async def decline(
            self,
            interaction: discord.Interaction,
            button: discord.ui.Button
        ):

            bot = interaction.client

            bot.db.leave_event(
                self.event_id,
                interaction.user.name
            )

            await self.refresh(interaction)


async def setup(bot):
    await bot.add_cog(PlanCog(bot))