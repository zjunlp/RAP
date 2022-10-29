import json
import os.path
import sys
from copy import deepcopy
from datetime import datetime
from os import path

from typing import Dict, List, Optional, Set, Tuple, Union
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from tqdm import tqdm


class Metric:
    def __init__(self):
        self.tp = 0.
        self.gold_num = 0.
        self.pred_num = 0.

    @staticmethod
    def safe_div(a, b):
        if b == 0.:
            return 0.
        else:
            return a / b

    def compute_f1(self, prefix=''):
        tp = self.tp
        pred_num = self.pred_num
        gold_num = self.gold_num
        p, r = self.safe_div(tp, pred_num), self.safe_div(tp, gold_num)
        return {prefix + 'tp': tp,
                prefix + 'gold': gold_num,
                prefix + 'pred': pred_num,
                prefix + 'P': p * 100,
                prefix + 'R': r * 100,
                prefix + 'F1': self.safe_div(2 * p * r, p + r) * 100
                }

    def count_instance(self, gold_list, pred_list, verbose=False):
        if verbose:
            print("Gold:", gold_list)
            print("Pred:", pred_list)
        self.gold_num += len(gold_list)
        self.pred_num += len(pred_list)

        dup_gold_list = deepcopy(gold_list)
        for pred in pred_list:
            if pred in dup_gold_list:
                self.tp += 1
                dup_gold_list.remove(pred)


def init_es():
    return Elasticsearch()


def read_data_from_file(file_name):
    inputs = open('store/' + file_name, 'r')
    return json.load(inputs)


def create_index(es, name):
    index_mappings = {
        "mappings": {
            "properties": {
                "key": {
                    "type": "text"
                },
                "value": {
                    "type": "text"
                },
                "sent": {
                    "type": "text"
                },
                "source": {
                    "type": "text"
                }
            }
        }
    }
    if es.indices.exists(index=name) is not True:
        print("create", name)
        es.indices.create(index=name, body=index_mappings)


# del_index 删除已建立的库
def del_index(es, index_name):
    es.indices.delete(index=index_name)


def search(es, query, index_name):
    query_contains = {
        'query': {
            'match': {
                'key': query,
            }
        }
    }
    searched = es.search(index=index_name, body=query_contains, size=32)
    return searched


def add_data_ace(es, data, index_name):
    index = 0
    actions = []
    print('---adding data---')
    for key in tqdm(data.keys()):
        item = {
            "_index": index_name,
            "_id": index,
            "_source": {
                "key": key,
                "trigger": data[key][0],
                "event_type": data[key][1],
                "schema": data[key][2]
            }
        }
        actions.append(item)
        index += 1
        if len(actions) == 1000:
            res, _ = helpers.bulk(es, actions)
            print(res)
            del actions[0:len(actions)]

    if index > 0:
        helpers.bulk(es, actions)
    print('---ending data---')


def add_data_casie(es, data, index_name):
    index = 0
    actions = []
    print('---adding data---')
    for key in tqdm(data.keys()):
        item = {
            "_index": index_name,
            "_id": index,
            "_source": {
                "key": key,
                "trigger": data[key][0],
                "event_type": data[key][1],
                "role_type": data[key][2]
            }
        }
        actions.append(item)
        index += 1
        if len(actions) == 1000:
            res, _ = helpers.bulk(es, actions)
            print(res)
            del actions[0:len(actions)]

    if index > 0:
        helpers.bulk(es, actions)
    print('---ending data---')


def add_data_triple(es, data, index_name):
    index = 0
    actions = []
    print('---adding data---')
    for key in tqdm(data.keys()):
        item = {
            "_index": index_name,
            "_id": index,
            "_source": {
                "key": key,
                "triple": data[key][0],
                "label": data[key][1],
                "head_ids": data[key][2],
                "tail_ids": data[key][3]
            }
        }
        actions.append(item)
        index += 1
        if len(actions) == 1000:
            res, _ = helpers.bulk(es, actions)
            print(res)
            del actions[0:len(actions)]

    if index > 0:
        helpers.bulk(es, actions)
    print('---ending data---')


def align_span_to_tokens(span: str, tokens: List[str]) -> Tuple[int, int]:
    # Eg align("John R. Allen, Jr.", ['John', 'R.', 'Allen', ',', 'Jr.'])
    char_word_map = {}
    num_chars = 0
    for i, w in enumerate(tokens):
        for _ in w:
            char_word_map[num_chars] = i
            num_chars += 1
    char_word_map[num_chars] = len(tokens)

    query = span.replace(" ", "")
    text = "".join(tokens)
    assert query in text
    i = text.find(query)
    start = char_word_map[i]
    end = char_word_map[i + len(query) - 1]
    assert 0 <= start <= end
    return list(range(start, end + 1))


