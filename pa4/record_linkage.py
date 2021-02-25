# CS122: Linking restaurant records in Zagat and Fodor's data sets
#
# Corry Ke


import numpy as np
import pandas as pd
import jellyfish as jf
import util

def find_matches(mu, lambda_, block_on_city=False):
    '''
    Takes in acceptable false positive and negative rates
    and a boolean (whether to block by city) and returns
    three dataframes that contains restaurant matches, possible
    matches, and unmatches across the two given datasets.

    Input:
        mu:
        lambda:
        block_on_city:

    Returns
        (tuple of dataframes): (matches, possible_matches, unmatches)
    '''

    header_list = ["rest_name", "city", "address"]
    zagat = pd.read_csv("zagat.csv", names = header_list)
    fodors = pd.read_csv("fodors.csv", names = header_list)
    known = pd.read_csv("known_links.csv", names = ["zagat", "fodors"])

    matched_pairs = pair(known)
    matches = create_matches(zagat, fodors, matched_pairs)
    unmatches = create_unmatches(zagat, fodors)

    match_ind = [(x, x) for x in range(0, 50)]
    unmatch_ind = [(x, x) for x in range(0, 1000)]
    match_tup = generate_tuples(matches, matches, match_ind)
    unmatch_tup = generate_tuples(unmatches, unmatches, unmatch_ind)

    match_tuples, possible_tuples, unmatch_tuples =  \
            assign_tuple(match_tup, unmatch_tup, mu, lambda_)

    pass


def pair(known_links):
    '''
    Takes in a dataframe of known matches
    and generate a list of tuples containing 
    the matches.

    Input:
        known_links: pandas dataframe
    
    Returns:
        (lst) list of tuples of indeces for each match
    '''

    pairs = [(x, y) for x, y in zip(known_links["zagat"], known_links["fodors"])]

    return pairs


def create_matches(df1, df2, pairs):
    '''
    Create a merged dataframe from a list
    of tuples of indices of known matches.

    Inputs:
        df1
        df2
        pairs: (lst) of tuples containing indices
    
    Returns:
        (pandas dataframe)
    '''

    header = ["z_rest_name", "z_city", "z_address", 
                "f_rest_name", "f_city", "f_address"]

    matches = combine_indices(df1, df2, pairs, header)

    return matches


def create_unmatches(df1, df2):
    '''
    Takes in two dataframes and generate 
    1000 pairs of restaurants that are unmatches
    at random.

    Inputs:
        df1
        df2

    Returns:
        (pandas dataframe)
    '''

    header = ["z_rest_name", "z_city", "z_address", 
                "f_rest_name", "f_city", "f_address"]

    zs = df1.sample(1000, replace = True, random_state = 1234)
    fs = df2.sample(1000, replace = True, random_state = 5678)
    z_index = zs.index
    f_index = fs.index
    indices = []
    rows = []

    for i, val in enumerate(z_index):
        indices.append((val, f_index[i]))
    unmatches = combine_indices(df1, df2, indices, header)

    return unmatches


def combine_indices(df1, df2, indices, header):
    '''
    Generate a new dataframe from tuples
    of indices and header.
    '''

    rows = []
    for pair in indices:
        z, f = pair
        z_rest = df1.loc[z].tolist()
        f_rest = df2.loc[f].tolist()
        rows.append(z_rest + f_rest)

    merged_df = pd.DataFrame(rows, columns = header)

    return merged_df


def generate_tuples(df1, df2, indices):
    '''
    For given dataframes, compute the 
    tuple of Jaro-Winkler distances for the 
    pair of restaurants in the pairs of indices.

    Inputs:
        df1
        df2
        indices: (lst) lst of tuples of indices
    
    Returns:
        (dict) of tuples of j-w distances
    '''

    tuples_dict = {}

    for pair in indices:
        ind1, ind2 = pair
        name_score = jf.jaro_winkler(df1.loc[ind1, 'z_rest_name'], df2.loc[ind2, 'f_rest_name'])
        city_score = jf.jaro_winkler(df1.loc[ind1, 'z_city'], df2.loc[ind2, 'f_city'])
        add_score = jf.jaro_winkler(df1.loc[ind1, 'z_address'], df2.loc[ind2, 'f_address'])

        name_cat = util.get_jw_category(name_score)
        city_cat = util.get_jw_category(city_score)
        add_cat = util.get_jw_category(add_score)
        
        tuples_dict[pair] = (name_cat, city_cat, add_cat)

    return tuples_dict


