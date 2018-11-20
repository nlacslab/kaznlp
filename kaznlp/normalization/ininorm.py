#  -*- coding: UTF-8 -*-

from __future__ import division
from kaznlp.normalization.emojiresolver import EmojiResolver
import re


# Regular expressions
REX_LAT = re.compile('[a-z]', re.I)
REX_CYR = re.compile(u'[а-яёәіңғүұқөһ]', re.U|re.I)
REX_DIG = re.compile('\d+')
REX_NONALPHA = re.compile(u'[^a-zа-яёәіңғүұқөһ]', re.U|re.I)
REX_NONALNUM = re.compile(u'[^a-zа-яёәіңғүұқөһ\d]+', re.U|re.I)


class CharCleaner():
    '''
    Performs initial text cleaning by replacing "noisy" characters 
    with appropriate analogues (e.g. "invisible" spaces become empty strings).
    '''        
    def __init__(self):
        # keys and values of the following dictionary may look the same, 
        # but they are NOT (they have different unicodes)
        # refrain from editing unless absolutely need to
        self.uncom_reps = {
                u'\u00a0': ' ', 
                u'​': '', u'‪': '', u'‎': '', u'‬': '', u'‏': '', u'­': '', 
                u'¬': '', '‚': ', ', u'¸': ', ', u'́': u'', u'‑': u'-', u'−': u'-', 
                # u'': u'•', u'⁰': u'°', u'': u'°', \
                u'ı': 'y', 
                u'ə': u'ә', 
                u'Ə': u'Ә', 
                u'ӊ': u'ң', 
                u'Ӊ': u'Ң', 
                # u'ќ': u'қ', 
                # u'Ќ': u'Қ', 
                u'ë': u'ё', 
                u'Ë': u'Ё', 
                }
        pattern = u'[%s]'%'\\'.join(self.uncom_reps.keys())
        self.rex_ur = re.compile(pattern, re.U)
        
    def clean(self, txt, count=False):
        '''
        Given a string [txt] finds all "noisy" characers and replaces them 
        with appropriate analogues (e.g. "invisible" spaces become empty strings).
        If [count] set to True returns a tuple consisting of a new string and 
        a number of replacements made.
        If [count] set to False (default) returns only the resulting string.
        '''
        # map "noisy" matches returned by re.sub to "clean" substitutes.
        rep = lambda m:self.uncom_reps.get(m.group(0), m.group(0))
        return self.rex_ur.subn(rep, txt) if count else self.rex_ur.sub(rep, txt)


