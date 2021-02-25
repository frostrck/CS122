# CS122: Linking restaurant records in Zagat and Fodor's data sets
#
# Corry Ke


import numpy as np
import pandas as pd
import jellyfish
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
    return known


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

    header = ["z_rest_name", "z_city", "z_address", 
                "f_rest_name", "f_city", "f_address"]

    combine_indices(df1, df2, pairs, header)

    return matches


def create_unmatches(df1, df2):
    '''
    Takes in two dataframes and generate 
    1000 pairs of restaurants that are unmatches
    at random.
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


if __name__ == '__main__':

    header_list = ["rest_name", "city", "address"]
    zagat = pd.read_csv("zagat.csv", names = header_list)
    fodors = pd.read_csv("fodors.csv", names = header_list)
    known = pd.read_csv("known_links.csv", names = ["zagat", "fodors"])
    zs = zagat.sample(1000, replace = True, random_state = 1234)
    fs = fodors.sample(1000, replace = True, random_state = 5678)

    matches = pair(known)

    print(create_unmatches(zagat, fodors))




    # matches, possibles, unmatches = \
    #     find_matches(0.005, 0.005, block_on_city=False)

    # print("Found {} matches, {} possible matches, and {} "
    #       "unmatches with no blocking.".format(matches.shape[0],
    #                                            possibles.shape[0],
    #                                            unmatches.shape[0]))
