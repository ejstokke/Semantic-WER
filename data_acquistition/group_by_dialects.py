# from speaker_data_simplified import speakers
import pandas as pd
import json
import os

print(os.listdir())
data_path = 'Data/NPSC'
data_folders = os.listdir(data_path)

eval_folders = ["20180611", "20180201", "20170209", "20180307", "20180109"
]

test_folders = ["20171219", "20180530", "20171122", "20170207"
]
train = []
for folder in data_folders:
    if folder not in eval_folders + test_folders:
        train.append(folder)

for f in train:
    print(f, end=", ")
# # FUTURE: change this to include all files in data_folders
# file_path = os.path.join(data_path, data_folders[1], f"{data_folders[1]}_sentence_data.json")

# f = open(file_path , encoding='utf-8')
# data = json.load(f)

# sentences_by_dialect = dict()

# for sentence in data['sentences']:
#     dialect = speakers[sentence['speaker_id']]['dialect']
#     sentence_text = sentence['sentence_text']
#     sentences_by_dialect.setdefault(dialect, []).append(sentence_text)

# df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in sentences_by_dialect.items() ]))
# print(df)