def search_triple(es, instance, knowledge_type, index_name="nyt_store", sep=" [SEP] "):
    for res in search(es, instance, index_name)["hits"]["hits"]:
        source = res["_source"]
        if source["key"] == instance:
            continue
        suffix = ""

        if "triple" in knowledge_type:
            suffix += sep
            for triple in source["triple"]:
                suffix = suffix + triple + " "

        if "label" in knowledge_type:
            suffix += sep
            for lab in source["label"]:
                lab = lab
                suffix = suffix + lab + " "

        if "ins" in knowledge_type:
            suffix += sep + "The most similar sentence is: "

        suffix = suffix + source["key"]
        return instance + suffix


def search_t2e_casie(es, sent, index_name="casie_store", threshold=20, k=8):
    ins_inject_set = set()
    trigger_inject_set = set()
    arg_type_inject_set = set()
    event_type_inject_set = set()

    for res in search(es, sent, index_name)['hits']['hits']:
        if sent == res["_source"]["key"]: continue
        if res["_score"] < threshold: break

        trigger_list = res["_source"]["trigger"]
        event_list = res["_source"]["event_type"]
        arg_type_list = res["_source"]["role_type"]
        key = res["_source"]["key"]

        # only add the most similar sentence
        if len(ins_inject_set) < 1: ins_inject_set.add(key)

        if len(trigger_inject_set) < k:
            for tri, et in zip(trigger_list, event_list):
                if len(trigger_inject_set) == k: break
                trigger_inject_set.add(tri + " triggers " + et)

        if len(arg_type_inject_set) < k:
            for args, et in zip(arg_type_list, event_list):
                if len(args) == 0: continue
                inject_str = et + " has arguments like "
                for idx, arg in enumerate(args):
                    inject_str += arg
                    if idx < len(args) - 1: inject_str += ", "
                arg_type_inject_set.add(inject_str)

        if len(event_type_inject_set) < k:
            for et in event_list:
                event_type_inject_set.add(et)

        # end retrieving
        if len(ins_inject_set) == 1 and len(trigger_inject_set) >= k and len(
                arg_type_inject_set) >= k and len(event_type_inject_set) >= k: break

    if len(event_type_inject_set) != 0:
        sent += " </s> The sentence may demonstrate events like "
        for idx, et in enumerate(event_type_inject_set):
            sent += et
            if idx < len(event_type_inject_set) - 1:
                sent += ", "
        sent += "."

    if len(arg_type_inject_set) != 0:
        sent += " </s> "
        for idx, args in enumerate(arg_type_inject_set):
            sent += args
            if idx < len(arg_type_inject_set) - 1:
                sent += "; "
        sent += "."

    if len(trigger_inject_set) != 0:
        sent += ' </s> '
        for idx, tri in enumerate(trigger_inject_set):
            sent += tri
            if idx < len(trigger_inject_set) - 1:
                sent += '; '
        sent += "."

    return sent


def search_t2e_ace(es, sent, index_name="ace_store", threshold=20, k=4):
    ins_inject_set = set()
    trigger_inject_set = set()
    schema_inject_set = set()
    for res in search(es, sent, index_name)['hits']['hits']:
        if sent == res["_source"]["key"]: continue
        if res["_score"] < threshold: break

        trigger_list = res["_source"]["trigger"]
        event_list = res["_source"]["event_type"]
        schema_list = res["_source"]["schema"]
        key = res["_source"]["key"]

        if len(ins_inject_set) < 1: ins_inject_set.add(key)

        if len(trigger_inject_set) < k:
            for tri, et in zip(trigger_list, event_list):
                if len(trigger_inject_set) == k: break
                trigger_inject_set.add(tri + " triggers " + et)

        if len(schema_inject_set) < k:
            for schema, et in zip(schema_list, event_list):
                schema_inject_set.add(
                    et + " is a " + schema
                    + " event."
                )

        if len(ins_inject_set) == 1 and len(trigger_inject_set) >= k and len(schema_inject_set) >= k: break

    if len(schema_inject_set) != 0:
        sent = sent + " </s> "
        for idx, schema in enumerate(schema_inject_set):
            sent += schema
            if idx < len(schema_inject_set) - 1: sent += '; '
        sent += "."

    if len(ins_inject_set) != 0:
        sent = sent + " </s> " + ' The most similar sentence: ' + \
               list(ins_inject_set)[0]

    return sent
