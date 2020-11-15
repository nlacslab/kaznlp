
# KazNLP: NLP tools for Kazakh language

This project aims at building free/open source language processing tools for [Kazakh](https://en.wikipedia.org/wiki/Kazakh_language).
The proposed set of tools is designed to tackle a wide range of NLP problems that can be divided into pre-processing, core processing, and application-level routines.
It is expected that the tools will be implemented in [Python 3](https://www.python.org/) programming language and released under [CC-SA-BY](https://creativecommons.org/licenses/by-sa/4.0/) or compatible licenses.


If you would like to cite the project in your research or elsewhere, for now, please, cite individual tools separately, using corresponding citing instructions.
A single paper, describing the toolkit as a whole is coming soon...


The project is implemented by the computer science lab of the National Laboratory Astana, Nazarbayev University.

Contact info: figure out or run the following code (need python 3.6+ or [online interpreter](https://www.python.org/shell/))
```python
frst_name = 'Aibek'
last_name = 'Makazhanov'
sep1, sep2 = '.', '@'
print(f'\n{frst_name.lower()}{sep1}{last_name.lower()}{sep2}nu{sep1}edu{sep1}kz\n')
```

<hr>


## Contents
[1. Installation](#ch1)<br>


[2. Initial normalization module](#ch2)<br>
[2.1 Example usage](#ch21)<br>
[2.2 Citing](#ch22)<br>


[3. Tokenizers](#ch3)<br>
[3.1 Example usage](#ch31)<br>
[3.2 Citing](#ch32)<br>


[4. Language identification](#ch4)<br>
[4.1 Example usage](#ch41)<br>
[4.2 Citing](#ch42)<br>


[5. Morphological processing](#ch5)<br>
[5.1 Analyzer](#ch51)<br>
[5.2 Tagger](#ch52)<br>
[5.3 Example usage](#ch53)<br>
[5.4 Citing](#ch54)<br>

[6. References](#ch6)<br>


<hr>


## <a name="ch1"></a> 1. Installation

For software engineering reasons the tools are not _yet_ released as a single PyPI package.
Thus for now, there is no installation per se.
To use the tools just clone this repository like so:
```shell
> git clone https://github.com/nlacslab/kaznlp.git
```
Alternatively, you can download and unzip the archived version: https://github.com/nlacslab/kaznlp/archive/master.zip


The archive or a cloned repository will contain `kaznlp` directory, which hosts all the code and models.
In order to correctly import the tools, your own code _must_ be in the same directory with `kaznlp` (not inside `kaznlp`).
The current release, contains `tutorial.py`, which is located in the root of repo, i.e. in the same directory with `kaznlp`.
To check, if everything is working, you can run this test code like so:
```shell
> python tutorial.py
```

This should generate a lengthy output, which will be discussed in the _usage example_ sections with respect to each tool.
For now, just make sure that there are no error messages.

If you encountered problems with the above command, make sure that you are using `Python 3.6` or a higher version.



## <a name="ch2"></a> 2. Initial normalization module

Noisy User Generated Text (NUGT) is notoriously difficult to process due to prompt introduction of neologisms, e.g. esketit (stands for let’s get it, pronounced \[ɛɕˈkerɛ\]), and peculiar spelling, e.g. b4 (stands for before). Moreover speakers of more than one language tend to mix them in NUGT (a phenomenon commonly referred to as code-switching) and/or use transliteration (spelling in non-national alphabets). All of this increases lexical variety, thereby aggravating the most prominent problems of CL/NLP, such as out-of-vocabulary lexica and data sparseness.


Kazakhstani segment of Internet is not exempt from NUGT and the following cases are the usual suspects in wreaking the “spelling mayhem”:

* _spontaneous transliteration_ – switching alphabets, respecting no particular rules or standards, e.g. Kazakh word “біз” (we as pronoun; awl as noun) can be spelled in three additional ways: “биз”, “быз”, and “biz”;

* _use of homoglyphs_ – interchangeable use of identical or similar looking Latin and Cyrillic alphabets, e.g. Cyrillic letters “е” (U+0435), “с” (U+0441), “і” (U+0456), and “р” (U+0440) in the Kazakh word «есірткі» (drugs) can be replaced with Latin homoglyphs “e” (U+0065), “c” (U+0063), “i” (U+0069), and “p” (U+0070), which, although appear identical, have different Unicode values;

* _code switching_ – use of Russian words and expressions in Kazakh text and vice versa;

* _word transformations_ – excessive duplication of letters, e.g. “керемееет” instead of “керемет” (great), or segmentation of words, e.g. “к е р е м е т”.

We propose an approach for initial normalization of Kazakh NUGT. Here an important distinction must be drawn. Unlike with lexical normalization, for initial normalization we do not attempt to recover standard spelling of ill-formed words, in fact, we do not even bother detecting those. All that we really care about at this point is to provide an intermediate representation of the input NUGT that will not necessarily match its lexically normalized version, but will be less sparse. Thus, we aim at improving performance of downstream applications by reducing vocabulary size (effectively, parameter space) and OOV rate.


Our approach amounts to application of the following straightforward procedures:
* _noise reduction_ - removes or replaces "_function_" symbols (e.g. non-breaking spaces (U+00A0) become regular spaces, while "invisible" spaces (U+200B) get removed) and some other rarely used (in Kaznet) symbols;
* _homoglyph resolution_ - given a mixed script word (i.e. a word with Latin + Cyrillic letters) tries to convert it to a single script token by making apropriate substitutions for homoglyphs;
* _transliteration (optional)_ - translates symbols of the Latin alphabet and national symbols of the Kazakh Cyrillic alphabet into Russian Cyrillic, in our opinion, a common denominator for the three alphabets used in the Kazakh-Russian environment. See \[1\] for details;
* _desegmentation (optional)_ - joins space-separated segmented words, e.g. "L O V E" becomes "LOVE";
* _deduplication (optional)_ - collapses consecutive occurrences of the same character, e.g. "yesss" becomes "yes";
* _emoji resolution (optional)_ - replaces emojies with their official Unicode descriptions, e.g. ☺ becomes "&lt;emj&gt;smilingface&lt;/emj&gt;".


### <a name="ch21"></a> 2.1 Examples usage



```python

# =======================
# INITIAL NORMALIZATION =
# =======================
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                # import initial normalization module
from kaznlp.normalization.ininorm import Normalizer

txt = 'Қайыpлы таӊ! Ə​нші бaлааапaн ☺️☺️☺️ L O V E  🇰🇿'
ininormer = Normalizer()

# by default only cleaning and script fixing is performed
# returns a tuple: normalized text (a string) and stats (a dictionary)
# the stats dictionary has the following structure:
# stats = {'cleaned': number of "noisy" characters either deleted or replaced,
#          'l2c':number of mix-scripted words converted to all-cyrillic script,
#          'c2l':number of mix-scripted words converted to all-latin script};

(norm_txt, stats) = ininormer.normalize(txt)
print(f'Normalized text: {norm_txt.rjust(39)}')
print(f'Normalization stats: {stats}')

# stats can be omitted by setting [stats] flag to False
# in that case a single string is returned (not a tuple)
norm_txt = ininormer.normalize(txt, stats=False)

# let's compare the texts before and after normalization
voc = lambda x: len(set([c for c in x]))
print(f'\nOriginal text: {txt.rjust(49)}\t(len: {len(txt)}; vocab (chars): {voc(txt)})')
print(f'Normalized text: {norm_txt.rjust(39)}\t(len: {len(norm_txt)}; vocab (chars): {voc(norm_txt)})')

# as we can see, the normalized string is shorter than the original and has fewer unique characters:
```

    Normalized text: Қайырлы таң! Әнші балааапан ☺️☺️☺️ L O V E  🇰🇿
    Normalization stats: {'cleaned': 3, 'l2c': 2, 'c2l': 0}
    
    Original text:   Қайыpлы таӊ! Ə​нші бaлааапaн ☺️☺️☺️ L O V E  🇰🇿	(len: 47; vocab (chars): 26)
    Normalized text: Қайырлы таң! Әнші балааапан ☺️☺️☺️ L O V E  🇰🇿	(len: 46; vocab (chars): 24)



```python
# let's get rid of segmented words and duplicate characters
# through the desegment parameter we set the length of space-separated single letter sequences
# beyond which they will be joined together ("L O V E" in our example is such a sequence of length 4)
# through the dedupe parameter we set the length of repeated character sequences
# beyond which such sequences will collapse to a single character ("ааа" in our example is such a sequence of length 3)
norm_txt = ininormer.normalize(txt, desegment=2, dedupe=2, stats=False)
print(f'\nOriginal text: {txt.rjust(49)}\t(len: {len(txt)}; vocab (chars): {voc(txt)})')
print(f'Normalized text: {norm_txt.rjust(39)}\t(len: {len(norm_txt)}; vocab (chars): {voc(norm_txt)})')
```

    
    Original text:   Қайыpлы таӊ! Ə​нші бaлааапaн ☺️☺️☺️ L O V E  🇰🇿	(len: 47; vocab (chars): 26)
    Normalized text: Қайырлы таң! Әнші балапан ☺️☺️☺️ LOVE 🇰🇿	(len: 40; vocab (chars): 24)



```python
# transliterate and resolve emojies
# transliteration is performed from Latin and Kazakh Cyrillic to Russian Cyrillic
# transliteration rules are arbitrary, please see [1] for details
# emoji resolution replace special symbols with their unicode descriptions, e.g. ☺️ becomes smilingface
# replaced entries are enclosed in <emj></emj> tags
norm_txt = ininormer.normalize(txt, translit=True, emojiresolve=True, stats=False)
print(f'\nOriginal text: {txt.rjust(49)}\t(len: {len(txt)}; vocab (chars): {voc(txt)})')
print(f'Normalized text: {norm_txt.rjust(39)}\t(len: {len(norm_txt)}; vocab (chars): {voc(norm_txt)})')
```

    
    Original text:   Қайыpлы таӊ! Ə​нші бaлааапaн ☺️☺️☺️ L O V E  🇰🇿	(len: 47; vocab (chars): 26)
    Normalized text: Каыырлы тан! Аншы балааапан <emj>smilingface</emj><emj>smilingface</emj><emj>smilingface</emj> Л О В Е  <emj>Kazakhstan</emj>	(len: 125; vocab (chars): 36)



```python
# do everything in one go
norm_txt = ininormer.normalize(txt, translit=True, desegment=2, dedupe=2, emojiresolve=True, stats=False)
print(f'\nOriginal text: {txt.rjust(49)}\t(len: {len(txt)}; vocab (chars): {voc(txt)})')
print(f'Normalized text: {norm_txt.rjust(39)}\t(len: {len(norm_txt)}; vocab (chars): {voc(norm_txt)})')
```

    
    Original text:   Қайыpлы таӊ! Ə​нші бaлааапaн ☺️☺️☺️ L O V E  🇰🇿	(len: 47; vocab (chars): 26)
    Normalized text: Каыырлы тан! Аншы балапан <emj>smilingface</emj><emj>smilingface</emj><emj>smilingface</emj> ЛОВЕ <emj>Kazakhstan</emj>	(len: 119; vocab (chars): 36)


### <a name="ch22"></a> 2.2 Citing


To cite the initial normalization module please use the following:

* B. Myrzakhmetov, Zh. Yessenbayev and A. Makazhanov. "Initial Normalization of User Generated Content: Case Study in a Multilingual Setting" to appear in Proceedings of AICT 2018.


<hr>


## <a name="ch3"></a> 3.Tokenizers


Tokenization is one of the basic NLP tasks, concerned with splitting the input text into so called tokens.
Usually tokens are represented by words, numbers, punctuation and other symbols found in the text.
There is also a problem of sentence boundary detection, where the task is to split a given text into sentences.

In our approach we have joined both problems, casting them as a single sequence labeling task.
In such a setting each character will be assigned one of four possible labels: (i) S - start of a sentence, (ii) T - start of a token, (iii) I - inside of a token, (iv) - outside of a token.
Having enough training data one can train a model to learn either joint or conditional character-label distributions, and obtain a sort of a sentence-token boundary tagger (see \[2\] for details).
We have trained a tri-gram HMM model as well as an LSTM neural network model.
LSTM model, however, was implemented in Java and is currently being implemented in Python to be included into the next release.

### <a name="ch31"></a> 3.1 Example usage


```python

# ==============
# TOKENIZATION =
# ==============

# import HMM-based tokenizer
from kaznlp.tokenization.tokhmm import TokenizerHMM
import os

# input text with two sentences
txt = u'Көш жүре түзеледі.Ақсақ қой түстен кейін маңырайды.'

# as we initialize an HMM tokenizer, we specify the path to the model file,
# which is included in the release and located in the tokenization directory
mdl = os.path.join('kaznlp', 'tokenization', 'tokhmm.mdl')
tokhmm = TokenizerHMM(model=mdl)

# we then pass the input to the tokenize method,
# which returns a list of sentences, each represented by a list of tokens
sents_toks = tokhmm.tokenize(txt)
print(sents_toks)

# we can see that for the given input
# the method correctly finds sentences and tokens:
```

    [['Көш', 'жүре', 'түзеледі', '.'], ['Ақсақ', 'қой', 'түстен', 'кейін', 'маңырайды', '.']]



```python
# additionally we have implemented a regular expression-based tokenizer
# it is very fast, but it does not perform sentence splitting
# it still outputs a list of lists (to be consistent in output format),
# but it always outputs a single list in a list, i.e. everything is a single sentence

# import and initialize regex-based tokenizer
from kaznlp.tokenization.tokrex import TokenizeRex
tokrex = TokenizeRex()

print(tokrex.tokenize(txt))
```

    [['Көш', 'жүре', 'түзеледі', '.', 'Ақсақ', 'қой', 'түстен', 'кейін', 'маңырайды', '.']]



```python
# as we can see regex tokenizer is more than 1000x faster than the HMM model
# thus in a scenarios where one does not care about sentences
# for example, vocabulary extraction, it may be better to use the regex tolenizer

%timeit tokhmm.tokenize(txt)
%timeit tokrex.tokenize(txt)
```

    7.66 ms ± 139 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)
    12.6 µs ± 101 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)


### <a name="ch32"></a> 3.2 Citing


To cite the tokenization module please use the following:

* A. Toleu, G. Tolegen, A. Makazhanov. "Character-based Deep Learning Models for Token and Sentence Segmentation" Proceedings of TurkLang 2017.


<hr>


## <a name="ch4"></a> 4. Language identification


Language identification (LID) of text is the task of detecting what language(s) a given text is written in.
If the set of possible languages is known in advance, the task is called a closed class LID. 
Historically LID has been applied to documents as a whole, but with growing amount of multi-lingual data,
LID for individual words or phrases has also gained importance.


We approach the task as a closed class LID, where we consider two languages: Kazakh and Russian,
and a catch-all category "other" for any other language.
To this end we train two Naive Bayes models that differ only in feature representation:
where one uses word N-grams as features, the other employs character N-grams for the same purpose.


Our implementation allows for both separate and combined application of the aforementioned models, 
as well as for both document- and word-level LID.
For the details, please, consult \[3\].


### <a name="ch41"></a> 4.1 Example usage


```python

# =========================
# LANGUAGE IDENTIFICATION =
# =========================

# import Naive Bayes LID implementation
from kaznlp.lid.lidnb import LidNB
import os

#input texts written in Kazakh and Russian respectively
txt_kaz = 'Еңбек етсең ерінбей, тояды қарның тіленбей.'
txt_rus = 'Нет, нет, нет, нет! Мы хотим сегодня! Мы хотим сейчас!'

# as we initialize LidNB, we must specify the path
# to at least either of word or character models
# the models are included in the release and located in the lid directory
cmdl = os.path.join('kaznlp', 'lid', 'char.mdl')
landetector = LidNB(word_mdl=None, char_mdl=cmdl)

# to obtain document-level predictions we call the predict method
# the method expects a list of lowercased tokens
# as tokens do not have to be grouped by s  entences, we use a regex tokenizer
doclan = landetector.predict(tokrex.tokenize(txt_kaz, lower=True)[0])
print(f'Document "{txt_kaz}" is written in {doclan}.')
```

    Document "Еңбек етсең ерінбей, тояды қарның тіленбей." is written in kazakh.



```python
# do the same for the second input text
# only this time call [predict_wp] method, which returns a dictionary
# that contains probabilities for each language and a prediction under the "result" key
doclan = landetector.predict_wp(tokrex.tokenize(txt_rus, lower=True)[0])
print(f'Document "{txt_rus}" has the following language probabilities:\n{doclan}.')
```

    Document "Нет, нет, нет, нет! Мы хотим сегодня! Мы хотим сейчас!" has the following language probabilities:
    {'kazakh': 0.37063914566921563, 'russian': 0.4127970225204484, 'other': 0.21656383181033592, 'result': 'russian'}.



```python
# finally we can try out word-level LID on a multi-lingual document
print(f'Input document is multi-lingual:\n"{txt_kaz} {txt_rus}".')
print('\nPer-word language detection:')
for i, wrd in enumerate(tokrex.tokenize(txt_kaz + txt_rus)[0]):
    wrdlan = landetector.predict(wrd.lower())
    print(f'{str(i+1).rjust(2)}) {wrd.ljust(15)}{wrdlan}')

# as it can be seen on our test document the method achieves ~83% accuracy,
# i.e., 20 out of 24 tokens are correct.
```

    Input document is multi-lingual:
    "Еңбек етсең ерінбей, тояды қарның тіленбей. Нет, нет, нет, нет! Мы хотим сегодня! Мы хотим сейчас!".
    
    Per-word language detection:
     1) Еңбек          kazakh
     2) етсең          kazakh
     3) ерінбей        kazakh
     4) ,              other
     5) тояды          russian
     6) қарның         kazakh
     7) тіленбей       kazakh
     8) .              other
     9) Нет            russian
    10) ,              other
    11) нет            russian
    12) ,              other
    13) нет            russian
    14) ,              other
    15) нет            russian
    16) !              other
    17) Мы             kazakh
    18) хотим          russian
    19) сегодня        russian
    20) !              other
    21) Мы             kazakh
    22) хотим          russian
    23) сейчас         russian
    24) !              other


