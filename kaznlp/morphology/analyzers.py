# -*- coding: UTF-8 -*-

from __future__ import division
import os
import kaznlp.morphology.utils as utils


class AnalyzerDD():

    def __init__(self, md={}, tm={}, sfx={},
                 unts=['R_X'],
                 prn_sgs=True, oov=False,
                 sdlm=' ', mdlm='_', log=None):
        self.md = md
        self.tm = tm
        self.sfx = sfx
        self.unts = unts
        # self.parms = parms
        self.plm = None
        self.prn_sgs = prn_sgs
        self.oov = oov
        self.sdlm = sdlm
        self.mdlm = mdlm
        self.log = log

    def load_model(self, mdl_dir):
        # build morpheme and transition dictionaries
        self.getff_md(os.path.join(mdl_dir, 'md'))
        self.getff_tm(os.path.join(mdl_dir, 'tm'))
        # build suffix-paradigm mappings
        self.getff_sfx(os.path.join(mdl_dir, 'sfx'))

    # get morpheme dictionary from file
    def getff_md(self, fn, enc='utf-8', dlm='\t', mdlm=None):
        mdlm = mdlm and mdlm or self.mdlm
        for l in utils.get_lines(fn, enc, strip=1):
            # morpheme mapping
            [t1, t2] = l.split(dlm)
            self.md[t2] = self.md.get(t2, {})
            self.md[t2][t1] = 1

    # get transition dictionary from file
    def getff_tm(self, fn, enc='utf-8', dlm='\t', mdlm=None):
        mdlm = mdlm and mdlm or self.mdlm
        for l in utils.get_lines(fn, enc, strip=1):
            # morpheme mapping
            [t1, t2] = l.split(dlm)
            self.tm[t1] = self.tm.get(t1, {})
            self.tm[t1][t2] = 1

    # get sufix-paradigm mapping from file
    def getff_sfx(self, fn, enc='utf-8', dlm='\t', mdlm=None):
        for l in utils.get_lines(fn, enc, strip=1):
            [sf, sfx] = l.split(dlm)
            self.sfx[sf] = self.sfx.get(sf, {})
            self.sfx[sf][sfx] = 1

    # get tags for unsegmented inputs from file
    def getff_unts(self, fn, enc='utf-8'):
        self.unts = utils.get_lines(fn, enc, strip=1)

    # returns segementation on shallow morphs
    def segment(self, pfx, ret={}, cpos='*', cseq=''):
        # roots must have at least one vowel
        # (achronyms are handled by the anlysis)
        if not (pfx and utils.get_vowels(pfx)):
            return
        for m in self.tm.get(cpos, []):
            # check for root case
            if m.split(self.mdlm)[0] == 'R':
                # if we got a suitable root or oov roots are fine - save
                if self.oov or pfx in self.md[m]:
                    root = pfx + self.mdlm + m
                    if cseq:
                        new_anl = root + self.sdlm + cseq
                    else:
                        new_anl = root
                    ret[new_anl] = 1
                continue
            # iterate through the surface forms of the morpheme
            for msf in self.md[m]:
                # get full morpheme - with sf; and left pos
                mor = msf + self.mdlm + m
                # update morph. seq
                if cseq:
                    new_seq = mor + self.sdlm + cseq
                else:
                    new_seq = mor
                if pfx.endswith(msf):
                    # we got a suitable sf
                    new_pfx = pfx[:-1*len(msf)]
                    # no vowel in a candidate root - skip
                    if not utils.get_vowels(new_pfx):
                        continue
                    # skip if we got unseen suffix and prune mode is on
                    if self.prn_sgs:
                        sf = utils.get_parse_sf(new_seq,
                                                self.sdlm, self.mdlm, '')
                        tg = utils.get_parse_tg(new_seq,
                                                self.sdlm, self.mdlm, '-')
                        if tg not in self.sfx.get(sf, []):
                            continue
                    # continue recursively into the depth
                    self.segment(new_pfx, ret, m, new_seq)

    # returns analyses including all root-word possibilities
    def analyze(self, tkn, top=0):
        # punctuation
        if tkn in utils.punc_tag:
            tkn + self.mdlm + 'R_' + utils.punc_tag[tkn]
            return False, [tkn + self.mdlm + 'R_' + utils.punc_tag[tkn]]
        # numerals
        if not utils.rex_num.sub('', tkn):
            return False, [tkn + '_R_SN']
        # get segmentations
        sgs = {}
        self.segment(tkn, sgs)
        anls = list(sgs.keys())
        # unsegmented input tag by special tags
        if not anls:
            for t in self.unts:
                anls.append(tkn + self.mdlm + t)

        return bool(sgs), anls
