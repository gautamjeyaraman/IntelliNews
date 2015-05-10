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
        ent = []
        dup = []
        for x in entities:
            if x[0].lower() not in dup:
                dup.append(x[0].lower())
                ent.append(x)
        entities = ent
        entities.sort(key=lambda x: len(x[0]))
        for x in entities:
            content = content.replace(x[0], '<a href="/search/' + x[0] + '" class="' + x[1] + '">' + x[0] + "</a>")
        doc["content"] = content
        self.render("document_viewer.html", doc=doc, sim=sim)

class HomeViewHandler(cyclone.web.RequestHandler, DatabaseMixin):

    @defer.inlineCallbacks
    def get(self):
        graph = RestClient()
        topics = yield graph.getTopics()
        topics = [[x[0], x[1][:3]] for x in topics]
        response = {}
        for item in topics:
            response[item[0]] = []
            for x in item[1]:
                doc = yield self.search_engine.getDocument(x)
                doc["content"] = doc["content"][:100] + "..."
                response[item[0]].append(doc)
        self.render("home.html", data=response)


class SearchViewHandler(cyclone.web.RequestHandler, DatabaseMixin):

    @defer.inlineCallbacks
    def get(self, term):
        results = yield self.search_engine.search(term)
        self.render("search.html", results=results, term=term)
