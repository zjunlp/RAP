#!/bin/bash
export seed=5
export data="nyt_retrieved"
python ../train.py \
--ex_index=${data} \
--epoch_num=100 \
--device_id=3 \
--corpus_type=${data} \
--ensure_corres \
--ensure_rel