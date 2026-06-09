import discord
from discord import app_commands
from discord.ext import commands
from typing import List


# ----------------------------
# Utils
# ----------------------------
def parse_list(value: str) -> List[str]:
    return value.split(",") if value else []


def validate_date(date: str) -> bool:
    return len(date) == 5 and date[2] == "." and date.replace(".", "").isdigit()


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
    def build(event, participants, drivers):
        embed = discord.Embed(
            title="📅 TERMIN",
            description=f"**Datum:** {event[3]}\n**Zeit:** {event[4]}",
            color=0x00AAFF
        )

        embed.add_field(
            name="👍 Teilnehmer",
            value="\n".join(participants) if participants else "-",
            inline=False
        )

        embed.add_field(
            name="🚗 Fahrer",
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

        event_id = self.bot.db.create_event(interaction.channel_id, date, time)

        event = self.bot.db.get_event(event_id)

        embed = PlanRenderer.build(event, [], [])

        view = self.PlanView(event_id)

        msg = await interaction.channel.send(embed=embed, view=view)

        self.bot.db.update_message(event_id, msg.id)

        await interaction.response.send_message("✅ erstellt", ephemeral=True)

    # ---------------- PERSISTENT VIEW ----------------
    class PlanView(discord.ui.View):
        def __init__(self, event_id: int):
            super().__init__(timeout=None)
            self.event_id = event_id

        # ---------------- Resolver ----------------
        def get_data(self, bot):
            event = bot.db.get_event(self.event_id)
            participants = parse_list(event[5])
            drivers = parse_list(event[6])
            return event, participants, drivers

        def save(self, bot, participants, drivers):
            bot.db.update(self.event_id, participants, drivers)

        async def refresh(self, interaction: discord.Interaction):
            bot = interaction.client
            event, participants, drivers = self.get_data(bot)
      
            embed = PlanRenderer.build(event, participants, drivers)
            await interaction.response.edit_message(embed=embed, view=self)

        # ---------------- BUTTONS ----------------

        @discord.ui.button(emoji="👍", style=discord.ButtonStyle.success, custom_id="plan:join")
        async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        
            bot = interaction.client
            event, participants, drivers = self.get_data(bot)

            user = interaction.user.name

            if user in participants:
                participants.remove(user)
            else:
                participants.append(user)
            
            if user in drivers:
              drivers.remove(user)

            self.save(bot, participants, drivers)
            await self.refresh(interaction)

        @discord.ui.button(emoji="🚗", style=discord.ButtonStyle.primary, custom_id="plan:driver")
        async def driver(self, interaction: discord.Interaction, button: discord.ui.Button):
          
            bot = interaction.client
            event, participants, drivers = self.get_data(bot)

            user = interaction.user.name

            if user not in participants:
              participants.append(user)

            if user in drivers:
                drivers.remove(user)
            else:
                drivers.append(user)
            
            self.save(bot, participants, drivers)
            await self.refresh(interaction)

        @discord.ui.button(emoji="👎", style=discord.ButtonStyle.danger, custom_id="plan:decline")
        async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):

            bot = interaction.client
            event, participants, drivers = self.get_data(bot)

            user = interaction.user.name
        
            participants = [p for p in participants if p != user]
            drivers = [d for d in drivers if d != user]

            self.save(bot, participants, drivers)
            await self.refresh(interaction)


async def setup(bot):
    await bot.add_cog(PlanCog(bot))