import sqlite3
import sys

def read_typofile(typofilename):
    with open(typofilename, "r") as typofile:
        typos = [l.strip().split(",") for l in typofile.readlines()[1:]]
        for x in typos:
            if x[-1] == "":
                x[-1] = "0"
        return typos


def read_bsfile(bsfilename):
    with open(bsfilename, "r") as backslashfile:
        return [l.strip().split(",") for l in backslashfile.readlines()[1:]]

def apply_corrections(typofilename, bsfilename, connection):
    stmt_typo = "UPDATE tokens SET token_text = ?, phon_ort_discrepancy = ? WHERE token_text = ? AND language_code = ?;"
    stmt_backslash = ('UPDATE tokens SET nonstandard_spelling = 1, standardized_form = ? '
                      'WHERE token_text = ? AND nonstandard_spelling = 0 AND language_code = "nn-NO";')
    typos = read_typofile(typofilename)
    bstypos = read_bsfile(bsfilename)
    typo_values = [(x[1], x[3], x[0], x[2]) for x in typos]
    bs_values = [(x[1], x[0]) for x in bstypos]

    cursor = connection.cursor()

    cursor.executemany(stmt_typo, typo_values)
    cursor.executemany(stmt_backslash, bs_values)
    connection.commit()

if __name__ == "__main__":    
    typos = sys.argv[1]
    bs_typos = sys.argv[2]
    db = sys.argv[3]
    try:
        sqliteConnection = sqlite3.connect(db)
        print("Successfully Connected to SQLite")

        apply_corrections(typos, bs_typos, sqliteConnection)
        print("Corrections applied")


    except sqlite3.Error as error:
        print("Error while creating a sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
            print("sqlite connection is closed")