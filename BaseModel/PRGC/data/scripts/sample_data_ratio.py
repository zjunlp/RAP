#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
import math
import shutil
import random
import argparse
import json


def split_ratio_file(in_filename, out_filename, ratio=0.1, seed=None):
    lines = json.load(open(in_filename, "r"))
    if seed:
        random.seed(seed)
        random.shuffle(lines)
    lines = lines[:math.ceil(len(lines) * ratio)]
    print(out_filename, len(lines))
    with open(out_filename, 'w') as output:
        json.dump(lines, output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-src')
    parser.add_argument('-tgt')
    parser.add_argument('-seed')
    options = parser.parse_args()

    source_folder = options.src
    target_folder = options.tgt

    os.makedirs(target_folder, exist_ok=True)

    for ratio in [0.01, 0.05, 0.1]:
        ratio_folder = os.path.join(target_folder, "%s" % ratio)

        os.makedirs(ratio_folder, exist_ok=True)
        split_ratio_file(
            in_filename=os.path.join(source_folder, 'train_triples.json'),
            out_filename=os.path.join(ratio_folder, 'train_triples.json'),
            ratio=ratio,
            seed=options.seed,
        )
        for filename in os.listdir(source_folder):
            if filename != 'train_triples.json':
                shutil.copy(
                    os.path.join(source_folder, filename),
                    os.path.join(ratio_folder, filename),
                )


if __name__ == "__main__":
    main()