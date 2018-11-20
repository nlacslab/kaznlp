# -*- coding: UTF-8 -*-

import sys
import os
import codecs
import time
import math
import re


# punctuation
punc_tag = {
    u'"':u'TRN',
    u'\'':u'APS',
    u',':u'UTR',
    u'.':u'NKT',
    u'\\':u'BSLH',
    u'/':u'SLH',
    u'-':u'DPH',
    u':':u'QNKT',
    u';':u'UNKT',
    u'?':u'SUR',
    u'!':u'LEP',
    u'«':u'ATRN',
    u'»':u'ZTRN',
    u'“':u'ATRN',
    u'”':u'ZTRN',
    u'``':u'ATRN',
    u"''":u'ZTRN',
    u'—':u'DSH',
    u'(':u'AZZ',
    u')':u'ZZZ',
    u'[':u'ADZ',
    u']':u'ZDZ',
    u'{':u'ASZ',
    u'}':u'ZSZ'}

# numerals
rex_num = re.compile('[\d]+[\.,‚]*[\d]*',re.U)

# time routings
def gettime(tmstr,tf='%Y-%m-%d, %H:%M:%S'):
    return time.strptime(tmstr,tf)

def saytime(tm=None,tf='%Y-%m-%d, %H:%M:%S'):
    if tm is None:
        tm = time.localtime()
    else:
        tm = time.localtime(gettime(tm))
    return time.strftime(tf,tm)

# ios
def get_lines(fn,enc='utf-8',strip=1,keep_emp=0,comm=None):
    lns = []
    for l in codecs.open(fn,'r',enc).readlines():
        #skip comments if required
        if comm:
            cidx = l.find(comm)
            if cidx+1:
                l = l[:cidx]
        #strip if required
        l = (strip and [l.strip()] or [l])[0]
        #skip empty lines if keep_emp is false
        if not (keep_emp or l): continue
        lns.append(l)
    return lns

# getting sentences from a file - specific action
def get_sens(fn,enc='utf-8',dlm='*_*',bad_tkn='?_?'):
    sens = []
    cs = []
    for l in get_lines(fn,enc,strip=1)+[dlm]:
        if l==dlm:
            if cs: sens.append(cs)
            cs = []
        elif not l==bad_tkn:
            cs.append(l)
    return sens


# ngram LM
class nglm():
    
    def __init__(self,N,seqs={},voc={},alpha=0.001,log=None):
        self.seqsize = N
        self.seqs = seqs
        self.voc = voc
        self.alpha = alpha
        self.log = log
        self.vocsize = len(voc)
    
    def build_ff(self,fn,enc='utf-8',dlm='\t',ndlm=' ',em='*'):
        for l in get_lines(fn,enc,strip=1,comm='#'):
            ents = l.split(dlm)
            seq,cnt = tuple(ents[:-1]),int(ents[-1])
            self.seqs[seq] = cnt
            pfx = seq[:-1]
            self.voc[pfx] = self.voc.get(pfx,0) + int(cnt)
        self.vocsize = self.seqsize==1 and len(self.seqs) or len(self.voc)

    def prb(self,s):
        p = 1.0*self.seqs.get(s,0) + self.alpha
        p /= (self.voc.get(s[:len(s)-1],0) + self.alpha*self.vocsize)
        return math.log(p)
    
    def chain_prb(self,seq):
        return sum([self.prb(s) for s in seq])

# text processing

# vowel regex
vwl = re.compile(u'[аәеёиоөуүұыіэюя]+',re.U|re.I)
def get_vowels(txt):
    return vwl.findall(txt)


# get ngrams from a sequence
def get_ngrams(N=1,seq=[],frnt=1,rear=1,atag='*'):
    if not seq:
        return []
    ret = []
    seq = frnt and (N-1)*['*'] + seq or seq
    seq = rear and seq + (N-1)*['*'] or seq
    for i in range(len(seq)-N+1):
        ret.append(tuple(seq[i:i+N]))
    return ret


# split morpheme into surface form and pos transition(s)
def split_morph(m,mdlm='_'):
    ms = {'sf':'?','lp':'?','rp':'?'}
    ents = m.split(mdlm)
    ms['sf'] = ents[0]
    try:
        ms['lp'] = ents[1]
    except:
        pass
    try:
        ms['rp'] = ents[2]
    except:
        pass
    return ms


