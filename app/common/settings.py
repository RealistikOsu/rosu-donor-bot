import os

from dotenv import load_dotenv


def read_bool(value: str) -> bool:
    return value.lower() == "true"  # keep it simple


load_dotenv()


APP_ENV = os.environ["APP_ENV"]
APP_COMPONENT = os.environ["APP_COMPONENT"]

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

ROSU_DISCORD_GUILD_ID = int(os.environ["ROSU_DISCORD_GUILD_ID"])
ROSU_DISCORD_DONOR_ROLE_ID = int(os.environ["ROSU_DISCORD_DONOR_ROLE_ID"])
ROSU_DISCORD_ADMIN_LOGS_CHANNEL_ID = int(
    os.environ["ROSU_DISCORD_ADMIN_LOGS_CHANNEL_ID"],
)

READ_DB_SCHEME = os.environ["READ_DB_SCHEME"]
READ_DB_HOST = os.environ["READ_DB_HOST"]
READ_DB_PORT = int(os.environ["READ_DB_PORT"])
READ_DB_USER = os.environ["READ_DB_USER"]
READ_DB_PASS = os.environ["READ_DB_PASS"]
READ_DB_NAME = os.environ["READ_DB_NAME"]
READ_DB_USE_SSL = read_bool(os.environ["READ_DB_USE_SSL"])
READ_DB_CA_CERTIFICATE = os.environ["READ_DB_CA_CERTIFICATE"]
INITIALLY_AVAILABLE_READ_DB = os.environ["INITIALLY_AVAILABLE_READ_DB"]

# TODO: per-database settings?
DB_POOL_MIN_SIZE = int(os.environ["DB_POOL_MIN_SIZE"])
DB_POOL_MAX_SIZE = int(os.environ["DB_POOL_MAX_SIZE"])

SERVICE_READINESS_TIMEOUT = int(os.environ["SERVICE_READINESS_TIMEOUT"])
