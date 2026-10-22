import discord
from discord.ext import commands
from database import add_warning, get_warnings
from utils.permissions import is_staff
from utils.embeds import log_embed

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="clear", description="Удалить сообщения")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        amount = max(1, min(amount, 100))
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"🧹 Удалено сообщений: {len(deleted)}", delete_after=4)

    @commands.hybrid_command(name="timeout", description="Выдать тайм-аут")
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: discord.Member, minutes: int, *, reason="Не указана"):
        until = discord.utils.utcnow() + discord.timedelta(minutes=minutes)
        await member.timeout(until, reason=reason)
        await ctx.send(embed=log_embed("🔇 Тайм-аут", f"{member.mention}\nПричина: {reason}"))

    @commands.hybrid_command(name="kick", description="Кикнуть участника")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="Не указана"):
        await member.kick(reason=reason)
        await ctx.send(embed=log_embed("👢 Участник исключён", f"{member}\nПричина: {reason}"))

    @commands.hybrid_command(name="ban", description="Заблокировать участника")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="Не указана"):
        await member.ban(reason=reason)
        await ctx.send(embed=log_embed("🔨 Участник заблокирован", f"{member}\nПричина: {reason}"))

    @commands.hybrid_command(name="warn", description="Выдать предупреждение")
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason="Не указана"):
        await add_warning(
            ctx.guild.id, member.id, ctx.author.id, reason,
            discord.utils.utcnow().isoformat()
        )
        await ctx.send(embed=log_embed("⚠️ Предупреждение", f"{member.mention}\nПричина: {reason}", discord.Color.orange()))

    @commands.hybrid_command(name="warnings", description="Показать предупреждения")
    @commands.has_permissions(moderate_members=True)
    async def warnings(self, ctx, member: discord.Member):
        rows = await get_warnings(ctx.guild.id, member.id)
        if not rows:
            text = "Предупреждений нет."
        else:
            text = "\n".join(
                f"• {reason} — <@{moderator}> — {created[:19]}"
                for reason, moderator, created in rows[:15]
            )
        await ctx.send(embed=log_embed(f"⚠️ Предупреждения: {member}", text, discord.Color.orange()))

async def setup(bot):
    await bot.add_cog(Moderation(bot))
