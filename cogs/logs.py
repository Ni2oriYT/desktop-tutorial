import discord
from discord.ext import commands
from config import LOG_CHANNEL_ID

class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def send(self, guild, title, description, color=discord.Color.blurple()):
        channel = guild.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(embed=discord.Embed(
                title=title, description=description, color=color,
                timestamp=discord.utils.utcnow()
            ))

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.guild and not message.author.bot:
            await self.send(message.guild, "🗑️ Сообщение удалено",
                f"Автор: {message.author.mention}\nКанал: {message.channel.mention}\n"
                f"Содержимое: {message.content[:1500] or '*без текста*'}",
                discord.Color.red())

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.guild and not before.author.bot and before.content != after.content:
            await self.send(before.guild, "✏️ Сообщение изменено",
                f"Автор: {before.author.mention}\nКанал: {before.channel.mention}\n"
                f"Было: {before.content[:700]}\nСтало: {after.content[:700]}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.display_name != after.display_name:
            await self.send(after.guild, "👤 Изменён ник",
                f"Пользователь: {after.mention}\nБыло: `{before.display_name}`\nСтало: `{after.display_name}`")

        before_roles = {r.id for r in before.roles}
        after_roles = {r.id for r in after.roles}
        if before_roles != after_roles:
            added = [r.mention for r in after.roles if r.id not in before_roles]
            removed = [r.name for r in before.roles if r.id not in after_roles]
            await self.send(after.guild, "🎭 Изменены роли",
                f"Пользователь: {after.mention}\nДобавлены: {', '.join(added) or '—'}\n"
                f"Удалены: {', '.join(removed) or '—'}")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel == after.channel:
            return
        if before.channel and after.channel:
            title, desc = "🔀 Перемещение в голосовом", f"{member.mention}: {before.channel.mention} → {after.channel.mention}"
        elif after.channel:
            title, desc = "🔊 Вход в голосовой", f"{member.mention} вошёл в {after.channel.mention}"
        else:
            title, desc = "🔇 Выход из голосового", f"{member.mention} вышел из {before.channel.mention}"
        await self.send(member.guild, title, desc)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        await self.send(member.guild, "🟢 Вход на сервер", f"{member.mention} присоединился.")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        await self.send(member.guild, "🔴 Выход с сервера", f"{member} покинул сервер.")

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        await self.send(channel.guild, "📁 Создан канал", f"{channel.mention if hasattr(channel, 'mention') else channel.name}")

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        await self.send(channel.guild, "🗑️ Удалён канал", f"`{channel.name}`")

async def setup(bot):
    await bot.add_cog(Logs(bot))
