import os
import json

FILE_PATH = os.path.join(os.path.dirname(__file__), 'player_config.json')

def save_selected_player(player_option):
    config = {"player": player_option}
    with open(FILE_PATH, 'w') as f:
        json.dump(config, f)

def get_selected_player():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as f:
            config = json.load(f)
            return config.get('player', 'mpv')
    return 'mpv'


    