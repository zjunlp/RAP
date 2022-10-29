import json
import os.path
from os import path
import sys
from retrieve_utils import *
from tqdm import tqdm
import argparse
import shutil


def construct_store(es, data_name):
    file_name = data_name + "_store.json"
    index_name = data_name + "_store"
    if es.indices.exists(index_name):
        print("index", index_name, "has already exists!!")
        return
    data = read_data_from_file(file_name=file_name)
    print("number of instances in store:", len(data.keys()))
    create_index(es, index_name)
    if data_name == "ace":
        add_data_ace(es, data, index_name)
    elif data_name == "casie":
        add_data_casie(es, data, index_name)
    elif data_name == "nyt" or data_name == "webnlg":
        add_data_triple(es, data, index_name)


def retrieve_prgc(es, knowledge_type, data_name):
    index_name = data_name + "_store"
    origin_folder = "../BaseModel/PRGC/data/" + data_name + "/"
    retrieved_folder = "../BaseModel/PRGC/data/" + data_name + "_retrieved/"
    if not os.path.exists(retrieved_folder):
        os.makedirs(retrieved_folder)
    for fold in ["train", "test", "val"]:
        raw = json.load(open(origin_folder + fold + "_triples.json", "r"))
        writer = open(retrieved_folder + fold + "_triples.json", "w")
        new_file = []
        for i in tqdm(range(len(raw))):
            raw_line = raw[i]
            sent = raw_line["text"]
            retrieved_sent = search_triple(es=es, instance=sent, knowledge_type=knowledge_type,
                                           index_name=index_name, sep=" [SEP] ")
            raw_line["text"] = retrieved_sent
            new_file.append(raw_line)
        json.dump(new_file, writer)
    shutil.copy(
        os.path.join(origin_folder, "rel2id.json"),
        os.path.join(retrieved_folder, "rel2id.json"),
    )


def retrieve_rp(es, knowledge_type, data_name):
    index_name = data_name + "_store"
    origin_folder = "../BaseModel/RelationPrompt/outputs/data/" + data_name + "/"
    retrieved_folder = "../BaseModel/RelationPrompt/outputs/data/" + data_name + "_retrieved/"
    if not os.path.exists(retrieved_folder):
        os.makedirs(retrieved_folder)
    for fold in ["train", "test", "dev"]:
        data = open(origin_folder + "raw_" + fold + ".json", "r").readlines()
        writer = open(retrieved_folder + fold + ".json", "w")
        for i in tqdm(range(len(data))):
            line = json.loads(data[i])
            tokens = line["triplets"][0]["tokens"]
            sent = " ".join(tokens)
            re_sent = search_triple(es=es, instance=sent, knowledge_type=knowledge_type,
                                    index_name=index_name, sep=" </s> ")
            re_tokens = re_sent.split()
            for idx in range(len(line["triplets"])):
                line["triplets"][idx]["tokens"] = re_tokens
            writer.write(json.dumps(line) + '\n')


def retrieve_degree(es, data_name="ace", k=8, index_name="ace_store"):
    input_dir = "../BaseModel/DEGREE/processed_data/" + data_name
    output_dir = '../BaseModel/DEGREE/processed_data/retrieved/' + data_name
    print("generating", output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    threshold = 20
    print("k:", k)
    print("threshold:", threshold)

    for fold in [
        "train",
        "dev"
        , "test"
        , "train.001"
        , "train.003"
        , "train.005"
        , "train.010"
        , "train.020"
        , "train.030"
    ]:
        outputs = open(path.join(output_dir, fold + ".w1.oneie.json"), "w")
        with open(path.join(input_dir, fold + ".w1.oneie.json"), "r") as inputs:
            print('---generating ' + fold + ' set---')
            data = inputs.readlines()
            for _, line in zip(tqdm(range(len(data))), data):
                line = json.loads(line)
                sent = line["sentence"]
                inject_list = []
                for res in search(es, sent, index_name)['hits']['hits']:
                    # 如果句子检索相同则跳过
                    if sent == res["_source"]["key"]: continue
                    if res["_score"] < threshold: break
                    ins = res["_source"]["key"]
                    event_list = list(set(res["_source"]["event_type"]))
                    inject_list.append((ins, event_list))
                    if len(inject_list) >= k: break
                line["retrieval"] = inject_list
                outputs.writelines(json.dumps(line) + '\n')
                outputs.flush()


def retrive_t2e(data_name="casie", threshold=20, k=8):
    folder_list = list()
    if data_name == "casie":
        folder_list = ["casie", "casie_001", "casie_010"]
    elif data_name == "ace":
        folder_list = ["ace", "ace_001", "ace_003", "ace_005", "ace_010", "ace_020", "ace_030"]

    for folder in folder_list:
        input_dir = '../BaseModel/Text2Event/data/text2tree/' + folder
        output_dir = "../BaseModel/Text2Event/data/text2tree/" + folder + "_retrieved"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        print("generating", output_dir)
        for fold in [
            "train",
            "val"
            , "test"
        ]:
            shutil.copy(os.path.join(input_dir, "event.schema"), os.path.join(output_dir, "event.schema"), )
            inputs = open(path.join(input_dir, fold + ".json"), "r")
            outputs = open(os.path.join(output_dir, fold + ".json"), "w")
            print('---generating ' + fold + ' set---')
            data_list = inputs.readlines()
            for idx, line in zip(tqdm(range(len(data_list))), data_list):
                line = json.loads(line)
                if data_name == "casie":
                    line["text"] = search_t2e_casie(es, line["text"], k=k, threshold=threshold,
                                                    index_name="casie_store")
                elif data_name == "ace":
                    line["text"] = search_t2e_ace(es, line["text"], k=k, threshold=threshold,
                                                  index_name="ace_store")
                outputs.writelines(json.dumps(line) + "\n")
                outputs.flush()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    ## Required parameters
    parser.add_argument("--base_model", default="prgc", type=str, required=True,
                        help="relationprompt, prgc, t2e, degree")

    args = parser.parse_args()
    base_model = args.base_model

    knowledge_type_triple = ["ins", "label", "triple"]
    knowledge_type_event = ["trigger", "event_type", "schema"]

    method2datas = {
        "prgc": ["nyt", "webnlg"],
        "relationprompt": ["nyt", "webnlg"],
        "t2e": ["casie", "ace"],
        "degree": ["ace"]
    }

    es = init_es()

    # # delete the existing index
    # del_index(es, "ace_store")

    print("-" * 20, "generate data for", base_model, "-" * 20)

    if base_model == "prgc":
        for data_name in method2datas[base_model]:
            print("-" * 20, "retrieving for", data_name, "-" * 20)
            construct_store(es, data_name)
            retrieve_prgc(es, knowledge_type_triple, data_name)

    elif base_model == "relationprompt":
        for data_name in method2datas[base_model]:
            print("-" * 20, "retrieving for", data_name, "-" * 20)
            construct_store(es, data_name)
            retrieve_rp(es, knowledge_type_triple, data_name)

    elif base_model == "t2e":
        for data_name in method2datas[base_model]:
            print("-" * 20, "retrieving for", data_name, "-" * 20)
            construct_store(es, data_name)
            retrive_t2e(data_name)

    elif base_model == "degree":
        for data_name in method2datas[base_model]:
            print("-" * 20, "retrieving for", data_name, "-" * 20)
            construct_store(es, data_name)
            retrieve_degree(es, data_name + "05e_bart", k=8, index_name=data_name + "_store")
