'''
Created on Sep 8, 2013

@author: Andresta
'''
import os, json

from datetime import datetime as dt
from model.Dictionary import WordDictionary, TriggerDictionary
from model.Document import DocumentBuilder
from features.FeatureExtraction import FeatureExtraction
from classifier.Scaler import Scaler
from classifier.SVM import SVM
from sklearn.feature_extraction import DictVectorizer
from sklearn.svm import LinearSVC
from sklearn.externals import joblib

class Learning(object):
    '''
    Learning steps:
    1. define docs for learning
    2. extract features
    3. build input data for classifier
    4. build a model and save it
    '''

    # suffix and extension of id file
    DOCID_SUFFIX_EXT = "_doc_ids.json"
    
    # directory for saving svm model
    MODEL_DIR = "classifier/model"
    
    def __init__(self, source, dict_type):
        '''
        Constructor
        '''
        self.src = source
        self.dict_type = dict_type
        self.wdict = None
        self.tdict = None
        self.doc_builder = None
        self.extraction = None
                        
        self._set(dict_type)
                
        
        self.path = source + '/' + self.MODEL_DIR
            
    def _set(self, dict_type):
        """
        initialize dictionary type to be used in learning process
        initialize document builder
        initialize feature extraction
        """       
        
        self.wdict = WordDictionary(self.src)    
        self.wdict.load(dict_type)
               
        self.tdict = TriggerDictionary(self.src)
        self.tdict.load(dict_type)
        
        self.doc_builder = DocumentBuilder(self.src, self.wdict, self.tdict)         
        self.extraction = FeatureExtraction(self.src, self.wdict, self.tdict)
        
        
    def learn(self, docid_list_fname, scaler_function):
        X = []
        Y = []
          
        dt_start = dt.now()
        if not isinstance(docid_list_fname, list):
            # get list of doc ids from file
            path = self.src + '/' + docid_list_fname + self.DOCID_SUFFIX_EXT
            if not os.path.exists(path):
                raise ValueError(path + " is not exist")
            with open(path, 'r') as f: 
                doc_ids = json.loads(f.read())
        else:
            doc_ids = docid_list_fname
            
        # init feature
        print "now extracting", len(doc_ids), "docs"
        for doc_id in doc_ids:             
            o_doc = self.doc_builder.build(doc_id)
            samples = self.extraction.extract_tp(o_doc)            
            
            for sample in samples:
                X.append(sample[2])
                Y.append(sample[1])                   
        
        # print statistic
        pos = self.extraction.sample_pos
        neg = self.extraction.sample_neg
        stat = (pos, neg, pos + neg)
        print stat
        print "percentege of positif data:", pos * 100.0 / (pos + neg)        
        print "time to extract feature", dt.now() - dt_start
        
        # init svm classifier
        svm = SVM(self.src, "linear", grid_search = True, class_weight = 'auto')        
        svm.create()
        
        # fit training data
        svm.fit(X, Y)        
        

if __name__ == "__main__":
                            
    source = "E:/corpus/bionlp2011/project_data"
    dict_type = "train"
    doc_ids = ["PMC-2222968-04-Results-03","PMID-1682217", "PMID-8098618", "PMID-8675228", "PMC-1134658-06-Results-05"]
    doc_ids = "train"
    learning = Learning(source, dict_type)
    learning.learn(doc_ids, "norm")
    #print learning.vec
    
        
        