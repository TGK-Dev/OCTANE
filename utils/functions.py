
def make_db_temp(id):
        return {'_id': id, 'blacklist': [], 'welcome': None, 'mod_log': None, 'case': 1, 'starboard': {'channel': None, 'threshold': 5, 'self_star': False, 'toggle': False}, 'suggestion': None,
                "Tickets": {'category': None, 'log_channel': None, 'partner_ship': {'support_roles': [], 'ping_roles': None}, 'support': {'support_roles': [], 'ping_roles': None}}
        }

def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content