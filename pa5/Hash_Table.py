# CS122 W'21: Markov models and hash tables
# Corry Ke

TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hash_Table:


    def __init__(self, cells, defval):
        '''
        Construct a new, empty hash table with a fixed number of cells equal to the
        parameter "cells", which yields the value defval upon looking up an empty
        cell

        Inputs:
            cells: (int) size of our initial hash table
            defval: the default value our table returns if it is indeed empty
    
        Returns:
            None
        '''
        self.defval = defval
        self.size = 0
        self.capacity = cells
        self.table = [None] * cells
        

    def lookup(self, key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.

        Input: 
            key: (str) key we wish to look up in our table
        
        Returns: 
            hash table value of the associated key
        '''
        start = self.hash_(key)

        for i in range(0, self.capacity):
            index = (start + i) % self.capacity
            if self.table[index] is not None:
                if self.table[index][0] == key:
                    return self.table[index][1]
                else:
                    continue
            else:
                return self.defval


    def update(self, key, val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val". If our table occupy rate exceeds TOO_FULL, increase the
        hash table capacity and rehash the entire table.

        Input: 
            key: (str) key of a pair
            val: (str) value of a pair

        Returns:
            None
        '''
        start = self.hash_(key)

        for i in range(0, self.capacity):
            index = (start + i) % self.capacity
            if self.table[index] is None:
                self.table[index] = (key, val)
                self.size += 1
                break
            else:
                if self.table[index][0] == key:
                    self.table[index] = (key, val)
                    break
                else: 
                    continue

        if self.size / self.capacity >= TOO_FULL:
            self.rehash()


    def hash_(self, s):
        '''
        A hash function that takes in a string and returns a hash 
        value using the string hash function as described in lecture. 
        '''
        h = 0
        for char in s:
            h = h * 37 
            h += ord(char)
            h = h % self.capacity
        return h
    
### GRADER COMMENT: missing docstring
### PENALTY: -1
    def rehash(self):
        self.capacity = self.capacity * GROWTH_RATIO
        values = self.table[:]
        self.table = [None] * self.capacity
        self.size = 0

        for pair in values:
            if pair is not None:
                key, val = pair
                self.update(key, val)


    def __str__(self): 
        '''
        A string representation for our class that returns
        our hash table as a list.

        Input:
            None
        Returns:
            (str) hash table
        '''
        return "the hash table is: %s" % (self.table)

    