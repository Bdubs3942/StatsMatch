import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template


def create_app():
    load_dotenv(Path(__file__).resolve().parents[1] / '.env')
    app = Flask(__name__)
    app.config['API_FOOTBALL_KEY'] = os.environ.get('API_FOOTBALL_KEY', '').strip()
    from .routes.api import players_api
    from .routes.search import search_page
    from .routes.detail import detail_page
    from .routes.explore import explore_pages
    app.register_blueprint(search_page)
    app.register_blueprint(detail_page)
    app.register_blueprint(players_api)
    app.register_blueprint(explore_pages)

    @app.errorhandler(404)
    def not_found(error):
        return render_template('not_found.html', title='Page not found'), 404

    return app
