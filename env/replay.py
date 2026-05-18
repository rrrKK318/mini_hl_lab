"""
env/replay.py
Save human-readable replay JSON for each episode.
"""
import json
import os
from datetime import datetime

REPLAY_DIR = "data/replays"

def ensure_dir():
    os.makedirs(REPLAY_DIR, exist_ok=True)

def save_replay(level_name, agent_name, episode_data):
    ensure_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{level_name}_{agent_name}_{timestamp}.json"
    filepath = os.path.join(REPLAY_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(episode_data, f, indent=2, ensure_ascii=False)
    return filepath
