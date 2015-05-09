import cyclone.web
from cyclone_server.db.mixin import DatabaseMixin
from cyclone_server import routes
from doc_processor import DocProcessor


should_process = True

class Application(cyclone.web.Application):
    def __init__(self, settings):
        handlers = routes.routes

        # Set up database connections
        DatabaseMixin.setup(settings)

        #Processing pipeline
        if should_process:
            processor = DocProcessor()
            processor.process()

        cyclone.web.Application.__init__(self, handlers, **settings)
