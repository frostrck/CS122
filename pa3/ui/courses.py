### CS122, Winter 2021: Course search engine: search
###
### Your name(s)

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
      - terms a string: "quantum plato"]

    Returns a pair: list of attribute names in order and a list
    containing query results.
    '''

    select = ["courses.dept", "courses.course_num"]
    relations = ["courses"]
    where = []
    columns = ["dept", "day", "time_start", "time_end", "walking_time", 
            "enroll_lower", "enroll_upper", "building", "terms"]
    args = [] 
    on = []

    for col in columns:
        if col in args_from_ui:
            if col == "dept" or col == "terms":
                if "course_title" not in select:
                    select.append("courses.title") 
                if col == "dept":
                    where.append("courses.dept = ?")
                else:
                    where.append("courses.terms = ?")
                args.append(args_from_ui[col])
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

            # elif col == "walking_time" or col == "building":
            #     relations.add("gps") 
            #     relations.add("meeting_patterns") 
            #     relations.add("sections") 

            #     select.extend(["walking_time", "building"]])
            #     if col == "walking_time":
            #         where.append("")
            #     else:
            #         where.append("gps.building_code")
            
            elif col == "enroll_lower" or col == "enroll_upper": 
                if col == "enroll_lower":
                    where.append("sections.enrollment >= ?")
                else:
                    where.append("sections.enrollment <= ?")
                args.append(args_from_ui[col])
    
    
    query = ("SELECT " + ", ".join(select) +
            " FROM " + " JOIN ".join(relations) +
            " ON " + " AND ".join(on) +
            " WHERE " + " AND ".join(where))

    db = sqlite3.connect(DATABASE_FILENAME)
    c = db.cursor()
    #c.execute(query, *args)

    print(args)
    return ([], [])

def build_relations(relations, where):
    '''
    '''
    relations = set("courses")





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

EXAMPLE_1 = {"dept": "CMSC",
             "day": ["MWF", "TR"],
             "time_start": 1030,
             "time_end": 1500,
             "enroll_lower": 20,
             "terms": "computer science"}

if __name__ == "__main__":
    find_courses(EXAMPLE_0)
    find_courses(EXAMPLE_1)
