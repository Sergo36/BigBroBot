import psycopg2

conn = psycopg2.connect(dbname="bla_bla_nodes", user="postgres", password="postgres", host="127.0.0.1", port="5432")
with conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE telegram_id = %(tid)s", {'tid': 502691086})
        (id, ) = cursor.fetchone()
        print(id)


conn.close()
