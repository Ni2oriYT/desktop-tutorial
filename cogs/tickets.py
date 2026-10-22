import discord
from discord.ext import commands
from config import (
    APPLICATION_CHANNEL_ID, TICKET_CATEGORY_ID, APPLICATION_IMAGE_URL,
    RECRUITER_ROLE_ID,
)
from utils.embeds import application_embed
from views.ticket_view import TicketView

def _ticket_channel_name(user):
    safe_name = "".join(ch for ch in user.name.lower() if ch.isalnum() or ch in "-_")[:70]
    return f"заявка-{safe_name or user.id}"

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="ticket_panel", description="Создать панель заявок")
    @commands.has_permissions(administrator=True)
    async def ticket_panel(self, ctx):
        channel = ctx.guild.get_channel(APPLICATION_CHANNEL_ID) or ctx.channel
        await channel.send(embed=application_embed(APPLICATION_IMAGE_URL), view=TicketCreateView())
        await ctx.send("Панель заявок создана.", ephemeral=True)

class TicketCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Подать заявку", emoji="📋", style=discord.ButtonStyle.success, custom_id="ticket:create")
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Не настроена категория заявок.", ephemeral=True)
            return

        existing = discord.utils.get(category.text_channels, name=_ticket_channel_name(interaction.user))
        if existing:
            await interaction.response.send_message(f"У вас уже есть заявка: {existing.mention}", ephemeral=True)
            return

        await interaction.response.send_modal(ApplicationModal())


class ApplicationModal(discord.ui.Modal, title="Анкета кандидата GTA 5 RP"):
    age = discord.ui.TextInput(
        label="Сколько вам лет?", placeholder="Например: 18", max_length=3
    )
    timezone = discord.ui.TextInput(
        label="Ваш часовой пояс", placeholder="Например: МСК (UTC+3)", max_length=40
    )
    level = discord.ui.TextInput(
        label="Уровень персонажа", placeholder="Укажите уровень персонажа", max_length=30
    )
    hours = discord.ui.TextInput(
        label="Сколько часов наиграно?", placeholder="Общее время в игре", max_length=40
    )
    about = discord.ui.TextInput(
        label="Расскажите о себе", style=discord.TextStyle.paragraph,
        placeholder="Опыт игры, интересы и почему хотите вступить", max_length=800
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Acknowledge the modal immediately; channel creation can outlast Discord's 3s window.
        await interaction.response.defer(ephemeral=True, thinking=True)
        guild = interaction.guild
        category = guild.get_channel(TICKET_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.followup.send("Не настроена категория заявок.", ephemeral=True)
            return

        channel_name = _ticket_channel_name(interaction.user)
        existing = discord.utils.get(category.text_channels, name=channel_name)
        if existing:
            await interaction.followup.send(f"У вас уже есть заявка: {existing.mention}", ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        recruiter_role = guild.get_role(RECRUITER_ROLE_ID) if RECRUITER_ROLE_ID else None
        if recruiter_role:
            overwrites[recruiter_role] = discord.PermissionOverwrite(
                view_channel=True, send_messages=True, read_message_history=True
            )
        for role in guild.roles:
            if role.permissions.moderate_members or role.permissions.administrator:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        channel = await guild.create_text_channel(
            channel_name, category=category, overwrites=overwrites,
            topic=f"user_id={interaction.user.id}",
            reason=f"Новая заявка от {interaction.user}"
        )
        answers = discord.Embed(
            title="📋 Анкета кандидата",
            description=(
                f"**Возраст:** {self.age.value}\n"
                f"**Часовой пояс:** {self.timezone.value}\n"
                f"**Уровень персонажа:** {self.level.value}\n"
                f"**Время в игре:** {self.hours.value}\n\n"
                f"**О себе:**\n{self.about.value}"
            ),
            color=discord.Color.blurple()
        )
        recruiter_mention = recruiter_role.mention if recruiter_role else ""
        await channel.send(
            content=f"{interaction.user.mention} {recruiter_mention}".strip(),
            embed=answers,
            view=TicketView()
        )
        await interaction.followup.send(f"Анкета отправлена! Канал заявки: {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
