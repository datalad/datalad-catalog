import json
import sys

"""A module with miscellaneous utility functions that are used across other modules
"""

def read_json_file(file_path):
    """
    Load content from catalog metadata file for current node
    """
    try:
        with open(file_path) as f:
            return json.load(f)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

def find_duplicate_object_in_list(list_to_search: list, new_obj: object, keys_to_match):
    """"""
    existing_objects = list_to_search
    for key in keys_to_match:
        existing_objects = [obj for obj in existing_objects if (
            key in new_obj) and (key in obj) and (
            obj[key] == new_obj[key])]
    
    if not bool(existing_objects):
        return None
    else:
        return existing_objects[0]