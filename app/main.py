#!/usr/bin/env python3
import base64
import os
import ssl
import sys
import logging

import discord
from discord.ext import commands
from discord.ext import tasks

# add .. to path
srv_root = os.path.join(os.path.dirname(__file__), "..")

sys.path.append(srv_root)

from app.repositories import users
from app.common import settings
from app.adapters import database
from app import state
from app.constants import Privileges

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            help_command=None,
            *args,
            **kwargs,
        )


intents = discord.Intents.default()
intents.presences = True
intents.members = True
intents.message_content = True

bot = Bot(intents=intents)


async def send_admin_log_embed(
    member: discord.Member | discord.User,
    log: str,
) -> None:
    rosu_guild = bot.get_guild(settings.ROSU_DISCORD_GUILD_ID)
    admin_logs_channel = rosu_guild.get_channel(  # type: ignore
        settings.ROSU_DISCORD_ADMIN_LOGS_CHANNEL_ID,
    )

    if not admin_logs_channel:
        return

    embed = discord.Embed(
        title="Automated supporter bot log",
        description=f"{member.mention} {log}",
        color=4360181,
    )
    embed.set_footer(text="This is an automated action performed by the bot service.")
    await admin_logs_channel.send(embed=embed)  # type: ignore


@tasks.loop(hours=12)
async def check_expired_supporters() -> None:
    rosu_guild = bot.get_guild(settings.ROSU_DISCORD_GUILD_ID)
    rosu_supporter_role = rosu_guild.get_role(settings.ROSU_DISCORD_DONOR_ROLE_ID)  # type: ignore

    if not rosu_supporter_role:
        return

    # First check for the existing expired supporters on discord server.
    for member in rosu_supporter_role.members:
        user = await users.fetch_one_from_discord_id(member.id)

        if user is None:  # They are not in rosu database somehow, we will expire them.
            logging.info(
                "User %s (%d) with supporter role is not in rosu database, expiring them.",
                member.name,
                member.id,
            )
            await member.remove_roles(rosu_supporter_role)
            await send_admin_log_embed(member, "just had their supporter role removed.")
            continue

        if user["privileges"] & Privileges.USER_DONOR:
            logging.info(
                "User %s (%d) is still a supporter, skipping.", member.name, member.id
            )
            continue

        logging.info(
            "User %s (%d) is no longer a supporter, expiring them.",
            member.name,
            member.id,
        )
        await member.remove_roles(rosu_supporter_role)
        await send_admin_log_embed(member, "just had their supporter role removed.")

    # Now check for the existing supporters in rosu database.
    for user in await users.fetch_all_supporters():
        if not user["discord_id"]:
            logging.info(
                "User %s (%d) is a supporter but does not have a discord id, skipping.",
                user["username"],
                user["id"],
            )
            continue

        member = rosu_guild.get_member(int(user["discord_id"]))  # type: ignore
        if not member:
            logging.info(
                "User %s (%d) is a supporter but not on discord, skipping.",
                user["username"],
                user["id"],
            )
            continue

        if rosu_supporter_role in member.roles:
            logging.info(
                "User %s (%d) is still a supporter, skipping.",
                user["username"],
                user["id"],
            )
            continue

        logging.info(
            "User %s (%d) is a supporter but does not have a supporter role, adding it.",
            user["username"],
            user["id"],
        )
        await member.add_roles(rosu_supporter_role)
        await send_admin_log_embed(member, "just had their supporter role added.")


@bot.event
async def on_ready() -> None:
    state.read_database = database.Database(
        database.dsn(
            scheme=settings.READ_DB_SCHEME,
            user=settings.READ_DB_USER,
            password=settings.READ_DB_PASS,
            host=settings.READ_DB_HOST,
            port=settings.READ_DB_PORT,
            database=settings.READ_DB_NAME,
        ),
        db_ssl=(
            ssl.create_default_context(
                purpose=ssl.Purpose.SERVER_AUTH,
                cadata=base64.b64decode(settings.READ_DB_CA_CERTIFICATE).decode(),
            )
            if settings.READ_DB_USE_SSL
            else False
        ),
        min_pool_size=settings.DB_POOL_MIN_SIZE,
        max_pool_size=settings.DB_POOL_MAX_SIZE,
    )
    await state.read_database.connect()

    await bot.tree.sync()
    check_expired_supporters.start()


@bot.tree.command(
    name="update",
    description="Awards you your role rewards.",
)
async def update(interaction: discord.Interaction) -> None:
    await interaction.response.defer(ephemeral=True)

    supporter_role = interaction.guild.get_role(settings.ROSU_DISCORD_DONOR_ROLE_ID)  # type: ignore
    user = await users.fetch_one_from_discord_id(interaction.user.id)  # type: ignore

    if user is None:
        await interaction.followup.send(
            "You have not linked your Discord account to your RealistikOsu account yet.\n"
            "You can do that here: https://ussr.pl/settings/discord-integration",
            ephemeral=True,
        )
        return

    if not user["privileges"] & Privileges.USER_DONOR and supporter_role in interaction.user.roles:  # type: ignore
        await interaction.user.remove_roles(supporter_role)  # type: ignore
        await send_admin_log_embed(
            interaction.user,
            "just had their supporter role removed.",
        )
        await interaction.followup.send(
            "Your supporter role has been removed as you are no longer a supporter.",
            ephemeral=True,
        )
        return

    if not user["privileges"] & Privileges.USER_DONOR:
        await interaction.followup.send(
            "You are not a supporter on RealistikOsu.\n"
            "You can become one here: https://ussr.pl/donate",
            ephemeral=True,
        )
        return

    if supporter_role in interaction.user.roles:  # type: ignore
        await interaction.followup.send(
            "You already have the supporter role!",
            ephemeral=True,
        )
        return

    await interaction.user.add_roles(supporter_role)  # type: ignore
    await send_admin_log_embed(interaction.user, "just had their supporter role added.")
    await interaction.followup.send(
        "Your supporter role has been added!",
        ephemeral=True,
    )


if __name__ == "__main__":
    bot.run(settings.DISCORD_TOKEN)
