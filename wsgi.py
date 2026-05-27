import sys
import os

path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.insert(0, path)

os.environ["DB_PATH"] = os.path.join(path, "data", "completada.db")

from a2wsgi import ASGIMiddleware
from app.main import app
from app.database import init_db

init_db()

application = ASGIMiddleware(app)
