import json

speakers = {}

file_path = '..\\Data\\project_files\\NPSC_speaker_data.json'

f = open(file_path , encoding='utf-8')
data = json.load(f)

for speaker in data:
    speakers[speaker['speaker_id']] = {
        'gender': speaker['gender'],
        'dialect': speaker['dialect'],
        'name': speaker['speaker_name']
        }

if __name__ == '__main__':
    pass
