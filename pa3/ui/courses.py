### CS122, Winter 2021: Course search engine: search
###
### Corry Ke

from math import radians, cos, sin, asin, sqrt
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')


def find_courses(args_from_ui):
    '''
    Takes a dictionary containing search criteria and returns courses
    that match the criteria.  The dictionary will contain some of the
    following fields:

      - dept a string
      - day a list with variable number of elements
           -> ["'MWF'", "'TR'", etc.]
      - time_start an integer in the range 0-2359
      - time_end an integer in the range 0-2359
      - walking_time an integer
      - enroll_lower an integer
      - enroll_upper an integer
      - building a string
      - terms a string: "quantum plato"

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''

    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()

    columns = ["dept", "day", "time_start", "time_end", "building", "walking_time", 
                "enroll_lower", "enroll_upper", "terms"]
    select = ["courses.dept", "courses.course_num"]
    relations = ["courses"]
    where = []
    args = [] 
    on = []

    for col in columns:
        if col in args_from_ui:
            value = args_from_ui[col]
            if col == "dept" or col == "terms":
                process_dept_terms(col, value, on, select, where, args, relations)
                continue

            if "meeting_patterns" not in relations:
                process_relations(relations, on)

            if "sections.section_num" not in select:
                select.extend(["sections.section_num", "meeting_patterns.day", 
                            "meeting_patterns.time_start", "meeting_patterns.time_end"])

            if col == "day" or col == "time_start" or col == "time_end": 
                if col == "day":
                    process_day(col, value, args, where)
                    continue
                process_time(col, value, where)
                args.append(value)

            elif col == "building":
                db.create_function("time_between", 4, compute_time_between)
                building = args_from_ui["building"]
                time = args_from_ui["walking_time"]
                build_distance_query(time, value, select, where, args, on)
                relations.append("(gps AS a JOIN gps AS b)")
            
            elif col == "enroll_lower" or col == "enroll_upper":
                process_enroll(col, value, args, select, where)
    
    query = construct_query(select, relations, on, where)

    r = c.execute(query, args)
    result = r.fetchall()
    db.close()
    header = get_header(c)

    if len(result) == 0:
        header = []

    return(header, result)


def process_dept_terms(col, value, on, select, where, args, relations):
    '''
    Appends clauses to relevant lists for query if "dept" 
    or "terms" are present in the dictionary

    Inputs:
        col: (str) the key ("dept" or "terms)
        value: (str) the value of associated key
        on: (lst) elements for the ON clause of the query
        select: (lst) elements for the SELECT clause of the query
        where: (lst) elements for the WHERE clause of the query
        args: (lst) variables used when constructing the query
        relations: (lst) elements for the JOIN clause of the query
    
    Returns:
        None
    '''

    if "courses.title" not in select:
        select.append("courses.title") 

    if col == "dept":
        where.append("courses.dept = ?")
        args.append(value)
    else:
        on.append("courses.course_id = catalog_index.course_id")
        relations.append(build_terms_query(args, value, where, on))


def build_terms_query(args, s, where, on):
    '''
    A helper function that builds the components
    for the query if the key "terms" is present in
    the input dictionary

    Inputs:
        args: (lst) variables used when constructing the query
        s: (str) the string of terms
        where: (lst) elements for the WHERE clause of the query
        on: (lst) elements for the ON clause of the query

    Returns:
        None
    '''

    words = s.split()
    base_relation = "catalog_index"

    if len(words) > 1:
        args.insert(0, words[0])
        words = words[1:]
        relations = [base_relation]
        on = []
        terms = ["catalog_index.word = ?"]
        counter = 0

        for word in words: 
            alias = "c" + str(counter)
            relation_alias = base_relation + " " + alias
            relations.append(relation_alias)
            on.append("catalog_index.course_id = " + alias + ".course_id")
            terms.append(alias+".word=?")
            args.insert(0, word)
            counter += 1

        query = "(" + " JOIN ".join(relations) + " ON " + " AND ".join(on) + " AND (" + " AND ".join(terms) + "))"
        return query

    else:
        args.append(words[0])
        where.append("catalog_index.word = ?")
        return base_relation


def process_day(col, value, args, where):
    '''
    Process the clause lists if the dict key is 
    “day".

    Inputs:
        col: (str) dict key "day"
        value: (list) value associated with the key "day"
        args: (lst) variables used when constructing the query
        where: (lst) elements for the WHERE clause of the query

    Returns:
        None
    '''

    if len(value) == 1:
        args.append(value[0])
        where.append("meeting_patterns.day = ?")

    else:
        days = tuple(value)
        terms = "( ?"
        args.append(value[0])
        for val in value[1:]:
            terms = terms + ", ?"
            args.append(val)
        where.append("meeting_patterns.day IN " +  terms + ")")


def process_time(col, value, where):
    '''
    Processes the necessary lists if the dict key is 
    "time_start" or "time_end"

    Inputs:
        col: (str) the dictionary key
        value: (int) the start/end time
        where: (lst) the list for WHERE clause
    
    Returns:
        None
    '''

    if col == "time_start":
        where.append("meeting_patterns.time_start >= ?")
    else:
        where.append("meeting_patterns.time_end <= ?")


def process_relations(relations, on):
    '''
    Takes in a "join" and "on" clauses lists and appends necessary
    tables and IDs beyond keys beyond "terms" and "dept" is present
    in args_from_ui

    Input:
        relations: list that will be used in the JOIN clause
        on: list that will be used in the ON clause
    
    Returns: 
        None
    '''

    relations.append("meeting_patterns") 
    relations.append("sections")
    on.append("courses.course_id = sections.course_id")
    on.append("sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id")


def process_enroll(col, value, args, select, where):
    '''
    Processes the necessary lists if the dict key is 
    "enroll_lower" or "enroll_upper"

    Inputs:
        col: (str) the key of the form "enroll____"
        value: (int) value associated with enroll
        args: (lst) variables used when constructing the query
        select: (lst) elements for the SELECT clause of the query
        where: (lst) elements for the WHERE clause of the query

    Returns
        None
    '''

    select.append("sections.enrollment")
    if col == "enroll_lower":
        where.append("sections.enrollment >= ?")
    else:
        where.append("sections.enrollment <= ?")
    args.append(value)


def construct_query(select, relations, on, where):
    '''
    Constructs the final query for execution

    Inputs:
        select: (lst) elements for the SELECT clause of the query
        where: (lst) elements for the WHERE clause of the query
        relations: (lst) elements for the JOIN clause of the query
        on: (lst) elements for the ON clause of the query

    Returns:
        query: (str) the string of SQL query
    '''

    if where == [] or on == []:
        if where == []:
            query = ("SELECT " + ", ".join(select) +
                    " FROM " + " JOIN ".join(relations) +
                    " ON " + " AND ".join(on) +
                    " COLLATE NOCASE")
            
        if on == []:
            query = ("SELECT " + ", ".join(select) +
                " FROM " + " JOIN ".join(relations) +
                " WHERE " + " AND ".join(where) + 
                " COLLATE NOCASE")

    else:
        query = ("SELECT " + ", ".join(select) +
            " FROM " + " JOIN ".join(relations) +
            " ON " + " AND ".join(on) +
            " WHERE " + " AND ".join(where) + 
            " COLLATE NOCASE")

    return query


def build_distance_query(time, building, select, where, args, on):
    '''
    Constructs a query that checks the walking time/distance
    between buildings.

    Inputs:
        time: (str) the acceptable time of walking between two buildings
        building: (str) the building of origin
        select: (lst) elements for the SELECT clause of the query
        where: (lst) elements for the WHERE clause of the query
        on: (lst) elements for the ON clause of the query
        args: (lst) variables used when constructing the query

    Returns:
        None
    '''

    on.append("sections.building_code = a.building_code")
    select.extend(["a.building_code", "time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time"])
    where.append("walking_time <= ?")
    where.append("b.building_code = ?")
    args.append(time)
    args.append(building)




########### auxiliary functions #################
########### do not change this code ############

def compute_time_between(lon1, lat1, lon2, lat2):
    '''
    Converts the output of the haversine formula to walking time in minutes
    '''
    meters = haversine(lon1, lat1, lon2, lat2)

    # adjusted downwards to account for manhattan distance
    walk_speed_m_per_sec = 1.1
    mins = meters / (walk_speed_m_per_sec * 60)

    return mins


def haversine(lon1, lat1, lon2, lat2):
    '''
    Calculate the circle distance between two points
    on the earth (specified in decimal degrees)
    '''
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    # 6367 km is the radius of the Earth
    km = 6367 * c
    m = km * 1000
    return m


def get_header(cursor):
    '''
    Given a cursor object, returns the appropriate header (column names)
    '''
    desc = cursor.description
    header = ()

    for i in desc:
        header = header + (clean_header(i[0]),)

    return list(header)


def clean_header(s):
    '''
    Removes table name from header
    '''
    for i, _ in enumerate(s):
        if s[i] == ".":
            s = s[i + 1:]
            break

    return s


########### some sample inputs #################


EXAMPLE_0 = {"terms": "computer science"}

EXAMPLE_2 = {"day": ["M", "T"], "building": "RY", "walking_time": 10}

EXAMPLE_1 = {"dept": "math",
             "terms" : "differential calculus"}

EXAMPLE_3 = {
            "terms": "science mathematics economics",
            "day": ["MWF"],
            "building": "RY",
            "walking_time": 1
            }

EXAMPLE_4 = {"dept": "math"}

