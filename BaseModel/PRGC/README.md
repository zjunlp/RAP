# RAP for PRGC

The code is basically borrowed from [here](https://github.com/hy-struggle/PRGC), with slight modification.

## Requirements

The main requirements are:

  - python==3.7.9
  - pytorch==1.6.0
  - transformers==3.2.0
  - tqdm

## Split Data

Run the following commands to randomly split the datasets.

```bash
cd data
bash run_sample.bash
```

For each datasets, we get the corresponding low resource  folders `nyt_retrieved_ratio` and `webnlg_retrieved_ratio`  with 5 different random seeds, taking `nyt_retrieved_ratio` as example, we can get folders as follow:

```text
data/nyt_retrieved_ratio
├── seed2
│   ├── 0.1
│   ├── 0.01
│   └── 0.05
├── seed3
│   └── ...
├── seed5
│   └── ...
├── seed7
│   └── ...
└── seed11
    └── ...
```

## Usage

**1. Get pre-trained BERT model for PyTorch**

Download [BERT-Base-Cased](https://huggingface.co/bert-base-cased/tree/main) which contains `pytroch_model.bin`, `vocab.txt` and `config.json`. Put these under `./pretrain_models`.

**2. Train**

Just run the script in `./script` by `sh train.sh`.

Here's an example:

```bash
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
```

**3. Evaluate**

Just run the script in `./script` by `sh evaluate.sh`.

Here's an example:

```bash
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
```
