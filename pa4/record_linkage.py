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
        mu: (float) max acceptable false positive
        lambda: (float) max acceptable false negative
        block_on_city: (bool)

    Returns: (tuple) of dataframes: matches, possible_matches, unmatches
    '''

    z_header = ["z_rest_name", "z_city", "z_address"]
    f_header = ["f_rest_name", "f_city", "f_address"]
    
    zagat = pd.read_csv("zagat.csv", names = z_header )
    fodors = pd.read_csv("fodors.csv", names = f_header)
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

    match_pairs, possible_pairs, unmatch_pairs = find_all_matches(zagat, fodors, 
            match_tuples, possible_tuples, unmatch_tuples, block_on_city)

    grand_header = z_header + f_header
    all_matches = combine_indices(zagat, fodors, match_pairs, grand_header)
    all_unmatches = combine_indices(zagat, fodors, unmatch_pairs, grand_header)
    all_possibles = combine_indices(zagat, fodors, possible_pairs, grand_header)

    return all_matches, all_possibles, all_unmatches


def pair(known_links):
    '''
    Takes in a dataframe of known matches
    and generate a list of tuples containing 
    the matches.

    Input:
        known_links: pandas dataframe
    
    Returns: (lst) of tuples of indices for each match
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
    
    Returns: pandas dataframe
    '''

    header = ["z_rest_name", "z_city", "z_address", 
                "f_rest_name", "f_city", "f_address"]
    matches = combine_indices(df1, df2, pairs, header)

    return matches


def create_unmatches(df1, df2):
    '''
    Takes in two dataframes and generate 
    1000 pairs of restaurants that are (most likely) unmatches
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

    Inputs:
        df1
        df2
        indices: (lst) of indices from each df that we are merging
        header: (lst) of columns for new df

    Returns: (df) merged dataframe
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
    
    Returns: (dict) of indices and tuples of j-w distances
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


def assign_tuple(matched_tup, unmatched_tup, mu, lambda_):
    '''
    From a list of matched tuples and unmatched tuples,
    partition all possible tuples into match, unmatch, 
    possible according acceptable false pos and false
    neg rates.

    Inputs:
        match_tup: (lst) of tuples that occured in matches
        unmatch_tup: (lst) of tuples that occured in unmatches
        mu: (float) false pos threshhold
        lambda_: (float) flase neg threshhold

    Returns: (tuple) of sets of match, possible, and unmatch tuples
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

    match_counts = count_tuples(matched_tup)
    unmatch_counts = count_tuples(unmatched_tup)
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

    return match_tuples, possible_tuples, unmatch_tuples


def count_tuples(tuples_dict):
    '''
    Given a dict indices and tuples, count their number
    of times of appearance and store them into a dictionary

    Inpus:
        tups: (dict) of indices and tuple
    
    Returns: (dict) of counts
    '''

    tup_counts = {}
    tup_list = list(tuples_dict.values())
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
        m: (dict) relative frequency of a tuple in matches
        u: (dict) relative frequency of a tuple in unmatches
        remaining_tuples: (lst) all tuples (excluding m = u = 0)
    
    Returns: (lst) of sorted tuples in the order: u = 0 first, 
                then in decreasing m / u
    '''
    
    key = lambda x: -1 if u[x] == 0 else m[x] / u[x]
    remaining_tuples.sort(key = key)    

    first_nonzero = 0

    while u[remaining_tuples[first_nonzero]] == 0:
        first_nonzero += 1

    sorted_tuples = remaining_tuples[:first_nonzero
                    ] + remaining_tuples[first_nonzero:][::-1]

    return sorted_tuples


def generate_all_indices(df1, df2, block_on_city):
    '''
    Takes in two dataframes and generate a list
    of tuples of all possible combinations of
    their indices.

    Inputs:
        df1
        df2
    
    Returns: (lst) of tuples of possible indices
    '''

    size1 = df1.index.size
    size2 = df2.index.size

    if block_on_city:
        all_indices = []
        for x in range(0, size1):
            for y in range(0, size2):
                if df1.iloc[x,1] == df2.iloc[y,1]:
                    all_indices.append((x, y))
    else:
        all_indices = [(x, y) for x in range(0, size1) for y in range(0, size2)]

    return all_indices


def find_all_matches(df1, df2, match_tuples, possible_tuples, unmatch_tuples, block_on_city = False):
    '''
    Given two dataframes, determine whether each pair is a 
    match, unmatch, or possible match, and output
    three lists that contain the indices of pairs
    for each possibility

    Inputs:
        df1
        df2
        match_tuples: (set) tuples that are considered matches
        possible_tuples: (set) tuples that are considered possible matches
        unmatch_tuples: (set) tuples that are considered unmatches
        block_on_city: (bool)

    Returns: (tuple) of lists of indices that are matches, possibles, and unmatches
    '''

    match_pairs = []
    possible_pairs = []
    unmatch_pairs = []
    all_indices = generate_all_indices(df1, df2, block_on_city)
    all_tuples = generate_tuples(df1, df2, all_indices)

    for pair, tup in all_tuples.items():
        if tup in match_tuples:
            match_pairs.append(pair)
        elif tup in possible_tuples:
            possible_pairs.append(pair)
        else:
            unmatch_pairs.append(pair)

    return match_pairs, possible_pairs, unmatch_pairs


if __name__ == '__main__':
    matches, possibles, unmatches = \
        find_matches(0.005, 0.005, block_on_city=False)

    print("Found {} matches, {} possible matches, and {} "
          "unmatches with no blocking.".format(matches.shape[0],
                                               possibles.shape[0],
                                               unmatches.shape[0]))