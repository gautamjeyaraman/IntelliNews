from cyclone_server.db.postgres import PostgresDatabase
from psycopg2.extras import NamedTupleConnection
from twisted.enterprise.adbapi import ConnectionPool


postgres_connection_settings = None


class DatabaseMixin(object):
    postgresql = None

    @classmethod
    def setup(cls, settings):
        conf = settings.get("postgresql_settings")
        if conf:
            postgres_connection_settings = dict(
                    host=conf.host, port=conf.port,
                    database=conf.database, user=conf.username,
                    password=conf.password,
                    cp_min=1, cp_max=conf.poolsize,
                    cp_reconnect=True, cp_noisy=settings['debug'],
                    connection_factory=NamedTupleConnection)
            pg_cpool = ConnectionPool("psycopg2", **postgres_connection_settings)
            cls.postgresql = pg_cpool
            print pg_cpool
        cls.preferred_db_class = PostgresDatabase
      
    def _connect(self):
        return self.postgresql

    @property
    def database(self):
        if not hasattr(self, '_db'):
            connection = self._connect()
            self._db = self.preferred_db_class(connection)
        return self._db
