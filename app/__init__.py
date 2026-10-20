from flask import Flask, render_template


def create_app():
    app = Flask(__name__)
    from .routes.search import search_page
    from .routes.detail import detail_page
    app.register_blueprint(search_page)
    app.register_blueprint(detail_page)

    @app.errorhandler(404)
    def not_found(error):
        return render_template('not_found.html', title='Page not found'), 404

    return app
