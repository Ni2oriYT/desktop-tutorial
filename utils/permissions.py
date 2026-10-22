import discord

def is_staff(member: discord.Member) -> bool:
    return member.guild_permissions.manage_guild or member.guild_permissions.moderate_members

def is_admin(member: discord.Member) -> bool:
    return member.guild_permissions.administrator
