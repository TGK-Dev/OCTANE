import discord

async def Normal_CallBack(interaction:  discord.Interaction):
    await interaction.response.defer(thinking=True, ephemeral=False)
    try:
        data = interaction.client.active_tag[interaction.command.name]
        await interaction.followup.send(data['content'])
    except KeyError:
        await interaction.followup.send("Tag not found / out of date.")

async def Argument_CallBack(interaction:  discord.Interaction, member: str, channel: discord.TextChannel=None):
    await interaction.response.defer(thinking=True, ephemeral=False)
    try:
        data = interaction.client.active_tag[interaction.command.name]
        await interaction.followup.send(data['content'].format(member=member, channel=channel.mention if channel else ""))
    except KeyError:
        await interaction.followup.send("Tag not found / out of date.")
    except Exception as e:
        embed = discord.Embed(title="Error", description=f"```\n{e}\n```", color=discord.Color.red())
        await interaction.followup.send(f"Error: {e}")
