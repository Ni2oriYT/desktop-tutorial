import discord
from config import (
    ACCEPTED_CHANNEL_ID, CHECK_CATEGORY_ID, MEMBER_ROLE_ID, MEMBER_ROLE_2_ID,
)
from database import next_number
from utils.embeds import log_embed

def _applicant_id(channel):
    topic = channel.topic if channel else None
    if not topic or "user_id=" not in topic:
        return None
    value = topic.split("user_id=", 1)[1].split(";", 1)[0]
    return int(value) if value.isdigit() else None

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not isinstance(interaction.user, discord.Member):
            return False
        if not (
            interaction.user.guild_permissions.administrator
            or interaction.user.guild_permissions.manage_guild
            or interaction.user.guild_permissions.moderate_members
        ):
            await interaction.response.send_message(
                "У вас нет прав для обработки заявок.", ephemeral=True
            )
            return False
        return True

    async def _remove_check_channels(self, interaction: discord.Interaction):
        """Delete every check voice channel recorded on this application."""
        ticket_channel = interaction.channel
        if not isinstance(ticket_channel, discord.TextChannel) or not ticket_channel.topic:
            return
        marker = "check_voice_ids="
        if marker not in ticket_channel.topic:
            return
        raw_ids = ticket_channel.topic.split(marker, 1)[1].split(";", 1)[0]
        for raw_id in raw_ids.split(","):
            if not raw_id.isdigit():
                continue
            check_channel = interaction.guild.get_channel(int(raw_id))
            if check_channel:
                try:
                    await check_channel.delete(reason=f"Заявка обработана: {interaction.user}")
                except discord.HTTPException:
                    pass

    async def _remove_applicant_access(self, interaction: discord.Interaction):
        user_id = _applicant_id(interaction.channel)
        user = interaction.guild.get_member(user_id) if user_id else None
        if user and interaction.channel:
            try:
                await interaction.channel.set_permissions(
                    user, overwrite=None, reason=f"Заявка обработана: {interaction.user}"
                )
            except discord.HTTPException:
                pass

    @discord.ui.button(label="Принять", emoji="🟢", style=discord.ButtonStyle.success, custom_id="ticket:accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user_id = _applicant_id(interaction.channel)
        user = guild.get_member(user_id) if user_id else None

        if user:
            roles = [guild.get_role(role_id) for role_id in (MEMBER_ROLE_ID, MEMBER_ROLE_2_ID) if role_id]
            roles = [role for role in roles if role]
            if roles:
                try:
                    await user.add_roles(*roles, reason=f"Заявка принята: {interaction.user}")
                except discord.Forbidden:
                    pass

        channel = guild.get_channel(ACCEPTED_CHANNEL_ID)
        if channel:
            await channel.send(embed=log_embed(
                "✅ Игрок принят",
                f"Игрок: {user.mention if user else 'не найден'}\n"
                f"Модератор: {interaction.user.mention}",
                discord.Color.green()
            ))

        await interaction.response.send_message("Заявка принята.", ephemeral=True)
        await self._remove_check_channels(interaction)
        await self._remove_applicant_access(interaction)
        if interaction.channel:
            await interaction.channel.edit(name=f"accepted-{interaction.channel.name}")
            await interaction.channel.set_permissions(guild.default_role, view_channel=False)

    @discord.ui.button(label="Пригласить на проверку", emoji="🔎", style=discord.ButtonStyle.primary, custom_id="ticket:check")
    async def check(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        category = guild.get_channel(CHECK_CATEGORY_ID)
        if not isinstance(category, discord.CategoryChannel):
            await interaction.response.send_message("Не настроена категория проверок.", ephemeral=True)
            return

        number = await next_number(f"check:{guild.id}")
        channel = await guild.create_voice_channel(
            f"Проверка {number:03d}",
            category=category,
            reason=f"Проверка заявки модератором {interaction.user}"
        )

        user_id = _applicant_id(interaction.channel)
        user = guild.get_member(user_id) if user_id else None

        if user:
            await channel.set_permissions(user, connect=True, view_channel=True)
        await channel.set_permissions(interaction.user, connect=True, view_channel=True)
        ticket_channel = interaction.channel
        if isinstance(ticket_channel, discord.TextChannel):
            topic = ticket_channel.topic or ""
            marker = "check_voice_ids="
            ids = []
            if marker in topic:
                ids = topic.split(marker, 1)[1].split(";", 1)[0].split(",")
                topic = topic.split(marker, 1)[0].rstrip("; ")
            ids = [value for value in ids if value.isdigit()]
            ids.append(str(channel.id))
            await ticket_channel.edit(topic=f"{topic};{marker}{','.join(ids)}"[:1024])
        await interaction.response.send_message(
            f"Создан голосовой канал {channel.mention}.", ephemeral=True
        )

    @discord.ui.button(label="Отклонить", emoji="🔴", style=discord.ButtonStyle.danger, custom_id="ticket:reject")
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Заявка отклонена.", ephemeral=True)
        await self._remove_check_channels(interaction)
        await self._remove_applicant_access(interaction)
        if interaction.channel:
            await interaction.channel.edit(name=f"rejected-{interaction.channel.name}")
            await interaction.channel.set_permissions(interaction.guild.default_role, view_channel=False)
