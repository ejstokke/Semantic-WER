import apertium
import pandas as pd
from operator import itemgetter 
from itertools import groupby

import sqlite3

# Translation models
nno_nob = apertium.Translator('nno', 'nob')
nob_nno = apertium.Translator('nob', 'nno_e')

#SQL select query

select_stmt = '''SELECT s.sentence_id, s.language_code, n.token_text,
              n.standardized_form, n.token_order FROM normtokens n
              LEFT JOIN sentences s ON s.sentence_id = n.sentence_id
              ORDER BY s.sentence_id, n.token_order;'''

def text_or_standard(tokdict):
    if tokdict["standardized_form"] is not None:
        return tokdict["standardized_form"].replace("_", " ")
    else:
        return tokdict["token_text"]

def translate_corpus(conn):
    toks_df = pd.read_sql_query(select_stmt, conn)
    toks = toks_df.to_dict('records')

    sentence_tokens = [sorted([token for token in sent], key=lambda x:x["token_order"])
                       for key, sent in groupby(toks, key=itemgetter('sentence_id'))]

    sents = []
    for toklist in sentence_tokens:
        sents.append((toklist[0]["sentence_id"], toklist[0]["language_code"],
                      " ".join([text_or_standard(w) for w in toklist])))
    
    translated = []
    for s in sents:
        s_text = s[2]
        converted = True
        lcode = s[1]
        s_id = s[0]
        if lcode == "nn-NO":
            translated.append((True, nno_nob.translate(s_text), "nb-NO", s_id))
        elif s[1] == "nb-NO":
            translated.append((True, nob_nno.translate(s_text), "nn-NO", s_id))
        else:
            translated.append((False, s_text, lcode, s_id))
    
    return translated


if __name__ == "__main__":
    db = "stortinget_speech_corpus_postproc.db"
    try:
        sqliteConnection = sqlite3.connect(db)
        print("Successfully Connected to SQLite")
        print(translate_corpus(sqliteConnection))

    except sqlite3.Error as error:
        print("Sqlite error, ", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("sqlite connection is closed")



