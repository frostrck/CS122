# CS122 W'21: Markov models and hash tables
# YOUR NAME HERE

import sys
import math
import Hash_Table

HASH_CELLS = 57

class Markov:

    def __init__(self, k, s):
        '''
        Construct a new k-order Markov model using the statistics of string "s"
        '''
        self.alphabet = list(set(list(s)))
        self.s = s
        self.k = k
        self.ht = Hash_Table.Hash_Table(HASH_CELLS, self.all_char)
        

    def log_probability(self, s):
        '''
        Get the log probability of string "s", given the statistics of
        character sequences modeled by this particular Markov model
        This probability is *not* normalized by the length of the string.
        '''
        
    
    def count_all_char(self, s):
        '''
        Get the total number unique characters that appeared
        in our string.
        
        Input:
            (str) Input string
        Returns
            (int) number of unique characters that appeared
        '''
        characters = set()
        for char in s:
            characters.add(char)
        return len(characters)

    def find_preceeding_k(self, i):
        if self.k <= i:
            return self.s[i - self.k: i]
        else:
            return self.s[::-1][:self.k - i + 1] + self.s[:i]

def identify_speaker(speech1, speech2, speech3, order):
    '''
    Given sample text from two speakers (1 and 2), and text from an
    unidentified speaker (3), return a tuple with the *normalized* log probabilities
    of each of the speakers
    uttering that text under a "order" order character-based Markov model,
    and a conclusion of which speaker uttered the unidentified text
    based on the two probabilities.
    '''
    ### YOUR CODE HERE ###


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
    # num_args = len(sys.argv)

    # if num_args != 5:
    #     print("usage: python3 " + sys.argv[0] + " <file name for speaker A> " +
    #           "<file name for speaker B>\n  <file name of text to identify> " +
    #           "<order>")
    #     sys.exit(0)
    
    # with open(sys.argv[1], "r") as file1:
    #     speech1 = file1.read()

    # with open(sys.argv[2], "r") as file2:
    #     speech2 = file2.read()

    # with open(sys.argv[3], "r") as file3:
    #     speech3 = file3.read()

    # res_tuple = identify_speaker(speech1, speech2, speech3, int(sys.argv[4]))

    # print_results(res_tuple)

    s = "hello"
    m = Markov(4, "hello")
    print(s[2])
    print(m.find_preceeding_k(2))