class ScriptFixer():
    '''
    Performs "script fixing" by resolving homoglyphs, 
    e.g. replacing latin 'a', 'c', 'e', etc. with cyrillic counterparts 
    (and vice versa) if need be.
    '''    
    def __init__(self):
        self.hglyphs_latcyr = {
                'A': u'А', 
                'a': u'а', 
                'B': u'В', 
                # 'b': u'в', 
                'C': u'С', 
                'c': u'с', 
                'E': u'Е', 
                'e': u'е', 
                'F': u'Ғ', 
                # 'f': u'ғ', 
                'H': u'Н', 
                'h': u'һ', 
                'I': u'І', 
                'i': u'і', 
                'K': u'К', 
                # 'k': u'к', 
                'M': u'М', 
                # 'm': u'м', 
                # 'l': u'і', 
                'O': u'О', 
                'o': u'о', 
                'P': u'Р', 
                'p': u'р', 
                'T': u'Т', 
                'X': u'Х', 
                'x': u'х', 
                'Y': u'Ү', 
                'y': u'у', 
                }
        self.hglyphs_cyrlat = {v:k for k, v in self.hglyphs_latcyr.items()}
        self.rex_latcyr = re.compile(u'[%s]'%''.join(self.hglyphs_latcyr), re.U)
        self.rex_cyrlat = re.compile(u'[%s]'%''.join(self.hglyphs_cyrlat), re.U)
        
    def fix(self, txt, count=False, verbose=False):
        '''
        Given a string [txt] finds all homoglyphs and replaces them 
        with appropriate analogues (e.g. latin "a" becomes cyrillic "a").
        Returns a following dictionary:
        ret = {'text':homoglyph-resoved text;
               'fixed':if [fixed] is False contains None, otherwise contains a following dictionary:
                       fixed = {'l2c':number of latin-to-cyrillic replacements, 
                                'c2l':number of cyrillic-to-latin replacements};
               'unres':if [verbose] is False contains None, otherwise contains the following dictionary:
                       unres = {'all':contains a list of token coordinates, which contain ONLY homoglyphs (and therefore unresolved);
                                'mix':contains a list of token coordinates, which cannot be spelled purely in latin or cyrillic \
                                even after homoglyphs (if any) are resolved}
              }
        Token coordinates are defined as a tuple (pos, len), where pos is an offset (in chars) from the beginning of the text\ 
        and len is its length in chars.
        '''        
        def islat(t):
            '''
            Given a token [t] resolves cyrillic homoglyphs to latin analogues.
            Returns a tuple of two elements:
            (i)  boolean value, which is True if [t] can be rendered in latin alphabet and False otherwise;
            (ii) if (i) is True, revised token, rendered in latin, otherwise, an unchanged token.
            '''
            rep = lambda m:self.hglyphs_cyrlat.get(m.group(0), m.group(0))
            rev = self.rex_cyrlat.sub(rep, t)
            ret = not REX_LAT.sub('', REX_DIG.sub('', rev))
            return (ret, ret and rev or t)
        
        def iscyr(t):
            '''
            Given a token [t] resolves latin homoglyphs to cyrillic analogues.
            Returns a tuple of two elements:
            (i)  boolean value, which is True if [t] can be written purely in cyrillic alphabet and False otherwise;
            (ii) revised token, written purely in cyrillic alphabet.
            '''
            rep = lambda m:self.hglyphs_latcyr.get(m.group(0), m.group(0))
            rev = self.rex_latcyr.sub(rep, t)
            ret = not REX_CYR.sub('', REX_DIG.sub('', rev))
            return (ret, ret and rev or t)
        
        ret = {'text':txt, \
               'fixed':(count   and [{'l2c':0, 'c2l':0}] or [None])[0], \
               'unres':(verbose and [{'all':[], 'mix':[]}] or [None])[0]}
        
        pos = 0
        for tok in REX_NONALNUM.split(txt):
            # update token position
            pos = txt.find(tok, pos)
            # skip single script tokens (all-latin or all-cyrillic)
            # if not (rex.lat.search(tok) and rex.cyr.search(tok)):
            if not (REX_LAT.search(tok) and REX_CYR.search(tok)):
                pos += len(tok)
                continue
            # try homoglyph resolution
            lattok = islat(tok)
            cyrtok = iscyr(tok)
            if lattok[0] and (not cyrtok[0]):
                # resolving cyrillic to latin is succesful
                txt = txt[:pos] + lattok[1] + txt[pos + len(tok):]
                if ret['fixed']: ret['fixed']['c2l'] += 1
            elif (not lattok[0]) and cyrtok[0]:
                # resolving latin to cyrillic is succesful
                txt = txt[:pos] + cyrtok[1] + txt[pos + len(tok):]
                if ret['fixed']: ret['fixed']['l2c'] += 1
            elif lattok[0] and cyrtok[0]:
                # token contains both latin and cyrillic hmoglyths - therefore unresolved
                if ret['unres']:
                    ret['unres']['all'].append((pos, len(tok)))
            elif not (lattok[0] or cyrtok[0]) and REX_CYR.search(tok)\
            and REX_LAT.search(tok):
                if ret['unres']:
                    ret['unres']['mix'].append((pos, len(tok)))
            pos += len(tok)
        ret['text'] = txt

        return ret


class Transliterator():
    '''
    Performs transliteration from latin and "Kazakh cyrillic" into cyrillic.
    Transliteration rules are given in self.latcyr and self.qazcyr dictionaries.
    These rules do not reflect ANY writing system, they are task/language specific.
    '''
    def __init__(self):
        self.latcyr = {'a': u'а', 
                       'b': u'б', 
                       'c': u'с', 
                       'd': u'д', 
                       'e': u'е', 
                       'f': u'ф', 
                       'g': u'г', 
                       'h': u'х', 
                       'i': u'ы', 
                       'j': u'ж', 
                       'k': u'к', 
                       'l': u'л', 
                       'm': u'м', 
                       'n': u'н', 
                       'o': u'о', 
                       'p': u'п', 
                       'q': u'к', 
                       'r': u'р', 
                       's': u'с', 
                       't': u'т', 
                       'u': u'у', 
                       'v': u'в', 
                       'w': u'ш', 
                       'x': u'х', 
                       'y': u'ы', 
                       'z': u'з', 
                       'ch': u'ч', 
                       'kh': u'х', 
                       'sh': u'ш', 
                       'zh': u'ж'
                       }
        self.qazcyr = {u'ә': u'а', 
                       u'і': u'ы', 
                       u'ң': u'н', 
                       u'ғ': u'г', 
                       u'ү': u'у', 
                       u'ұ': u'у', 
                       u'қ': u'к', 
                       u'ө': u'о', 
                       u'һ': u'х', 
                       u'и': u'ы', 
                       u'й': u'ы', 
                       # u'ц': u'с', 
                       u'щ': u'ш', 
                       u'ё': u'е', 
                       u'ь': u'', 
                       u'ъ': u''
                       }
        pat = u'[cksz]h|[a-z]|[%s]'%''.join(self.qazcyr.keys())
        self.rex_tl = re.compile(pat, re.U|re.I)
    
    def translit(self, txt):
        '''
        Given a string [txt] outputs a new text with characters transliterated 
        according to the rules defined in the constractor.
        Original case of characters is preserved.
        Diphthongs, like ch, sh, etc., are considered to be uppercase, 
        if the first character of a diphthong is upper.
        '''
        def replace(match):
            '''
            substitues a match found by re.sub 
            with appropriate value from translit table
            '''
            m = match.group(0)
            r = self.latcyr.get(m.lower(), self.qazcyr.get(m.lower(), m))
            return r==m and m or (r.upper() if m[0].isupper() else r)
            
        return self.rex_tl.sub(replace, txt)


