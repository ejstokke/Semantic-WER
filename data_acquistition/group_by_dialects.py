from speaker_data_simplified import speakers
import pandas as pd
import json
import os

data_path = 'Data\\NPSC'
data_folders = os.listdir(data_path)

# FUTURE: change this to include all files in data_folders
file_path = os.path.join(data_path, data_folders[1], f"{data_folders[1]}_sentence_data.json")

f = open(file_path , encoding='utf-8')
data = json.load(f)

sentences_by_dialect = dict()

for sentence in data['sentences']:
    dialect = speakers[sentence['speaker_id']]['dialect']
    sentence_text = sentence['sentence_text']
    sentences_by_dialect.setdefault(dialect, []).append(sentence_text)

df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in sentences_by_dialect.items() ]))
print(df)