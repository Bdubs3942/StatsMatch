"""Reusable API-Football player profile lookup."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PlayerAPIError(Exception):
    """The player data provider could not complete the request."""


def search_player_profiles(name, api_key, page=1):
    parameters = {'search': name}
    if page != 1:
        parameters['page'] = page
    query = urlencode(parameters)
    request = Request(
        f'https://v3.football.api-sports.io/players/profiles?{query}',
        headers={'x-apisports-key': api_key, 'Accept': 'application/json'},
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        raise PlayerAPIError('Unable to fetch players from API-Football.') from error

    if not isinstance(data, dict) or data.get('errors'):
        raise PlayerAPIError('API-Football rejected the request. Check your API key and plan limits.')
    if not isinstance(data.get('response'), list):
        raise PlayerAPIError('API-Football returned an unexpected response.')
    return data
