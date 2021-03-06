# CS122 W'21: Markov models and hash tables
# Corry Ke

import sys
import math
import Hash_Table

# from os import listdir                these two imports were for getting filenames in 
# from os.path import isfile, join      loop testing in shell, not used in actual coding of Markov

HASH_CELLS = 57


class Markov:


    def __init__(self, k, s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"

        Inputs:
            k: (int) order of our Markov model
            s: (str) training text
        '''
        self.alphabet = list(set(list(s)))
        self.n = len(self.alphabet)
        self.k = k
        self.s = s
        self.ht = Hash_Table.Hash_Table(HASH_CELLS, 0)


    def log_probability(self, s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.

        Input:
            s: (str) a new string of texts

        Returns:
            (float) log-prob of the string under our model
        '''
        summed_probabilities = 0
        self.update_hash(self.k, self.s, self.ht)
        self.update_hash(self.k + 1, self.s, self.ht)
        complete_s = s[-self.k:] + s

        for i in range(len(complete_s) - self.k):
            k_gram = complete_s[i:i + self.k]
            k1_gram = complete_s[i:i + self.k + 1]
            context_count = self.ht.lookup(k_gram)
            new_count = self.ht.lookup(k1_gram)
            p = (new_count + 1) / (context_count + self.n)
            p = math.log(p)
            summed_probabilities += p

        return summed_probabilities
    

    def update_hash(self, k, s, h):
        '''
        Takes in an integer k, string, and hash table, generate all k-grams 
        in that string, and updates their counts in the hash table.

        Inputs:
            k: (int) length chunks of our string
            s: (str) string of text
            h: (Hast_Table) that keeps track of counts of k-grams
        
        Returns:
            None
        '''
        complete_s = s[-k:] + s
        for i in range(len(complete_s) - k):
           k_gram = complete_s[i:i + k]
           count = h.lookup(k_gram)
           h.update(k_gram, count + 1) 


def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers (1 and 2), and text from an
    unidentified speaker (3), return a tuple with the *normalized* log probabilities
    of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.

    Inputs:
        speech1: (str) training text for speaker 1
        speech2: (str) training text for speaker 2
        speech3: (str) text from unidentified speaker
        order: (int) order of Markov model

    Returns:
        P(speaker1), P(speaker2), conclusion
    '''
    n = len(speech3)
    speaker1 = Markov(order, speech1)
    speaker2 = Markov(order, speech2)
    prob1 = speaker1.log_probability(speech3) / n
    prob2 = speaker2.log_probability(speech3) / n

    if prob1 > prob2:
        conclusion = "A"
    else:
        conclusion = "B"

    return prob1, prob2, conclusion


def print_results(res_tuple):
    '''
    Given a tuple from identify_speaker, print formatted results to the screen
    '''

    (likelihood1, likelihood2, conclusion) = res_tuple
    
    print("Speaker A: " + str(likelihood1))
    print("Speaker B: " + str(likelihood2))

    print("")

    print("Conclusion: Speaker " + conclusion + " is most likely")


if __name__=="__main__":
    num_args = len(sys.argv)

    if num_args != 5:
        print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
              "<file name for speaker B>\n  <file name of text to identify> " +
              "<order>")
        sys.exit(0)
    
    with open(sys.argv[1], "r") as file1:
        speech1 = file1.read()

    with open(sys.argv[2], "r") as file2:
        speech2 = file2.read()

    with open(sys.argv[3], "r") as file3:
        speech3 = file3.read()

    res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    print_results(res_tuple)


    # My own loop testing code below:

    # mypath = "./speeches/bush-kerry3"
    # onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    # for f in onlyfiles:
    #     print(f)
    #     file1 = "./speeches/kerry1+2.txt"
    #     file2 = "./speeches/bush1+2.txt"
    #     file3 = "./speeches/bush-kerry3/" + f

    #     with open(file1, "r") as file1:
    #         speech1 = file1.read()

    #     with open(file2, "r") as file2:
    #         speech2 = file2.read()

    #     with open(file3, "r") as file3:
    #         speech3 = file3.read()

    #     res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[1]))

    #     print_results(res_tuple)
