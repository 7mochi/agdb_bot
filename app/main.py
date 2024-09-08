#!/usr/bin/env python3
import functools
import os
import sys
import textwrap
from collections.abc import Callable
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands, tasks

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
    await serverlist_cronjob.start()


def guild_only() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(
            interaction: discord.Interaction,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
            if interaction.guild is None:
                await interaction.response.send_message(
                    "This command cannot be used in DMs. Consider joining the AGDB Discord server to use this command and many more! https://discord.gg/8btSjbYYFc",
                    ephemeral=True,
                )
                return
            return await func(interaction, *args, **kwargs)

        return wrapper

    return decorator


def is_user_admin() -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(
            interaction: discord.Interaction,
            *args: Any,
            **kwargs: Any,
        ) -> Any:
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
                ▸ **Related SteamIDs:** {", ".join(player.relatedSteamIDs) if player.relatedSteamIDs else "N/A"}
                ▸ **Banned:** {player.isBanned}
                ▸ **Ban reason:** {player.banReason if player.isBanned else "N/A"}
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
@app_commands.describe(reason="Reason for the ban")
@guild_only()
@is_user_admin()
async def ban(
    interaction: discord.Interaction,
    steam_id: str,
    reason: str,
) -> None:
    await interaction.response.defer(ephemeral=False)

    ban_response = await agdb_api.ban_player(steam_id, reason)

    if ban_response is None:
        await interaction.followup.send("Failed to ban player, player not found")
        return

    ban_embed = discord.Embed(
        color=discord.Color.red(),
    )
    ban_embed.set_author(
        name=f"Player Banned: {ban_response.steamID}",
    )
    ban_embed.add_field(
        name="",
        value=ban_response.message,
    )

    channel = bot.get_channel(settings.DISCORD_BAN_LOG_CHANNEL_ID)

    player = await agdb_api.fetch_player_info(steam_id)
    assert player is not None

    player_embed = discord.Embed(
        color=discord.Color.red(),
    )

    player_embed.set_author(
        name=f"A player has been AGDB banned: {player.steamName}",
        url=player.steamUrl,
        icon_url=f"https://assets.ppy.sh/old-flags/{player.country}.png",  # TODO: Using osu! flags for now
    )
    player_embed.set_thumbnail(url=player.avatar)
    player_embed.add_field(
        name="",
        value=textwrap.dedent(
            f"""\
                ▸ **SteamID:** {player.steamID}
                ▸ **Related SteamIDs:** {", ".join(player.relatedSteamIDs) if player.relatedSteamIDs else "N/A"}
                ▸ **Ban reason:** {player.banReason if player.isBanned else "N/A"}
                ▸ **Nicknames:** {", ".join(player.nicknames[:5])}
            """,
        ),
    )

    assert isinstance(channel, discord.TextChannel)
    assert channel is not None

    await interaction.followup.send(embed=ban_embed)
    await channel.send(embed=player_embed)


@bot.tree.command(
    name="unban",
    description="Unbans a player",
)
@app_commands.describe(steam_id="SteamID of the player to unban")
@guild_only()
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

    unban_embed = discord.Embed(
        color=discord.Color.green(),
    )
    unban_embed.set_author(
        name=f"Player Unbanned: {unban_response.steamID}",
    )
    unban_embed.add_field(
        name="",
        value=unban_response.message,
    )

    channel = bot.get_channel(settings.DISCORD_BAN_LOG_CHANNEL_ID)

    player = await agdb_api.fetch_player_info(steam_id)
    assert player is not None

    player_embed = discord.Embed(
        color=discord.Color.green(),
    )

    player_embed.set_author(
        name=f"A player has been AGDB unbanned: {player.steamName}",
        url=player.steamUrl,
        icon_url=f"https://assets.ppy.sh/old-flags/{player.country}.png",  # TODO: Using osu! flags for now
    )
    player_embed.set_thumbnail(url=player.avatar)
    player_embed.add_field(
        name="",
        value=textwrap.dedent(
            f"""\
                ▸ **SteamID:** {player.steamID}
                ▸ **Related SteamIDs:** {", ".join(player.relatedSteamIDs) if player.relatedSteamIDs else "N/A"}
                ▸ **Nicknames:** {", ".join(player.nicknames[:5])}
            """,
        ),
    )

    assert isinstance(channel, discord.TextChannel)
    assert channel is not None

    await interaction.followup.send(embed=unban_embed)
    await channel.send(embed=player_embed)


@tasks.loop(minutes=10)
async def serverlist_cronjob() -> None:
    channel = bot.get_channel(settings.DISCORD_AGDB_SERVERLIST_CHANNEL_ID)

    serverlist = await agdb_api.fetch_serverlist()
    assert serverlist is not None

    assert isinstance(channel, discord.TextChannel)
    assert channel is not None

    latest_messages = [message async for message in channel.history(limit=100)]

    content = textwrap.dedent(
        f"""\
                *Please note: Some servers may not be displayed. The server list is updated automatically every 10 minutes, so it might not reflect all servers at the moment.*

                Here are some of the servers currently using AGDB

                **Servers using AGDB** (Server count: {len(serverlist)})
            """,
    )

    for server in serverlist:
        content += f"- {server.serverName} (AGDB v{server.agdbVersion})\n"
        content += f"  - IP: {server.ipPort}\n"

    for message in latest_messages:
        assert bot.user is not None

        if message.author.id == bot.user.id:
            await message.edit(content=content)
            return

    await channel.send(content=content)


if __name__ == "__main__":
    logger.configure_logging()
    bot.run(settings.DISCORD_TOKEN)
