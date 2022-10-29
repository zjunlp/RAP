for seed in 2 3 5 7 11
do
    python scripts/sample_data_ratio.py -seed ${seed} \
        -src ./webnlg_retrieved \
        -tgt ./webnlg_retrieved_ratio/seed${seed}
    python scripts/sample_data_ratio.py -seed ${seed} \
        -src ./nyt_retrieved \
        -tgt ./nyt_retrieved_ratio/seed${seed}
done