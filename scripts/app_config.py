import os
import json

FILE_PATH = os.path.join(os.path.dirname(__file__), 'app_config.json')

def load_config():
    if os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'r') as f:
            return json.load(f)
    return {"player": "mpv", "visto": {}}

def save_config(datos):
    with open(FILE_PATH, 'w') as f:
        json.dump(datos, f, indent=4)

def save_selected_player(player_option):
    config = load_config()
    config["player"] = player_option
    save_config(config)

def get_selected_player():
    config = load_config()
    return config.get('player', 'mpv')

def mark_as_seen(anime_title, episode_number):
    config = load_config()
    if anime_title not in config["visto"]:
        config["visto"][anime_title] = []
    if episode_number not in config["visto"][anime_title]:
        config["visto"][anime_title].append(episode_number)
    save_config(config)

def get_seen_animes():
    config = load_config()
    return config["visto"]

