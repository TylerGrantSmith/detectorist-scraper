import pymongo
import requests
import re
import pymongo
import string
import pickle
import nltk

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet

# mocked from https://github.com/nkpng2k/news_article_sentiment_analysis/blob/master/preprocessor_mk1.py

class PostPreprocessor(object):

    def __init__(self, stop_words='en', tfidf=True, lemmatize=False, vectorizer=None, lda_model=None):
        self.stop_words = _get_stop_words(stop_words)
        self.tfidf = tfidf
        self.lemmatize = lemmatize

    def _launch_mongo(self):
        mc = pymongo.MongoClient()
        db = mc[db_name]
        coll = db[coll_name]
        return coll

    def run(self):
        coll = self._launch_mongo()
        docs = []

        for doc in coll.find(snapshot=True).batch_size(25):
            try: 
                cleaned = self._correct_sentences(doc['message'])
                cleaned_tokens = self._tokenize(cleaned)

                docs.append(cleaned_tokens)
                success += 1
                print(f"Success #{success}")
            except TypeError:
                error_counter += 1
                print(f"TypeError, Moving On.  Error #{error_counter}")
            
        if self.tfidf:
            self.vectorizer = TfidfVectorizer(preprocessor = lambda x: x, tokenizer=lambda x: x, min_df = 0.00005, max_df = 0.90).fit(docs)
        else:
            self.vectorizer = CountVectorizer(preprocessor = lambda x: x, tokenizer=lambda x: x, min_df = 0.00005, max_df = 0.90).fit(docs)
        
        print(len(self.vectorizer.vocabulary_), 'training lda')

        vectorized_docs = self.vectorizer.transform(docs)
        self._train_lda(vectorized_docs)

        print('Pickling')

        with open(processor_filepath, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
        with open(lda_model_filepath, 'wb') as f:
            pickle.dump(self.lda_model, f)
    
        print("Success TfIdf Vectorizer and LDA model have been trained.")


if __name__ == "__main__":
    db_name = "ao"
    coll_name = "posts"
    uri = ''
    processor_filepath = ''
    classifier_filepath = ''
    lda_filepath = ''
    prep = TextProcessor(lemmatize=True)
    prep.run(processor_filepath, lda_filepath, db_name, coll_name, uri)



            
