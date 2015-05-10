from twisted.internet import defer
from cyclone import httpclient
import json


HOST = "localhost"
PORT = 7474

base_url = 'http://%s:%d/db/data/' % (HOST, PORT)


class RestClient(object):

    @defer.inlineCallbacks
    def cypher_query(self, query, **kwargs):
        args = {'query': query}
        if kwargs:
            args["params"] = kwargs
        response = yield self.post_request('cypher', args)
        defer.returnValue(response)

    def __cypher_query_batch_request_body(self, qid, query, **kwargs):
        args = {'query': query}
        if kwargs:
            args["params"] = kwargs
        body = {
                'method': 'POST',
                'to': 'cypher',
                'body': args,
                'id': qid}
        return body

    @defer.inlineCallbacks
    def __post_batch_request(self, args):
        response = yield self.post_request('batch', args)
        defer.returnValue(response)

    @defer.inlineCallbacks
    def post_request(self, requestURL, requestArgs):
        headers = {'Content-Type': ['application/json']}
        url = base_url + requestURL
        data = json.dumps(requestArgs)
        response = yield httpclient.fetch(url, method='POST',
                headers=headers, postdata=data)
        response = json.loads(response.body)
        defer.returnValue(response)

    def addDocument(self, doc, entities):
        batch = []
        query = "START n=node:node_auto_index(idid={docId})"\
                " WITH count(*) as exists"\
                " WHERE exists=0 "\
                " CREATE (e {idid:{docId}, ictype:'doc', index:'in'})"
        batch.append(self.__cypher_query_batch_request_body(0, query, docId=doc["id"]))
        i = 1
        for key in entities.keys():
            for item in entities[key]:
                query = "START n=node:node_auto_index(inm={ent})"\
                        " WITH count(*) as exists"\
                        " WHERE exists=0 "\
                        " CREATE (e {inm:{ent}, itag:{entA}, ictype:{typ}, index:'in'})"
                batch.append(self.__cypher_query_batch_request_body(i, query, ent=item.lower(), entA=item, typ=key))
                i += 1
                query1 = "start d=node:node_auto_index(idid={docId}), e=node:node_auto_index(inm={ent})"\
                         " CREATE UNIQUE d-[r:HAS]->e"
                batch.append(self.__cypher_query_batch_request_body(i, query1, docId=doc["id"], ent=item.lower()))
                i += 1
        self.__post_batch_request(batch)

    @defer.inlineCallbacks
    def entitiesInDoc(self, doc_id):
        query = "START d=node:node_auto_index(idid={did})"\
                " MATCH d-[m:HAS]->t"\
                " RETURN t.itag"
        response = yield self.cypher_query(query, did=doc_id)
        response = response["data"]
        tags = []
        for x in response:
            tags.extend(x)
        defer.returnValue(tags)
