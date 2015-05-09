import query


class PostgresDatabase(object):
    def __init__(self, connection):
        self.connection = connection

    def get_sample(self, sample):
        return self.connection.runQuery(
            query._SAMPLE, (sample, )).\
            addCallback(self._got_sample)
            
    def _got_sample(self, rows):
        if rows:
            return (row[0].id, row[0].title)
