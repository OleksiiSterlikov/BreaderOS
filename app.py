import os

from flask import Flask

from routes.main import bp as main_bp


def env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def create_app() -> Flask:
    app = Flask(__name__)
    app.register_blueprint(main_bp)
    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", "5000"))
    debug = env_flag("APP_DEBUG", False)
    use_reloader = env_flag("APP_USE_RELOADER", False)
    use_debugger = env_flag("APP_USE_DEBUGGER", debug)

    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=use_reloader,
        use_debugger=use_debugger,
    )
