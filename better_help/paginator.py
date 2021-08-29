import discord
from typing import List, Union
from discord.ext import commands


class Paginator:
    def __init__(self, colour=discord.Embed.Empty, no_info="No information provided", index_show_categories=True,
                 code_block=True, command_list_code_block=False, cog_list_code_block=True, char_limit=6000, field_limit=15):
        self._pages = []

        self.ending_note = None
        self.colour = colour
        self.code_block = code_block
        self.command_list_code_block = command_list_code_block
        self.cog_list_code_block = cog_list_code_block
        self.no_info = no_info
        self.char_limit = char_limit
        self.field_limit = field_limit
        self.index_show_categories = index_show_categories
        self.prefix = "```" if code_block else ""
        self.suffix = "```" if code_block else ""
        self.clear()

    def clear(self):
        self._pages = []

    def _new_page(self, title: str, desc: str):
        return discord.Embed(title=title, description=desc, colour=self.colour)

    def _add_page(self, page: discord.Embed):
        page.set_footer(text=self.ending_note)
        self._pages.append(page)

    def _check_embed(self, embed: discord.Embed, *chars: str):
        return (len(embed) + sum(len(char) for char in chars if char) < self.char_limit and
                len(embed.fields) < self.field_limit)

    def _add_commands(self, embed: discord.Embed, page_title: str, command_list: List[commands.Command]):
        paginator = commands.Paginator(prefix="", suffix="", max_size=1000)

        for command in command_list:
            pre = "" if self.command_list_code_block else "`"
            parent = command.full_parent_name
            paginator.add_line(f"{pre}{command.name if not parent else f'{parent} {command.name}'}{pre}")

            if isinstance(command, commands.Group):
                for cmd_ in command.commands:
                    paginator.add_line(f"{pre}{cmd_}{pre}")

        for page in paginator.pages:
            pre = "```" if self.command_list_code_block else ""
            page = page.replace("\n", " ")
            embed.add_field(name="Commands:", inline=False,
                            value=f"{pre}{page}{pre}")
            self._add_page(embed)
            embed = self._new_page(page_title, embed.description)

    def _get_command_info(self, command: Union[commands.Command, commands.Group]):
        info = ""
        if command.description:
            info += command.description + "\n\n"
        if command.help:
            info += command.help

        return info if info else self.no_info

    @staticmethod
    def _get_command_aliases(command: Union[commands.Command, commands.Group]):
        return "\n".join(command.aliases)

    @staticmethod
    def _format_cooldown(bucket):
        if bucket == commands.BucketType.default:
            return "global"
        return bucket.name

    def add_command(self, command: commands.Command, signature: str, show_cooldown: bool, show_brief: bool, show_info_title: bool):
        info = self._get_command_info(command)

        page = self._new_page(f"Help: {command.qualified_name}",
                              f"{self.prefix}{info}{self.suffix}" if info and not show_info_title else "")

        if show_info_title and info:
            page.add_field(name="Info:", inline=False, value=f"{self.prefix}{info}{self.suffix}")

        if command.brief and show_brief:
            page.add_field(name="Brief:", inline=False, value=f"{self.prefix}{command.brief}{self.suffix}")

        page.add_field(name="Usage:", inline=False, value=f"{self.prefix}{signature}{self.suffix}")

        if command.aliases:
            page.add_field(name="Aliases:", inline=True,
                           value=f"{self.prefix}\n{self._get_command_aliases(command)}{self.suffix}")

        if command._buckets._cooldown and show_cooldown:
            cooldown = command._buckets._cooldown
            per = round(cooldown.per) if round(cooldown.per) == cooldown.per else cooldown.per
            page.add_field(name="Cooldown:", inline=True,
                           value=f"{self.prefix}{per} second{'s' if cooldown.per > 1 else ''} ({self._format_cooldown(cooldown.type).title()}){self.suffix}")

        self._add_page(page)

    def add_group(self, group: commands.Group, commands_list: List[commands.Command], signature: str):
        page = self._new_page(f"Help: {group.name}",
                              f"{self.prefix}{self._get_command_info(group)}{self.suffix}" or "")

        page.add_field(name="Usage:", inline=False, value=f"{self.prefix}{signature}{self.suffix}")

        if group.aliases:
            page.add_field(name="Aliases:", inline=True,
                           value=f"{self.prefix}{self._get_command_aliases(group)}{self.suffix}")

        if group._buckets._cooldown:
            cooldown = group._buckets._cooldown
            page.add_field(name="Cooldown:", inline=True,
                           value=f"{self.prefix}{cooldown.per} second {self._format_cooldown(cooldown.type)}{self.suffix}")

        self._add_commands(page, f"Help: {group.name}", commands_list)

    def add_cog(self, title: Union[str, commands.Cog], commands_list: List[commands.Command]):
        if commands_list:
            cog = isinstance(title, commands.Cog)
            page_title = title.qualified_name if cog else title
            page = self._new_page(page_title, (title.description or self.no_info) if cog else self.no_info)

            self._add_commands(page, page_title, commands_list)

    def add_index(self, include: bool, title: str, bot: commands.Bot):
        if include:
            index = self._new_page(title, bot.description)

            if self.index_show_categories:
                for page_no, page in enumerate(self._pages, 2):
                    pre = "```" if self.command_list_code_block else ""
                    index.add_field(name=f"{page.title} (Page {page_no}):", inline=False,
                                    value=f"{pre}{page.description or self.no_info}{pre}")

            index.set_footer(text=self.ending_note)
            self._pages.insert(0, index)
        else:
            self._pages[0].description = bot.description

    @property
    def pages(self):
        if len(self._pages) == 1:
            return self._pages

        pages = []
        for n, page in enumerate(self._pages, start=1):
            page: discord.Embed
            page.description = f"`Page: {n}/{len(self._pages)}`\n{page.description}"
            pages.append(page)

        return pages
