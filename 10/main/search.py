# coding: utf-8

from __future__ import unicode_literals
import os
from collections import defaultdict
import sys
from vbcode import decode
import pickle
import numpy as np
from unicodedata import normalize

def get_titles(input_filename):
  with open(input_filename,'r',10000) as f:
      titles = defaultdict(dict)
      for line in f:
          try:
              doc_id, cat_id, url, title = line.strip().split(b'\t')
              titles[int(doc_id)] = {'title': title, 'url':url}
          except Exception as e:
              doc_id, cat_id, url = line.strip().split(b'\t')
              titles[int(doc_id)] = {'title':'', 'url': url}
  return titles

def load_index(index_filename):
  with open(index_filename, 'r') as f:
      index = pickle.load(f)
  return index

def search(titles, index, query, text_path):
    query = normalize('NFKC',query.decode('utf-8'))
    for q in query.strip().split(' '):
        print("search:", query)
        if len(q.strip())==0: continue

        bi_gram_qs = get_bigram_queries(q.strip())
        if not index[bi_gram_qs[0]]: continue

        # doc_Get the intersection of id
        doc_ids = set( get_decoded_data(index[bi_gram_qs[0]].keys()[0]) )
        for bi_gram_q in bi_gram_qs[1:]:
            doc_ids = doc_ids & set( get_decoded_data(index[bi_gram_q].keys()[0]) )
        doc_ids = list(doc_ids)

        if len(doc_ids)==0: continue

        location_lists = []
        for bi_gram_q in bi_gram_qs:
            # doc_Get the index list of id
            all_doc_ids = get_decoded_data( index[bi_gram_q].keys()[0] )
            idx_list = [ all_doc_ids.index(doc_id) for doc_id in doc_ids ]
            #Get the location for each document in each query
            location_list = [ get_decoded_data(index[bi_gram_q].values()[0][idx]) for idx in idx_list ]
            location_lists.append( location_list )

        doc_id_idx_idx, locations4snippet = check_sequence(location_lists)
        #print "doc_id_idx_idx:", doc_id_idx_idx
        #print "doc_ids:", doc_ids
        squewed_doc_ids = ( doc_ids[doc_id_idx] for doc_id_idx in doc_id_idx_idx )
        for doc_id, location in zip( squewed_doc_ids, locations4snippet):
            print "doc_id:",doc_id
            if doc_id in titles:
                print titles[doc_id]['title']
                if location<50:
                    start = 0
                else:
                    start = location - 50
                end = location + 50
                with open(text_path+'/'+str(doc_id), 'r') as f:
                    print(f.read().strip().decode('utf-8')[start:end])

def get_bigram_queries(query):
    bi_gram_qs = []
    for i in range(0, len(query), 2):
        bi_gram_q = query[i:i+2].strip()
        if len(bi_gram_q) ==1 and i>0:
            bi_gram_q = query[i-1:i+1]
        bi_gram_qs.append( bi_gram_q )
    return bi_gram_qs

def get_decoded_data(encoded_data):
    decoded_data = decode(encoded_data)
    return np.cumsum(decoded_data).tolist()

def check_sequence(location_lists):
    length = len(location_lists)

    doc_id_idx_idx = []
    locations4snippet = []
    for doc_i, location_list in enumerate(location_lists[0]):
        for location in location_list:
            if length==1:
                return [doc_i]
            elif check_next_node(1, doc_i, location, location_lists, length):
                doc_id_idx_idx.append(doc_i)
                locations4snippet.append(location)
            else:
                continue
    return doc_id_idx_idx, locations4snippet

def check_next_node(i, doc_i, location, location_lists, last_node):
    for next_location in location_lists[i][doc_i]:
        if location < next_location <= location+2:
            if i < last_node-1:
                return check_next_node(i+1, doc_i, location+2, location_lists, last_node)
            else:
              return True
        else:
            return False

if __name__=='__main__':
    basepath = os.getcwd()
    index_filename = basepath + '/index_bigram.pkl'
    file_path = basepath + '/../works/input'
    ifname = file_path + '/10000entries.txt'
    text_path = file_path + '/texts'

    titles = get_titles(ifname)
    index = load_index(index_filename)

    print("get search query")
    query = input()
    search(titles, index, query, text_path)
    print("done")