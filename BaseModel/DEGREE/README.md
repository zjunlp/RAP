# RAP for DEGREE

The code is basically borrowed from [here](https://github.com/PlusLabNLP/DEGREE), with slight modification.

## Requirements

General

- Python (verified on 3.8)

Python Packages

- see requirements.txt

```bash
conda create -n degree python=3.8
conda activate degree
pip install -r requirements.txt
```

## Dataset

### Preprocessing
#### `ace05e`
1. Prepare data processed from [DyGIE++](https://github.com/dwadden/dygiepp#ace05-event)
2. Put the processed data into the folder `processed_data/ace05e_dygieppformat`
3. Run `./scripts/process_ace05e.sh`

The data folder should be like following after preprocessing
```text
processed_data/ace05e_bart
├── dev.w1.oneie.json
├── test.w1.oneie.json
├── train.001.w1.oneie.json
├── train.003.w1.oneie.json
├── train.005.w1.oneie.json
├── ...
└── train.w1.oneie.json
```

## Retrieving

Run the following command to generate retrieved reference for dataset.
```bash
cd ../../retrieval
python retrieve.py --base_model degree
```
And the retrieved data will be in the folder `processed_data/retrieved`

## Training

**Generate data**
```Bash
python degree/generate_data_degree_e2e.py -c config/config_degree_e2e_ace05e.json
```

**train**
```Bash
python degree/train_degree_e2e.py -c config/config_degree_e2e_ace05e.json
```

The model will be stored at `./output/degree_e2e_ace05e/[timestamp]/best_model.mdl` in default.

## Evaluation

Evaluate on the model
```Bash
python degree/eval_end2endEE.py -c config/config_degree_e2e_ace05e.json -e [e2e_model]
```