### <a name="ch42"></a> 4.2 Citing


To cite the tokenization module please use the following:

* Zh. Kozhirbayev, Zh. Yessenbayev and A. Makazhanov. "Document and Word-level Language Identification for Noisy User Generated Text" to appear in Proceedings of AICT 2018


<hr>


## <a name="ch5"></a> 5. Morphological processing


Morphological processing (MP) is an essential core processing routine in NLP.
It amounts to recovering internal structure of words (morphology) conditioning on the context they appear in.

Arguably the most common approach to MP is a two-step pipeline, 
where given a word and its context the first step is to 
find all possible morphological representations (analyses) of that word
and the second is to chose the analysis most appropriate in the given context.
This is usually achieved by a successive application of such tools as 
morphological analyzers and morphological disambiguators or taggers.


### <a name="ch51"></a> 5.1 Analyzer


Morphological analyzer returns for a given word all possible triples
of values `<dictionary form>` `<part of speech>` `<grammatical characteristics>`,
i.e. all possible analyses.

For instance, for the word _тағам_:

1) `<тағам>` `<noun>` `<singular, nominative>` (food)<br>
2) `<таға>` `<noun>` `<1sg possession, nominative>` (my horseshoe)<br>
3) `<тақ>` `<verb, transitive>` `<present/future, 1sg>` (I \[will\] wear)<br>.

