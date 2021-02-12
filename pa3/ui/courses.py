### CS122, Winter 2021: Course search engine: search
###
### Your name(s)

from math import radians, cos, sin, asin, sqrt
import sqlite3
import os


# Use this filename for the database
DATA_DIR = os.path.dirname(__file__)
DATABASE_FILENAME = os.path.join(DATA_DIR, 'course-info.db')

columns = ["dept", "day", "time_start", "time_end", "building", "walking_time", 
            "enroll_lower", "enroll_upper", "terms"]


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

    select = ["courses.dept", "courses.course_num"]
    relations = ["courses"]
    where = []
    args = [] 
    on = []

    for col in columns:
        if col in args_from_ui:
            if col == "dept" or col == "terms":
                if "course_title" not in select:
                    select.append("courses.title") 
                if col == "dept":
                    where.append("courses.dept = ?")
                    args.append(args_from_ui[col])
                else:
                    
                    relations.append(build_term_query(args, args_from_ui[col], where, on))
                continue

            if "meeting_patterns" not in relations:
                relations.append("meeting_patterns") 
                relations.append("sections")
                on.append("courses.course_id = sections.course_id")
                on.append("sections.meeting_pattern_id = meeting_patterns.meeting_pattern_id")

            if "sections.section_num" not in select:
                select.extend(["sections.section_num", "meeting_patterns.day", 
                            "meeting_patterns.time_start", "meeting_patterns.time_end"])

            if col == "day" or col == "time_start" or col == "time_end": 
                if col == "day":
                    days = []
                    for day in args_from_ui[col]:
                        days.append("meeting_patterns.day = ?")
                        args.append(day)
                    where.append(" AND ".join(days))
                    continue
                elif col == "time_start":
                    where.append("meeting_patterns.time_start >= ?")
                else:
                    where.append("meeting_patterns.time_end <= ?")
                args.append(args_from_ui[col])

            elif col == "building":
                db.create_function("time_between", 4, compute_time_between)
                building = args_from_ui["building"]
                time = args_from_ui["walking_time"]
                relations.append(build_distance_query(time, building, select, where, args, on))
            
            elif col == "enroll_lower" or col == "enroll_upper":
                select.append("sections.enrollment")
                if col == "enroll_lower":
                    where.append("sections.enrollment >= ?")
                else:
                    where.append("sections.enrollment <= ?")
                args.append(args_from_ui[col])
            
    
    query = ("SELECT " + ", ".join(select) +
            " FROM " + " JOIN ".join(relations) +
            " ON " + " AND ".join(on) +
            " WHERE " + " AND ".join(where) + 
            " COLLATE NOCASE")
    r = c.execute(query, args)
    result = r.fetchall()
    db.close()
    butts = get_header(c)
    if len(result) == 0:
        butts = []
    return (butts, result)

def build_distance_query(time, building, select, where, args, on):
    # SELECT a.building_code, b.building_code, time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time
    # FROM gps AS a JOIN gps AS b
    # WHERE a.building_code < b.building_code
    on.append("sections.building_code = a.building_code")
    select.extend(["a.building_code", "time_between(a.lon, a.lat, b.lon, b.lat) AS walking_time"])
    where.append("walking_time <= ?")
    where.append("b.building_code=?")
    args.append(time)
    args.append(building)
    return "(gps AS a JOIN gps AS b)"
    


def build_term_query(args, s, where, on):
    # select * from courses join (catalog_index join catalog_index c2 join catalog_index c3 on catalog_index.course_id=c2.course_id and catalog_index.course_id=c3.course_id
    # and (catalog_index.word="computer" and c2.word="science" and c3.word="bio")) on courses.course_id=catalog_index.course_id where courses.dept="CMSC";
    on.append("courses.course_id = catalog_index.course_id")
    words = s.split()
    base_relation = "catalog_index"
    if len(words) > 1:
        args.insert(0, words[0])
        words = words[1:]
        relations = [base_relation]
        on = []
        terms = ["catalog_index.word=?"]
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
        where.append("catalog_index.word=?")
        return base_relation


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

EXAMPLE_0 = {"time_start": 930,
             "time_end": 1500,
             "day": ["MWF"]}

DAD = {
  "terms": "mathematics",
  "day": ["MWF"],
  "building": "RY",
  "walking_time":0,
  "enroll_lower": 20
}

EXAMPLE_1 = {"dept": "CMSC",
             "day": ["MWF", "TR"],
             "time_start": 1030,
             "time_end": 1500,
             "enroll_lower": 20,
             "terms": "computer science"}

if __name__ == "__main__":
    print(find_courses(DAD))
    # find_courses(EXAMPLE_1)
