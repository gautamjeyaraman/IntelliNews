import query


class PostgresDatabase(object):
    def __init__(self, connection):
        self.connection = connection

    def insert_doc(self, doc):
        return self.connection.runOperation(
            query._CREATE_DOC, (doc["title"], doc["date"], doc["img_url"]))

    def get_id_from_title(self, title):
        return self.connection.runQuery(
            query._GET_ID_FROM_TITLE, (title, )).\
            addCallback(lambda x: x[0].id)
