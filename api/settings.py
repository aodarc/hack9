import os

POSTGRES_DB = os.environ.get('POSTGRES_DB', "hack9")
POSTGRES_PASS = os.environ.get('POSTGRES_PASS', "hack9")
POSTGRES_USER = os.environ.get('POSTGRES_USER', "hack9")
POSTGRES_PORT = int(os.environ.get("POSTGRES_PORT", 5432))
POSTGRES_HOST = os.environ.get("POSTGRES_HOST", "postgres_db")

POSTGRES_URL = f"postgres://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
broker_url = ""
AWS_ACCESS_KEY = ""
AWS_SECRET_KEY = ""