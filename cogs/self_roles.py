import discord
from discord.ext import commands
from utils.checks import checks

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
    

    @discord.ui.select(placeholder="Select Your Role Section from Below", max_values=14, custom_id="self_role_menu_main:min",
        options=[
                discord.SelectOption(label="Announcement", value="835442987382210570", emoji="<a:tgk_announce:848804249525551134>"),
                discord.SelectOption(label="Server Events", value="836925033506275399", emoji="<a:celebrateyay:821698856202141696>"),
                discord.SelectOption(label="Server Polls", value="793535450597294101", emoji="<a:rainbowbirdupvote:804053833306210344>"),
                discord.SelectOption(label="Server Updates", value="804055217108680725", emoji="<a:TGK_slots:842628623571091457>"),
                discord.SelectOption(label="Movie Night", value="791347199119327252", emoji="<a:tgk_movienight:842675039833030666>"),
                #
                discord.SelectOption(label="Giveaways", value="800685251276963861", emoji="<a:tadaa:806631994770849843>"),
                discord.SelectOption(label="Flash Giveaways", value="822021066548969482", emoji="<a:celebrate:817302382630273054>"),
                discord.SelectOption(label="Other Giveaway", value="848809346972516363", emoji="<a:tgk_gift:820323551520358440>"),
                #
                discord.SelectOption(label="Partnership", value="797448080223109120", emoji="<a:pandanod:809461710879588384>"),
                discord.SelectOption(label="No Partnership", value="810593886720098304", emoji="<a:bunnyno:809007055230074930>"),
                #
                discord.SelectOption(label="Heists", value="804068344612913163", emoji="<a:flymoney:803336135803404301>"),
                discord.SelectOption(label="Partner Heists", value="804069957528584212", emoji="<a:peperobber:929627184308568134>"),
                discord.SelectOption(label="Outside Heists", value="806795854475165736", emoji="<a:bhaago:821993760492879872>"),
                discord.SelectOption(label="Shopper's Delight", value="799517544674230272", emoji="<a:yippeeee:804392376441110598>")])
    async def self_main(self, select: discord.ui.select, interaction: discord.Interaction):
        guild = interaction.guild
        added = []
        await interaction.response.defer(ephemeral=True)
        for roles in select.values:
            role = discord.utils.get(guild.roles, id=int(roles))
            if role in interaction.user.roles:
                continue
            else:
                added.append(role.mention)
                await interaction.user.add_roles(role)
        if len(added) == 0:
            m = await interaction.followup.send("No role added as you already have roles from selected menu", ephemeral=True)
        else:
            m = await interaction.followup.send(content="Added Role: "+", ".join(added), ephemeral=True)

class self_cmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self_role())
        print(f"{self.__class__.__name__} Is Ready")
    
    @commands.command()
    @commands.check_any(checks.can_use())
    async def rr(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title="Some important self roles",color=ctx.guild.me.color,
        description="Use dropdown menu to select required roles.")
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=self_role())

def setup(bot):
    bot.add_cog(self_cmd(bot))

#<a:heist:929627130210426941> <a:tgk_right:929627387732320257> <@&804068344612913163>\n<a:peperobber:929627184308568134> <a:tgk_right:929627387732320257> <@&804069957528584212>\n<a:Partner:929627243062362123> <a:tgk_right:929627387732320257> <@&797448080223109120>\n<a:winners_emoji:867972307103141959> <a:tgk_right:929627387732320257> <@&800685251276963861>\n<a:calendar:854663256420909066> <a:tgk_right:929627387732320257> <@&836925033506275399>