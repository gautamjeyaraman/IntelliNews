from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn import linear_model, svm, ensemble, neighbors
from sklearn.grid_search import RandomizedSearchCV
from sklearn import cross_validation
from numpy import array
import scipy.sparse as sp
import numpy as np
import scipy
from time import time
from operator import itemgetter
import read
import pickle
import nltk
import sys

########

MODELS_PATH = "model.bin"

########

model = {'vectorizers': [],
         'chi_models': [],
         'classifier': None}

lemmatize = nltk.stem.wordnet.WordNetLemmatizer().lemmatize
word_tokenize = nltk.word_tokenize
pos_tag = nltk.tag.pos_tag

def normalize(f, all_pos, _type):
    nf = []
    count = 1
    for x in f:
        pos = all_pos[f.index(x)]
        nf_dict = {}
        if _type == "term":
            nf.append(x.lower())
        elif _type == "pos":
            nf.append(" ".join([y[1] for y in pos]))
        elif _type == "pos_term":
            for item in pos:
                nf_dict[item[1] + "_" + lemmatize(item[0], 'v').lower()] = True
            nf.append(nf_dict)
        elif _type == "pos_ngram_term":
            nf.append(" ".join([y[1]+ "_" + lemmatize(y[0], 'v').lower() for y in pos]))
        else:
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
            
            nf.append(nf_dict)
        sys.stdout.write("Processing progress: %d   \r" % (count) )
        sys.stdout.flush()
        count += 1
    #Code to pre process data
    #TODO: normalize the text
    return nf

def ngrams(data, labels, mn=1, mx=1, nm=500, _type = "term", donorm = False, stopwords = True, verbose = True, analyzer_char = False):
    if donorm:
        data = data[_type]
    
    ftrain = data
    y_train = labels
    
    t0 = time()
    analyzer_type = 'word'
    if analyzer_char:
        analyzer_type = 'char'
        
    if _type == "feature" or _type == "pos_term":
        vectorizer = DictVectorizer()
    elif stopwords:
        vectorizer = TfidfVectorizer(ngram_range=(mn, mx),stop_words='english',analyzer=analyzer_type,sublinear_tf=True)
    else:
        vectorizer = TfidfVectorizer(ngram_range=(mn, mx),sublinear_tf=True,analyzer=analyzer_type)

    if verbose:
        print "extracting ngrams... where n is [%d,%d]" % (mn,mx)
    
    X_train = vectorizer.fit_transform(ftrain)
    model['vectorizers'].append(vectorizer)
    
    if verbose:
        print "done in %fs" % (time() - t0), X_train.shape

    y = array(y_train)    
    
    numFts = nm
    '''if numFts < X_train.shape[1]:
        t0 = time()
        ch2 = SelectKBest(chi2, k=numFts)
        X_train = ch2.fit_transform(X_train, y)
        model['chi_models'].append(ch2)
        assert sp.issparse(X_train)'''

    if verbose:
        print "Extracting best features by a chi-squared test.. ", X_train.shape    
    return X_train, y
      

