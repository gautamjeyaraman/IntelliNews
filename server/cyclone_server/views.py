import cyclone.web
from twisted.internet import defer
from graphdb import RestClient
from cyclone_server.db.mixin import DatabaseMixin

class IndexHandler(cyclone.web.RequestHandler):

    def get(self):
        self.render("index.html")


class DocumentViewHandler(cyclone.web.RequestHandler, DatabaseMixin):

    @defer.inlineCallbacks
    def get(self, doc_id):
        doc = yield self.search_engine.getDocument(doc_id)
        sim = yield self.search_engine.getSimilarDocs(doc_id)
        graph = RestClient()
        entities = yield graph.entitiesInDoc(doc_id)
        content = doc["content"]
        entities = list(set(entities))
        for x in entities:
            content = content.replace(x, '<a href="/search/' + x + '">' + x + "</a>")
        doc["content"] = content
        self.render("document_viewer.html", doc=doc, sim=sim)

class HomeViewHandler(cyclone.web.RequestHandler):

    def get(self):
        self.render("home.html")


class SearchViewHandler(cyclone.web.RequestHandler, DatabaseMixin):

    @defer.inlineCallbacks
    def get(self, term):
        results = yield self.search_engine.search(term)
        self.render("search.html", results=results, term=term)
