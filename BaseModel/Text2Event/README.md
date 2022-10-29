# RAP for Text2Event





## Requirements

General

- Python (verified on 3.8)
- CUDA (verified on 11.1)

Python Packages

- see requirements.txt

```bash
conda create -n text2event python=3.8
conda activate text2event
pip install -r requirements.txt
```

## Dataset

### Casie

The casie dataset is in the folder `data/text2tree`.

```text
data/text2tree/
├── casie
├── casie_001
└── casie_010
```

### ACE05

We followed the same split ratio in DEGREE, so when implement ace in Text2Event, please conduct the dataset preprocessing in `BaseModel/DEGREE` folder.

After preprocessing in DEGREE, run `python ./preprocess/convert_ace.py` to convert the data in Text2Event format. The processed data folders are listed below.

```text
data/text2tree/
├── ace
├── ace_001
├── ace_003
├── ace_005
├── ace_010
├── ace_020
└── ace_030
```

### Data Format

Data folder contains four files：

```text
data/text2tree/casie
├── event.schema
├── test.json
├── train.json
└── val.json
```

train/val/test.json are data files, and each line is a JSON instance.
Each JSON instance contains `text` and `event` fields, in which `text` is plain text, and `event` is event linearized form.
If you want to use other key names, it is easy to change the input format in `run_seq2seq.py`.


### Retrieval
Generate the retrieved reference as command following:
```bash
cd ../../retrieval
python retrieve.py --base_model t2e
```

For each split setting, a new folder will be generated like `ace_001_retrieved/`.

## Model Training

Training scripts as follows:

- `run_seq2seq.py`: Python code entry, modified from the transformers/examples/seq2seq/run_seq2seq.py
- `run_seq2seq.bash`: Model training script logging to the log file.

Trained models are saved in the `models/` folder.

```bash
bash run_seq2seq.bash -d 1 -f tree -m t5-base -l 3e-4 --data casie_010_retrieved --lr_scheduler linear --warmup_steps 300 -b 16 --epoch 50 --eval_steps 100 --gradient_accumulation_steps 1
bash run_seq2seq.bash -d 1 -f tree -m t5-large -l 3e-4 --data ace_005_retrieved --lr_scheduler linear --warmup_steps 100 -b 4 --epoch 60 --eval_steps 50 --gradient_accumulation_steps 8 
```
- `-d` refers to the GPU device id.
- `-m` refers to the `model-folder-path` ,  we select `t5-base` as backbone for `CASIE` and `t5-large`  for `ACE05` .
- `-l` refers to the learning rate.
- `--data` refers to the dataset_name, we take `casie_010_retrieved` and `ace_005_retrieved` as example here.
- `-b` refers to the batch size.

## Model Evaluation

```bash
bash run_eval.bash -d 0 -m <model-folder-path> -i <data-folder-path> -c -b 8
```

The evaluation is also conducted after training.

