# -*- coding: UTF-8 -*-
from __future__ import print_function
import os

from kaznlp.normalization.ininorm import Normalizer

from kaznlp.tokenization.tokrex import TokenizeRex
from kaznlp.tokenization.tokhmm import TokenizerHMM

from kaznlp.lid.lidnb import LidNB

from kaznlp.morphology.analyzers import AnalyzerDD
from kaznlp.morphology.taggers import TaggerHMM


# =======================
# INITIAL NORMALIZATION =
# =======================
print()

# basic example
# by default performs cleaning, script fixing
# returns normalized text and stats
txt = 'Қайыpлы таӊ! Ə​нші бaлааапaн ☺️☺️☺️ L O V E  🇰🇿'
ininormer = Normalizer()
print(ininormer.normalize(txt))

# desegment and deduplicate on top of that
print(ininormer.normalize(txt, desegment=2, dedupe=2))

# transliterate and resolve emojies
print(ininormer.normalize(txt, translit=True, emojiresolve=True))

# do everything without returning stats
print(ininormer.normalize(txt, translit=True, desegment=2,
                          dedupe=2, emojiresolve=True, stats=False))


# ==============
# TOKENIZATION =
# ==============
print()

txt = u'Көш жүре түзеледі. Ақсақ қой түстен кейін маңырайды.'
tokrex = TokenizeRex()
sents_toks = tokrex.tokenize(txt)
print(sents_toks)

mdl = os.path.join('kaznlp', 'tokenization', 'tokhmm.mdl')
tokhmm = TokenizerHMM(model=mdl)
sents_toks = tokhmm.tokenize(txt)
print(sents_toks)


# =========================
# LANGUAGE IDENTIFICATION =
# =========================
txt_kaz = u'Еңбек етсең ерінбей, тояды қарның тіленбей.'
txt_rus = u'Нет, нет, нет, нет! Мы хотим сегодня! Мы хотим сейчас!'

landetector = LidNB(char_mdl=os.path.join('kaznlp', 'lid', 'char.mdl'))

print()
doclan = landetector.predict(tokrex.tokenize(txt_kaz, lower=True)[0])
print(f'Document "{txt_kaz}" is written in {doclan}.')

print()
doclan = landetector.predict_wp(tokrex.tokenize(txt_rus, lower=True)[0])
print(f'Document "{txt_rus}" has the following language probabilities {doclan}.')

print()
print(f'Input document is mixed:\n"{txt_kaz} {txt_rus}".')
print('\nPer-word language detection:')
for i, wrd in enumerate(tokrex.tokenize(txt_kaz + txt_rus)[0]):
    wrdlan = landetector.predict(wrd.lower())
    print(f'{str(i+1).rjust(2)}) {wrd.ljust(15)}{wrdlan}')


# ============
# MORPHOLOGY =
# ============

# create a morphological analyzer instance
analyzer = AnalyzerDD()
analyzer.load_model(os.path.join('kaznlp', 'morphology', 'mdl'))

# try analysis
print()
wrd = 'алмасын'
[iscovered, alist] = analyzer.analyze(wrd)
print('"{}" is covered by the analyzer.'.format(wrd))
print('Analyses are:')
for i, a in enumerate(alist):
    print(f'{str(i+1).rjust(2)}) {a}')

# create a morphological tagger instance
print()
tagger = TaggerHMM(lyzer=analyzer)
tagger.load_model(os.path.join('kaznlp', 'morphology', 'mdl'))

txt = u'Еңбек етсең ерінбей, тояды қарның тіленбей.'
tokenizer = TokenizerHMM(model=mdl)
for sentence in tokenizer.tokenize(txt):
    print(f'input sentence:\n{sentence}\n')
    print('tagged sentence:')
    lower_sentence = map(lambda x: x.lower(), sentence)
    for i, a in enumerate(tagger.tag_sentence(lower_sentence)):
        print(f'{str(i+1).rjust(2)}) {sentence[i].ljust(15)}{a}')
