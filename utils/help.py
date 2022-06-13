from discord.ext import commands, menus
import discord

class HelpGroupPaginator(menus.ListPageSource):
    def __init__(self, help_: 'EmbedHelpCommand', group, entries):
        super().__init__(entries, per_page=7)
        self.group = group
        self.help = help_

    async def format_page(self, menu, entries):

        embed = discord.Embed(title=self.group.qualified_name, colour=self.help.COLOUR)


        if self.group.help:
            embed.description = (self.group.help)

        for command in entries:
            value = '...'
            if command.brief:
                value = (command.brief)
            embed.add_field(name=command.name, value=value, inline=True)

        embed.set_footer(text="use gk.help [command] for more info on a command")

        # you can format the embed however you'd like
        return embed


class EmbedHelpCommand(commands.HelpCommand):
    # Set the embed colour here
    COLOUR = discord.Colour.blurple()

    def get_ending_note(self, _):
        return _('Use {prefix}{help} [command] for more info on a command.', prefix="dh!", help=self.invoked_with)

    def get_command_signature(self, command):
        return '{0.qualified_name} {0.signature}'.format(command)

    async def send_bot_help(self, mapping):

        embed = discord.Embed(title='Bot Commands', colour=self.COLOUR)
        description = (self.context.bot.description)
        if description:
            embed.description = description

        for cog, commands in mapping.items():
            name = ('No Category') if cog is None else cog.qualified_name
            filtered = await self.filter_commands(commands, sort=True)
            if filtered:
                value = '\u2002'.join(c.name for c in commands)
                if cog and cog.description:
                    value = '{0}\n'.format((cog.description))

                embed.add_field(name=name, value=value, inline=False)

        embed.set_footer(text="use gk.help [command] for more info on a command")
        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):

        embed = discord.Embed(title=f'{cog.qualified_name} Commands', colour=self.COLOUR)

        if cog.description:
            embed.description = (cog.description)

        filtered = await self.filter_commands(cog.get_commands(), sort=True)
        for command in filtered:
            value = '...'
            if command.brief:
                value = f"Usage: `{command.brief}`"

            embed.add_field(name=command.name, value=value, inline=False)

        embed.set_footer(text="use gk.help [command] for more info on a command")
        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        entries = await self.filter_commands(group.commands, sort=True)
        menu = menus.MenuPages(HelpGroupPaginator(self, group, entries))
        await menu.start(self.context)

    async def send_command_help(self, command):

        embed = discord.Embed(title=command.qualified_name, colour=self.COLOUR)
        if command.description:
            embed.description = (command.description)
        if command.brief:
            embed.add_field(name="Usage:", value=f"`{command.brief}`", inline=False)
        if command.aliases:
            embed.add_field(name="Aliases", value=', '.join(command.aliases), inline=False)

        embed.set_footer(text="use gk.help [command] for more info on a command")
        await self.get_destination().send(embed=embed)