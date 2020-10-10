import os, sys, optparse
import tqdm
import pymagnitude

import re
# from copy import deepcopy
from numpy import dot
from numpy.linalg import norm
import pandas as pd

class LexSub:

    def __init__(self, wvec_file, topn=10,lexicon=None):
        self.wvecs = pymagnitude.Magnitude(wvec_file)
        # self.wvecfile = wvec_file
        self.topn = topn
        self.lexicon = lexicon

        # list_wvec_dictkey = []
        # for key,val in self.wvecs:
        #     list_wvec_dictkey.append(key)
        #
        # self.wvecDict = set(list_wvec_dictkey)

    def substitutes(self, index, sentence):
        "Return ten guesses that are appropriate lexical substitutions for the word at sentence[index]."
        # print("word: ",sentence[index])
        new_wvecs = retrofit(self.wvecs,self.lexicon,sentence[index],num_iters=10)
        # new_wvecs = retrofit(self.wvecs,self.lexicon,sentence[index],num_iters=5)

        # new_wvecs = retrofit(self.wvecs,self.lexicon,sentence[index],num_iters=10,wvecDict=self.wvecDict)

        return new_wvecs[:self.topn]
        # return(list(map(lambda k: k[0], self.wvecs.most_similar(sentence[index], topn=self.topn))))


'''Helper function'''
# def retrofit(wvecs,lexicon,word,num_iters=10,wvecDict=None):
def retrofit(wvecs,lexicon,word,num_iters=10):

    # new_wvecs = deepcopy(wvecs)
    '''initialize new word vector'''
    new_wvecs = wvecs

    # wvec_dict = set(new_wvecs.keys())
    '''get top N words from GloVe that are most similar to word from text '''
    # wvec_dict = set(map(lambda k: k[0], wvecs.most_similar(word, topn=150)))
    wvec_dict = set(map(lambda k: k[0], wvecs.most_similar(word, topn=500)))


    # wvec_dict = wvecDict

    '''get list of mutual/intersected word between Lexicon and the N most similar words'''
    loop_dict = wvec_dict.intersection(set(lexicon.keys()))
    # print(len(loop_dict))
    '''dict to store words as key and new vectors as value'''
    result_vector={}

    ''' iterate based on number of time we want to update'''
    for iter in range(num_iters):
        # print("iter:",iter)
        '''loop through every node also in ontology (else just use data estimate)'''
        for word_sub in loop_dict:
            # print('iter: ',iter,word_sub)
            '''get list of neighbor words (from Lexicon) that match the top N most similar word'''
            word_neighbours = set(lexicon[word_sub]).intersection(wvec_dict)
            # print(len(word_neighbours), " num_neighbours")
            num_neighbours = len(word_neighbours)
            '''if words in list of mutual word do not have neighbor word, we just use estimate (no retrofit)'''
            if num_neighbours == 0:
                continue
            # the weight of the data estimate if the number of neighbours
            new_vec = num_neighbours * wvecs.query(word_sub)
            # loop over neighbours and add to new vector (currently with weight 1)
            for pp_word in word_neighbours:
                new_vec += new_wvecs.query(pp_word)
            result_vector[word_sub]=new_vec/(2*num_neighbours)
                # new_vec += calculate_cosine_sim(new_wvecs.query(pp_word), new_wvecs.query(word_sub))
            # result_vector[word_sub] = (num_neighbours * calculate_cosine_sim(new_wvecs.query(word),
                                                               # new_wvecs.query(word_sub)) + new_vec) / 2 * num_neighbours

    '''
    #Lexical substitutions
    dict_similarity_result = {}
    # set of Context word(c)
    wvec_dict = set(map(lambda k: k[0], wvecs.most_similar(word, topn=50)))
    # Target (t)
    vector_target = wvecs.query(word)
    # lexicon (sub)
    for word_sub in loop_dict:
        # vector of lexicon (sub=substitute)
        vector_sub = wvecs.query(word_sub)
        cos_sim = calculate_cosine_sim(vector_sub, vector_target)

        # number of context word
        num_context = 0
        # iterate context word
        for word_context in wvec_dict:
            vector_context= wvecs.query(word_context)
            cos_sim +=  calculate_cosine_sim(vector_sub, vector_context)

            num_context += 1
        dict_similarity_result[word_sub] = cos_sim/(num_context+1)
    '''

    '''get word vector of interested word in text'''
    vector_mainWord = wvecs.query(word)
    '''create new dict that stores calculated cosine similarity between new word vector with interested word vector '''
    dict_similarity_result= {}
    for word,vector in result_vector.items():
        dict_similarity_result[word] = calculate_cosine_sim(vector_mainWord, vector)

    '''sort result dict by similarity'''
    dict_similarity_result={k: v for k, v in sorted(dict_similarity_result.items(), key=lambda item: item[1],reverse=True)}

    '''return to list of the most similar word'''
    list_most_similar_word = list(dict_similarity_result.keys())

    return list_most_similar_word

def calculate_cosine_sim(vect1,vect2):
    return dot(vect1, vect2)/(norm(vect1)*norm(vect2))

''' Read the Lexicon (word relations) as a dictionary '''
isNumber = re.compile(r'\d+.*')
def norm_word(word):
    if isNumber.search(word.lower()):
        return '---num---'
    elif re.sub(r'\W+', '', word) == '':
        return '---punc---'
    else:
        return word.lower()

def read_lexicon(filename):
    lexicon = {}
    for line in open(filename, 'r',encoding='utf-8'):
        words = line.lower().strip().split()
        lexicon[norm_word(words[0])] = [norm_word(word) for word in words[1:]]
    return lexicon

if __name__ == '__main__':
    optparser = optparse.OptionParser()
    # optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input', 'dev.txt'), help="input file with target word in context")
    optparser.add_option("-i", "--inputfile", dest="input", default=os.path.join('data', 'input', 'test.txt'), help="input file with target word in context")

    optparser.add_option("-w", "--wordvecfile", dest="wordvecfile", default=os.path.join('data', 'glove.6B.100d.magnitude'), help="word vectors file")
    optparser.add_option("-n", "--topn", dest="topn", default=10, help="produce these many guesses")
    optparser.add_option("-l", "--logfile", dest="logfile", default=None, help="log file for debugging")
    optparser.add_option("-L", "--lexiconfile", dest="lexicon", default=os.path.join('data', 'lexicons','wordnet-synonyms.txt'), help="lexicon file")

    (opts, _) = optparser.parse_args()

    if opts.logfile is not None:
        logging.basicConfig(filename=opts.logfile, filemode='w', level=logging.DEBUG)

    lexicon = read_lexicon(opts.lexicon)
    # wvecs = read_glove(opts.wordvecfile)
    # print(wvecs)
    lexsub = LexSub(opts.wordvecfile, int(opts.topn),lexicon)

    num_lines = sum(1 for line in open(opts.input,'r'))

    i = 0
    with open(opts.input) as f:
        for line in tqdm.tqdm(f, total=num_lines):
        # for line in f:
            # print("-----------------line number----------------------: ",i)
            fields = line.strip().split('\t')

            # print("fields: ", fields)
            print(" ".join(lexsub.substitutes(int(fields[0].strip()), fields[1].strip().split())))
            # print('\n')
            # if i==5:
                # break
            i += 1
