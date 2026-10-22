import discord
from discord.ext import commands
from database import init_db
from config import TOKEN
from views.ticket_view import TicketView
from cogs.tickets import TicketCreateView

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
INTENTS.messages = True
INTENTS.guilds = True
INTENTS.voice_states = True
INTENTS.moderation = True

class BlackwoodBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=INTENTS,
            help_command=None,
        )

    async def setup_hook(self):
        await init_db()

        for extension in (
            "cogs.welcome",
            "cogs.moderation",
            "cogs.tickets",
            "cogs.logs",
        ):
            await self.load_extension(extension)

        self.add_view(TicketView())
        self.add_view(TicketCreateView())

        await self.tree.sync()

    async def on_ready(self):
        print(f"Бот запущен: {self.user} ({self.user.id})")
        print(f"Серверов: {len(self.guilds)}")

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("DISCORD_TOKEN не найден в .env")
    bot = BlackwoodBot()
    bot.run(TOKEN)
