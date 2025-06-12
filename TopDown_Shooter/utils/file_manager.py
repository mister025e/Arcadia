import os
import csv

# We assume this module is imported from TopDown_Shooter context.
# Path to leaderboard.csv in the data folder
HERE = os.path.dirname(os.path.abspath(__file__))
LEADERBOARD_PATH = os.path.join(HERE, '..', 'data', 'leaderboard.csv')


def load_leaderboard():
    """
    Read leaderboard.csv (if it exists) and return a list of {'name':str,'score':int},
    sorted descending by score, top 10 only.
    """
    path = os.path.abspath(LEADERBOARD_PATH)
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get('name', '').strip()
            try:
                score = int(row.get('score', '0'))
            except ValueError:
                continue
            if name:
                entries.append({'name': name, 'score': score})
    # sort and return top 10
    entries.sort(key=lambda e: e['score'], reverse=True)
    return entries[:10]


def save_leaderboard(entries):
    """
    Write the given list of {'name','score'} to leaderboard.csv (top 10).
    Creates the data directory if needed.
    """
    os.makedirs(os.path.dirname(LEADERBOARD_PATH), exist_ok=True)
    path = os.path.abspath(LEADERBOARD_PATH)
    # Only keep top 10
    to_write = sorted(entries, key=lambda e: e['score'], reverse=True)[:10]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'score'])
        writer.writeheader()
        for e in to_write:
            writer.writerow({'name': e['name'], 'score': e['score']})


def add_score_to_leaderboard(name, score):
    """
    Add (name, score) to the CSV leaderboard if it belongs in the top 10.
    """
    if not name:
        return
    entries = load_leaderboard()
    entries.append({'name': name, 'score': score})
    save_leaderboard(entries)