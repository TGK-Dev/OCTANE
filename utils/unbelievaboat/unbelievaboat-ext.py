# Unbelievaboat extensions not in the base API
import unbelievaboat

class client(unbelievaboat.client):
    def reset_economy(self, guild):
        users = self.get_leaderboard(guild)
        for i in users:
            self.set_user_bal(guild, i["user_id"], cash=0, bank=0)
        
    def change_bal_all(self, guild, cash=0, bank=0):
        users = self.get_leaderboard(guild)
        for i in users:
            self.change_user_bal(guild, i["user_id"], cash=cash, bank=bank)
            
    def set_bal_all(self, guild, cash=0, bank=0):
        users = self.get_leaderboard(guild)
        for i in users:
            self.set_user_bal(guild, i["user_id"], cash=cash, bank=bank)
