# -*- coding: UTF-8 -*-
import math


def softmax(data, maxval=None):
    maxval = maxval or max(data.values())
    distr = {k: math.exp((v + 1) / (abs(maxval) + 1)) for k, v in data.items()}
    argmax = (float('-inf'), None)
    tot = sum(distr.values())
    for k in distr.keys():
        distr[k] /= tot
        if distr[k] > argmax[0]:
            argmax = (distr[k], k)
    return argmax[-1], distr


class NB():

    def __init__(self, mdl_fn):
        self.classes = []
        self.level = 'WORD'
        self.other = 'other'
        self.min_ngram, self.max_ngram = 1, 1
        self.trm_probs = {}
        self.load_model(mdl_fn)

    def load_model(self, fn):

        def reset_secs(d):
            return {k: 0 for k in d}

        secs = {'ngram_range': 0,
                'classes': 0,
                'feature-type': 0,
                'features': 0}
        for line in open(fn, 'r').readlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('[') and line.endswith(']'):
                if line == '[ngram range]':
                    secs = reset_secs(secs)
                    secs['ngram_range'] = 1
                elif line == '[classes]':
                    secs = reset_secs(secs)
                    secs['classes'] = 1
                elif line == '[feature-type]':
                    secs = reset_secs(secs)
                    secs['feature-type'] = 1
                elif line == '[features]':
                    secs = reset_secs(secs)
                    secs['features'] = 1
            elif secs['ngram_range']:
                [self.min_ngram, self.max_ngram] = [
                        int(v) for v in line.split()]
            elif secs['classes']:
                self.classes.append(line)
            elif secs['feature-type']:
                self.level = (line in ['CHAR', 'WORD']) and line or self.level
            elif secs['features']:
                try:
                    [trm, lbl, prb] = line.split('\t')
                except:
                    continue
                self.trm_probs[trm, lbl] = float(prb)
        self.other = self.classes[-1]

    def predict(self, toks):
        return self.predict_wp(toks).get('result')

    def predict_wp(self, toks):
        prbs = {}
        docs = []
        if self.level == 'CHAR':
            for t in toks:
                docs.append([c for c in t])
        else:
            docs.append(toks)
        # compute probability of a document
        for doc in docs:
            if self.min_ngram == self.max_ngram == 1:
                # unigrams do not require word/sentence initial/final symbols
                pass
            else:
                doc = ['*'] + doc + ['*']
            # ngram counts
            buff = []
            for tok in doc:
                buff.append(tok)
                if len(buff) < self.min_ngram:
                    continue
                if len(buff) > self.max_ngram:
                    buff = buff[1:]
                for i in range(self.min_ngram, self.max_ngram+1):
                    if i > len(buff):
                        continue
                    ngm = ' '.join(buff[-1*i:])
                    for c in self.classes:
                        prbs[c] = prbs.get(c, 0.0)
                        prbs[c] += self.trm_probs.get(
                                (ngm, c), self.trm_probs['<OOV>', c])
        # if nothing came out - label as other
        if not prbs:
            ret = {c: (c == self.other and 1.0 or 0.0) for c in self.classes}
            ret['result'] = self.other
        else:
            # add priors
            ret = {'result': [float('-inf'), 'None']}
            mxp = float('-inf')
            for c in self.classes:
                prbs[c] = prbs.get(c, 0.0)
                prbs[c] += self.trm_probs.get(('<PRR>', c), 0.0)
                if prbs[c] > mxp:
                    mxp = prbs[c]
            # normalize probabilities
            [argmax, ret] = softmax(prbs, mxp)
            ret['result'] = argmax
        return ret


class LidNB():

    def __init__(self, word_mdl=None, char_mdl=None):
        self.word_mdl = word_mdl and NB(word_mdl) or None
        self.char_mdl = char_mdl and NB(char_mdl) or None

    def predict(self, toks):
        return self.predict_wp(toks).get('result')

    def predict_wp(self, toks):
        if self.word_mdl and self.char_mdl:
            # combine model probabilities
            prbs = {}
            pd1 = self.word_mdl.predict_wp(toks)
            del pd1['result']
            pd2 = self.char_mdl.predict_wp(toks)
            del pd2['result']
            for k, v in pd1.items():
                prbs[k] = pd1[k] + pd2[k]
            [argmax, ret] = softmax(prbs)
            ret['result'] = argmax
            return ret
        else:
            model = self.word_mdl or self.char_mdl
            return model.predict_wp(toks)
