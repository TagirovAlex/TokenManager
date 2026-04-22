import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    host = app.config.get('SERVER_HOST', '0.0.0.0')
    port = app.config.get('SERVER_PORT', 5000)
    debug = app.config.get('SERVER_DEBUG', True)
    app.run(host=host, port=port, debug=debug)
