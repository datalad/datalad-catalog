"""
Generate web-browser-based user interface for browsing metadata of a DataLad
dataset.

INPUTS:
  - array of json objects? OR url of datalad dataset? (latter implies that `datalad meta-dump` will be 1st required step)
  - dictionary / schema of fields to search for
  - dictionary / schema of fields to map to 
STEP 1:
Load JSON data
STEP 2:
Loop through all objects, map to correct fields, create json blobs:
  - identify type: dataset / file
  - identify superdataset ("type" dataset, no "root_dataset_id" field)
  - should we map data based on extractor used, i.e. should we depend on the
    definitions of metalad extractors? probably not. but we should search for
    specific keys/fields, meaning we should know they are there, somehow...
  - investigate path, dataset_path, etc to establish directory tree to current
    entity
  - ...
STEP 3:
Create html, js, css from templates.
STEP 4:
Create new repo with

Example:
 > webui_generate.py -o <path-to-output-directory> <path-to-input-file>
"""

#--------
# Imports
#--------
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass
from pathlib import Path
import json
import logging
import os
import hashlib

#----------------
# Parse arguments
#----------------
argument_parser = ArgumentParser(
    description="Parse arguments for webui_generate")

argument_parser.add_argument(
    "-o", "--outputdir",
    type=str,
    help="Directory to which outputs are written")

argument_parser.add_argument(
    "file_path",
    type=str,
    help="The '.json' file containing all metadata from which the web UI will\
    be generated. List of objects wrapped in single object with single key: 'all'")

arguments: Namespace = argument_parser.parse_args(sys.argv[1:])
print(arguments, file=sys.stderr)

#-----------------
# Helper functions
#-----------------
def md5blob(identifier='', version=''):
    """
    Create md5sum of an identifier and version number, to serve as a
    filename for a json blob
    """
    blob_string = identifier + "-" + version
    blob_hash = hashlib.md5(blob_string.encode('utf-8')).hexdigest()
    return blob_hash

# if __name__ == "__main__":
#     import sys
#     fib(int(sys.argv[1]))

#-------------------
# Data prep and load
#-------------------
# Create output directory if it does not exist
if arguments.outputdir is True:
    out_dir = arguments.outputdir
else:
    out_dir = os.path.join(os.getcwd(), 'web')
Path(out_dir).mkdir(parents=True, exist_ok=True)
# Load data from input file
# Assume for now that the data were exported by using `datalad meta-dump`, and that all exported objects were added to an array in a json file
try:
    with open(arguments.file_path) as f:
        metadata = json.load(f)
except:
    print("Exception occurred: ", sys.exc_info()[0])

#-----------
# Data parse
#-----------
std_fields = ["type", "root_dataset_id", "root_dataset_version", "dataset_path", "dataset_id", "dataset_version", 'extraction_time']
datasets = [item for item in metadata if item["type"] == "dataset"]
for i, ds in enumerate(datasets):
    new_obj = {}
    # Standard fields
    for field in std_fields:
        if field in ds:
            new_obj[field] = ds[field]
    # Subdatasets
    subdatasets = [item for item in datasets if "root_dataset_id" in item and item["root_dataset_id"] == ds["dataset_id"] and item["root_dataset_version"] == ds["dataset_version"]]
    new_obj["subdatasets"] = []
    for subds in subdatasets:
        new_sub_obj = {}
        new_sub_obj["dataset_id"] = subds["dataset_id"]
        new_sub_obj["dataset_version"] = subds["dataset_version"]
        new_sub_obj["dataset_path"] = subds["dataset_path"]
        new_obj["subdatasets"].append(new_sub_obj)
    # Files
    # Superdatasets
    blob_hash = md5blob(ds["dataset_id"], ds["dataset_version"])
    blob_file = os.path.join(out_dir, blob_hash + ".json")
    with open(blob_file, 'w') as fp:
        json.dump(new_obj, fp)


# # Single use case: get a specific dataset and all its subdatasets, create json blob from this data, with filename an md5sum of dataset id and version.
# subds1 = [item for item in metadata if item["dataset_id"] == "5b1081d6-84d7-11e8-b00a-a0369fb55db0" and item["type"] == "dataset"]
# print(len(datasets))
# print(len(subds1))
# some_obj = subds1[1]
# blob_hash = md5blob(some_obj["dataset_id"], some_obj["dataset_version"])
# blob = os.path.join(out_dir, blob_hash + ".json")
# with open(blob, 'w') as fp:
#     json.dump(some_obj, fp)





### ----------------

# TODOS:
# TODO: figure out logging
# TODO: figure out installation / building process
# TODO: figure out automated updates to serving content somewhere
# TODO: figure out CI
# TODO: check for duplicate dataset objects (these exist due to multiple datalad extractors generating multiple metadata objects)
# TODO: populate file structure ("children" field) in dataset blob...
#       need to figure out how to work with directories
