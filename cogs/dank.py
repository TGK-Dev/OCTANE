import discord
from discord.ext import commands

class dank(commands.Cog):
	"""docstring for error"""
	def __init__(self, client):
		self.client = client


	@commands.Cog.listener()
	async def on_ready(self):
		print('Dank Loaded ')
"""
@client.command() 
async def hmm(ctx, early_role: discord.Role=None, req_role: discord.Role=None):

    req_role = req_role if req_role else ctx.guild.default_role
    early_role = early_role if early_role else ctx.guild.premium_subscriber_role

    await ctx.send(f"{req_role.name},hmm")

@client.command()
async def heist(ctx, host: discord.Member, amount, erole: discord.Role=None, rrole: discord.Role=None):
    x = str('yes')
    usercolor = host.color

    #role and channel mentions
    erole = erole if erole else ctx.guild.premium_subscriber_role
    rrole = rrole if rrole else ctx.guild.default_role
    channel = ctx.channel

    #embed things
    em = discord.Embed(color=usercolor, description=f"{host.mention} will be hosting a heist ")
    em.add_field(name='Check List:', value=f"- disable passive mode (pls settings passive disable)\n- withdraw 2,000 coins (pls with 2000)\n- you will have 1 minute, 30 seconds to join\n- you must have the {rrole.mention} role to join")
    await ctx.send(f'{rrole.mention}', embed=em)
    
    #overwrite
    eoverwrite = channel.overwrites_for(erole)#early roles 
    eoverwrite.send_messages = True

    roverwrite = channel.overwrites_for(rrole)#req roles
    roverwrite.send_messages = True
    #closing overwrite
    eeoverwrite = channel.overwrites_for(erole)
    eeoverwrite.send_messages = None

    rqoverwrite = channel.overwrites_for(rrole)
    rqoverwrite.send_messages = None
    #last Close
    coverwrite = channel.overwrites_for(ctx.guild.default_role)
    coverwrite.send_messages = False



    #dank things
    def check(m):
        return m.author.id == 488614633670967307
    message = await client.wait_for('message', check=check)

    sheit = ['is starting a bank robbery']
    
    messageContent = message.content
    if len(messageContent) > 0:
        for word in sheit:
            if word in messageContent:
                await ctx.send(f'Channel unlocked for {erole.name} early 10s')
                await channel.set_permissions(erole, overwrite=eoverwrite)
                await asyncio.sleep(10)
                await ctx.send(f'Channel unlocked for {rrole.name}')
                return await channel.set_permissions(rrole, overwrite=roverwrite)

                def check(c):
                    return m.author.id == 488614633670967307
                message = await client.wait_for('message', check=check)

                eheit = ['Time is up to join ']

                if message.author.id == 488614633670967307:
                    messageContent = message.content
                    if len(messageContent) > 0:
                        for eword in eheit:
                            if eword in messageContent:
                                await ctx.set_permissions(erole, overwrite=eeoverwrite)
                                await ctx.set_permissions(rrole, overwrite=rqoverwrite)
                                await ctx.set_permissions(ctx.guild.default_role, overwrite=coverwrite)
                                return ctx.send('Channel Locked For All ROle')
    else:
        return
@client.command()
async def starter(ctx, member: discord.Member=None):

    member = member if member else ctx.author

    role = get(ctx.guild, name="BlackListed")
    await member.add_roles(member, role)
    await ctx.send('role added')
    await asyncio.sleep(10)
    await member.remove_roles(member, role)
    await ctx.send('Role removed')

"""
def setup(client):
    client.add_cog(dank(client))
