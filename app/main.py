#!/usr/bin/env python3
import functools
import os
import sys
import textwrap
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands

# add .. to path
srv_root = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(srv_root)

from app import logger
from app.adapters import agdb_api
from app.common import settings


class Bot(commands.Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            commands.when_mentioned_or("!"),
            help_command=None,
            *args,
            **kwargs,
        )


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = Bot(intents=intents)


@bot.event
async def on_ready() -> None:
    await bot.tree.sync()


def guild_only():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            if interaction.guild is None:
                await interaction.response.send_message(
                    "This command cannot be used in DMs. Consider joining the AGDB Discord server to use this command and many more! https://discord.gg/8btSjbYYFc",
                    ephemeral=True,
                )
                return
            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator


def is_user_admin():
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(interaction: discord.Interaction, *args, **kwargs):
            guild = bot.get_guild(settings.DISCORD_AGDB_GUILD_ID)
            assert guild is not None

            member = guild.get_member(interaction.user.id)
            assert member is not None

            admin_role = discord.utils.get(
                guild.roles,
                id=settings.DISCORD_ADMIN_ROLE_ID,
            )
            if admin_role in member.roles:
                return await func(interaction, *args, **kwargs)
            else:
                await interaction.response.send_message(
                    "You don't have permission to use this command",
                    ephemeral=True,
                )
                return

        return wrapper

    return decorator


@bot.tree.command(
    name="info",
    description="Returns a player's information",
)
@app_commands.describe(steam_id="SteamID of the player to check")
@guild_only()
async def info(
    interaction: discord.Interaction,
    steam_id: str,
) -> None:
    await interaction.response.defer(ephemeral=False)

    player = await agdb_api.fetch_player_info(steam_id)

    if player is None:
        await interaction.followup.send("Player not found")
        return

    player_embed = discord.Embed(
        color=discord.Color.green(),
    )
    player_embed.set_author(
        name=f"Player Information for {player.steamName}",
        url=player.steamUrl,
        icon_url=f"https://assets.ppy.sh/old-flags/{player.country}.png",  # TODO: Using osu! flags for now
    )
    player_embed.set_thumbnail(url=player.avatar)
    player_embed.add_field(
        name="",
        value=textwrap.dedent(
            f"""\
                ▸ **SteamID:** {player.steamID}
                ▸ **Related SteamIDs:** {", ".join(player.relatedSteamIDs) if player.relatedSteamIDs else "None"}
                ▸ **Banned:** {player.isBanned}
                ▸ **Nicknames:** {", ".join(player.nicknames[:5])}
            """,
        ),
    )

    await interaction.followup.send(embed=player_embed)


@bot.tree.command(
    name="ban",
    description="Bans a player",
)
@app_commands.describe(steam_id="SteamID of the player to ban")
@guild_only()
@is_user_admin()
async def ban(
    interaction: discord.Interaction,
    steam_id: str,
) -> None:
    await interaction.response.defer(ephemeral=False)

    ban_response = await agdb_api.ban_player(steam_id)

    if ban_response is None:
        await interaction.followup.send("Failed to ban player, player not found")
        return

    player_embed = discord.Embed(
        color=discord.Color.red(),
    )
    player_embed.set_author(
        name=f"Player Banned: {ban_response.steamID}",
    )
    player_embed.add_field(
        name="",
        value=ban_response.message,
    )

    await interaction.followup.send(embed=player_embed)


@bot.tree.command(
    name="unban",
    description="Unbans a player",
)
@guild_only()
@is_user_admin()
@app_commands.describe(steam_id="SteamID of the player to unban")
@is_user_admin()
async def unban(
    interaction: discord.Interaction,
    steam_id: str,
) -> None:
    await interaction.response.defer(ephemeral=False)

    unban_response = await agdb_api.unban_player(steam_id)

    if unban_response is None:
        await interaction.followup.send("Failed to unban player, player not found")
        return

    player_embed = discord.Embed(
        color=discord.Color.green(),
    )
    player_embed.set_author(
        name=f"Player Unbanned: {unban_response.steamID}",
    )
    player_embed.add_field(
        name="",
        value=unban_response.message,
    )

    await interaction.followup.send(embed=player_embed)


if __name__ == "__main__":
    logger.configure_logging()
    bot.run(settings.DISCORD_TOKEN)
