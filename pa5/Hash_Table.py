# CS122 W'21: Markov models and hash tables
# Corry Ke


TOO_FULL = 0.5
GROWTH_RATIO = 2


class Hash_Table:

    def __init__(self,cells,defval):
        '''
        Construct a new hash table with a fixed number of cells equal to the
        parameter "cells", and which yields the value defval upon a lookup to a
        key that has not previously been inserted

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
        


    def lookup(self,key):
        '''
        Retrieve the value associated with the specified key in the hash table,
        or return the default value if it has not previously been inserted.

        Input: 
            key: (int) key we wish to look up in our table
        
        Returns: 
            hash table value of the associated key
        '''
        if self.table[key] != None:
            return self.table[key]
        else:
            return self.defval


    def update(self,key,val):
        '''
        Change the value associated with key "key" to value "val".
        If "key" is not currently present in the hash table,  insert it with
        value "val". If our table occupy rate exceeds TOO_FULL, 

        Input: 

        Returns:
            None
        '''
        temp_key = key 

        while self.table[temp_key] != None:
            temp_key += 1
        
        self.table[temp_key] = val
        self.size += 1

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
    
    def rehash(self):
        self.capacity = self.capacity * GROWTH_RATIO
        values = self.table[:]
        self.table = [None] * self.capacity
        self.size = 0

        for val in values:
            if val != None:
                key = self.hash_(val)
                self.update(key, val)

    def __str__(self): 
        return "the hash table is: %s" % (self.table)

if __name__ == "__main__":
    ht = Hash_Table(1, "empty")
    print(ht)
    key = ht.hash_("hi")
    ht.update(key, "hi")
    print(ht)
    print(ht.lookup(1))
    print(ht.lookup(2))