The morphological analyzer included in the current release is
the implementation of a data-driven analyzer due to Makhambetov et al. \[4\].
A finite state transducer-based implementation is built upon HFST toolkit
and released separately [here](https://github.com/apertium/apertium-kaz/tree/nla) due to being non-Python.


### <a name="ch52"></a> 5.2 Tagger

The tagger chooses an analysis (a triple from the example above) best suited for the given context,
e.g. in a passage like «_галстук тағам_» (I’ll wear a tie) the tagger should return the analysis (3) for _тағам_ (see
the example above).

The current implementation is based on a trigram HMM with Laplacian smoothing.


### <a name="ch53"></a> 5.3 Example usage


```python

# ============
# MORPHOLOGY =
# ============

from kaznlp.morphology.analyzers import AnalyzerDD

# create a morphological analyzer instance
analyzer = AnalyzerDD()
# load the model directory located in the morphology directory
analyzer.load_model(os.path.join('kaznlp', 'morphology', 'mdl'))

wrd = 'алмасын'

# to analyze a given word we call the analyze method with the word as an argument
# the method returns a tuple (iscovered, alist), where:
# iscovered - a boolean value indicating if the word was accepted by the analyzer
# alist - a list of resulting analyses
[iscovered, alist] = analyzer.analyze(wrd)
print(f'"{wrd}" is{not iscovered and " not" or ""} covered by the analyzer.')
print('Analyses are:')
for i, a in enumerate(alist):
    print(f'{str(i+1).rjust(2)}) {a}')
```

    "алмасын" is covered by the analyzer.
    Analyses are:
     1) алма_R_ZE сы_S3 н_C4
     2) алма_R_ZEQ сы_S3 н_C4
     3) ал_R_ETK ма_ETK_ETB с_ETB_ESM ы_S3 н_C4
     4) ал_R_ET ма_ET_ETB с_ETB_ESM ы_S3 н_C4
     5) алмас_R_SE ы_S3 н_C4
     6) алмас_R_ZE ы_S3 н_C4
     7) ал_R_ETK ма_ETK_ETB сын_M2
     8) ал_R_ET ма_ET_ETB сын_M2
     9) алмас_R_ET ын_V1



