from peewee import PostgresqlDatabase, Model

pg_db = PostgresqlDatabase(database='nodes', user='postgres', password='password',
                           host='127.0.0.1', port=5432)


class BaseModel(Model):
    class Meta:
        database = pg_db