def run(verbose = True):
    t0 = time()

    train = read.getTrainSet()
    labels  = array([x[1] for x in train])
    data = [x[0] for x in train]
    pos = [pos_tag(word_tokenize(x)) for x in data]

    new_data = {}
    #new_data['pos'] = normalize(data, pos, 'pos')
    new_data['term'] = normalize(data, pos,  'term')
    #new_data['pos_term'] = normalize(data, pos, 'pos_term')
    #new_data["pos_ngram_term"] = normalize(data, pos, "pos_ngram_term")
    #new_data['feature'] = normalize(data, pos, 'feature')
    
    data = new_data

    # The number of ngrams to select was optimized by CV
    X_train1, y_train = ngrams(data, labels, 1, 1, 2000, donorm = True, verbose = verbose, _type="term")
    X_train2, y_train = ngrams(data, labels, 2, 2, 4000, donorm = True, verbose = verbose, _type="term")
    X_train3, y_train = ngrams(data, labels, 3, 3, 100,  donorm = True, verbose = verbose, _type="term")
    X_train4, y_train = ngrams(data, labels, 4, 4, 1000, donorm = True, verbose = verbose, analyzer_char = True, _type="term")    
    X_train5, y_train = ngrams(data, labels, 5, 5, 1000, donorm = True, verbose = verbose, analyzer_char = True, _type="term")
    X_train6, y_train = ngrams(data, labels, 3, 3, 2000, donorm = True, verbose = verbose, analyzer_char = True, _type="term")
    #X_train7, y_train = ngrams(data, labels, donorm = True, verbose = verbose, _type="feature")
    #X_train8, y_train = ngrams(data, labels, 2, 2, 4000, donorm = True, verbose = verbose, _type="pos")
    #X_train9, y_train = ngrams(data, labels, 3, 3, 100,  donorm = True, verbose = verbose, _type="pos")
    #X_train91, y_train = ngrams(data, labels, 4, 4, 100,  donorm = True, verbose = verbose, _type="pos")
    #X_train10, y_train = ngrams(data, labels, 5, 5, 100,  donorm = True, verbose = verbose, _type="pos")
    #X_train110, y_train = ngrams(data, labels, donorm = True, verbose = verbose, _type="pos_term")
    #X_train11, y_train = ngrams(data, labels, 4, 4, 4000, donorm = True, verbose = verbose, _type="pos_ngram_term")
    #X_train12, y_train = ngrams(data, labels, 2, 2, 4000, donorm = True, verbose = verbose, _type="pos_ngram_term")
    #X_train13, y_train = ngrams(data, labels, 3, 3, 4000,  donorm = True, verbose = verbose, _type="pos_ngram_term")

    X_tn = sp.hstack([X_train1, X_train2, X_train3, X_train4, X_train5, X_train6])
    
    if verbose:
        print "######## Total time for feature extraction: %fs" % (time() - t0), X_tn.shape
    
    models = runClassifiers(X_tn, labels)

    model['classifier'] = models

    model['metadata'] = {0: "term", 1: "term", 2: "term", 3: "term", 4: "term", 5: "term"}

    pickle.dump(model, open(MODELS_PATH, "wb"))
    
    print "DONE"


# Utility function to report best scores
def report(grid_scores, n_top=3):
    top_scores = sorted(grid_scores, key=itemgetter(1), reverse=True)[:n_top]
    for i, score in enumerate(top_scores):
        print("Model with rank: {0}".format(i + 1))
        print("Mean validation score: {0:.3f} (std: {1:.3f})".format(
              score.mean_validation_score,
              np.std(score.cv_validation_scores)))
        print("Parameters: {0}".format(score.parameters))
        print("")
        
        
def runClassifiers(X_train, y_train, y_test = None, verbose = True):
    
    models = [  linear_model.LogisticRegression(C=3,  class_weight='auto'), \
                svm.SVC(C=0.3,kernel='linear', probability=True, class_weight='auto') ,  \
                #neighbors.KNeighborsClassifier(), \
                #ensemble.RandomForestClassifier(n_estimators=500, n_jobs=4, max_features = 15, min_samples_split=10, random_state = 100),  \
                #ensemble.GradientBoostingClassifier(n_estimators=400, subsample = 0.5, min_samples_split=15, random_state = 100) \
              ]
    dense = [False, False, True, True, True]    # if model needs dense matrix
    
    X_train_dense = X_train.todense()
    
    #params = {'C': scipy.stats.expon(scale=1), 'kernel': ['linear'], 'class_weight':['auto', None]}
    
    trained_models = []
    for ndx, model in enumerate(models):
        t0 = time()
        #random_search = RandomizedSearchCV(model, param_distributions=params, n_iter=100)

        print "Training: ", model, 20 * '_'        
        if dense[ndx]:
            model.fit(X_train_dense, y_train)
        else:
            model.fit(X_train, y_train)
            #random_search.fit(X_train, y_train)
            #report(random_search.grid_scores_)
        scores = cross_validation.cross_val_score(model, X_train, y_train, cv=11)
        print
        print "!!!!!!!!!!!!!11111111111111111111111111111!!!!!!!!!!!!!!!!!!!!"
        print scores
        print("ACCURACY: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2))
        print "!!!!!!!!!!!!!!111111111111111111111111111!!!!!!!!!!!!!!!!!!!!!!"
        print
        print "Training time: %0.3fs" % (time() - t0)
        trained_models.append(model)

    return trained_models

    
if __name__=="__main__":
    run()
