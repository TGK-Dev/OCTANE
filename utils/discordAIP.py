import aiohttp

import discord
from discord import Webhook
import os
import json


class BaseRequest():
    def __init__(self):
        self.Base_url = "https://discord.com/api/v9"
        print("Loaded")    

    async def get_user(id:int, token:str):

        headers = {
            "Authorization": f"Bot {token} ", "Content-Type": "application/jsons"
        }
        url = f"https://discord.com/api/v10/users/{id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                r = await response.json()
                await session.close()
                return r
            
    async def get_member(id:int, token:str,total_votes:int, vote_webhook:str):

        headers = {
            "Authorization": f"Bot {token}", "Content-Type": "application/jsons"
        }

        url = f"https://discord.com/api/v10/guilds/785839283847954433/members/{id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                r = await response.json()

                if 'code' in r.keys():
                    await BaseRequest.get_member(id, token)

                else:

                    embed = discord.Embed(title=f"Thank {r['user']['username']} for voting for Gambler's Kingdom", description=f"Thank <@{r['user']['id']}> for the vote :)\nYou get Role <@&786884615192313866> for 12 Hours\n**Vote Count:** {total_votes}\n\nYou can vote on top.gg [here](https://top.gg/servers/785839283847954433/vote) every 12 hours!", color=0x00ffb3)
                    embed.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/830519601384128523.gif?v=1")
                    embed.set_footer(text="Made by Jay and Utki", icon_url=f"https://cdn.discordapp.com/avatars/816699167824281621/1bf01631b86f25cb052d64b69759e8d4.png?size=4096")
                    webhook = Webhook.from_url(vote_webhook, session=session)

                    await webhook.send(username=f"OCT∆NΞ Logging", avatar_url="https://cdn.discordapp.com/avatars/816699167824281621/1bf01631b86f25cb052d64b69759e8d4.png?size=4096",embed=embed)
            
            add_role = f"https://discord.com/api/v9/guilds/785839283847954433/members/{id}/roles/786884615192313866"
            
            async with session.put(add_role, headers=headers) as response:
                await session.close()