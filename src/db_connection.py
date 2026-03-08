import psycopg2


def get_connection():

    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="fintek_db",
        user="finance",
        password="finance123"
    )

    return conn