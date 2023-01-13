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


def find_duplicate_object_in_list(
    list_to_search: list, new_obj: object, keys_to_match
):
    """"""
    existing_objects = list_to_search
    for key in keys_to_match:
        existing_objects = [
            obj
            for obj in existing_objects
            if (key in new_obj) and (key in obj) and (obj[key] == new_obj[key])
        ]

    if not bool(existing_objects):
        return None
    else:
        return existing_objects[0]


def merge_lists(existing_value, new_value):
    """Merges two lists

    Merges two lists of which the element types are determined
    locally and which are handled accordingly
    """
    # Return new_value if existing_value is None
    if existing_value is None:
        if not isinstance(new_value, list):
            return [new_value]
        return new_value
    # Return existing_value if new_value is None
    if new_value is None:
        if not isinstance(existing_value, list):
            return [existing_value]
        return existing_value
    # Ensure values are lists
    if not isinstance(existing_value, list):
        existing_value = [existing_value]
    if not isinstance(new_value, list):
        new_value = [new_value]
    # Then determine type of variable in list and handle accordingly
    if isinstance(new_value[0], (str, int)):
        return list(set(existing_value + new_value))
    if isinstance(new_value[0], object):
        for new_object in new_value:
            existing_object = find_duplicate_object_in_list(
                existing_value, new_object, new_object.keys()
            )
            if existing_object is None:
                existing_value.append(new_object)
            else:
                continue
        return existing_value
