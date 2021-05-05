__all__ = ["Help"]

from .paginator import Paginator
from .navigation import Navigation

import discord
from asyncio import TimeoutError
from discord.ext import commands
from discord.ext.commands.help import HelpCommand


class Help(HelpCommand):
    def __init__(self, **options):
        self.sort_commands = options.pop("sort_commands", True)

        self.code_block = options.pop("code_block", True)
        self.command_list_code_block = options.pop("command_list_code_block", False)
        self.cog_list_code_block = options.pop("cog_list_code_block", True)

        self.show_index = options.pop("show_index", True)
        self.index_title = options.pop("index_title", "Categories")
        self.index_show_categories = options.pop("index_show_categories", True)

        self.dm_help = options.pop("dm_help", False)
        self.dm_help_notification = options.pop("dm_help_notification", False)
        self.dm_help_message = options.pop("dm_help_message", "{0} Please check your DMs for help.")

        self.timeout = options.pop("timeout", 30)
        self.timeout_delete = options.pop("timeout_delete", True)
        self.timeout_remove_controls = options.pop("timeout_remove_controls", True)
        self.timeout_show_message = options.pop("timeout_show_message", True)
        self.timeout_message = options.pop("timeout_message", "Menu timed out.")

        self.closed_delete = options.pop("closed_delete", True)
        self.closed_remove_controls = options.pop("closed_remove_controls", False)
        self.closed_show_message = options.pop("closed_show_message", False)
        self.closed_message = options.pop("closed_message", "Menu closed.")

        self.colour = options.pop("colour", 0x9E3BFF)
        self.no_info = options.pop("no_info", "No information provided")
        self.ending_note = options.pop("ending_note", "")
        self.no_category = options.pop("no_category", "No Category")

        self.paginator_char_limit = options.pop("char_limit", 6000)
        self.paginator_field_limit = options.pop("field_limit", 15)

        self.navigation = options.pop("navigation", Navigation())
        self.paginator = Paginator(colour=self.colour, code_block=self.code_block, no_info=self.no_info,
                                   command_list_code_block=self.command_list_code_block,
                                   cog_list_code_block=self.cog_list_code_block,
                                   index_show_categories=self.index_show_categories,
                                   char_limit=self.paginator_char_limit, field_limit=self.paginator_field_limit)

        super().__init__(**options)

    async def prepare_help_command(self, ctx: commands.Context, command: commands.Command=None):
        if ctx.guild:
            permissions = ctx.channel.permissions_for(ctx.guild.me)
            if not permissions.embed_links:
                raise commands.BotMissingPermissions(("embed links",))
            if not permissions.read_message_history:
                raise commands.BotMissingPermissions(("read message history",))
            if not permissions.add_reactions:
                raise commands.BotMissingPermissions(("add reactions permission",))

        self.paginator.clear()
        self.paginator.ending_note = self.get_ending_note()
        await super().prepare_help_command(ctx, command)

    def get_ending_note(self):
        default ="Develop by Jay2404/Utik007\nType {0}{1} [command] for more info on a command.\n".format(self.clean_prefix, self.invoked_with)

        return self.ending_note or default

    async def send_pages(self):
        destination = self.get_destination()
        pages = self.paginator.pages
        total_pages = len(pages)

        if self.dm_help_notification and self.dm_help:
            try:
                await self.context.channel.send(embed=discord.Embed(description=self.dm_help_message.format(self.context.author)))
            except:
                pass

        message: discord.Message = await destination.send(embed=pages[0])

        if total_pages > 1:
            bot: commands.Bot = self.context.bot
            running = True
            index = 0

            for reaction in self.navigation:
                await message.add_reaction(reaction)

            while running:
                try:
                    def check(p: discord.RawReactionActionEvent):
                        if p.user_id != bot.user.id and message.id == p.message_id:
                            return True

                    p: discord.RawReactionActionEvent = await bot.wait_for("raw_reaction_add", timeout=self.timeout, check=check)

                    emoji = p.emoji.name if not p.emoji.id else f":{p.emoji.name}:{p.emoji.id}"

                    if emoji in self.navigation and p.user_id == self.context.author.id:
                        nav = self.navigation.get(emoji)

                        if not nav:
                            running = False

                            if self.closed_delete:
                                return await message.delete()

                            if self.closed_show_message:
                                p: discord.Embed = pages[index % total_pages]
                                p.clear_fields()
                                p.description = self.closed_message or p.Empty
                                await message.edit(embed=p)

                            if self.closed_remove_controls:
                                for reaction in self.navigation:
                                    try:
                                        await message.clear_reaction(reaction)
                                    except Exception:
                                        try:
                                            await message.remove_reaction(reaction, bot.user)
                                        except Exception:
                                            pass

                            return
                        else:
                            index += nav
                            embed: discord.Embed = pages[index % total_pages]

                            await message.edit(embed=embed)

                        try:
                            await message.remove_reaction(p.emoji, discord.Object(id=p.user_id))
                        except discord.errors.Forbidden:
                            pass

                except TimeoutError:
                    running = False

                    if self.timeout_delete:
                        return await message.delete()

                    if self.timeout_show_message:
                        p: discord.Embed = pages[index % total_pages]
                        p.clear_fields()
                        p.description = self.timeout_message or p.Empty
                        await message.edit(embed=p)

                    if self.timeout_remove_controls:
                        for reaction in self.navigation:
                            try:
                                await message.remove_reaction(reaction, bot.user)
                            except Exception:
                                pass

    def get_destination(self):
        ctx = self.context
        if self.dm_help:
            return ctx.author
        else:
            return ctx.channel

    def get_command_signature(self, command):
        parent = command.full_parent_name

        return '%s%s %s' % (self.clean_prefix, command.name if not parent else f"{parent} {command.name}", command.signature)

    async def send_bot_help(self, mapping: dict):
        bot = self.context.bot

        mapping = dict((name, []) for name in mapping)
        filtered = filter(lambda c: c.name != "help", bot.commands) if len(bot.commands) > 1 else bot.commands

        for cmd in await self.filter_commands(filtered, sort=self.sort_commands):
            mapping[cmd.cog].append(cmd)

        self.paginator.add_cog(self.no_category, mapping.pop(None))

        key = lambda cg: cg[0].qualified_name if isinstance(cg[0], commands.Cog) else str(cg[0])
        for cog, command_list in sorted(mapping.items(), key=key):
            self.paginator.add_cog(cog, command_list)
        self.paginator.add_index(self.show_index, self.index_title, bot)

        await self.send_pages()

    async def send_command_help(self, command: commands.Command):
        filtered = await self.filter_commands([command])
        if filtered:
            self.paginator.add_command(command, self.get_command_signature(command))
            await self.send_pages()

    async def send_group_help(self, group: commands.Group):
        filtered = await self.filter_commands(group.commands, sort=self.sort_commands)
        self.paginator.add_group(group, filtered, self.get_command_signature(group))
        await self.send_pages()

    async def send_cog_help(self, cog: commands.Cog):
        filtered = await self.filter_commands(cog.get_commands(), sort=self.sort_commands)
        self.paginator.add_cog(cog, filtered)
        await self.send_pages()