```python
# unaccepted words will receive an R_X tag

wrd = 'лмасын'
[iscovered, alist] = analyzer.analyze(wrd)
print(f'"{wrd}" is{not iscovered and " not" or ""} covered by the analyzer.')
print('Analyses are:')
for i, a in enumerate(alist):
    print(f'{str(i+1).rjust(2)}) {a}')
```

    "лмасын" is not covered by the analyzer.
    Analyses are:
     1) лмасын_R_X


\* Here a modified version of the KLC tag set is used.
A quick glossary can be found [here](https://github.com/nlacslab/kaznlp/blob/master/kaznlp/docs/morphology-tagset.MD).
For more details, please, consult \[5\].

\** The currrent release contains only a portion of data used in this demonstration, thus results may differ.

Let us now consider the tagging example.


```python
from kaznlp.morphology.taggers import TaggerHMM

tagger = TaggerHMM(lyzer=analyzer)
# same model directory is used to train the tagger
tagger.load_model(os.path.join('kaznlp', 'morphology', 'mdl'))

txt = u'Еңбек етсең ерінбей, тояды қарның тіленбей.'

# to tag a text we need to split it into sentences
# and feed tokenized sentences to the *tag_sentence* method
tokenizer = TokenizerHMM(model=mdl)
for sentence in tokenizer.tokenize(txt):
    print(f'input sentence:\n{sentence}\n')
    print('tagged sentence:')
    #the sentence must be lower-cased before tagging
    lower_sentence = map(lambda x: x.lower(), sentence)
    for i, a in enumerate(tagger.tag_sentence(lower_sentence)):
        #output each word with the most probable analysis
        print(f'{str(i+1).rjust(2)}) {sentence[i].ljust(15)}{a}')

```

    input sentence:
    ['Еңбек', 'етсең', 'ерінбей', ',', 'тояды', 'қарның', 'тіленбей', '.']
    
    tagged sentence:
     1) Еңбек          еңбек_R_ZE
     2) етсең          ет_R_ET се_M4 ң_P2
     3) ерінбей        ерін_R_ET бе_ET_ETB й_ETB_KSE
     4) ,              ,_R_UTR
     5) тояды          то_R_ET я_T1 ды_P3
     6) қарның         қарн_R_ZE ың_S2
     7) тіленбей       тіле_R_ET н_V1 бе_ET_ETB й_ETB_KSE
     8) .              ._R_NKT


