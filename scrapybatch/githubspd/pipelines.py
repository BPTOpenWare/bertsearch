# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import json
import copy

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from bert_serving.client import BertClient
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

INDEX_NAME = os.environ['INDEX_NAME']
INDEX_BERT_NAME = os.environ['INDEX_BERT_NAME']

class GithubspdPipeline:

    @staticmethod
    def create_bert_document(item, emb, index_name):
        return {
             '_op_type': 'index',
             '_index': index_name,
             'url': item.get('url'),
             'text': item.get('text'),
             'title': item.get('title'),
             'text_vector': emb
        }
    
    @staticmethod
    def create_document(item, index_name):
        return {
             '_op_type': 'index',
             '_index': index_name,
             'url': item.get('url'),
             'text': item.get('text'),
             'title': item.get('title')
        }

    def process_item(self, item, spider):
    
        # clean whitespace
        itemtextclean = ' '.join(item.get('text').split())
        itemtextclean.strip('\n')
        
        item['text'] = itemtextclean
        
        stddoc = self.create_document(item, INDEX_NAME)
        
        # split at 200 chars
        berttexts = self.get_split(item.get('text'))
        
        # call bert
        alldocs = []
        for doc, emb in zip(berttexts, self.bulk_predict(berttexts)):
            tempItem = copy.deepcopy(item)
            tempItem['text'] = doc
            d = self.create_bert_document(tempItem, emb, INDEX_BERT_NAME)
            alldocs.append(d)
            
        alldocs.append(stddoc)
        
        # index
        client = Elasticsearch('elasticsearch:9200')
        bulk(client, alldocs)
        
        return item
        
        
    @staticmethod
    def get_split(text1):
        l_total = []
        l_parcial = []
        if len(text1.split())//150 >0:
            n = len(text1.split())//150
        else: 
            n = 1
        for w in range(n):
            if w == 0:
                l_parcial = text1.split()[:200]
                l_total.append(" ".join(l_parcial))
            else:
                l_parcial = text1.split()[w*150:w*150 + 200]
                l_total.append(" ".join(l_parcial))
        return l_total
  
    @staticmethod  
    def bulk_predict(docs, batch_size=256):
        """Predict bert embeddings."""
        bc = BertClient(ip='bertserving', output_fmt='list')
        for i in range(0, len(docs), batch_size):
            batch_docs = docs[i: i+batch_size]
            embeddings = bc.encode(batch_docs, blocking=True)
            for emb in embeddings:
                yield emb

