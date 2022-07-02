import aiohttp
import asyncio

class Client:
    def __init__(self, token:str, loop=None, base_url="https://unbelievaboat.com/api/v1"):
        self._loop = loop or asyncio.get_event_loop()
        self._url = base_url
        self._session = aiohttp.ClientSession(
            headers={'Authorization': token, "Accept": "application/json"}, loop=self._loop)
        self.rate_limit = None
    
    def __del__(self):
        return self._loop.create_task(self._session.close())
    
    async def get_user_bal(self, guild: int, user: int):
        """Returns the balance of the specified user in the specified guild."""
        async with self._session.get(f"{self._url}/guilds/{guild}/users/{user}") as resp:
            return await resp.json()
            
    
    async def patch_user_bal(self, guild: int, user: int, cash: int, bank: int, reason: str = None):
        """Updates the balance of the specified user in the specified guild."""
        async with self._session.patch(f"{self._url}/guilds/{guild}/users/{user}", json={"cash": cash, "bank": bank, "reason": reason}) as resp:
            return await resp.json()