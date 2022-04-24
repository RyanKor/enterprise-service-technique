# codeing: utf-8

from __future__ import unicode_literals
from collections import defaultdict
from unicodedata import normalize
import MeCab
from vbcode import encode
import numpy as np
import os
import pickle

def get_title_data(input_filename):
    titles = defaultdict(str)
    with open(input_filename, 'r', 10000) as f:
        for line in f:
            try:
                doc_id, cat_id, url, title = line.strip().split(b'\t')
                titles[int(doc_id)] = title
            except Exception as e:
                doc_id, cat_id, url = line.strip().split(b'\t')
                titles[int(doc_id)] = ''
    return titles

def create_index(doc_base_path,titles):
    main_index = defaultdict(dict)
    for doc_id in titles.keys():
        try:
            main_index = get_index_dic(doc_base_path, doc_id, main_index)
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            print(e)
    compressed_main_index = compress_postinglist(main_index)
    save_index(compressed_main_index)

def save_index(index):
    with open('index_bigram.pkl','w') as f:
        pickle.dump(index, f)

def compress_postinglist(index):
    for key_word, posting_dic in index.items():
        tup_did_location = zip( posting_dic.keys()[0],posting_dic.values()[0] ) # [(),()]
        tup_did_location.sort(key=lambda x:x[0]) # [(),()]

        doc_id_list = []
        lctn_pl = []
        for doc_id, location_list in tup_did_location:
            doc_id_list.append(doc_id)
            lctn_pl.append( encode( get_differences(location_list) ) )
        d_pl = get_differences(doc_id_list)
        index[key_word] = { encode(d_pl) : lctn_pl}
    return index

def get_differences(sorted_list):
    if len(sorted_list)>1:
        diff_list = ( np.array(sorted_list) - np.array([0]+sorted_list[:-1]) ).tolist()
    else:
        diff_list = sorted_list
    return diff_list

def get_index_dic(doc_base_path, doc_id, main_index):
    with open(doc_base_path+'/'+str(doc_id), 'r') as f:
        doc = f.read().strip()
        doc = normalize('NFKC',doc.decode('utf-8')).lower()
        word_list, word_location = bi_gram_tokenize(doc)

        for word, location in zip(word_list, word_location):
            if main_index[word]:
                _keys = main_index[word].keys()[0]
                if doc_id in _keys:
                    main_index[word][_keys][-1] += [location]
                else:
                    main_index[word][_keys].append( [location] )
                    main_index[word] = {_keys+(doc_id,): main_index[word].values()[0]}
            else:
                main_index[word][(doc_id,)] = [ [location] ]
    return main_index

def mecab_tokenize(doc):
    tagger = MeCab.Tagger(b'-Ochasen')
    node = tagger.parseToNode(doc.encode('utf-8'))
    word_list = []
    while node:
        ns = node.surface
        word_list.append(ns)
        node = node.next
    return word_list

def bi_gram_tokenize(doc):
    word_list = []
    word_location = []
    for i in range(len(doc)):
        term = doc[i:i+2].strip()
        if len(term)!=0:
            #print "term:",term
            word_list.append( term )
            word_location.append( i )
    return word_list, word_location

def main(input_filename, doc_base_path):
    titles = get_title_data(input_filename)
    create_index(doc_base_path,titles)

if __name__=='__main__':
    ifpath = os.getcwd()+'/../works/input'
    ifname = ifpath + '/10000entries.txt'
    doc_base_path = ifpath + '/texts'
    main(ifname, doc_base_path)