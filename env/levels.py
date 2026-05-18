"""
env/levels.py
Defines 5 levels for the grid world.
"""

LEVELS = {
    "level_1_simple_path": [
        "S..G",
        "####",
    ],
    "level_2_trap": [
        "S..G",
        ".T..",
        "####",
    ],
    "level_3_key_door": [
        "S.K.DG",
        "######",
    ],
    "level_4_enemy_timing": [
        "S..E.G",
        ".T....",
        "######",
    ],
    "level_5_conflict": [
        "S.B..K..D..G",
        ".T.M.E.T.M..",
        "############",
    ],
}

def get_level(name):
    if name not in LEVELS:
        raise ValueError(f"Unknown level: {name}")
    return LEVELS[name]

def list_levels():
    return list(LEVELS.keys())
