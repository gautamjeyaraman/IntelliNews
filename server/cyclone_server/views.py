import cyclone.web

class IndexHandler(cyclone.web.RequestHandler):

    def get(self):
        self.render("index.html")

class DocumentVieweHandler(cyclone.web.RequestHandler):

    def get(self):
        self.render("document_viewer.html")
