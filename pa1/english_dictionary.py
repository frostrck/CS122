# CS122: Auto-completing keyboard using Tries
# Distribution
#
# Matthew Wachs
# Autumn 2014
#
# Revised: August 2015, AMR
#   December 2017, AMR
#
# Corry Ke 

import os
import sys
from sys import exit

import autocorrect_shell


class EnglishDictionary(object):
    def __init__(self, wordfile):
        '''
        Constructor

        Inputs:
          wordfile (string): name of the file with the words.
        '''
        self.words = TrieNode()

        with open(wordfile) as f:
            for w in f:
                w = w.strip()
                if w != "" and not self.is_word(w):
                    self.words.add_word(w)

    def is_word(self, w):
        '''
        Is the string a word?

        Inputs:
           w (string): the word to check

        Returns: boolean
        '''
        return self.is_word_helper(w, self.words, 0)
    
    def is_word_helper(self, w, node, i):
        if i == len(w):
            return node.final
        char = w[i]
        if char in node.sub:
            return self.is_word_helper(w, node.sub[char], i + 1)
        return False


    def num_completions(self, prefix):
        '''
        How many words in the dictionary start with the specified
        prefix?

        Inputs:
          prefix (string): the prefix

        Returns: int
        '''
        # IMPORTANT: When you replace this version with the trie-based
        # version, do NOT compute the number of completions simply as
        #
        #    len(self.get_completions(prefix))
        #
        # See PA writeup for more details.

        # ADD YOUR CODE HERE AND REPLACE THE ZERO IN THE RETURN WITH A
        # SUITABLE RETURN VALUE.

        return 0

    def get_completions(self, prefix):
        '''
        Get the suffixes in the dictionary of words that start with the
        specified prefix.

        Inputs:
          prefix (string): the prefix

        Returns: list of strings.
        '''

        # ADD YOUR CODE HERE AND REPLACE THE EMPTY LIST
        # IN THE RETURN WITH A SUITABLE RETURN VALUE.

        suffs = self.get_completion_node(self.words, prefix, 0)
        return [suff for suff in suffs if suff]
    
    def get_completion_node(self, parent, suffix, i):
        if i == len(suffix):
            return self.get_completion_suffix(parent)
        char = suffix[i]
        if char in parent.sub:
            return self.get_completion_node(parent.sub[char], suffix, i + 1)
        return []


    def get_completion_suffix(self, parent):
        if not parent.sub: 
            return ['']

        complete = []
        for char, child in parent.sub.items():
            child_suff = self.get_completion_suffix(child)
            complete.extend([char + suff for suff in child_suff])

        return complete


class TrieNode(object):
    def __init__(self):
        self.count = 0
        self.final = False
        self.sub = {}

    def _add_word_helper(self, word, i): 
        '''
        A recursive helper function that adds a word by traversing
        trie nodes.

        Inputs:
            trie: (TrieNode) the current node of trie
            word: (string) the complete word we are adding to the trie
            i: (int) index used to extract the exact letter of word
        
        Returns:
            None 
        '''
        if i < len(word):
            char = word[i]
            if char not in self.sub:
                t = TrieNode()
                self.sub[char] = t
            else:
                t = self.sub[char]
            t._add_word_helper(word, i+1)
        else:

            self.final = True

        self.count += 1
            
    def add_word(self, word):
        '''
        A recursive function that adds a word to the trie

        Inputs:
            trie: (TrieNode) the current node of trie
            word: (string) the complete word we are adding to the trie

        Returns:
            None 
        '''
        self._add_word_helper(word, 0)
        
        
    def __repr__(self):
        ret = ''
        for c, node in self.sub.items():
            ret += f'char {c}, count: {str(node.count)}, final: {str(node.final)}; '
            ret += node.__repr__()
        return ret

    ### ADD ANY EXTRA METHODS HERE.


if __name__ == "__main__":
    #autocorrect_shell.go("english_dictionary")

    ed5 = EnglishDictionary("five")
    print(ed5.get_completions("are"))