"""Reusable API-Football player profile lookup."""
import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class PlayerAPIError(Exception):
    """The player data provider could not complete the request."""


def _error_details(errors, api_key):
    if isinstance(errors, dict):
        message = '; '.join(f'{key}: {value}' for key, value in errors.items())
    elif isinstance(errors, list):
        message = '; '.join(str(value) for value in errors)
    else:
        message = str(errors)
    return message.replace(api_key, '[redacted]') if api_key else message


def search_player_profiles(name, api_key, page=1):
    parameters = {'search': name}
    if page != 1:
        parameters['page'] = page
    return _get('players/profiles', parameters, api_key)


def get_player_statistics(player_id, api_key, season=2024):
    return _get('players', {'id': player_id, 'season': season}, api_key)


def _get(endpoint, parameters, api_key):
    """Shared authentication, transport and response validation."""
    query = urlencode(parameters)
    request = Request(
        f'https://v3.football.api-sports.io/{endpoint}?{query}',
        headers={'x-apisports-key': api_key, 'Accept': 'application/json'},
    )
    try:
        with urlopen(request, timeout=10) as response:
            data = json.load(response)
    except HTTPError as error:
        details = ''
        try:
            body = json.load(error)
            if isinstance(body, dict) and body.get('errors'):
                details = ': ' + _error_details(body['errors'], api_key)
        except (ValueError, OSError):
            pass
        raise PlayerAPIError(f'API-Football returned HTTP {error.code}{details}') from error
    except (URLError, TimeoutError, OSError, ValueError) as error:
        raise PlayerAPIError('Unable to fetch players from API-Football.') from error

    if not isinstance(data, dict):
        raise PlayerAPIError('API-Football returned an unexpected response.')
    if data.get('errors'):
        raise PlayerAPIError('API-Football: ' + _error_details(data['errors'], api_key))
    if not isinstance(data.get('response'), list):
        raise PlayerAPIError('API-Football returned an unexpected response.')
    return data
