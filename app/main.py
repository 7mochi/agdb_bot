#!/usr/bin/env python3
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


@bot.tree.command(
    name="info",
    description="Returns a player's information",
)
@app_commands.describe(steam_id="SteamID of the player to check")
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
                ▸ **Banned:** {player.isBanned}
                ▸ **Nicknames:** {", ".join(player.nicknames[:5])}
            """,
        ),
    )

    await interaction.followup.send(embed=player_embed)


if __name__ == "__main__":
    logger.configure_logging()
    bot.run(settings.DISCORD_TOKEN)
