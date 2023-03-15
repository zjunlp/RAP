# RAP

Code for our paper "Schema-aware Reference as Prompt Improves Data-Efficient Knowledge Graph Construction".

<div align=center><img src="./img/architecture.jpg" width="100%" height="80%" /></div>

## Requirements

```
Java 8 # for elasticsearch
elasticsearch==7.17.1
```


## Retrieving for Reference

The reference store can be downloaded from [here](https://drive.google.com/file/d/1lQW0nrMZzpyltuUKCMbmWw67yeejh1Qw/view?usp=sharing). Unzip the file and put the folder `store/` into `retrieval/`
folder, and the final directory structure is as follows:

```text
retrieval
├── store/
├── retrieve.py
└── retrieve_utils.py
```

For different base models, you can generate the reference by following codes:

```bash
cd retrieval/ 
python retrieve.py --base_model prgc
```

The parameter `--base_model` is for different base models, we can change it in `prgc`, `relationprompt`, `t2e`, `degree`.

For `Text2Event` and `DEGREE`, please follow the instruction README.md document in their corresponding folder to preprocess the datasets, and then generate the retrieved reference.


## BaseModel

We plugged RAP to several base models, which can be seen in the folders below: 

```text
BaseModel
├── DEGREE
├── PRGC
├── RelationPrompt
└── Text2Event
```

The code of above base models are borrowed from their original codes with slight modifacations.

**DEGREE** : Please follow the instruction [here](./BaseModel/DEGREE/README.md).

**PRGC** : Please follow the instruction [here](./BaseModel/PRGC/README.md).

**RelationPrompt** : Please follow the instruction [here](./BaseModel/RelationPrompt/README.md).

**Text2Event** : Please follow the instruction [here](./BaseModel/Text2Event/README.md).

