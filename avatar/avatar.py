import discord
from typing import Literal, Optional, Union
from redbot.core import app_commands, commands, Config


class Avatar(commands.Cog):
    """Get a user's global/guild avatar or decoration in a clean embed."""

    def __init__(self):
        self.config = Config.get_conf(self, identifier=524188088840)
        self.config.register_global(embed_color=None, use_embed=True)

    @commands.hybrid_command(name="avatar", usage="[user] [type]")
    @app_commands.describe(
        user="The user whose avatar you want to retrieve (defaults to you)",
        type="Which avatar asset to retrieve",
    )
    @commands.guild_only()
    async def avatar(
        self,
        ctx: commands.Context,
        user: Optional[Union[discord.Member, discord.User]] = None,
        type: Literal["global", "guild", "deco"] = "global",
    ) -> None:
        """Return a user's global avatar, server avatar, or avatar decoration.

        Optional arguments:
        - user: mention, username, or ID (defaults to you)
        - type: global, guild, or deco (defaults to global)
        """
        user = user or ctx.author
        asset_type = type.lower()
        display_avatar = user.display_avatar
        avatar_url = display_avatar.url
        title = "Avatar"

        if asset_type == "guild":
            if not isinstance(user, discord.Member):
                await ctx.send("Guild avatars are only available for members of this server.")
                return
            guild_avatar = user.guild_avatar
            if guild_avatar is not None:
                avatar_url = guild_avatar.url
            title = "Server Avatar"

        elif asset_type == "deco":
            decoration = getattr(user, "avatar_decoration", None)
            if decoration is not None:
                avatar_url = decoration.url
                title = "Avatar Decoration"
            else:
                await ctx.send("This user doesn't have an avatar decoration.")
                return

        embed_color = await self.config.embed_color()
        if embed_color is None:
            embed_color = getattr(user, "color", discord.Color.default())

        if not await self.config.use_embed():
            await ctx.send(avatar_url)
            return

        embed = discord.Embed(
            color=embed_color,
            description=f"**[{title}]({avatar_url})**",
        )
        embed.set_author(
            name=f"{user.name} · {getattr(user, 'display_name', user.name)}",
            icon_url=display_avatar.url,
        )
        embed.set_image(url=avatar_url)
        embed.set_footer(text=f"Rusty-Cogs · {asset_type.title()}")

        bot_member = ctx.guild.me
        if bot_member is None or not ctx.channel.permissions_for(bot_member).embed_links:
            await ctx.send("I need the **Embed Links** permission to display this avatar.")
            return

        await ctx.send(embed=embed)

    @commands.group(name="avatar_embed")
    @commands.is_owner()
    @commands.guild_only()
    async def avatar_embed(self, ctx: commands.Context) -> None:
        """Customize the avatar embed or send the image as a plain link."""

    @avatar_embed.command(name="color")
    @commands.is_owner()
    @commands.guild_only()
    async def avatar_embed_color(self, ctx: commands.Context, color: str) -> None:
        """Set the embed color with a HEX value, or use 'clear' for the default."""
        if color.lower() == "clear":
            await self.config.embed_color.set(None)
            await ctx.send("Embed color reset to the default.")
            return

        raw = color.strip().lstrip("#")
        if len(raw) not in (3, 6):
            await ctx.send("Invalid HEX color. Use 3 or 6 hexadecimal digits, or 'clear'.")
            return

        try:
            value = int(raw, 16)
            if len(raw) == 3:
                value = int("".join(char * 2 for char in raw), 16)
        except ValueError:
            await ctx.send("Invalid HEX color. Use 3 or 6 hexadecimal digits, or 'clear'.")
            return

        await self.config.embed_color.set(value)
        await ctx.send(f"Avatar embed color set to **#{value:06X}**.")

    @avatar_embed.command(name="show")
    @commands.is_owner()
    @commands.guild_only()
    async def avatar_embed_show(self, ctx: commands.Context, show: bool) -> None:
        """Enable or disable the avatar embed."""
        await self.config.use_embed.set(show)
        state = "enabled" if show else "disabled"
        await ctx.send(f"Avatar embeds {state}.")

    async def red_delete_data_for_user(self, **kwargs) -> None:
        """This cog does not store user-specific data."""
        return
