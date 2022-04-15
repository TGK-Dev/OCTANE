
def make_db_temp(id):
        return {'_id': id, 'blacklist': [], 'welcome': None, 'mod_log': None, 'case': 0, 'starboard': {'channel': None, 'threshold': 5, 'self_star': False, 'toggle': False}, 'suggestion': None}