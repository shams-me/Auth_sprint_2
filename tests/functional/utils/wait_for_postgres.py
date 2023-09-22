import psycopg
from psycopg import OperationalError

from functional.settings import test_settings
from functional.utils.backoff import backoff


# TODO: decide if we need this.
@backoff()
def wait_for_postgres():
    try:
        conn = psycopg.connect(**test_settings.postgres_credentials)
        conn.close()
        return
    except OperationalError:
        raise Exception("PostgreSQL is not ready...")


if __name__ == "__main__":
    wait_for_postgres()
