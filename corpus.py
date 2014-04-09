""" %%%%%%%%%%%%%%%%%%%%%%%%%%% EDA132: NLP %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
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

# Corpus class for NLP tagger

class Corpus():
    """
    Class for creating corpus object from CoNLL2009 corpus, 
    use with tagger class. 
    author: Ludwig Jacobsson
    """

    def __init__(self, filename, complete = True):
        self.complete = complete
        self.filename = filename        
        self.corpus = []
        self.ID = []
        self.FORM = [] 
        self.LEMMA = []
        self.PLEMMA = []
        self.sentences = [] 
        self.length = self.file_len() 
        if self.complete == True:
            self.POS = []
            self.PPOS =  []
            self.freq = {}
            self.freq_POS = {}
            self.unique_words, self.unique_tags = {}, {}
            self.bigrams = {}
            self.get_corpus() 
            self.uniqueness_dict()
            self.POSlength = len(self.unique_tags)
            self.POS_freq()
            #self.baseprob()
            self.normalize_freq()
            self.get_bigrams()
        else: 
            self.POS = None
            self.PPOS = None

    def normalize(self, source_dict):
        """
        Convert percentage from frequency in dict 
        """
        sum = 0
        for key, value in source_dict.iteritems():
            sum += value
        for key, value in source_dict.iteritems():
            source_dict[key] = float(value)/float(sum)
        return source_dict

    def normalize_freq(self):
        """
        Wrapper for normalizing the freq-attribute
        """
        for key, value in self.freq.iteritems():
            self.freq[key] = self.normalize(value)

    def P_bigram(self, POS, POS_n1):
        """
        P(t_n|t_(n-1)), Bigram probability
        """
        POS_bigram = self.bigrams[POS]
        if POS_n1 not in POS_bigram:
            return 0.0
        POS_occur = 0
        for key, value in POS_bigram.iteritems():
            POS_occur += value
        return float(POS_bigram[POS_n1])/float(POS_occur)

    def get_bigrams(self):
        """
        Get bigrams from corpus
        """
        bigrams = {}
        for i, POS in enumerate(self.POS):
            if POS not in bigrams:
                bigrams[POS] = {self.POS[i-1]:1}
            else:
                if self.POS[i-1] not in bigrams[POS]:
                    bigrams[POS][self.POS[i-1]] = 1
                else:
                    bigrams[POS][self.POS[i-1]] += 1

        self.bigrams = bigrams
    
    """
    def baseprob(self):
        words = {}
        for line in self.corpus:
            if line[1] in words:
                words[line[1]].append(line[4])
            else:
                words[line[1]] = [line[4]]
        for word in words:
            s = list(set(words[word]))
            # Make list of tuples per word with (POS, prob)
            words[word] = sorted([(k, float(j)/len(words[word])) for k, j in zip(s, map(words[word].count, s))], key=lambda entry: entry[1], reverse=True)
            # Append the number of POS per word for a later top-list        
            words[word].append(len(s))
        # Top list of words with most POS-tags
        sor = sorted([(word, words[word][-1]) for word in words], key = lambda entry: entry[1], reverse=True)        
        self.freq = words
        #return words
    """

    
    def POS_freq(self):
        """
        POS frequency dictionary for each unique word in corpus
        """
        freq = {}
        for ID, FORM, LEMMA, PLEMMA, POS, PPOS in self.corpus:
            if FORM not in freq:
                freq[FORM] = {}
            if POS not in freq[FORM]:
                freq[FORM][POS] = 1
            else:
                freq[FORM][POS] += 1
        self.freq = freq
    

    def most_freq(self):
        """
        The most frequent tag in corpus
        """
        POS_list = []
        for key, value in self.unique_tags.iteritems():
            POS_list.append([key, value])
        POS_list = sorted(POS_list, key=lambda pos: pos[1], reverse=True)

        return POS_list[0][0]

    def most_freq_tag(self, word): #, POS_dict):
        """
        The most frequent POS-tag for a word.
        
        Input: A word
        Output: Most frequent POS-tag for the word.
        """
        POS_list = []
        if word in self.freq:
            POS_dict = self.freq[word]
            success = True
        else:
            POS_dict = self.unique_tags    
            success = False

        for key, value in POS_dict.iteritems():
            POS_list.append([key, value])
    
        POS_list = sorted(POS_list, key=lambda pos: pos[1], reverse=True)
        return POS_list[0][0], success

    def get_corpus(self):
        """
        Load corpus from file
        """
        sentence = []
        sentences = []
        count = 1
        with open(self.filename, 'r') as f:
            for line in f:
                # If line is not between sentences
                if line.split():
                    if self.complete == True:
                        (ID_line, FORM_line, LEMMA_line, PLEMMA_line, POS_line, PPOS_line) = line.split()
                        self.corpus.append([ID_line, FORM_line, LEMMA_line, PLEMMA_line, POS_line, PPOS_line])
                        sentence.append([ID_line, FORM_line, LEMMA_line, PLEMMA_line, POS_line, PPOS_line])
                        self.ID.append(ID_line)
                        self.FORM.append(FORM_line)
                        self.LEMMA.append(LEMMA_line)
                        self.PLEMMA.append(PLEMMA_line)
                        self.POS.append(POS_line)
                        self.PPOS.append(PPOS_line)
                    else:
                        (ID_line, FORM_line, LEMMA_line, PLEMMA_line) = line.split()
                        self.corpus.append([ID_line, FORM_line, LEMMA_line, PLEMMA_line])
                        sentence.append([ID_line, FORM_line, LEMMA_line, PLEMMA_line])
                        self.ID.append(ID_line)
                        self.FORM.append(FORM_line)
                        self.LEMMA.append(LEMMA_line)
                        self.PLEMMA.append(PLEMMA_line)
                else:
                    
                    (ID_line, FORM_line, LEMMA_line, PLEMMA_line, POS_line, PPOS_line) = ['0', '<s>', '<s>', '<s>', '<s>',  '<s>']
                    self.corpus.append([ID_line, FORM_line, LEMMA_line, PLEMMA_line, POS_line, PPOS_line])
                    sentence.append([ID_line, FORM_line, LEMMA_line, PLEMMA_line, POS_line, PPOS_line])
                    self.ID.append(ID_line)
                    self.FORM.append(FORM_line)
                    self.LEMMA.append(LEMMA_line)
                    self.PLEMMA.append(PLEMMA_line)
                    self.POS.append(POS_line)
                    self.PPOS.append(PPOS_line)
                    
                    #if not line.split():
                    #print line
                    sentences.append(sentence)
                    sentence = []
        self.sentences = sentences

    def restrict_length(self, n):
        """
        Restrict length of sentences in corpus
        """
        loc_vec = [[0, 0, 0]]
        sentences = []
        POS = []
        for i, ID in enumerate(self.ID):
            if int(ID)==1:
                loc_vec.append([i-loc_vec[-1][2], loc_vec[-1][2], i])
        loc_vec = loc_vec[2:]
        loc_vec.append([len(self.ID)-loc_vec[-1][2], loc_vec[-1][2], len(self.ID)])
        
        for row in loc_vec:
            if row[0]<=n:
                for line in self.corpus[row[1]:row[2]]:
                    POS.append(line[4])
                sentences.append(self.corpus[row[1]:row[2]])
        self.POS = POS
        self.sentences = sentences
        self.length = len(POS)
        return sentences


    def uniqueness_dict(self):
        """
        Dictionarys of the unique tags and word with their frequncies
        """
        words = {}
        tags = {}
        #for sentence in corpus:
        for ID, FORM, LEMMA, PLEMMA, POS, PPOS in self.corpus:
            if FORM not in words:
                words[FORM] = 1
            else:
                words[FORM] += 1
            if POS not in tags:
                tags[POS] = 1
            else:
                tags[POS] += 1
        
        self.unique_words = self.normalize(words)
        self.unique_tags = self.normalize(tags)
    
    def file_len(self):
        """
        length of file
        """
        with open(self.filename) as f:
            for i, l in enumerate(f):
                pass
        return i + 1

