import json

file_path = 'Data\\project_files\\NPSC_speaker_data.json'

f = open(file_path , encoding='utf-8')
data = json.load(f)

amount_of_speakers = len(data)

dialects = dict()
genders = dict()
pob = dict()

for speaker in data:
    dialects[speaker['dialect']] = dialects.get(speaker['dialect'], 0) + 1
    genders[speaker['gender']] = genders.get(speaker['gender'], 0) + 1
    pob[speaker['pob_county']] = pob.get(speaker['pob_county'], 0) + 1

print(len(data))
print(dialects)
print(genders)
print(pob)