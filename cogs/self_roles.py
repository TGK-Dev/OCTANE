import discord
import datetime
from discord import guild
from discord.ext import commands
from discord.ui import view

game_role = [795711140108697630, 795711130378829835]
bot_role = [801392998465404958, 791713762041266226, 842809745802526730]
server_role = [835442987382210570, 836925033506275399,
               793535450597294101, 804055217108680725, 791347199119327252]
giveaways_roles = [800685251276963861, 822021066548969482, 848809346972516363]
partnership_roles = [797448080223109120, 810593886720098304]
dank_roles = [804068344612913163, 804069957528584212,
              806795854475165736, 799517544674230272]


class self_role(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    

    @discord.ui.select(placeholder="Select Your Role Section from Below", max_values=5, custom_id="self_role_menu_main:min",
        options=[discord.SelectOption(label="Heist", value="804068344612913163", emoji="<a:rarepepe:801693036911263744>"),
                discord.SelectOption(label="Partner Heists", value="804069957528584212", emoji="<a:peperobber:929627184308568134>"),
                discord.SelectOption(label="Partnership", value="797448080223109120", emoji="<a:Partner:929627243062362123>"),
                discord.SelectOption(label="Giveaway", value="800685251276963861", emoji="<a:winners_emoji:867972307103141959>"),
                discord.SelectOption(label="Server Events", value="836925033506275399", emoji="<a:calendar:854663256420909066>")])
    async def self_main(self, select: discord.ui.select, interaction: discord.Interaction):
        guild = interaction.guild
        added = []
        remove = []
        for roles in select.values:
            role = discord.utils.get(guild.roles, id=int(roles))
            if role in interaction.user.roles:
                remove.append(role.mention)
                await interaction.user.remove_roles(role)
            else:
                added.append(role.mention)
                await interaction.user.add_roles(role)
        await interaction.response.send_message("Added Role: "+", ".join(added)+"\n"+"Removed Roles: "+", ".join(remove), ephemeral=True)

class self_cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self_role())
        print(f"{self.__class__.__name__} Is Ready")
    
    @commands.command()
    async def rr(self, ctx):
        embed = discord.Embed(title="Some important self roles",color=ctx.guild.me.color,
        description="<a:heist:929627130210426941> <a:tgk_right:929627387732320257> <@&804068344612913163>\n<a:peperobber:929627184308568134> <a:tgk_right:929627387732320257> <@&804069957528584212>\n<a:Partner:929627243062362123> <a:tgk_right:929627387732320257> <@&797448080223109120>\n<a:winners_emoji:867972307103141959> <a:tgk_right:929627387732320257> <@&800685251276963861>\n<a:calendar:854663256420909066> <a:tgk_right:929627387732320257> <@&836925033506275399>")
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=self_role())

def setup(bot):
    bot.add_cog(self_cmd(bot))