class Desegmentor():
    '''
    Joins space-separated segmented words, e.g. "L O V E" becomes LOVE.
    Parameter [singlemax] specifies a maximum allowed number of
    isolated consecutive chars.
    Thus, only sequences longer than [singlemax] will be joined.
    Default is [singlemax=2], i.e. "O K" will not be joined by default.
    '''
    def __init__(self):
        pass
    
    def desegment(self, txt, singlemax=2):
        '''
        Given a string [txt] and max allowed number of consecutive
        isolated chars [singlemax], returns a new text, where
        segmented words (longer than [singlemax]) are joined.
        '''
        if singlemax<1: return txt
        uniseq = []
        ltok = 'ltok'
        pos, lpos = 0, 0
        for tok in REX_NONALNUM.split(txt):
            pos  = txt.find(tok, pos)
            if len(tok)<2:
                if len(ltok)<2 and not txt[lpos+len(ltok):pos].strip():
                    uniseq[0][0][1] = pos+1
                    uniseq[0].append(tok)
                else:
                    uniseq.insert(0, [[pos, pos+1], tok])
            ltok = tok
            lpos = pos
            pos  += len(tok)
        ret = txt
        for s in uniseq:
            rep = ''.join(s[1:])
            [beg, end] = s[0]
            if len(rep)>singlemax:
                ret = ret[:beg] + rep + ret[end:]
        return ret


class Deduper():
    '''
    Deduplicates consecutive occurances of the same character, e.g. "yesss" becomes "yes".
    Parameter [dupemax] specifies a maximum number of allowed consecutive chars.
    Thus, only sequences longer than [dupemax] will be joined.
    Default is [dupemax=2], i.e. "yess" will not be de-duped by default.
    '''
    def __init__(self):
        pass
    
    def dedupe(self, txt, dupemax=2):
        '''
        Given a string [txt] and max allowed number of duplications [dupemax],
        returns a deduplicated text.
        '''
        if dupemax<1:
            return txt # max number of duplicates cannot be less than one
        pat = u'([a-zа-яёәіңғүұқөһ])\\1{%d,}'%dupemax
        return re.sub(pat, lambda m:m.group(0)[0], txt)


class Normalizer():
    '''
    Performs normalization, by the following procedures:
        - noise reduction - mandatory;
        - scriptfixing - mandatory;
        - transliteration - optional;
        - desegmentation - optional;
        - deduplication - optional;
        - emoji resolution - optional.
    '''
    
    def __init__(self):
        self.cc = CharCleaner()
        self.sf = ScriptFixer()
        self.tl = Transliterator()
        self.ds = Desegmentor()
        self.dd = Deduper()
        self.em = EmojiResolver()
    
    # replacing unambiguous homoglyths
    def normalize(
            self,
            txt,
            translit=False,
            desegment=0,
            dedupe=0,
            emojiresolve=False,
            stats=True):
        '''
        Given a string [txt] returns the normalized string.
        Minimal mormalization consists of noise reduction
        (see CharCleaner class) and scriptfixing (see ScriptFixer class).
        Parameters:
            - translit:boolean if True, input is transliterated;
            - desegment:int max allowed number of consecutive isolated chars,
              if less than one, than desegmentation is ignored;
            - dedupe:int max allowed number of duplicates,
              if less than one, than deduplication is ignored;
            - emojiresolve:boolean, if True emojies in the input are replaced
              to their description, e.g. ☺️ becomes a <emj>smileyface</emj>;
            - stats:boolean, if true a dictionary with counts of noisy
              characters and homoglyphs replaced (see classes CharCleaner
              and ScriptFixer for dictionary structure).
        Returns:
            - if [stats]=False, returns a single string, which is a normalized
              version of the input;
            - if [stats]=True, returns a (string, dictionary) tuple, where
              the string is a normalizedversion of the input and the dictionry
              is as follows:
                  {'cleaned': number of substituted noisy characters;
                   'l2c': number of latin-to-cyrillic homoglyphs replaced; 
                   'c2l': number of cyrillic-to-latin homoglyphs replaced}
                  }
        '''
        # perform noise reduction
        [txt,cc_count] = self.cc.clean(txt,count=True)
        # perform scriptfixing
        sfres = self.sf.fix(txt, True, False)
        txt = sfres['text']
        # save stats if requested
        stt = {'cleaned': None, 'l2c': None, 'c2l': None}
        if stats:
            stt['cleaned'] = cc_count
            stt['l2c'] = sfres['fixed']['l2c']
            stt['c2l'] = sfres['fixed']['c2l']
        # transliterate if requested
        if translit:
            txt = self.tl.translit(txt)
        # desegment with provided parameter (if 0 txt will not change)
        txt = self.ds.desegment(txt, desegment)
        # dedupe with provided parameter (if 0 txt will not change)
        txt = self.dd.dedupe(txt, dedupe)
        # resolve emojies if requested
        if emojiresolve:
            txt = self.em.replace(txt)
        
        return (txt, stt) if stats else txt
