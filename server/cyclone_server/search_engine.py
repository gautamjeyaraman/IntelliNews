from cyclone_server import httpclient
import json
from twisted.internet import defer
import calendar


def timestamp(crdate):
    return calendar.timegm(crdate.timetuple()) * 1000


class SearchEngine(object):
    def __init__(self, conf):
        self.config = conf

    def index_document(self, doc):
        data = {
            "did": doc["id"],
            "title": doc["title"],
            "type": doc["type"],
            "content": doc["content"],
            "crdate": doc["date"].strftime(consts.YYYMMDD_DATE_FORMAT)
        }

        index_url = 'http://%s:%s/%s/%s/%s?timestamp=%s' % (
                self.config.host, self.config.port,
                self.config.index, self.config.document_type,
                doc["id"], timestamp(doc["date"])
        )
        data = json.dumps(data)
        yield httpclient.fetch(index_url, method='POST', postdata=data)
        defer.returnValue(True)

    @defer.inlineCallbacks
    def search(self, term, limit=10, skip=0):
        term = term.replace("/", " ").strip()
        if term == '':
            return
        qry = {
            "from": skip, "size": limit,
            "_source": ["title", "content", "did", "crdate", "type"],
            "query": {
                "filtered": {
                    "query": {
                        "query_string": {
                            "fields": ["title", "_all"],
                            "query": term
                        }
                    },
                  }
                },

                "highlight": {
                    "fields": {
                        "content": {
                            "fragment_size": 100,
                            "number_of_fragments": 1
                                },
                                "title": {}
                }
            }
        }

        search_url = 'http://%s:%s/%s/_search' % (self.config.host, self.config.port, self.config.index)
        response = yield httpclient.fetch(search_url, method='GET', postdata=json.dumps(qry))
        jsondata = json.loads(response.body)
        defer.returnValue(jsondata)

    @defer.inlineCallbacks
    def getSimilarDocs(self, doc_id, limit=10, skip=0):
        qry = {
                "from": skip, "size": limit,
                "_source": ["title", "content", "did", "crdate", "type"],
                "query": {
                    "filtered": {
                        "query": {
                            "more_like_this": {
                                "fields": ["content"],
                                "ids": [doc_id],
                                "min_term_freq": 2,
                                "min_word_len": 3
                                }
                            },
                        "filter": {
                             "not": {
                                    "term": {"did":doc_id}
                             }
                        }
                    }
                }

        search_url = 'http://%s:%s/%s/%s/_search' % (
                self.config.host, self.config.port,
                self.config.index, self.config.document_type)
        response = yield httpclient.fetch(search_url, method='POST', postdata=json.dumps(qry))
        jsondata = json.loads(response.body)
        defer.returnValue(jsondata)

