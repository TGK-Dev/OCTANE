
def make_db_temp(id):
        return {'_id': id, 'blacklist': [], 'welcome': None, 'mod_log': None, 'case': 1, 'starboard': {'channel': None, 'threshold': 5, 'self_star': False, 'toggle': False}, 'suggestion': None, 'join_roles': [],
                "Tickets": {'channel': None,'category': None, 'log_channel': None, 'transcript': {},'partner_ship': {'supprot_roles': [], 'ping_role': None}, 'support': {'supprot_roles': [], 'ping_role': None}}
        }

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content