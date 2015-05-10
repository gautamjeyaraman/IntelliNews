import sys
from numpy import array
import scipy.sparse as sp
import pickle
import json
from collections import defaultdict
import nltk
from sklearn.metrics import confusion_matrix, precision_score, recall_score

########

MODELS_PATH = "cyclone_server/model.bin"

########

lemmatize = nltk.stem.wordnet.WordNetLemmatizer().lemmatize
word_tokenize = nltk.word_tokenize
pos_tag = nltk.tag.pos_tag

print "Loading models"
model = pickle.load(open(MODELS_PATH, "rb"))
vectorizers = model['vectorizers']
chi_models = model['chi_models']
classifier = model['classifier']
metadata = model['metadata']
print "DONE"
print

def normalize(x, _type):
    nf_dict = {}
    if _type == "term":
        nf_dict = x.lower()
    elif _type == "pos":
        pos = pos_tag(word_tokenize(x))
        nf_dict = " ".join([y[1] for y in pos])
    elif _type == "pos_term":
        pos = pos_tag(word_tokenize(x))
        for item in pos:
            nf_dict[item[1] + "_" + lemmatize(item[0], 'v').lower()] = True
    elif _type == "pos_ngram_term":
        pos = pos_tag(word_tokenize(x))
        nf_dict = " ".join([y[1]+ "_" + lemmatize(y[0], 'v').lower() for y in pos])
    else:
        pos = pos_tag(word_tokenize(x))
        nf_dict["tokens"] = [y[0] for y in pos]
        nf_dict["pos_tags"] = [y[1] for y in pos]
        nf_dict["verbs"] = [lemmatize(y[0], 'v').lower() for y in pos if y[1][0] == "V" and len(y[0]) > 2]
        nf_dict["sent"] = x.lower()
        nf_dict["count"] = {"<per>": nf_dict["sent"].count("<per>"),
                            "<org>": nf_dict["sent"].count("<org>"),
                            "<loc>": nf_dict["sent"].count("<loc>")
                           }
    
    #CODE TO NORMALIZE, REMOVE THIS SOON
        del nf_dict["tokens"]
        del nf_dict["pos_tags"]
        for y in nf_dict["verbs"]:
            nf_dict["has_verb_" + y] = True
        del nf_dict["verbs"]
        del nf_dict["sent"]
        for y in nf_dict["count"].keys():
            nf_dict[y + "_count"] = nf_dict["count"][y]
        del nf_dict["count"]

    #Code to pre process data
    #TODO: normalize the text
    return nf_dict

def ngrams(_id, f, donorm = False, _type="term"):
    if donorm:
        f = normalize(f, _type)
    ftest  = [f]

    vectorizer = vectorizers[_id]
    X_test = vectorizer.transform(ftest)

    if chi_models:
        ch2 = chi_models[_id]
        X_test = ch2.transform(X_test)
    return X_test
      

def run(data):
    #print "Input text:"
    #print data
    test_ngram_data = [ngrams(k, data, donorm=True, _type=metadata[k]) for k in metadata.keys()]

    X_tt = sp.hstack(test_ngram_data)
    
    predictions = runClassifiers(X_tt)
    
    #print "TYPE: " + str(predictions[0][0])
    #print "CONFIDENCE: " + str(predictions[0][1])
    #print "SCORES: " + str(predictions)
    #print
    
    if predictions[0][1] > 0.75:
        return predictions[0][0]
    else:
        return "General"


eventDict = {0:"Entertainment",
             1: "Business",
             2: "Sports"}


def runClassifiers(X_test):
    
    preds = defaultdict(list)

    dense = [False, False, True, True]    # if model needs dense matrix
    
    X_test_dense = X_test.todense()

    for model in classifier:
        pred = model.predict_proba(X_test)
        for x in eventDict.keys():
            preds[x].append(array(pred[:,x]))
    predictProbs = []
    for x in eventDict.keys():
        #predictProbs.append(preds[x][0]*0.25 + preds[x][1]*0.25 + preds[x][2]*0.25 + preds[x][3]*0.25)
        predictProbs.append(preds[x][0]*0.4 + preds[x][1]*0.6)

    predictLabels = []
    for i in range(0,len(predictProbs[0])):
        checkProb = [predictProbs[j][i] for j in range(0,len(eventDict.keys())) ]
        #currentProb = max(checkProb)
        predictLabels.append([[eventDict[checkProb.index(currentProb)], currentProb] for currentProb in checkProb])

    final_pred = predictLabels[0]
    final_pred = sorted(final_pred, key=lambda x: x[1], reverse=True)
    
    return final_pred
    
    
def testModel(sentences, tag):
    correct = 0
    wrong = 0
    ch = defaultdict(lambda:{"correct":0,"wrong":0})
    y_pred = []
    for i in range(0,len(sentences)):
        #print "Sentence " + str(i)
        data = sentences[i]
        data = data.lower()
        correct_tag = tag[i].strip()
        '''if correct_tag[0] == "N" and correct_tag[:2] != "NC":
            correct_tag = "NONE"'''

        #test_ngram_data = [ngrams(j, data, donorm=True) for j in range(0, NO_OF_MODELS)]
        test_ngram_data = [ngrams(k, data, donorm=True, _type=metadata[k]) for k in metadata.keys()]
        X_tt = sp.hstack(test_ngram_data)
        
        predictions = runClassifiers(X_tt)
        
        predicted_tag = str(predictions[0][0])
        y_pred.append(predicted_tag)
        if correct_tag != predicted_tag:
            ch[correct_tag]["wrong"] += 1
            wrong += 1
            print data
            print "CORRECT TAG: " + correct_tag
            print "PREDICTED TAG: " + predicted_tag
        else:
            ch[correct_tag]["correct"] += 1
            correct += 1

    print "TOTAL: " + str(len(sentences))
    print "CORRECT: " + str(correct)
    print "WRONG: " + str(wrong)
    print "ACCURACY: " + str(correct*100.0/len(sentences))
    print
    for k in ch.keys():
        print k
        print "TOTAL: " + str(ch[k]["correct"] + ch[k]["wrong"])
        print "CORRECT: " + str(ch[k]["correct"])
        print "WRONG: " + str(ch[k]["wrong"])
        print "ACCURACY: " + str(ch[k]["correct"]*100.0/(ch[k]["correct"] + ch[k]["wrong"]))
        print

    #Check accuracy with confusion matrix
    tag = [str(s) for s in tag]
    cm = confusion_matrix(tag, y_pred)
    print
    print "CONFUSION MATRIX"
    print cm
    print
    '''pl.matshow(cm)
    pl.title('Confusion matrix')
    pl.colorbar()
    pl.ylabel('True label')
    pl.xlabel('Predicted label')
    pl.show()'''
    
    #Print out the precision and recall
    #print "PRECISION: " + str(precision_score(tag, y_pred, pos_label="ACQ"))
    #print "RECALL:" + str(recall_score(tag, y_pred, pos_label="ACQ"))



    
if __name__=="__main__":
    tool_type = "manual"
    if len(sys.argv) > 1:
        tool_type = sys.argv[1]
    if tool_type == "test":
        testSentences, testTags = read.getTestSet()
        testModel(testSentences, testTags)
    else:
        while True:
            print "Enter sentence:"
            txt = raw_input()
            run(txt)
