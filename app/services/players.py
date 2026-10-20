"""Local CSV player database shared by both screens."""
import csv
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock

DATA_FILE = Path(__file__).resolve().parents[2] / 'data' / 'players.csv'
FIELDS = ('id', 'name', 'country', 'age', 'position', 'height', 'weight', 'photo')
_lock = RLock()


def _write_rows(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with NamedTemporaryFile(mode='w', encoding='utf-8', newline='',
                                dir=path.parent, delete=False) as file:
            temporary = Path(file.name)
            writer = csv.DictWriter(file, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def load_search_progress(query):
    """Read pagination for this exact search, independently of browser sessions."""
    with _lock:
        path = DATA_FILE.with_name('search_progress.csv')
        if path.exists():
            with path.open(encoding='utf-8', newline='') as file:
                for row in csv.DictReader(file):
                    if row['query'] == query.strip().casefold():
                        return {'page': int(row['page']), 'total': int(row['total'])}
    return {}


def save_search_progress(query, page, total):
    with _lock:
        path = DATA_FILE.with_name('search_progress.csv')
        rows = {}
        if path.exists():
            with path.open(encoding='utf-8', newline='') as file:
                rows = {row['query']: row for row in csv.DictReader(file)}
        key = query.strip().casefold()
        rows[key] = {'query': key, 'page': page, 'total': total}
        _write_rows(path, ('query', 'page', 'total'), rows.values())


def load_players():
    with _lock:
        if not DATA_FILE.exists():
            return []
        with DATA_FILE.open(encoding='utf-8', newline='') as file:
            return list(csv.DictReader(file))


def save_player_profiles(profiles):
    """Insert or update profiles by API player ID, preserving earlier searches."""
    players = []
    for entry in profiles:
        profile = entry.get('player', {})
        if profile.get('id') is None or not profile.get('name'):
            continue
        player = {field: str(profile.get(field) or '') for field in FIELDS}
        player['country'] = str(profile.get('nationality') or '')
        players.append(player)

    with _lock:
        saved = {player['id']: player for player in load_players()}
        saved.update({player['id']: player for player in players})
        _write_rows(DATA_FILE, FIELDS, saved.values())
    return players
