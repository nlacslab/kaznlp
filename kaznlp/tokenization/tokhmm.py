# -*- coding: UTF-8 -*-

from kaznlp.models.hmm import HMM_DI
import re

# character processing regex with replacements
CPREX = {
        # uppercase mathcer and replacer
        re.compile(u'[A-ZА-ЯЁӘІҢҒҮҰҚӨҺ]',re.U):'CAP',
        # lowercase mathcer and replacer
        re.compile(u'[a-zа-яёәіңғүұқөһ]',re.U):'LOW',
        # sentence-final punctuation matcher and replacer
        re.compile(u'[\.\?\!]',re.U):'SFL',
        # spaces (tab, whitespace, new line, carrier) matcher and replacer
        re.compile(u'\s',re.U):'SPC',
        # digit matcher and replacer
        re.compile(u'\d',re.U):'DIG'
        }


class TokenizerHMM():
    
    def __init__(self, implementation=HMM_DI, model=None):
        self.hmm = implementation()
        if model:
            self.hmm.load_model(model)
    
    def get_sequence(slef, txt):
        ret = []
        for c in txt:
            for rex, rep in CPREX.items():
                if rex.match(c):
                    c = rep
                    break
            ret.append(c)
        return ret
    
    def tokenize(self, txt, lower=False):        
        ret = []
        curr_sen = []
        curr_tok = []
        for i, label in enumerate(self.hmm.generate(self.get_sequence(txt))):
            char = txt[i]
            if label == 'S':
                if curr_tok:
                    curr_tok = ''.join(curr_tok)
                    curr_tok = curr_tok.lower() if lower else curr_tok
                    curr_sen.append(curr_tok)
                if curr_sen:
                    ret.append(curr_sen)
                    curr_sen = []
                curr_tok = [char]
            elif label == 'T':
                if curr_tok:
                    curr_tok = ''.join(curr_tok)
                    curr_tok = curr_tok.lower() if lower else curr_tok
                    curr_sen.append(curr_tok)
                curr_tok = [char]
            elif label == 'I':
                curr_tok.append(char)
            elif label == 'O':
                if curr_tok:
                    curr_tok = ''.join(curr_tok)
                    curr_tok = curr_tok.lower() if lower else curr_tok
                    curr_sen.append(curr_tok)
                curr_tok = []
        if curr_tok:
            curr_tok = ''.join(curr_tok)
            curr_tok = curr_tok.lower() if lower else curr_tok
            curr_sen.append(curr_tok)
            ret.append(curr_sen)
        return ret
