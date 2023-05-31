import json

with open("notebooks/latex_hwer_table_data.json") as file:

    data = json.load(file)

for i, sent in enumerate(data):
    print(f"{i + 1} & {sent['transcript']} & {sent['gold_label']} & {sent['hwer']} & {sent['norbert']} & {sent['norbert2']} & {sent['nb-bert']} \\\\")
    print("\\hline")

