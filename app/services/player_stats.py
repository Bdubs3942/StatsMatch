"""Season statistics cached separately from player profiles."""
import csv
import json

from . import players

FIELDS = ('player_id', 'season', 'team_id', 'team_name', 'league_id', 'league_name',
          'statistics_json')

# API field spelling is intentional (appearences).
METRICS = (
    ('Appearances', 'games', 'appearences'),
    ('Starts', 'games', 'lineups'),
    ('Minutes played', 'games', 'minutes'),
    ('Rating', 'games', 'rating'),
    ('Goals', 'goals', 'total'),
    ('Assists', 'goals', 'assists'),
    ('Shots', 'shots', 'total'),
    ('Shots on target', 'shots', 'on'),
    ('Passes', 'passes', 'total'),
    ('Key passes', 'passes', 'key'),
    ('Pass accuracy (API value)', 'passes', 'accuracy'),
    ('Tackles', 'tackles', 'total'),
    ('Interceptions', 'tackles', 'interceptions'),
    ('Blocks', 'tackles', 'blocks'),
    ('Duels', 'duels', 'total'),
    ('Duels won', 'duels', 'won'),
    ('Dribble attempts', 'dribbles', 'attempts'),
    ('Successful dribbles', 'dribbles', 'success'),
    ('Fouls drawn', 'fouls', 'drawn'),
    ('Fouls committed', 'fouls', 'committed'),
    ('Yellow cards', 'cards', 'yellow'),
    ('Red cards', 'cards', 'red'),
    ('Saves', 'goals', 'saves'),
    ('Goals conceded', 'goals', 'conceded'),
    ('Penalties scored', 'penalty', 'scored'),
    ('Penalties missed', 'penalty', 'missed'),
)


def _load_rows():
    path = players.DATA_FILE.with_name('player_stats.csv')
    if not path.exists():
        return []
    with path.open(encoding='utf-8', newline='') as file:
        return list(csv.DictReader(file))


def load_player_statistics(player_id, season=2024):
    """None means never fetched; an empty list means fetched with no stats."""
    with players._lock:
        rows = [row for row in _load_rows()
                if row['player_id'] == str(player_id) and row['season'] == str(season)]
    if not rows:
        return None
    return [json.loads(row['statistics_json']) for row in rows if row['statistics_json']]


def save_player_statistics(player_id, response, season=2024):
    statistics = [stat for entry in response
                  if str((entry.get('player') or {}).get('id')) == str(player_id)
                  for stat in (entry.get('statistics') or [])]
    rows = []
    for stat in statistics:
        team, league = stat.get('team') or {}, stat.get('league') or {}
        rows.append({
            'player_id': str(player_id), 'season': str(season),
            'team_id': team.get('id'), 'team_name': team.get('name'),
            'league_id': league.get('id'), 'league_name': league.get('name'),
            'statistics_json': json.dumps(stat, ensure_ascii=False),
        })
    # Cache successful empty responses too, avoiding repeated calls on every visit.
    if not rows:
        rows = [dict.fromkeys(FIELDS, '')]
        rows[0].update(player_id=str(player_id), season=str(season))
    with players._lock:
        saved = [row for row in _load_rows()
                 if not (row['player_id'] == str(player_id) and row['season'] == str(season))]
        players._write_rows(players.DATA_FILE.with_name('player_stats.csv'), FIELDS, saved + rows)
    return statistics
