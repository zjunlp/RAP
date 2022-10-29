#!/bin/bash
export seed=5
export data="nyt_retrieved"
python ../evaluate.py \
--ex_index=${data} \
--device_id=1 \
--mode=test \
--corpus_type=${data} \
--ensure_corres \
--ensure_rel \
--corres_threshold=0.5 \
--rel_threshold=0.1 \
--restore_file=best