# get a shallow parse
def make_shlw(seg,sdlm=' ',mdlm='_'):
    if seg=='*':
        return '*'
    mrphs = seg.split(sdlm)
    shlw = [mrphs[0]]
    lpos = split_morph(mrphs[0])['rp']
    for m in mrphs[1:]:
        ms = split_morph(m)
        if ms['rp']=='?':
            shm = mdlm.join([ms['sf'],lpos,lpos])
        else:
            shm = mdlm.join([ms['sf'],lpos,ms['rp']])
            lpos = ms['rp']
        shlw.append(shm)
    return sdlm.join(shlw)

        
# get sf of a parse
def get_parse_sf(p,sdlm=' ',mdlm='_',joiner=''):
    sf = []
    for m in p.split(sdlm):
        sf.append(split_morph(m)['sf'])
    return joiner.join(sf)


# get tag of a parse
def get_parse_tg(p,sdlm=' ',mdlm='_',joiner='-'):
    tg = []
    for m in p.split(sdlm):
        tg.append(mdlm.join(m.split(mdlm)[1:]))
    return joiner.join(tg)


# get segmentation of a parse
def get_parse_seg(p,sdlm=' ',mdlm='_'):
    return get_parse_sf(p,sdlm,mdlm,' ')


# get stem sf, tag and tag of the last IG
def split_stm_lig(txt,stm_sf=1,sdlm=' ',mdlm='_',stm_dlm=' ',tag_dlm='-'):
    mrphs = txt.split(sdlm)
    stm,stm_tg,lig = [],[],[]
    got_lig = 0
    for i in range(len(mrphs)-1,-1,-1):
        m = mrphs[i]
        ms = split_morph(m,mdlm)
        if (not got_lig) and (not ms['rp']=='?'):
            lig.insert(0,ms['rp'])
            got_lig = 1
        if got_lig:
            stm.insert(0,stm_sf and ms['sf'] or m)
            tg = ms['lp'] + (not ms['rp']=='?' and mdlm+ms['rp'] or '')
            stm_tg.insert(0,tg)
        else:
            lig.insert(0,ms['lp'])
    stm = len(stm)>1 and stm[:-1] or stm
    stm = (not stm_sf and sdlm or '').join(stm)
    stm = stm_sf and stm or mdlm.join(stm.split(mdlm)[:-1])
    return ''.join(stm),tag_dlm.join(stm_tg),tag_dlm.join(lig)


# get IG-s
def get_igps(txt,sdlm=' ',mdlm='_',ig_dlm='-'):
    root,parm = split_root_parm(txt,sdlm,mdlm)
    igps = [split_morph(root,mdlm)['rp']]
    igps_cp = [root]
    for m in parm.split(sdlm):
        ms = split_morph(m,mdlm)
        if not ms['sf']: continue
        if ms['rp']=='?':
            igps[-1] += ig_dlm + ms['lp']
            igps_cp[-1] += sdlm + m
        else:
            igps.append(ms['rp'])
            igps_cp.append(m)
    return igps,igps_cp


# get the root of an analysis
def get_root(txt,sdlm=' ',mdlm='_'):
    return split_morph(txt.split(sdlm)[0])


# split the root and the paradigm in a raw form (mixed with sf)
def split_root_parm(txt,sdlm=' ',mdlm='_'):
    ents = txt.split(sdlm)
    root = ents[0]
    parm = sdlm.join(ents[1:])
    return root,parm


# get pos paradigm
def get_pos_paradigm(txt,sdlm=' ',mdlm='_',joiner='-'):
    root,parm = split_root_parm(txt,sdlm,mdlm)
    #parm = [get_root(txt,sdlm,mdlm)['rp']]
    #for m in txt.split(sdlm)[1:]:
    #ms = split_morph(m,mdlm)
    #pe = ms['lp'] + (not ms['rp']=='?' and mdlm+ms['rp'] or '')
    #parm.append(pe)
    ret =  get_parse_tg(root,sdlm,mdlm)
    ret += parm and joiner + get_parse_tg(parm,sdlm,mdlm,joiner) or ''
    return ret


def get_cnts(fn,cdlm='_',log=None):
    cnts = {}
    if not fn:
        return cnts
    for l in get_lines(fn):
        try:
            ents = l.split(cdlm)
            sq = cdlm.join(ents[:-1])
            cnt = float(ents[-1])
        except:
            continue
        cnts[sq] = cnt
    return cnts

