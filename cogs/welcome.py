import discord
from discord.ext import commands
from config import WELCOME_CHANNEL_ID, RULES_CHANNEL_ID, CHAT_CHANNEL_ID, APPLICATION_CHANNEL_ID
from utils.embeds import log_embed

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.get_channel(WELCOME_CHANNEL_ID)
        if channel:
            rules = member.guild.get_channel(RULES_CHANNEL_ID)
            chat = member.guild.get_channel(CHAT_CHANNEL_ID)
            applications = member.guild.get_channel(APPLICATION_CHANNEL_ID)
            navigation = "\n".join(
                line for line in (
                    f"• {rules.mention} — правила" if rules else None,
                    f"• {chat.mention} — общение" if chat else None,
                    f"• {applications.mention} — заявки" if applications else None,
                ) if line
            )
            description = f"{member.mention}, добро пожаловать на сервер!"
            if navigation:
                description += f"\n\n**Навигация по серверу:**\n{navigation}"
            await channel.send(embed=log_embed(
                "🎉 Новый участник!",
                f"{description}\n\nТы у нас **{member.guild.member_count}**-й участник.",
                discord.Color.green()
            ))

async def setup(bot):
    await bot.add_cog(Welcome(bot))
