import hashlib
import json
from pathlib import Path
import sys
import shutil
import yaml

from datalad.support.exceptions import InsufficientArgumentsError

"""A module with miscellaneous utility functions that are used across other modules
"""


def copy_overwrite_path(src: Path, dest: Path, overwrite: bool = False):
    """
    Copy or overwrite a directory or file
    """
    isFile = src.is_file()
    if dest.exists() and not overwrite:
        pass
    else:
        if isFile:
            try:
                shutil.copy2(src, dest)
            except shutil.SameFileError:
                pass
        else:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)


def md5sum_from_id_version_path(dataset_id, dataset_version, path=None):
    """Helper to get md5 hash of concatenated input variables"""
    long_name = dataset_id + "-" + dataset_version
    if path:
        long_name = long_name + "-" + str(path)
    return md5hash(long_name)


def md5hash(txt):
    """
    Create md5 hash of the input string
    """
    txt_hash = hashlib.md5(txt.encode("utf-8")).hexdigest()
    return txt_hash


def load_config_file(file: Path):
    """Helper to load content from JSON or YAML file"""
    with open(file) as f:
        if file.suffix == ".json":
            return json.load(f)
        if file.suffix in [".yml", ".yaml"]:
            return yaml.safe_load(f)


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


def get_available_entrypoints(group, include_load_error: bool = False) -> dict:
    """Return all entrypoints of a specific group known to the current
    installation

    Parameters
    ----------
    include_load_error: bool
        Set to True if entry points with load errors should be included
        in the returned dictionary (default is False)

    Returns
    -------
    dict
        A dictionary of entry points with key being the name
    """
    ep_dict = get_entry_points(f"datalad.metadata.{group}")
    entrypoints = ep_dict
    # Include all entrypoints vs only those without load errors
    if include_load_error:
        entrypoints = {
            name: ep_dict[name]
            for name in ep_dict.keys()
            if ep_dict[name].get("load_error", None) is None
        }
    # Raise error if no translators found
    if not bool(entrypoints):
        raise EntryPointsNotFoundError(f"No {group} entrypoints were found")
    return entrypoints


class EntryPointsNotFoundError(InsufficientArgumentsError):
    pass


def dir_exists(location) -> bool:
    """
    Check if a directory exists at location
    """
    if not isinstance(location, Path):
        location = Path(location)
    if location.exists() and location.is_dir():
        return True
    return False


class jsEncoder(json.JSONEncoder):
    """Class to return objects as strings for correct JSON encoding"""

    def default(self, obj):
        if isinstance(obj, object):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def write_jsonline_to_file(filename, line):
    """Write a single JSON line to file"""
    with open(filename, "a") as f:
        json.dump(line, f, cls=jsEncoder)
        f.write("\n")
