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


def get_entry_points(group: str) -> dict:
    """Return all entrypoints of a specific group known to the current installation

    Parameters
    ----------
    group : str
        A string representing the group for which entrypoints will be listed

    Returns
    -------
    entry_points : dict
        A dictionary of entry points
    """
    from datalad.support.entrypoints import iter_entrypoints
    from datalad.support.exceptions import CapturedException
    from importlib import import_module

    if sys.version_info < (3, 10):
        # 3.10 is when it was no longer provisional
        from importlib_metadata import distribution
    else:
        from importlib.metadata import distribution
    entry_points = {}
    for ename, emod, eload in iter_entrypoints(group):
        info = {}
        entry_points[f"{ename}"] = info
        try:
            info["module"] = emod
            dist = distribution(emod.split(".", maxsplit=1)[0])
            info["distribution"] = f"{dist.name} {dist.version}"
            mod = import_module(emod, package="datalad")
            version = getattr(mod, "__version__", None)
            if version:
                # no not clutter the report with no version
                info["version"] = version
            info["loader"] = eload
            eload()
            info["load_error"] = None
        except Exception as e:
            ce = CapturedException(e)
            info["load_error"] = ce.format_short()
            continue

    return entry_points
