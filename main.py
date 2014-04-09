""" %%%%%%%%%%%%%%%%%%%%%%%%%%%  EDA132: NLP %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 *
 * by: Ludwig Jacobsson | knd09lja | ludjac@gmail.com
 * %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
 * The objectives of this assignment are to:
    Get acquainted with an annotated corpus
    Extract bigram statistics from this corpus
    Implement a baseline part-of-speech tagger
    Implement the Viterbi algorithm
    Implement a part-of-speech tagger using hidden Markov models
 */ 
/* %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% */
"""
# /bin/python2

import numpy as N
from prettytable import PrettyTable
from corpus import *
# The corpus class is used to create a corpus object, see corpus.py  

# TAGGER CLASS #

class Tagger():
    """
    Tagger class for POS-tagging corpueses using the corpus class.
    (corpus-variant: CoNLL2009). 
    Implemented tagging methods:
        - baseline
        - noisy channel
        - viterbi
    Use print_stats() method to get stats after tagging. 
    author: Ludwig Jacobsson
    """
    def __init__(self, train_corpus = None, sentencelength = False):
        self.train_corpus = train_corpus
        self.accuracy = 'N/A'
        self.tagger = 'None'
        self.tag_corpus = 'None'
        self.miss = 0
        # Limit sentence length for Noisy Channel
        self.sentencelength = sentencelength
        # Set verbosity for debugging
        self.verbosity = 0
        # After tagging the new PPOS is attached to the tagger
        # TODO: Consider this design, should it be attached to the corpus?
        self.PPOS = None

    def baseline(self, tag_corpus):
        """
        Baseline tagger using probability for each word to tag
        """
        PPOS = []
        
        self.tagger = 'Baseline'
        self.tag_corpus = tag_corpus
        miss = 0
        # TAGGING
#        for tag_LEMMA in tag_corpus.LEMMA:
        for tag_FORM in tag_corpus.FORM:
             
            res_PPOS, success = self.train_corpus.most_freq_tag(tag_FORM)
            if self.verbosity == 1:
                print tag_FORM, self.train_corpus.most_freq_tag(tag_FORM)
                if tag_FORM in self.train_corpus.freq:
                    print self.train_corpus.freq[tag_FORM]
                else:
                    print "Not in freq"
            PPOS.append(res_PPOS)
            # Word not in train set
            if not success:
                miss += 1

        self.miss = miss
        # Calculate accuracy
        if tag_corpus.complete == True:
            self.calc_accuracy(tag_corpus, PPOS)        
        self.PPOS = PPOS
        return PPOS

    def viterbi(self, tag_corpus):
        """
        Viterbi algorithm tagging.
        """
        PPOS = []
        
        self.tagger = 'Viterbi'
        self.tag_corpus = tag_corpus
        miss = 0
       
        # Restrict length
        #tag_corpus.restrict_length(5)

        # This tagger does one scentence at a time
        sentences = tag_corpus.sentences

        # TAGGING
        for sentence in sentences:
            if self.verbosity == 1:  
                print sentence

            V = [{}]
            path = {}

            word = sentence[0][1] 
            if word in self.train_corpus.freq:
                POSes = self.train_corpus.freq[word]
            else:
                # Word not in train corpus
                # TODO: pick most common POS, current method is crap
                pos = self.train_corpus.most_freq()
                POSes = {pos:1.0}
                #print POSes
                self.miss += 1 
                         
            # First word
            for key, value in POSes.iteritems():
                V[0][key] = value * self.train_corpus.P_bigram(key, '<s>')
                path[key] = [key]
            
            # Rest of the words
            t2 = 0
            for t, line in enumerate(sentence[1:]): 
                t2 += 1
                V.append({})
                newpath = {}
                word = line[1]
                
                # Word not in train corpus     
                if word in self.train_corpus.freq:
                    POSes = self.train_corpus.freq[word]
                else:
                    # TODO: pick most common POS, current method is crap
                    pos = self.train_corpus.most_freq()
                    POSes = {pos:1.0}
                    #print POSes
                    #POSes = {'NN':1.0}
                    self.miss += 1 #'N/A'
                
                # Calculate paths and probabilities
                for key, value in POSes.iteritems():
                    
                    options = []
                    for pre_key, pre_value in path.iteritems():
                        pre_prob = V[t2-1][pre_value[-1]]
