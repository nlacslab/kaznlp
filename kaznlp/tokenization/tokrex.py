# -*- coding: UTF-8 -*-

import re

class TokenizeRex():
    '''
    Regex-based tokenizer. Fast, but does not perform sentence splitting.
    '''    
    def __init__(self):
        # regex that matches non-alphanums, non-hyphens, and non-spaces
        self.rex_split = re.compile(
                u'[^a-zа-яёәіңғүұқөһ\-\–\—\d\s]', re.U|re.I)
        # regex that matches leading untokenized hyphens, e.g. "Oh [-]yes"
        self.rex_hlead = re.compile(u'\s([\-\–\—]+)([^\s])', re.U)
        # regex that matches trailing untokenized hyphens, e.g. "yes[-] no"
        self.rex_htral = re.compile(u'([^\s])([\-\–\—]+)\s', re.U)
        # regex that matches *tokenized* multiple hyphen strings,
        # e.g. " [--] yes "
        self.rex_hmult = re.compile(u'\s([\-\–\—]{2, })\s', re.U)
    
    def tokenize(self, txt, lower=False):
        '''
        Returns a list of sentences. Each sentence is a list containing tokens.
        This particular implementation, however, 
        always returns a single sentence, i.e. performs no sentence splitting.
        If [lower] is True the input is lowercased *after* tokenization.
        '''
        # enclose non-alphanums, non-hyphens, and non-spaces into spaces
        spaced = self.rex_split.sub(' \g<0> ', txt)
        # detach hyphens
        dehyphened = self.rex_hlead.sub(' \g<1> \g<2>', u' %s'%spaced)
        dehyphened = self.rex_htral.sub('\g<1> \g<2> ', u'%s '%dehyphened)
        # break multi-hyphen strings
        while True:
            m = self.rex_hmult.search(dehyphened)
            if not m:
                break
            target = m.group(1)
            dehyphened = dehyphened[:m.start(1)]
            dehyphened += ' '.join(target) + dehyphened[m.end(1):]
        dehyphened = dehyphened.lower() if lower else dehyphened
        return [dehyphened.split()]
