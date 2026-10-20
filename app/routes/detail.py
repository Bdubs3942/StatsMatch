"""Detail screen: load one player and calculate per-90 statistics."""
from flask import Blueprint, current_app, render_template, request
from ..services.players import load_players
from ..services.api_football import PlayerAPIError, get_player_statistics
from ..services.player_stats import METRICS, load_player_statistics, save_player_statistics

detail_page = Blueprint('detail', __name__)


def per_90(total, minutes):
    if total is None or not minutes:
        return '—'
    return f'{float(total) * 90 / float(minutes):.2f}'


@detail_page.get('/players/<player_id>')
def show(player_id):
    player = next((p for p in load_players() if p['id'] == player_id), None)
    if player is None:
        return render_template('not_found.html', title='Player not found'), 404
    season = 2024
    error = None
    status = 200
    statistics = []
    try:
        statistics = load_player_statistics(player_id, season)
        if statistics is None:
            api_key = current_app.config.get('API_FOOTBALL_KEY')
            if not api_key:
                error, status = 'Season statistics are unavailable. Configure API_FOOTBALL_KEY.', 503
            else:
                data = get_player_statistics(player_id, api_key, season)
                statistics = save_player_statistics(player_id, data['response'], season)
    except PlayerAPIError as exception:
        error, status = str(exception), 502
    except (OSError, ValueError):
        current_app.logger.exception('Unable to read or save season statistics')
        error, status = 'Unable to read or save season statistics. Please try again.', 500
    return render_template(
        'detail.html', title=player['name'], player=player,
        query=request.args.get('q', '').strip(),
        statistics=statistics or [], metrics=METRICS, season=season, error=error,
        per_90=per_90,
    ), status
