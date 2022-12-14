import discord
from discord import app_commands, Interaction
from discord.ext import commands
import re

time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h": 3600, "s": 1, "m": 60, "d": 86400}

class TimeConverter(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, argument: str) -> int:
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise app_commands.BadArgument(f"{value} is an invalid time key! h|m|s|d are valid arguments")
            except ValueError:
                raise app_commands.BadArgument(f"{key} is not a number!")
        return round(time)

class MutipleRole(app_commands.Transformer):
    async def transform(self, interaction: Interaction, value: str,):
        value = value.split(" ")
        roles = [await commands.RoleConverter().convert(interaction, role) for role in value]
        return roles

class MultipleMember(app_commands.Transformer):
    async def transform(self, interaction: Interaction, value: str,):
        value = value.split(" ")
        value = [value.replace("<", "").replace(">", "").replace("@", "").replace("!", "") for value in value]
        members = [interaction.guild.get_member(int(member)) for member in value if member is not None]
        return members