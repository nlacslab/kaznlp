# -*- coding: UTF-8 -*-

from __future__ import division
import kaznlp.morphology.utils as utils
from kaznlp.morphology.analyzers import AnalyzerDD

import os
import itertools
import copy


class TaggerHMM():

    def __init__(
            self,
            mode='IP', cw=3,
            lyzer=None, transi=None, emissi=None,
            lkp={}, pc={},
            sen_dlm='*_*', seg_dlm=' ', mor_dlm='_', mor_jnr='-',
            gen_dlm='\t', ng_dlm=' ', pc_dlm='~@~',
            em='*', ph='#', de='utf-8', log=None):

        # general stuff
        self.mode = mode
        self.cw = cw
        # analyzer and transition, emission LM objects
        self.lyzer = lyzer or AnalyzerDD()
        self.transi = transi
        self.emissi = emissi
        # init dictionaries
        self.lkp = lkp
        self.pc = pc
        self.own_lkp = {}
        # sentence dlm
        self.sen_dlm = sen_dlm
        # segementation dlm (default in parenthesis): men_R_SIM( )i_C4
        self.seg_dlm = seg_dlm
        # morpheme dlm (default in parenthesis): men(_)R(_)SIM i(_)C4
        self.mor_dlm = mor_dlm
        # morpheme joiner (default in parenthesis): R(-)SIM(-)C4
        self.mor_jnr = mor_jnr
        # general delimeter (default in parenthesis): wrd(\t)tag
        self.gen_dlm = gen_dlm
        # ngram delimeter (default in parenthesis): w1( )w2( )w3
        self.ng_dlm = ng_dlm
        # empty marker for N-grams (default in parenthesis): (*) (*) wrd
        self.em = em
        # pre-computed data delimeter (default in parenthesis): w(~@~)f1(~@~)f2
        self.pc_dlm = pc_dlm
        # pre-computed data header-mark (default in parenthesis): (# )h1~@~h2
        self.ph = ph
        # default encoding: utf-8
        self.de = de
        # set log file descriptor
        self.log = log

    def load_model(self, mdl_dir):
        # create a transition LM instance
        self.new_transi(
                # pass transition smoothing coefficient
                smth=0.01)
        # build the transition LM: depending on MODE consider
        # either IG- or paradigm-based transition
        tfn = (self.mode.count('I') and 'ligs.' or 'prms.')
        tfn += str(self.cw) + 'gram'
        self.buildff_transi(os.path.join(mdl_dir, tfn))
        # create an emission LM instance
        self.new_emissi(
                # pass emission smoothing coefficient
                smth=0.01)
        # build the emission LM: depending on MODE consider
        # either wrd|prm or stm-prm|IG probabilities
        efn = self.mode.count('P') and 'wrd_tag' or 'stm_lig'
        self.buildff_emissi(os.path.join(mdl_dir, efn))
        # populate the look-up dictionary
        self.getff_lkp(os.path.join(mdl_dir, 'lkps'))

    # LM ROUTINES: TRANSITION
    def new_transi(self, cw=None, smth=1, log=None):
        cw = cw or self.cw
        log = log or self.log
        self.transi = utils.nglm(cw, {}, {}, smth, log)

    def buildff_transi(self, fn, enc=None, dlm=None, ndlm=None, em=None):
        enc = enc or self.de
        dlm = dlm or self.gen_dlm
        ndlm = ndlm or self.ng_dlm
        em = em or self.em
        self.transi.build_ff(fn, enc, dlm, ndlm, em)

    def set_transi(self, t):
        self.transi = t

    # LM ROUTINES: EMISSION
    def new_emissi(self, smth=1, log=None):
        log = log or self.log
        self.emissi = utils.nglm(2, {}, {}, smth, log)

    def buildff_emissi(self, fn, enc=None, dlm=None, ndlm=None, em=None):
        enc = enc or self.de
        dlm = dlm or self.gen_dlm
        ndlm = ndlm or self.ng_dlm
        em = em or self.em
        self.emissi.build_ff(fn, enc, dlm, ndlm, em)

    def set_emissi(self, e):
        self.emissi = e

    # DICTIONARIES: LOOK-UP and PRE-COMPUTED DATA
    def getff_lkp(self, fn, enc=None, dlm=None):
        enc = enc or self.de
        dlm = dlm or self.gen_dlm
        for l in utils.get_lines(fn, enc, strip=1):
            [sf, tg, cnt] = l.split(dlm)
            self.lkp[sf] = self.lkp.get(sf, []) + [tg]

    def getff_pc(self, fn, enc=None, pdlm=None, ph=None):
        enc = enc or self.de
        pdlm = pdlm or self.pc_dlm
        ph = ph or self.ph
        cats = {}
        for l in utils.get_lines(fn, enc, strip=1):
            if l.startswith(ph):
                if not cats:
                    for i, cat in enumerate(l[1:].split(self.pc_dlm)):
                        cats[cat] = i
                continue
            elif not cats:
                continue
            vals = l.split(pdlm)
            lyses = vals[cats['[lyses]']:]
            self.pc[vals[0]] = lyses

    def tag_sentence(self, s):

        def vbi(anls):
            # pre- and append "*" - empty ngram chars
            shft = self.cw - 1
            # empty entry
            emp = {'anl': self.em, 'emprb': 0.0, 'trtag': self.em}
            ems = [[emp] for i in range(shft)]
            anls = ems + anls + ems
            # viterbi prob-paths list
            vp = []
            # initial prb-s and path
            for i in range(shft):
                vp.append([(0.0, (i+1)*[self.em])])
            # calculate max prb path
            for i in range(shft, len(anls)):
                cc = [[float('-inf'), ''] for e in range(len(anls[i]))]
                for tup in itertools.product(
                        *(range(len(anls[j])) for j in range(i-shft, i))):
                    for ca, a in enumerate(anls[i]):
                        prb, pth, seq = 0.0, [], ()
                        for k, t in enumerate(tup):
                            seq += (anls[i - shft + k][t]['trtag'], )
                            if not pth:
                                [prb, pth_copy] = vp[i - shft + k][t]
                                pth = copy.copy(pth_copy)
                            else:
                                pth.append(anls[i - shft + k][t]['anl'])
                        seq += (a['trtag'], )
                        pth.append(a['anl'])
                        prb += self.transi.prb(seq)
                        if cc[ca][0] < prb:
                            cc[ca] = [prb, pth]
                vp.append(cc)
            return vp[-1][0][-1][shft:-shft]

        # get all analyses
        anls = self.analyze_sentence(s)
        return vbi(anls)

    # analyse a sentnece
    def analyze_sentence(self, s):
        # analyze words
        anls = []
        for w in s:
            # check own look-up first
            wa = self.own_lkp.get(w, {})
            if wa:
                # already formatted for tagging - save and continue
                anls.append(wa)
                continue
            # if not in own look-up, check pc
            wa = self.pc.get(w, [])
            # if not in pc, check look-ups
            wa = wa and wa or self.lkp.get(w, [])
            # if still unlucky - analyze
            wa = wa and wa or self.lyzer.analyze(w)[-1]
            # format for tagging and save
            tmp = []
            for a in wa:
                fa = {'anl': a}
                wrd = utils.get_parse_sf(a, self.seg_dlm, self.mor_dlm)
                tag = utils.get_parse_tg(
                        a, self.seg_dlm, self.mor_dlm, self.mor_jnr)
                trtag = tag
                if self.mode.count('I'):
                    trtag = utils.get_igps(
                            a, self.seg_dlm, self.mor_dlm, self.mor_jnr)[0][-1]
                    if self.mode == 'I':
                        wrd = a[:a.rfind(
                                trtag.split('-')[0])].rstrip(self.mor_dlm)
                        tag = trtag
                fa['trtag'] = trtag
                fa['emprb'] = self.emissi.prb((tag, wrd))
                tmp.append(fa)
            anls.append(tmp)
            # update own look-up
            self.own_lkp[w] = tmp
        return anls
