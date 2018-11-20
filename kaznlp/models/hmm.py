#  -*- coding: UTF-8 -*-
from __future__ import division
import math
import itertools


# HMM with deleted interpolation
class HMM_DI():

    def __init__(
            self,
            order=3,
            smoothing=None,
            count_delim='\t',
            sequence_delim='*_*',
            sequence_beg='<s>',
            sequence_end='</s>'):
        # N-gramm size
        self.order = order
        if self.order < 1 or self.order > 5:
            self.order = 1
        # smoothing vector (must be of length self.order + 2)
        self.smoothing = smoothing
        # counts delimeter (e.g. label N-gram<TAB>count)
        self.count_delim = count_delim
        # sequence (e.g. sentences) delimeter
        self.sequence_delim = sequence_delim
        # sequence start and end labels
        self.sequence_beg = sequence_beg
        self.sequence_end = sequence_end
        # state transistion table
        self.transitions = {}
        # state-observation table
        self.emissions = {}
        # vocabulary of states
        self.states = {}
        # vocabulary of observations
        self.observations = {}

    def load_model(self, model):
        ''' load a model from a file '''
        lines = open(model, 'r').readlines()
        # get the model's order
        self.order = int(lines[0].strip())
        # get smoothing vector - space separated
        self.smoothing = [float(lmb) for lmb in lines[1].strip().split()]
        # get the count delimiter (it supposed to be in quotes,
        # hence trimming one symbol from each side
        self.count_delim = lines[2].strip()[1:-1]
        # get sequence delimiter (again quotes trimming)
        self.sequence_delim = lines[3].strip()[1:-1]
        # get sequence beginning label (start state, default is '<s>')
        self.sequence_beg = lines[4].strip()[1:-1]
        # get sequence ending label (end state, default is '</s>')
        self.sequence_end = lines[5].strip()[1:-1]
        # get number of transitions
        N = int(lines[6].strip())
        for l in lines[7:7+N]:
            [transition, mle] = l.strip().split(self.count_delim)
            for state in transition.split():
                if state not in [self.sequence_beg, self.sequence_end]:
                    self.states[state] = 1
            self.transitions[tuple(transition.split())] = float(mle)
        # get number of state-observation pairs
        M = int(lines[7+N].strip())
        for i, line in enumerate(lines[8+N: 8+N+M]):
            [emission, mle] = line.strip().split(self.count_delim)
            tup = tuple(emission.split(' '))
            if len(tup) < 2:
                raise ValueError('Error loading model.\
                                 Line {}: too few state,\
                                 observation parameters'.format(i+7+N))
            elif len(tup) > 2:
                if len(tup) == 3 and not ''.join(tup[-2:]):
                    tup = [tup[0], ' ']
                else:
                    raise ValueError('Error loading model.\
                                     Line {}: consider removing spaces from\
                                     states or observations'.format(i+7+N))
            self.emissions[tup] = float(mle)

    def save_model(self, model):
        ''' load a model to a file '''
        fd = open(model, 'w')
        # zero-th line contains a single integer - the order of the model
        fd.write(f'{self.order}\n')
        # first line contains a single float - smoothing coefficient
        # (between 0 and 1)
        fd.write(f"{' '.join([str(lmb) for lmb in self.smoothing])}\n")
        # second line contains count delimiter enclosed into quotation marks
        fd.write(f'"{self.count_delim}"\n')
        # third line contains sequence delimiter enclosed into quotation marks
        fd.write(f'"{self.sequence_delim}"\n')
        # fourth line contains sequence beginning label
        # enclosed into quotation marks
        fd.write(f'"{self.sequence_beg}"\n')
        # fifth line contains sequence ending label
        # enclosed into quotation marks
        fd.write(f'"{self.sequence_end}"\n')
        # sixth line contains a single integer N -
        # number of state transition N-grams
        fd.write(f'{len(self.transitions)}\n')
        # next N lines contain state transition ngrams and
        # their frequences (MLE) delimitered by the count delimiter
        for transition, mle in sorted(
                self.transitions.items(),
                key=lambda x: x[1], reverse=True):
            fd.write(f"{' '.join(transition)}{self.count_delim}{mle:1.20f}\n")
        # next line contains a single integer M -
        # number of state-observation pairs
        fd.write(f'{len(self.emissions.values())}\n')
        # next M lines contain state state-observation pairs and
        # their frequences (MLE) delimitered by the count delimiter
        for emission, mle in sorted(
                self.emissions.items(),
                key=lambda x: x[1], reverse=True):
            fd.write(f"{' '.join(emission)}{self.count_delim}{mle:1.20f}\n")

    def train(
            self, trainfile,
            order=3,
            count_delim='\t',
            sequence_delim='*_*'):
        # N-gramm size
        self.order = int(order)
        if self.order < 1 or self.order > 5:
            self.order = 1
        # smoothing vector
        self.smoothing = (self.order + 2)*[0.0]
        # counts delimeter (e.g. label N-gram<TAB>count)
        self.count_delim = count_delim
        # sequence (e.g. sentences) delimeter
        self.sequence_delim = sequence_delim
        # state transistion table
        self.transitions = {}
        # state-observation table
        self.emissions = {}
        # vocabulary of states
        self.states = {}
        # vocabulary of observations
        self.observations = {}
        # read in the data and obtain counts
        transition_counts = {}
        emission_counts = {}
        input_length = 0.0
        buff = (self.order-1)*[self.sequence_beg]
        for line in open(trainfile, 'r').readlines():
            if not line.strip():
                continue
            input_length += 1
            # end of current sequence -
            # add sequence final markers and calc resulting transitions
            if line.strip() == self.sequence_delim:
                if self.order < 2:
                    continue
                for i in range(self.order - 1):
                    if buff:
                        ngrm = buff + [self.sequence_end]
                        for j in range(len(ngrm)):
                            pfx = tuple(ngrm[:len(ngrm)-j])
                            transition_counts[pfx] = transition_counts.get(
                                    pfx, 0.0) + 1
                    buff = buff[1:] + [self.sequence_end]
                buff = (self.order-1)*[self.sequence_beg]
                continue
            # get an observation-state pair
            [observ, state] = line.rstrip().split(self.count_delim)
            # update observations vocabulary
            self.observations[observ] = 1
            # update states vocabulary
            if state not in [self.sequence_beg, self.sequence_end]:
                self.states[state] = 1
            # count transistions
            ngrm = buff + [state]
            for i in range(len(ngrm)):
                pfx = tuple(ngrm[:len(ngrm)-i])
                transition_counts[pfx] = transition_counts.get(pfx, 0.0) + 1
            # count emissions
            emission_counts[state, observ] = emission_counts.get(
                    (state, observ), 0.0) + 1
            # update buffer
            if buff:
                buff = buff[1:] + [state]

        # compute MLEs and smoothing coeffcients for transitions
        lambdas = self.order*[0.0]
        for transition in transition_counts:
            if len(transition) < self.order:
                continue
            deleted = []
            for i in range(len(transition)):
                ngram = tuple(transition[:len(transition)-i])
                pfx = tuple(transition[:len(transition)-i-1])
                # calc mle
                self.transitions[ngram] = transition_counts.get(
                        ngram, 0.0)
                self.transitions[ngram] /= transition_counts.get(
                        pfx, input_length)
                # calc deleted mle
                if transition_counts.get(pfx, input_length) - 1 < 1:
                    deleted.insert(0, 0)
                else:
                    deleted.insert(0, transition_counts.get(
                            ngram, 0.0) - 1)
                    deleted[0] /= (transition_counts.get(
                            pfx, input_length) - 1)
            # adjust smoothing coefficients
            lambdas[deleted.index(
                    max(deleted))] += transition_counts[transition]
        # normalize and save smoothing coeffcients
        for i, lmb in enumerate(lambdas):
            self.smoothing[i] = lmb / sum(lambdas)

        # compute MLEs and smoothing coeffcients for emissions
        lambdas = 2*[0.0]
        for emission, count in emission_counts.items():
            [state, observ] = emission
            # calc mle
            self.emissions[emission] = count / transition_counts.get(
                    (state, ), count)
            # calc deleted mle
            if input_length > 1:
                deleted[0] = (transition_counts.get(
                        (state, ), count) - 1) / (input_length - 1)
            else:
                deleted[0] = 0
            if transition_counts.get((state, ), count) > 1:
                deleted[1] = (count - 1) / (
                        transition_counts.get((state, ), count) - 1)
            else:
                deleted[1] = 0
            deleted[1] = count - 1
            deleted[1] /= transition_counts.get((state, ), count) - 1
            deleted[1] = deleted[1] or 0
            lambdas[1 - int(deleted[0] > deleted[1])] += count
        # normalize and save smoothing coeffcients
        for i, lmb in enumerate(lambdas):
            self.smoothing[self.order+i] = lmb/sum(lambdas)

    def generate(self, observations):
        '''
        viterbi decoder
        '''
        def smoothed_emission(state, observ):
            if state == self.sequence_end:
                return 1.0
            ret = self.smoothing[self.order] * self.emissions.get(
                    (state, observ), 0)
            ret += self.smoothing[self.order+1] * self.transitions.get(
                    state, 0)
            return ret

        def smoothed_transition(states):
            ret = []
            for i in range(self.order):
                ret.append(self.smoothing[i] * self.transitions.get(
                        states[:i + 1], 0))
            return sum(ret)

        def backtrack(path):
            ret = []
            curstate = self.sequence_end
            for e in reversed(path):
                curstate = e[curstate]
                ret.insert(0, curstate)
            return ret

        ret = []
        # separate procedure for unigrams
        if self.order < 2:
            for o in observations:
                maxlike = [float('-inf'), None]
                for s in self.states:
                    like = smoothed_emission(s, o)
                    if like > maxlike[0]:
                        maxlike = [like, s]
                ret.append(maxlike[1])
            return ret

        # backpointers
        path = []
        # probabilities at previous and current steps
        prevporbs = {self.sequence_beg: math.log(1)}
        # states prefix
        state_pfx = (self.order-1) * [[self.sequence_beg]]
        # logarithm at zero
        LOGZERO = -1000
        for observ in observations + [self.sequence_end]:
            path.append({})
            currporbs = {}
            for state in (observ == self.sequence_end
                          and [self.sequence_end] or self.states):
                maxlogprob = float('-inf')
                for pfx in itertools.product(*tuple(state_pfx)):
                    tr_prob = smoothed_transition(pfx + (state, ))
                    em_prob = smoothed_emission(state, observ)
                    pp = prevporbs[pfx[-1]]
                    pp += tr_prob and math.log(tr_prob) or LOGZERO
                    pp += em_prob and math.log(em_prob) or LOGZERO
                    if maxlogprob < pp:
                        maxlogprob = pp
                        path[-1][state] = pfx[-1]
                currporbs[state] = maxlogprob
            state_pfx = state_pfx[1:] + [self.states.keys()]
            prevporbs = {k: v for k, v in currporbs.items()}
        return backtrack(path[1:])
