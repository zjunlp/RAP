import json
import os
import shutil
from tqdm import tqdm

type_start = '<extra_id_0>'
type_end = '<extra_id_1>'


def convert_ace():
    input_dir = '../DEGREE/processed_data/ace05e_bart'
    output_dir = './data/text2tree/ace'

    print("generating", output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for fold in [
        "train",
        "dev",
        "test",
        "train.001",
        "train.003",
        "train.005",
        "train.010",
        "train.020",
        "train.030"
    ]:

        with open(os.path.join(input_dir, fold + ".w1.oneie.json"), "r") as inputs:
            if fold == "dev": fold = "val"
            outputs = open(os.path.join(output_dir, fold + ".json"), "w")
            print('---generating ' + fold + ' set---')
            data = inputs.readlines()
            for _, line in zip(tqdm(range(len(data))), data):
                line = json.loads(line)
                sent = line["sentence"]
                event_str_rep_list = list()
                for event_mention in line["event_mentions"]:
                    event_type = event_mention["event_type"].split(":")[-1]
                    trigger = event_mention["trigger"]["text"]
                    role_str_list = list()
                    for arg in event_mention["arguments"]:
                        role_name = arg["role"]
                        role_text = arg["text"]
                        role_str = ' '.join([type_start, role_name, role_text, type_end])
                        role_str_list += [role_str]
                    role_str_list_str = ' '.join(role_str_list)
                    event_str_rep = f"{type_start} {event_type} {trigger} {role_str_list_str} {type_end}"
                    event_str_rep_list += [event_str_rep]
                event = f'{type_start} ' + ' '.join(event_str_rep_list) + f' {type_end}'
                outputs.writelines(json.dumps({"text": sent, "event": event}, ensure_ascii=False) + "\n")


def create_folder():
    source_folder = "./data/text2tree/ace"
    for ratio in ["001", "003", "005", "010", "020", "030"]:
        target_folder = "./data/text2tree/ace_" + ratio
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        for fold in ["event.schema", "test.json", "val.json"]:
            shutil.copy(
                os.path.join(source_folder, fold),
                os.path.join(target_folder, fold),
            )
        shutil.copy(
            os.path.join(source_folder, "train." + ratio + ".json"),
            os.path.join(target_folder, "train.json"),
        )


if __name__ == '__main__':
    convert_ace()
    create_folder()