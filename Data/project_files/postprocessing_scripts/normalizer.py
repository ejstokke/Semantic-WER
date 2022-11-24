import sqlite3
from operator import itemgetter 
from itertools import groupby
from grammars.number_grammar import numbergrammar_abovethirteen
from grammars.year_grammar import yeargrammar
from grammars.date_grammar import dategrammar
from grammars.abbrev_grammar import abbrevgrammar
from copy import deepcopy

def tokendict(ttpl):
    """Dict representation of tokens from db"""
    return {'token_id': ttpl[0], 'token_order': ttpl[1], 'token_text': ttpl[2], \
            'nonstandard_spelling': True if ttpl[3] == 1 else False, 'standardized_form': ttpl[4], \
           'special_status': ttpl[5], 'language_code': ttpl[6], 'phon_ort_discrepancy': ttpl[7], \
           'sentence_id': ttpl[8]}

def text_or_standard(token):
    return token['standardized_form'] if token['nonstandard_spelling'] else token['token_text']

def string_to_list_index(joinedstring):
    """return end indexes in string og each word when split on space"""
    returnlist = []
    length = len(joinedstring)
    for n, l in enumerate(joinedstring):
        if l == " ":
            returnlist.append(n)
    returnlist.append(length)
    return returnlist

def match_to_index(match, indexlist):
    """compare the end index of a match in a string, and return the index of the matching end token
    in a tokenized version of the searched string"""
    for n, ind in enumerate(indexlist):
        if match == ind:
            return n

def identify_matchspans(tokenlist, grammar):
    """Given a list of tokens and a grammar, return a list of matchspans as a dict with the original text of the match,
    the replacement text, the token length, the index of the start token in the token list and the index of the end token
    in the token list"""
    spans = []
    standardlist = [text_or_standard(t) for t in tokenlist]
    standardstring = " ".join(standardlist) # String representation of sent with standard orthography
    indexes = string_to_list_index(standardstring) # "Hei på deg": [3, 6, 10]
    searchmatches = grammar.searchString(standardstring)
    for m in searchmatches:
        matchlen = len(m[0][0].split(" ")) # Length of match in original form
        tokind = match_to_index(m[1], indexes) # Find endindex of match in standardstring. match_to_index(6, [3, 6, 10]) = 2
        spans.append({'orig': m[0][0], 'rep': m[0][1], 'length': matchlen, \
                      'span_start': tokind-matchlen+1, 'span_end': tokind+1}) # {'orig': 'på', 'rep': 'p.', 'length': 1, 'span_start': 2, 'span_end': 3}
    return spans

def prepare_converted_tokens(wordtoks):
    """Make new tokens with the additional k, v "converted": False """
    newsent = deepcopy(wordtoks)
    for tok in newsent:
        tok["converted"] = False
    return newsent


def normalize_tokens(grammar, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM tokens;")
    tokens = [tokendict(x) for x in cursor.fetchall()]

    sentence_tokens = [[token for token in sent] for key, sent in groupby(tokens, key=itemgetter('sentence_id'))]

    sentences = []
    for s in sentence_tokens: # [tokens in sent]
        standardlist =[text_or_standard(t) for t in s] # ['hei', 'på', 'deg']
        newsent = prepare_converted_tokens(s) # [{'token_text: 'hei'...
        spanlist = identify_matchspans(s, grammar) # [{'orig': 'på', 'rep': 'p.', 'length': 1, 'span_start': 2, 'span_end': 3}]
        for n, sp in enumerate(spanlist):
            oldstarttoken = s[sp['span_start']] # s[2]
            oldendtoken = s[sp['span_end']-1] # s[2]
            newtoken = {"converted": True, "token_id": f's{oldstarttoken["token_id"]}e{oldendtoken["token_id"]}',
                    "token_text": str(sp["rep"]), "token_order": oldstarttoken["token_order"],
                    "nonstandard_spelling": False, "standardized_form": None, "special_status": None,
                    "language_code": oldstarttoken["language_code"], "phon_ort_discrepancy": False,
                    "sentence_id": oldstarttoken["sentence_id"]}

            newsent = newsent[:sp['span_start']] + [newtoken] + newsent[sp['span_end']:] # Repl old token(s) w new token
            for addsp in spanlist[n:]: # Recalibrate start and end token indexes of subsequent spans since replaced tokens may shorten token list
                addsp['span_start'] = addsp['span_start'] - sp['length']+1
                addsp['span_end'] = addsp['span_end'] - sp['length']+1
        sentences.append(newsent)
    return sentences



if __name__ == "__main__":
    grammar = abbrevgrammar ^ dategrammar ^ yeargrammar ^ numbergrammar_abovethirteen
    converted_sents = convert("stortinget_speech_corpus.db", grammar)