### <a name="ch54"></a> 5.4 Citing


To cite morphological processing tools, please, use the following:

* O. Makhambetov, A. Makazhanov, I. Sabyrgaliyev, Zh. Yessenbayev. "Data-driven morphological analysis and disambiguation for Kazakh". InInternational Conference on Intelligent Text Processing and Computational Linguistics 2015, pp. 151-163.


<hr>


## <a name="ch6"></a> 6. References

\[1\] B. Myrzakhmetov, Zh. Yessenbayev and A. Makazhanov. "Initial Normalization of User Generated Content: Case Study in a Multilingual Setting" to appear in Proceedings of AICT 2018.

\[2\] A. Toleu, G. Tolegen, A. Makazhanov. "Character-based Deep Learning Models for Token and Sentence Segmentation" Proceedings of TurkLang 2017.

\[3\] Zh. Kozhirbayev, Zh. Yessenbayev and A. Makazhanov. "Document and Word-level Language Identification for Noisy User Generated Text" to appear in Proceedings of AICT 2018

\[4\] O. Makhambetov, A. Makazhanov, I. Sabyrgaliyev, Zh. Yessenbayev. "Data-driven morphological analysis and disambiguation for Kazakh". InInternational Conference on Intelligent Text Processing and Computational Linguistics 2015, pp. 151-163.

\[5\] O. Makhambetov, A. Makazhanov, Zh. Yessenbayev, B. Matkarimov, I. Sabyrgaliyev, A. Sharafudinov. (2013). Assembling the kazakh language corpus. In Proceedings of the 2013 Conference on Empirical Methods in Natural Language Processing (pp. 1022-1031).
