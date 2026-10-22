import discord
from config import (
    FAMILY_NAME, FAMILY_PROJECT, FAMILY_DESCRIPTION,
    FAMILY_REQUIREMENTS, FAMILY_APPLICATION_NOTES,
)

def log_embed(title, description, color=discord.Color.blurple()):
    return discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=discord.utils.utcnow(),
    )

def application_embed(image_url=""):
    project = FAMILY_PROJECT or "Игровой проект / сервер укажите в настройках"
    description = FAMILY_DESCRIPTION or (
        "Ищем активных и дружелюбных игроков, которым интересна совместная игра, "
        "общение и участие в жизни семьи."
    )
    requirements = FAMILY_REQUIREMENTS or (
        "• Уважительное общение и готовность играть вместе\n"
        "• Активность и участие в голосовых каналах\n"
        "• Соблюдение правил сервера и семьи"
    )
    notes = FAMILY_APPLICATION_NOTES or "Заявки рассматривает команда семьи. После отправки ожидайте ответа в канале заявки."
    e = discord.Embed(
        title=f"📣 Заявки на вступление в {FAMILY_NAME} открыты!",
        description=(
            f"**Проект:** {project}\n\n"
            f"### О семье\n{description}\n\n"
            f"### Требования к кандидатам\n{requirements}\n\n"
            f"{notes}\n\n"
            "Внимательно ознакомьтесь с условиями и нажмите кнопку ниже, чтобы подать заявку."
        ),
        color=discord.Color.blurple(),
    )
    if image_url:
        e.set_image(url=image_url)
    e.set_footer(text="Blackwood • Система заявок")
    return e
