import json
import requests

class client:
    def __init__(self, token):
        self.token = token
        self.base_url = "https://unbelievaboat.com/api/v1/"

    def fetch_errors(self, request):
        if request.status_code == 400:
            raise invalidData("Your request is invalid")
        elif request.status_code == 401:
            raise invalidPermissions("Your API token is invalid")
        elif request.status_code == 403:
            raise internetForbidden("You do not have permission to access this URL")
        elif request.status_code == 404:
            raise unexpectedURL("This page does not exist")
        elif request.status_code == 429:
            raise requestOverload("You are sending requests too quickly")
        elif request.status_code == 500:
            raise serverError("We had a problem with our server. Try again later")
        else:
            return 0

    def get_user_bal(self, guild, user):
        request = requests.get(self.base_url + "guilds/{guild}/users/{user}".format(guild=guild, user=user), headers={"Authorization": self.token})
        if self.fetch_errors(request) == 0:
            return json.loads(request.text)

    def set_user_bal(self, guild, user, cash=0, bank=0, reason=None):
        if reason == None:
            request = requests.put(self.base_url + "guilds/{guild}/users/{user}".format(guild=guild, user=user), headers={'Accept': 'application/json', 'Authorization': self.token}, data=json.dumps({"cash": cash, "bank": bank}))
        else:
            request = requests.put(self.base_url + "guilds/{guild}/users/{user}".format(guild=guild, user=user), headers={'Accept': 'application/json', 'Authorization': self.token}, data=json.dumps({"cash": cash, "bank": bank, "reason": reason}))
        if self.fetch_errors(request) == 0:
            return json.loads(request.text)

    def change_user_bal(self, guild, user, cash=0, bank=0, reason=None):
        if reason == None:
            request = requests.patch(self.base_url + "guilds/{guild}/users/{user}".format(guild=guild, user=user), headers={'Accept': 'application/json', 'Authorization': self.token}, data=json.dumps({"cash": cash, "bank": bank}))
        else:
            request = requests.patch(self.base_url + "guilds/{guild}/users/{user}".format(guild=guild, user=user), headers={'Accept': 'application/json', 'Authorization': self.token}, data=json.dumps({"cash": cash, "bank": bank, "reason": reason}))
        if self.fetch_errors(request) == 0:
            return json.loads(request.text)

    def get_leaderboard(self, guild, sort='total', limit=None, offset='1', page=None):
        if limit and page:
            request = requests.get(self.base_url + "guilds/{guild}/users?sort={sort}&limit={limit}&offset={offset}&page={page}".format(guild=guild, sort=sort, limit=limit, offset=offset, page=page), headers={"Authorization": self.token})
        if limit:
            request = requests.get(self.base_url + "guilds/{guild}/users?sort={sort}&limit={limit}&offset={offset}".format(guild=guild, sort=sort, limit=limit, offset=offset), headers={"Authorization": self.token})
        if page:
            request = requests.get(self.base_url + "guilds/{guild}/users?sort={sort}&offset={offset}&page={page}".format(guild=guild, sort=sort, offset=offset, page=page), headers={"Authorization": self.token})
        if not page and not limit:
            request = requests.get(self.base_url + "guilds/{guild}/users?sort={sort}&offset={offset}".format(guild=guild, sort=sort, offset=offset), headers={"Authorization": self.token})
        if self.fetch_errors(request) == 0:
            return json.loads(request.text)
        
    def get_guild(self, guild):
        request = requests.get(self.base_url + "guilds/{guild}".format(guild=guild), headers={"Authorization": self.token})
        if self.fetch_errors(request) == 0:
            return json.loads(request.text)

    def get_app_perms(self, guild):
        request = requests.get(self.base_url + "applications/@me/guilds/{}".format(guild), headers={"Authorization": self.token})
        if self.fetch_errors(request) == 0:
            if json.loads(request.text)["permissions"] == 1:
                return 1
            else:
                return 0


class invalidData(Exception):
    pass
class invalidPermissions(Exception):
    pass
class internetForbidden(Exception):
    pass
class unexpectedURL(Exception):
    pass
class requestOverload(Exception):
    pass
class serverError(Exception):
    pass
