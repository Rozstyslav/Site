from flask import Flask

def create_app():
    app = Flask(__name__)

    from .routes.web_routes import web as web_routes
    from .routes.api_routes import api as api_routes
    from .routes.http_m import http_m as http_m_routes

    app.register_blueprint(web_routes)
    app.register_blueprint(api_routes, url_prefix='/api')
    app.register_blueprint(http_m_routes, url_prefix='/http_m')

    return app