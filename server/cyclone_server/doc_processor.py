import os
import json
from datetime import datetime
from cyclone_server.db.mixin import DatabaseMixin
from twisted.internet import defer
from cyclone import httpclient
from graphdb import RestClient
import topic_classifier


dataset = "dataset"
url = "http://localhost:9080/process_doc"


class DocProcessor(DatabaseMixin):
    @defer.inlineCallbacks
    def process(self):
        print "Starting the news processor pipeline"
        
        print "Reading the news articles"
        articles = []
        for f in os.listdir(dataset):
            if f.split(".")[-1] == "json":
                dataDict = json.loads(open(dataset+"/"+f, "r").read())
                dataDict["content"] = open(dataset+"/"+f.split(".")[0]+".txt", "r").read()
                dataDict["date"] = datetime.strptime(dataDict["date"], "%a, %d %b %Y %H:%M:%S +0530")
                dataDict["type"] = topic_classifier.run(dataDict["content"])
                articles.append(dataDict)

        print "Inserting documents into the database"
        for article in articles:
            self.database.insert_doc(article)

        print "Getting document IDS from the database"
        for article in articles:
            article['id'] = yield self.database.get_id_from_title(article["title"])

        print "Indexing the document in ES"
        for article in articles:
            yield self.search_engine.index_document(article)

        print "Get entities and store in Neo4j"
        graph = RestClient()
        for article in articles:
            entities = yield self.getEntities(article["id"], article["content"])
            entities["TOPIC"] = [article["type"]]
            graph.addDocument(article, entities)


    @defer.inlineCallbacks
    def getEntities(self, _id, text):
        args = {'id': _id, 'contents': text}
        headers = {'Content-Type': ['application/json']}
        response = yield httpclient.fetch(url, method='POST', headers=headers,
                                          postdata=json.dumps(args))
        resp = json.loads(response.body)
        respDict = {"LOC": [], "PER": [], "ORG": []}
        if resp:
            if "PERSON" in resp:
                respDict["PER"] = [tagx for tagx in resp["PERSON"]]
            if "LOCATION" in resp:
                respDict["LOC"] = [tagx for tagx in resp["LOCATION"]]
            if "ORGANIZATION" in resp:
                respDict["ORG"] = [tagx for tagx in resp["ORGANIZATION"]]
        defer.returnValue(respDict)
