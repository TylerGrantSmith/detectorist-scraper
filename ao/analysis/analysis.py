from collections import namedtuple
import os

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import base64
import string
import re

from collections import Counter
from nltk.corpus import stopwords
stopwords = stopwords.words('english')

df = pd.read_csv('research_paper.csv')









import pymongo
import datetime

class MongoLoader:

    def __init__(self):
        self.client = None
        self.db = None

    def __enter__(self):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def __exit__(self):
        self.client.close()

    @classmethod
    def new_connection(uri, db):
        self.mongo_uri = uri
        self.mongo_db = db
