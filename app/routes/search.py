"""Search saved profiles first, then API-Football when no names match."""
from flask import Blueprint, current_app, render_template, request
from ..services.players import (
    load_players, save_player_profiles, load_search_progress, save_search_progress,
)
from ..services.api_football import PlayerAPIError, search_player_profiles

search_page = Blueprint('search', __name__)


@search_page.get('/')
def index():
    query = request.args.get('q', '').strip()
    saved_players = load_players()
    matches = sorted(saved_players, key=lambda player: int(player['id']))[:20] if not query else []
    error = None
    paging = {}
    status = 200
    page = request.args.get('page', 1, type=int)
    state = load_search_progress(query) if query else {}
    next_page = None
    if query:
        matches = [player for player in saved_players
                   if query.casefold() in player['name'].casefold()]
        continuing = (page > 1
                      and page == state.get('page', 0) + 1
                      and page <= state.get('total', 0))
        repeated = (page > 1 and page <= state.get('page', 0))
        if page < 1 or (page > 1 and not continuing and not repeated):
            error, status = 'Start a new search before loading the next page.', 400
        elif repeated:
            paging = {'current': state['page'], 'total': state['total']}
        elif matches and not continuing:
            if state:
                paging = {'current': state['page'], 'total': state['total']}
        elif len(query) < 4:
            error, status = 'No saved players match. Enter at least 4 characters to search the API.', 400
        elif not current_app.config.get('API_FOOTBALL_KEY'):
            error, status = 'Player search is unavailable. Set API_FOOTBALL_KEY before starting the app.', 503
        else:
            try:
                if continuing:
                    data = search_player_profiles(query, current_app.config['API_FOOTBALL_KEY'], page=page)
                else:
                    data = search_player_profiles(query, current_app.config['API_FOOTBALL_KEY'])
                new_players = save_player_profiles(data['response'])
                combined = {player['id']: player for player in matches}
                combined.update({player['id']: player for player in new_players})
                matches = list(combined.values())
                paging = data.get('paging') or {}
                save_search_progress(query, page, paging.get('total', page))
                state = {'page': page, 'total': paging.get('total', page)}
            except PlayerAPIError as exception:
                error, status = str(exception), 502
            except OSError:
                current_app.logger.exception('Unable to save player search results')
                error, status = 'Unable to save players. Please try again.', 500
        if state.get('page', 0) < state.get('total', 0):
            next_page = state['page'] + 1
    return render_template(
        'search.html', title='Player directory', query=query,
        players=matches, total_players=len(load_players()), error=error, paging=paging,
        next_page=next_page,
    ), status
