import os
import csv

HERE = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(HERE, '..', 'data', 'settings.csv')

# Default limits for each stat: (min, max, step)
STAT_LIMITS = {
    'rotation_speed':   (80, 160, 5),    # default 120, now ±40°
    'movement_speed':   (4, 8, 0.5),  # default 6, now ±2 units/sec
    'health_points':    (80, 150, 5),    # default 115, now ±35 HP
    'shot_power':       (10, 40, 1),    # default 25, now ±15 damage
    'shot_delay':       (0.3, 0.7, 0.1),  # default 0.5, now ±0.2 s
    'projectile_speed': (8, 16, 1),    # default 12, now ±4 units/sec
}

DEFAULTS = {
    'Player 1': { stat: (min+max)/2 for stat, (min, max, _) in STAT_LIMITS.items() },
    'Player 2': { stat: (min+max)/2 for stat, (min, max, _) in STAT_LIMITS.items() },
}

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return DEFAULTS.copy()
    settings = { 'Player 1':{}, 'Player 2':{} }
    with open(SETTINGS_PATH, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            p = row['player']
            if p in settings:
                for stat in STAT_LIMITS:
                    val = row.get(stat, '')
                    try:
                        settings[p][stat] = float(val)
                    except:
                        settings[p][stat] = DEFAULTS[p][stat]
    return settings

def save_settings(settings):
    os.makedirs(os.path.dirname(SETTINGS_PATH), exist_ok=True)
    with open(SETTINGS_PATH, 'w', newline='') as f:
        fieldnames = ['player'] + list(STAT_LIMITS.keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for p in ['Player 1','Player 2']:
            row = {'player':p}
            row.update({stat:settings[p][stat] for stat in STAT_LIMITS})
            writer.writerow(row)
