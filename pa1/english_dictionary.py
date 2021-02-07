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

### GRADER COMMENT: Function and class definitions 
###  should be separated by two blank lines

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
    
    ### GRADER COMMENT: multiple copies of traversal
    def is_word_helper(self, w, node, i):
        '''
        Recursive helper that determines whether a complete
        word ends on this node

        Inputs:
            w: (str) the word of interest
            node: (TrieNode) the cuurent node
            i: (int) the index that keeps track of our position in the word
        
        Returns:
            (bool) whether a word ended on a node
        '''

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
        return self.num_completions_r(self.words, prefix, 0)

    ### GRADER COMMENT: multiple copies of traversal
    ### PENALTY: -3 points
    def num_completions_r(self, trie, prefix, i):
        '''
        Recursive helper that gives the word count of a prefix
        node.

        Inputs:
            trie: (TrieNode) the current TrieNode
            prefix: (str) a string of prefix
            i: (int) the index that keeps track of our position in the prefix
        
        Returns:
            (int) number of words in the Trie that begins with prefix
        '''
        
        if i == len(prefix):
            return trie.count
        
        char = prefix[i]
        if char in trie.sub:
            return self.num_completions_r(trie.sub[char], prefix, i + 1)
        else:
            return 0

        
    def get_completions(self, prefix):
        '''
        Get the suffixes in the dictionary of words that start with the
        specified prefix.

        Inputs:
          prefix (string): the prefix

        Returns: list of strings.
        '''

        suffs = self.get_completion_node(self.words, prefix, 0)
        return [suff for suff in suffs if suff]
    
    ### GRADER COMMENT: function name isn't descriptive, get_prefix is better
    ### PENALTY: -2 points

    ### GRADER COMMENT: using i for 0 check is confusing,
    ###  it's better to just use 0
    ### PENALTY: -2 points

    ### GRADER COMMENT: does not handle case of no link
    ### PENALTY: -2 points
    def get_completion_node(self, parent, prefix, i):
        '''
        A helper that recursively navigates the subtrie to get 
        to children nodes of a parent
        
        Inputs:
            parent: (TrieNode) the current, parent TrieNode
            prefix: (string) the prefix of interest
            i: (int) index that keeps track of the posistion of 

        Returns: 
            (lst) a list of all suffixes following a prefix 
        '''
        if i == len(prefix):
            return self.get_completion_suffix(parent)

        char = prefix[i]
        if char in parent.sub:
            return self.get_completion_node(parent.sub[char], prefix, i + 1)

        return []


    def get_completion_suffix(self, parent):
        '''
        A recursive helper that gathers all the suffix of a
        parent(prefix) node.

        Inputs:
            parent: (TrieNode) the current node

        Returns:
            (lst) A list of all suffixes from that parent node
        '''
        if not parent.sub: 
            return ['']

        complete = []
        for char, child in parent.sub.items():
            child_suff = self.get_completion_suffix(child)
            complete.extend([char + suff for suff in child_suff])

        return complete


class TrieNode(object):
    def __init__(self):
        '''
        Constructor
        
        Inputs: 
            None
        '''
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
  
    ### GRADER COMMENT: Missing docstrings
    ### PENALTY: -1 point  
    def __repr__(self):
        ret = ''
        for c, node in self.sub.items():
            ret += f'char {c}, count: {str(node.count)}, final: {str(node.final)}; '
            ret += node.__repr__()
        return ret


if __name__ == "__main__":
    autocorrect_shell.go("english_dictionary")

    
