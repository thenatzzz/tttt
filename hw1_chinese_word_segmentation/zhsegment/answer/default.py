import re, string, random, glob, operator, heapq, codecs, sys, optparse, os, logging, math
from functools import reduce
from collections import defaultdict
from math import log10

class Segment:

    def __init__(self, Pw):
        self.Pw = Pw

    def segment(self, text):
        "Return a list of words that is the best segmentation of text."
        if not text: return []
        segmentation = [ w for w in text ] # segment each char into a word
        return segmentation

    def Pwords(self, words):
        "The Naive Bayes probability of a sequence of words."
        return product(self.Pw(w) for w in words)

#### Support functions (p. 224)

def product(nums):
    "Return the product of a sequence of numbers."
    return reduce(operator.mul, nums, 1)

class Pdist(dict):
    "A probability distribution estimated from counts in datafile."
    def __init__(self, data=[], N=None, missingfn=None):
        for key,count in data:
            self[key] = self.get(key, 0) + int(count)
        self.N = float(N or sum(self.values()))
        self.missingfn = missingfn or (lambda k, N: 1./N)
    def __call__(self, key):
        if key in self: return self[key]/self.N
        else: return self.missingfn(key, self.N)

def datafile(name, sep='\t'):
    "Read key,value pairs from file."
    with open(name,encoding='utf8') as fh:
        for line in fh:
            (key, value) = line.split(sep)
            yield (key, value)

if __name__ == '__main__':
    optparser = optparse.OptionParser()
    optparser.add_option("-c", "--unigramcounts", dest='counts1w', default=os.path.join('data', 'count_1w.txt'), help="unigram counts [default: data/count_1w.txt]")
    optparser.add_option("-b", "--bigramcounts", dest='counts2w', default=os.path.join('data', 'count_2w.txt'), help="bigram counts [default: data/count_2w.txt]")
    optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input', 'dev.txt'), help="file to segment")
    optparser.add_option("-l", "--logfile", dest="logfile", default=None, help="log file for debugging")
    (opts, _) = optparser.parse_args()

    if opts.logfile is not None:
        logging.basicConfig(filename=opts.logfile, filemode='w', level=logging.DEBUG)

    Pw = Pdist(data=datafile(opts.counts1w))
    segmenter = Segment(Pw)
    with open(opts.input,encoding='utf8') as f:
        for line in f:
            print(" ".join(segmenter.segment(line.strip())))
