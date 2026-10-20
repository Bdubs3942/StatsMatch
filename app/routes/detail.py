"""Detail screen: load one player and calculate per-90 statistics."""
from flask import Blueprint, render_template, request
from ..services.players import load_players

detail_page = Blueprint('detail', __name__)


def per_90(total, minutes):
    return f'{int(total) * 90 / int(minutes):.2f}' if int(minutes) else '—'


@detail_page.get('/players/<player_id>')
def show(player_id):
    player = next((p for p in load_players() if p['id'] == player_id), None)
    if player is None:
        return render_template('not_found.html', title='Player not found'), 404
    return render_template(
        'detail.html', title=player['name'], player=player,
        query=request.args.get('q', '').strip(),
        goals_per_90=per_90(player['goals'], player['minutes']),
        assists_per_90=per_90(player['assists'], player['minutes']),
    )
