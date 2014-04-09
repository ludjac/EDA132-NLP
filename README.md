EDA132: NLP
=========== 
*
 * by: Ludwig Jacobsson | knd09lja | ludjac@gmail.com
 * The objectives of this assignment are to:
     Get acquainted with an annotated corpus
     Extract bigram statistics from this corpus
     Implement a baseline part-of-speech tagger
     Implement the Viterbi algorithm
     Implement a part-of-speech tagger using hidden Markov models

Instructions for running NLP-algorithm
======================================

When executing main.py in python2 the following will run:
	
	* POS-tagging dev-corpus with baseline-algorithm
	* POS-tagging dev-corpus with viterbi-algorithm
	* POS-tagging dev-corpus with noisy channel-algorithm
	* POS-tagging test-corpus with viterbi-algorithm and write PPOS to
	  file 'test_PPOS'
	* Print stats for the above

To generate a confusion-matrix run the tagger-class method confusion(),  
either supply a PPOS set (tagger.confusion(PPOS)) or it will pick the PPOS set from the
previous tag run. The confusion matrix will be printed to a file called
confusion.html and can easliy be viewed in a browser, for example Google Chrome. 