def assign_tuple(match_tup, unmatch_tup, mu, lambda_):
    '''
    From a list of matched tuples and unmatched tuples,
    partition all possible tuples into match, unmatch, 
    possible according acceptable false pos and false
    neg rate.

    Inputs:
        match_tup: (lst) of tuples that occured in matches
        unmatch_tup: (lst) of tuples that occured in unmatches
        mu: (float) false pos threshhold
        lambda_: (float) flase neg threshhold

    Returns:
    '''
    match_tuples = set()
    possible_tuples = set()
    unmatch_tuples = set()

    all_tuples = []
    levels = ["high", "medium", "low"]
    for level1 in levels:
        for level2 in levels:
            for level3 in levels:
                all_tuples.append((level1, level2, level3))

    match_counts = count_tuples(match_tup)
    unmatch_counts = count_tuples(unmatch_tup)

    m, u = calc_tup_prob(match_counts, unmatch_counts, all_tuples)
    remaining_tup = all_tuples.copy()

    for tup in all_tuples:
        if m[tup] == 0 and u[tup] == 0:
            possible_tuples.add(tup)
            remaining_tup.remove(tup)

    sorted_tuples = prob_sort(m, u, remaining_tup)

    false_pos = 0
    false_neg = 0

    for i, tup in enumerate(sorted_tuples):
        false_pos += u[tup]
        if false_pos <= mu:
            match_tuples.add(tup)
        else:
            break

    for i, tup in enumerate(sorted_tuples[::-1]):
        false_neg += m[tup]
        if false_neg <= lambda_ and tup not in match_tuples:
            unmatch_tuples.add(tup)
        else:
            break

    for tup in sorted_tuples:
        if tup not in match_tuples and tup not in unmatch_tuples:
            possible_tuples.add(tup)

    print(len(unmatch_tuples) + len(possible_tuples) + len(match_tuples))
    return match_tuples, possible_tuples, unmatch_tuples


def count_tuples(tups_dict):
    '''
    Given a dict of tuples, count their number
    of times of appearance and store them into a dictionary

    Inpus:
        tups: (dict) of indices and tuple
    
    Returns:
        (dict) of counts
    '''
    tup_counts = {}
    tup_list = list(tups_dict.values())

    for tup in tup_list:
        if tup in tup_counts:
            tup_counts[tup] += 1
        else:
            tup_counts[tup] = 1

    return tup_counts


def calc_tup_prob(match_counts, unmatch_counts, all_tuples):
    '''
    Given a dict of tuple counts, calculate their relative
    frequency that they appear in matches/unmatches.

    Inputs:
        match_counts: (dict) number of appearance in matches
        unmatch_counts: (dict) numer of appearance in unmatches
        all_tuples: (lst) all possible tuple combinations
    
    Returns:
        m: (dict) tuples' relative freq in matches
        u: (dict) tuples' relative freq in unmatches
    '''
    m = {}
    u = {}

    for tup in all_tuples: 
        if tup in match_counts:
            m[tup] = match_counts[tup] / 50
        else:
            m[tup] = 0
        
        if tup in unmatch_counts:
            u[tup] = unmatch_counts[tup] / 1000
        else:
            u[tup] = 0

    return m, u


def prob_sort(m, u, remaining_tuples):
    '''
    Given the relative frequencies 
    of appearance in matches and unmatches,
    sort tuples based on decreasing m / u

    Inputs:
        m:
        u:
        remaining_tuples:
    
    Returns:
        (lst) of sorted tuples (u = 0 first, then in
        decreasing m / u)
    '''
    
    key = lambda x: -1 if u[x] == 0 else m[x] / u[x]
    remaining_tuples.sort(key = key)    

    first_nonzero = 0

    while u[remaining_tuples[first_nonzero]] == 0:
        first_nonzero += 1

    sorted_tuples = remaining_tuples[:first_nonzero
                    ] + remaining_tuples[first_nonzero:][::-1]

    return sorted_tuples

def find_all_matches(df1, df2, match_tuples, possible_tuples, unmatch_tuples):
    for ind1 in df1.itertuples():
        for ind2 in df2.itertuples():
            index_pair = (ind1, ind2)



if __name__ == '__main__':

    header_list = ["rest_name", "city", "address"]
    zagat = pd.read_csv("zagat.csv", names = header_list)
    fodors = pd.read_csv("fodors.csv", names = header_list)
    known = pd.read_csv("known_links.csv", names = ["zagat", "fodors"])
    zs = zagat.sample(1000, replace = True, random_state = 1234)
    fs = fodors.sample(1000, replace = True, random_state = 5678)

    pairs = pair(known)
    matches = create_matches(zagat, fodors, pairs)
    unmatches = create_unmatches(zagat, fodors)
    
    match_ind = [(x, x) for x in range(0, 50)]
    unmatch_ind = [(x, x) for x in range(0, 1000)]
    match_tup = generate_tuples(matches, matches, match_ind)
    unmatch_tup = generate_tuples(unmatches, unmatches, unmatch_ind)

    print(assign_tuple(match_tup, unmatch_tup, 0.005, 0.005))
    print(len([(x, y) for x in range(0, 50) for y in range(0, 1000)]))

    # matches, possibles, unmatches = \
    #     find_matches(0.005, 0.005, block_on_city=False)

    # print("Found {} matches, {} possible matches, and {} "
    #       "unmatches with no blocking.".format(matches.shape[0],
    #                                            possibles.shape[0],
    #                                            unmatches.shape[0]))