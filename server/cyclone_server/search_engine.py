from cyclone import httpclient
import json
from twisted.internet import defer
import calendar


def timestamp(crdate):
    return calendar.timegm(crdate.timetuple()) * 1000


class SearchEngine(object):
    def __init__(self, conf):
        self.config = conf

    @defer.inlineCallbacks
    def index_document(self, doc):
        data = {
            "did": doc["id"],
            "title": doc["title"],
            "image_url": doc["img_url"],
            "content": doc["content"],
            "crdate": doc["date"].strftime('%Y%m%d'),
            "type": doc["type"]
        }

        index_url = 'http://%s:%s/%s/%s/%s?timestamp=%s' % (
                self.config.host, self.config.port,
                self.config.index, self.config.document_type,
                doc["id"], timestamp(doc["date"])
        )
        data = json.dumps(data)
        r = yield httpclient.fetch(index_url, method='POST', postdata=data)
        defer.returnValue(True)

    @defer.inlineCallbacks
    def search(self, term, limit=10, skip=0):
        term = term.replace("/", " ").strip()
        if term == '':
            return
        qry = {
            "from": skip, "size": limit,
            "_source": ["title", "did", "crdate", "type", "image_url"],
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
        jsondata = jsondata["hits"]["hits"]
        jsondata = [{"title": x["_source"]["title"],
                     "id": x["_source"]["did"],
                     "text": x["highlight"]["content"][0],
                     "img": x["_source"]["image_url"]
                    } for x in jsondata]
        defer.returnValue(jsondata)

    @defer.inlineCallbacks
    def getSimilarDocs(self, doc_id, limit=10, skip=0):
        search_url = 'http://%s:%s/%s/%s/%s/_mlt?mlt_fields=content' % (
                self.config.host, self.config.port,
                self.config.index, self.config.document_type,
                str(doc_id)
        )
        response = yield httpclient.fetch(search_url, method='POST')
        jsondata = json.loads(response.body)
        jsondata = jsondata["hits"]["hits"]
        jsondata = [x["_source"] for x in jsondata][:3]
        defer.returnValue(jsondata)

    @defer.inlineCallbacks
    def getDocument(self, doc_id):
        qry = {
            "query": {
                "bool": {
                    "must": [
                        {
                        "term": {
                            "doc.did": doc_id
                            }
                        }
                    ]
                }
            }
        }
        search_url = 'http://%s:%s/%s/%s/_search' % (
                self.config.host, self.config.port,
                self.config.index, self.config.document_type
        )
        response = yield httpclient.fetch(search_url, method='POST', postdata=json.dumps(qry))
        jsondata = json.loads(response.body)
        jsondata = jsondata["hits"]["hits"][0]["_source"]
        defer.returnValue(jsondata)
