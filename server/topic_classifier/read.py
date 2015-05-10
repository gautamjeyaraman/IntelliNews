import os
import json
from collections import defaultdict


topics = ["entertainment", "business", "sports"]


data = defaultdict(list)

for topic in topics:
    for f in os.listdir(topic):
        data[topic].append(open(topic+"/"+f, "r").read())


def getTrainSet():
    content = []
    for topic in topics:
        content.extend([[x, topics.index(topic)] for x in data[topic] ])
    return content
