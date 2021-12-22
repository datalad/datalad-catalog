import json
import sys

# A module with miscellaneous functions that are used across other modules

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