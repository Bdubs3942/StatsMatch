"""JSON endpoint for real player searches by name."""
from flask import Blueprint, current_app, jsonify, request

from ..services.api_football import PlayerAPIError, search_player_profiles

players_api = Blueprint('players_api', __name__, url_prefix='/api')


@players_api.get('/players')
def search_players():
    name = request.args.get('name', '').strip()
    if len(name) < 4:
        return jsonify(error='Provide a player name with at least 4 characters.'), 400

    api_key = current_app.config.get('API_FOOTBALL_KEY')
    if not api_key:
        return jsonify(error='Set the API_FOOTBALL_KEY environment variable before starting the app.'), 503

    try:
        data = search_player_profiles(name, api_key)
    except PlayerAPIError as error:
        return jsonify(error=str(error)), 502

    return jsonify(
        players=data['response'],
        paging=data.get('paging', {}),
    )