#                        pre_prob = V[t][pre_value[-1]]
                        bigram = self.train_corpus.P_bigram(key, pre_value[-1])
                        (prob, state) = ((pre_prob*value*bigram), pre_value[-1])
                        options.append((prob, state))
                    # Get best path and prob
                    (prob, state) = max(options)
                    V[t2][key] = prob
#                    V[t+1][key] = prob
                    newpath[key] = path[state] + [key]
                path = newpath
            if self.verbosity == 1:  
                print path
            #print V[t]
            # Get best path and prob
            #if t2 == 1:
            (prob, state) = max((V[t2][pre_value[-1]], pre_value[-1]) for pre_key, pre_value in path.iteritems())
#                (prob, state) = max((V[t+1][pre_value[-1]], pre_value[-1]) for pre_key, pre_value in path.iteritems())
            #else: 
            #    (prob, state) = max((V[t2-1][pre_value[-1]], pre_value[-1]) for pre_key, pre_value in path.iteritems())                
#                (prob, state) = max((V[t][pre_value[-1]], pre_value[-1]) for pre_key, pre_value in path.iteritems())                
            if self.verbosity == 1:  
                print path[state]
            PPOS.extend(path[state])
        # Calc accuracy
        if tag_corpus.complete == True:
            self.calc_accuracy(tag_corpus, PPOS)        
        self.PPOS = PPOS
        return PPOS

    def noisychannel(self, tag_corpus):
        """
        Noisy channel tagger.
        NOTE: Restrict scentece length, max ~ 8 words.
            - tagger.sentencelength(n), or class init(scentencelength = n)
        """
        def rec_prob(sentence, PPOS, prob, res, n):
            # Recursive function for the noisy channel
            if n == 0: # Bottom 
                if self.verbosity == 1:
                    print " "
                    print "         PPOS: ", PPOS, "   Accu Prob = ", prob
                    print " "
                return [prob, PPOS[1:]] 
            else: # Not bottom
                word = sentence[0][1]
                # Word in train corpus?
                if word in self.train_corpus.freq:
                    POSes = self.train_corpus.freq[word]
                else:
                    # TODO: pick most common POS, current method is crap
                    pos = self.train_corpus.most_freq()
                    POSes = {pos:1.0}
                    #POSes = {'NN':1.0}
                    self.miss += 1 #'N/A'
                # Set verbosity  
                if self.verbosity == 1:
                    print "Word: ", word, POSes # POSes #line[2]
                # Go through POS tags for word
                for key, value in POSes.iteritems():
                    if self.verbosity == 1:
                        print "     ", "P(",word,"|", key, ") = ", value
                        print "     ", "P(", key,"|", PPOS[-1],") = ", self.train_corpus.P_bigram(key, PPOS[-1])
                    
                    curr_prob = value*self.train_corpus.P_bigram(key, PPOS[-1])
                    if self.verbosity == 1:
                        print "     ", "P(",word,"|", key, ")P(", key,"|",PPOS[-1],") = ", curr_prob 
                        
                        print "         PPOS: ", PPOS, "   Accu Prob = ", prob
                        print " "
                    # Recursive call
                    # move sentence, add Tag to PPOS, newprob, result, next
                    # level
                    rec = rec_prob(sentence[1:], PPOS + [key], curr_prob*prob, res, n-1)
                    # Check if new path is better
                    if rec[0]>res[0]:
                        res = rec
                    if self.verbosity == 1:
                        print " REC!! ", res, "n = ", n
            return res
        
        self.tagger = 'Noisy Channel'
        self.tag_corpus = tag_corpus
        PPOS = []
        
        # Set sentencelength for tagger to cope with load
        if self.sentencelength is not False:
            tag_corpus.restrict_length(self.sentencelength)
        

        # TAGGING 
        for sentence in self.tag_corpus.sentences:
            if self.verbosity == 1:
                print sentence
            # Start recursive Calculates
            res = rec_prob(sentence, ['<s>'], 1, [0], len(sentence))
            PPOS.extend(res[1])
        
        # Calc accuracy
        if tag_corpus.complete == True:
            self.calc_accuracy(tag_corpus, PPOS)        
        self.PPOS = PPOS
        return PPOS

    def calc_accuracy(self, corpus, PPOS):
        """
        Calculates the accuracy of the tagger. 
        """
        hit = 0
        miss = 0
        #for sentence in corpus:
        for i, POS in enumerate(corpus.POS):
            if PPOS[i] == POS:
                hit += 1
            else:
                miss += 1
        # Set accuracy for the tagger
        self.accuracy = float(hit)/float(corpus.length)
        return self.accuracy

    def confusion(self, PPOS=None):
        """
        Print confusion table to file 'confusion.txt'
        """
        if self.PPOS is not None and PPOS is None:
            PPOS = self.PPOS
        if PPOS is None and self.PPOS is None:
            print "No PPOS-set supplied."
            return
        # Create matrix with zeros
        conf_M = N.zeros([self.train_corpus.POSlength, self.train_corpus.POSlength])
        # create key for accesing correct column/row
        MK = {key:i for i, key in enumerate(self.train_corpus.unique_tags)}
        for i, PPOS_tag in enumerate(PPOS): 
            conf_M[MK[PPOS_tag]][MK[self.tag_corpus.POS[i]]] += 1

        # Create a PrettyTable for displaying the confusion matrix
        POSes = [key for i, key in enumerate(self.train_corpus.unique_tags)]
        axes = POSes[:]
        axes.insert(0, 'PPOS \ POS')
        table = PrettyTable(axes)
        for i in xrange(len(POSes)):
            a = conf_M[i, :][:].tolist()
            a.insert(0, POSes[i])          
            table.add_row(a)
        # Write prettytable to text file
        table.get_html_string 
        with open('confusion.html', 'w') as f:
            f.write(table.get_html_string())
        return conf_M

    def print_stats(self):
        """
        Print stats for the tagger
        """
        print "------------------------------------------"
        print "Stats for POS-tagging:"
        print "Tagger: ", self.tagger
        if self.tagger == 'Noisy Channel':
            print "Max sentence length: ",  self.sentencelength
        print " "
        print "Corpus for training: ", self.train_corpus.filename
        print "               Words:", self.train_corpus.length
        print "     Unique POS-tags:", self.train_corpus.POSlength
        print "        Unique words:", len(self.train_corpus.unique_words)
        print " "
        print "Corpus for tagging:  ", self.tag_corpus.filename
        #print "     Unique POS-tags:", self.tag_corpus.POSlength
        print "               Words:", self.tag_corpus.length
        print " "
        print "Accuracy: ", self.accuracy
        print "Number times word missing: ",self.miss
        print "------------------------------------------"


if __name__ == '__main__':

    dev_corp = Corpus('CoNLL2009-ST-English-development-pos.txt')     
    train_corp = Corpus('CoNLL2009-ST-English-train-pos.txt') 
    test_corp = Corpus('CoNLL2009-ST-test-words.txt', complete=False)
#    print dev_corp.freq['point']
    #dev_corp.restrict_length(5)
    #print dev_corp.sentences
        
    tagger1 = Tagger(train_corpus = train_corp, sentencelength=False)
    PPOS = tagger1.baseline(dev_corp)
    tagger1.print_stats()
    
    tagger2 = Tagger(train_corpus = train_corp, sentencelength=False)
    PPOS = tagger2.viterbi(dev_corp)
    tagger2.print_stats()
    tagger2.confusion()
    
    tagger3 = Tagger(train_corpus = train_corp, sentencelength=8)
    PPOS = tagger3.noisychannel(dev_corp)
    tagger3.print_stats() 
    
    tagger4 = Tagger(train_corpus = dev_corp, sentencelength=False)
    PPOS = tagger4.viterbi(test_corp)
    with open('test_PPOS', 'w') as f:
        f.write(str(PPOS))
    tagger4.print_stats()
    