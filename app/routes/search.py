"""Search screen: filter players by name, team, or position."""
from flask import Blueprint, render_template, request
from ..services.players import load_players

search_page = Blueprint('search', __name__)


@search_page.get('/')
def index():
    query = request.args.get('q', '').strip()
    players = load_players()
    matches = [
        player for player in players
        if query.casefold() in ' '.join(
            player[field] for field in ('name', 'team', 'position')
        ).casefold()
    ]
    return render_template(
        'search.html', title='Player directory', query=query,
        players=matches, total_players=len(players),
    )
