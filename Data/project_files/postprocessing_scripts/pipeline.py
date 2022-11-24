import sqlite3
from operator import itemgetter 
from itertools import groupby

from normalizer import normalize_tokens
from feilretting import apply_corrections
from oversettelse import translate_corpus

from grammars.number_grammar import numbergrammar_abovethirteen
from grammars.year_grammar import yeargrammar
from grammars.date_grammar import dategrammar
from grammars.abbrev_grammar import abbrevgrammar

# Tables

create_normtokens_table = '''CREATE TABLE IF NOT EXISTS normtokens (
                    normtok_id TEXT PRIMARY KEY,
                    token_order INTEGER NOT NULL,
                    token_text TEXT NOT NULL,
                    nonstandard_spelling INTEGER NOT NULL,
                    converted INTEGER NOT NULL,
                    standardized_form TEXT,
                    special_status TEXT,
                    language_code TEXT,
                    phon_ort_discrepancy INTEGER NOT NULL,
                    sentence_id INTEGER NOT NULL,
                    UNIQUE(token_order, sentence_id),
                    FOREIGN KEY(sentence_id) REFERENCES sentences(sentence_id) ON DELETE CASCADE ON UPDATE CASCADE);'''

create_normsentences_table = '''CREATE TABLE IF NOT EXISTS normsentences (
                    normsentence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    normsentence_text TEXT NOT NULL,
                    sentence_id INTEGER NOT NULL,
                    FOREIGN KEY(sentence_id) REFERENCES sentences(sentence_id) ON DELETE CASCADE ON UPDATE CASCADE);'''

create_transsentences_table = '''CREATE TABLE IF NOT EXISTS transsentences (
                    transsentence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    translated INTEGER NOT NULL,
                    transsentence_text TEXT NOT NULL,
                    language_code TEXT,
                    sentence_id INTEGER NOT NULL,
                    FOREIGN KEY(sentence_id) REFERENCES sentences(sentence_id) ON DELETE CASCADE ON UPDATE CASCADE);'''


def create_sents_from_tokens(tokentable, toktextcol, connection):
    stmt = f"SELECT {toktextcol}, sentence_id FROM {tokentable} ORDER BY sentence_id, token_order;"
    cursor = connection.cursor()
    tokens = cursor.execute(stmt).fetchall()
    return [(" ".join([token[0] for token in sent]), key) for key, sent in groupby(tokens, key=itemgetter(1))]

def regenerate_sents(connection):
    sentences = create_sents_from_tokens("tokens", "token_text", connection)
    cursor = connection.cursor()
    update_stmt = "UPDATE sentences SET sentence_text = ? WHERE sentence_id = ?;"
    cursor.executemany(update_stmt, sentences)
    connection.commit()


def insert_normalized(grammar, connection):
    normalized_toks = normalize_tokens(grammar, connection)
    tokvals = []
    normalized_sents = []
    for sent in normalized_toks:
        normsent_text = " ".join([w["token_text"] for w in sent])
        sent_id = sent[-1]["sentence_id"]
        normalized_sents.append((normsent_text, sent_id))
        for t in sent:
            tokvals.append((t["token_id"], t["token_order"], t["token_text"], t["nonstandard_spelling"],
                            t["standardized_form"], t["special_status"], t["language_code"],
                            t["phon_ort_discrepancy"], t["sentence_id"], t["converted"]))
    

    insert_sent_stmt = '''INSERT OR REPLACE INTO normsentences (normsentence_text, sentence_id) VALUES (?,?);'''
    insert_tok_stmt = '''INSERT OR REPLACE INTO normtokens (normtok_id, token_order, token_text, nonstandard_spelling,
                     standardized_form, special_status, language_code, phon_ort_discrepancy, sentence_id, converted)
                     VALUES (?,?,?,?,?,?,?,?,?,?);'''
    
    cursor = connection.cursor()
    cursor.executemany(insert_sent_stmt, normalized_sents)
    print("Inserted normalized sentences")
    cursor.executemany(insert_tok_stmt, tokvals)
    print("Inserted normalized tokens")
    connection.commit()

def insert_translated(connection):
    translated_sents = translate_corpus(connection)

    insert_trans_stmt = '''INSERT OR REPLACE INTO transsentences
                        (translated, transsentence_text, language_code, sentence_id)
                        VALUES (?,?,?,?);'''
    cursor = connection.cursor()
    cursor.executemany(insert_trans_stmt, translated_sents)
    print("Inserted translated sentences")
    connection.commit()


if __name__ == "__main__":
    db = "stortinget_speech_corpus.db"
    typos = "feilretting_NPSC-søk-erstatt.csv"
    bs_typos = "feilretting_NPSC-bakstrek.csv"
    grammar = abbrevgrammar ^ dategrammar ^ yeargrammar ^ numbergrammar_abovethirteen

    try:
        sqliteConnection = sqlite3.connect(db)
        print("Successfully Connected to SQLite")

        # Setup of new tables
        cursor = sqliteConnection.cursor()
        cursor.execute(create_normtokens_table)
        print("Created normtokens table")
        cursor.execute(create_normsentences_table)
        print("Created normsentence table")
        cursor.execute(create_transsentences_table)
        print("Created transsentences table")
        sqliteConnection.commit()

        # Run correction scripts
        apply_corrections(typos, bs_typos, sqliteConnection)
        print("Applied corrections")

        # # Regenerate sentences based on tokens
        regenerate_sents(sqliteConnection)
        print("Regenerated sentences")
        
        # # Make normalized version
        insert_normalized(grammar, sqliteConnection)

        # Make translated version of normalized text
        insert_translated(sqliteConnection)


    except sqlite3.Error as error:
        print("SQL error: ", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("sqlite connection is closed")