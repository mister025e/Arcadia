import os
import json

# We assume this module is imported from TopDown_Shooter context.
# Find the directory where this file lives, so we can place leaderboard.json there.
HERE = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_PATH = os.path.join(HERE, '..', 'data', 'leaderboard.json')


def load_leaderboard():
    """
    Read leaderboard.json (if it exists) and return a list of {name:str,score:int}.
    Otherwise return an empty list.
    """
    path = os.path.abspath(LEADERBOARD_PATH)
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            cleaned = []
            for e in data:
                if isinstance(e, dict) and 'name' in e and 'score' in e:
                    cleaned.append({'name': e['name'], 'score': e['score']})
            return sorted(cleaned, key=lambda x: x['score'], reverse=True)[:10]
        except Exception:
            return []
    else:
        return []


def save_leaderboard(leaderboard_list):
    """
    Overwrite leaderboard.json with the given top‐10 list of {name,score}.
    """
    os.makedirs(os.path.dirname(LEADERBOARD_PATH), exist_ok=True)
    with open(os.path.abspath(LEADERBOARD_PATH), 'w') as f:
        json.dump(leaderboard_list[:10], f, indent=2)


def add_score_to_leaderboard(name, score):
    """
    Insert a new (name,score) into the existing top‐10.
    If it belongs in the top‐10, keep the list sorted and truncated to 10.
    """
    lb = load_leaderboard()
    lb.append({'name': name, 'score': score})
    lb_sorted = sorted(lb, key=lambda x: x['score'], reverse=True)[:10]
    save_leaderboard(lb_sorted)
