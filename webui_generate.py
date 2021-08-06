"""
Generate web-browser-based user interface for browsing metadata of a DataLad
dataset.

INPUTS:
  - '.json' file with an array of json objects
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
from functools import reduce
import operator

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
    Create md5sum of an identifier and version number (joined by a dash), to
    serve as a filename for a json blob.
    """
    blob_string = identifier + "-" + version
    blob_hash = hashlib.md5(blob_string.encode('utf-8')).hexdigest()
    return blob_hash

def load_json_file(filename):
    """
    """
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        print("Exception occurred: ", sys.exc_info()[0])


def core_extractor(src_object, dest_object):
    """
    """

def core_dataset_extractor(src_object, dest_object):
    """
    """
    # Load schema/template dictionary, where each key represents the exact
    # same key in the destination object, and each associated value
    # represents the key in the source object which value is to be copied.
    schema = load_json_file(os.path.join("templates", "core_dataset_schema.json"))
    # Copy source to destination values, per key
    for key in schema:
        dest_object[key] = src_object[schema[key]]
    
    return dest_object


def studyminimeta_extractor(src_object, dest_object):
    """
    Extracts fields from a JSON object resulting from `metalad_studyminimeta`-
    based extraction of metadata from a datalad dataset. The extracted fields
    are mapped to a JSON object required for UI rendering in the data browser
    frontend.
    """
    # Load schema/template dictionary, where each key represents the exact
    # same key in the destination object, and each associated value
    # represents the key in the source object which value is to be copied.

    #TODO: request to add fields to studyminimeta in metalad:
    # - license, DOI
    
    schema = load_json_file(os.path.join("templates", "studyminimeta_schema.json"))    
    metadata = {}
    # Extract core objects/lists from src_object
    metadata["dataset"] = next((item for item in src_object["extracted_metadata"]["@graph"] if "@type" in item and item["@type"] == "Dataset"), False)
    if not metadata["dataset"]:
        print("Error: object where '@type' equals 'Dataset' not found in src_object['extracted_metadata']['@graph'] during studyminimeta extraction")

    metadata["publicationList"] = next((item for item in src_object["extracted_metadata"]["@graph"] if "@id" in item and item["@id"] == "#publicationList"), False)
    if not metadata["publicationList"]:
        print("Error: object where '@id' equals '#publicationList' not found in src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    else:
        metadata["publicationList"] = metadata["publicationList"]["@list"]
    
    metadata["personList"] = next((item for item in src_object["extracted_metadata"]["@graph"] if "@id" in item and item["@id"] == "#personList"), False)
    if not metadata["personList"]:
        print("Error: object where '@id' equals '#personList' not found in src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    else:
        metadata["personList"] = metadata["personList"]["@list"]

    # Standard/straightforward fields: copy source to destination values, per key
    for key in schema:
        if isinstance(schema[key]) and len(schema[key])==2:
            dest_object[key] = metadata[schema[key][0]][schema[key][1]]
        else:
            dest_object[key] = schema[key]
    
    # Authors
    for author in metadata["dataset"]["author"]:
        author_details = next((item for item in metadata["personList"] if item["@id"] == author["@id"]), False)
        if not author_details:
            print(f"Error: Person details not found in '#personList' for @id = {author["@id"]}")
        else:
            dest_object["authors"].append(author_details)   

    # Publications
    for pub in metadata["publicationList"]:
        new_pub = {"type" if k == "@type" else k:v for k,v in pub.items()}
        new_pub = {"doi" if k == "sameAs" else k:v for k,v in new_pub.items()}
        new_pub["publication"] = {"type" if k == "@type" else k:v for k,v in new_pub.items()}
        new_pub.pop("@id") if "@id" in new_pub
        new_pub["publication"].pop("@id") if "@id" in new_pub["publication"]
        for i, author in enumerate(new_pub["author"]):
            author_details = next((item for item in metadata["personList"] if item["@id"] == author["@id"]), False)
            if not author_details:
                print(f"Error: Person details not found in '#personList' for @id = {author["@id"]}")
            else:
                new_pub["author"][i] = author_details
        dest_object["publications"].append(author_details)
    
    return dest_object

# https://stackoverflow.com/questions/14692690/access-nested-dictionary-items-via-a-list-of-keys
def get_by_path(root, items):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, items, root)

def set_by_path(root, items, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(root, items[:-1])[items[-1]] = value

def del_by_path(root, items):
    """Delete a key-value in a nested object in root by item sequence."""
    del get_by_path(root, items[:-1])[items[-1]]

# if __name__ == "__main__":
#     import sys
#     fib(int(sys.argv[1]))

#-------------------
# Prep and load data
#-------------------
# Create output directory if it does not exist
if arguments.outputdir is True:
    out_dir = arguments.outputdir
else:
    repo_path = os.path.realpath(__file__)
    out_dir = os.path.join(repo_path, '_build')

metadata_out_dir = os.path.join(out_dir, 'metadata')
datasets_out_dir = os.path.join(out_dir, 'datasets')
assets_out_dir = os.path.join(out_dir, 'assets')
Path(out_dir).mkdir(parents=True, exist_ok=True)
Path(metadata_out_dir).mkdir(parents=True, exist_ok=True)
Path(datasets_out_dir).mkdir(parents=True, exist_ok=True)

# Load data from input file
# (assume for now that the data were exported by using `datalad meta-dump`,
# and that all exported objects were added to an array in a json file)
metadata = load_json_file(arguments.file_path)

#-----------
# Parse data
#-----------
EXTRACTORS = {
    # "metalad_core": "core_extractor", 
    "metalad_core_dataset": "core_dataset_extractor",
    "metalad_studyminimeta": "studyminimeta_extractor"
}
# LOGIC:
# 1. Find all objects with type dataset
# 2. For each dataset:
#   - Find md5sum of id and version.
#   - Check if associated file/object has already been created. If yes, load object from file. If not, create empty object.
#   - Populate key-value pairs based on extractor type (metalad_core, metalad_core_dataset, metalad_studyminimeta)
#   - Add extra key-value pairs required for UI, but not contained in any extractors or not available in required format
#   - Find all subdatasets for current dataset. For each subdataset:
#       = 
datasets = [item for item in metadata if item["type"] == "dataset"]
for i, dataset in enumerate(datasets):
    # First check if file for object has already been created. If yes, load object from file. If not, create empty object.
    blob_hash = md5blob(dataset["dataset_id"], dataset["dataset_version"])
    blob_file = os.path.join(out_dir, blob_hash + ".json")
    if os.path.isfile(blob_file):
        new_obj = load_json_file(blob_file)
    else:
        new_obj = {}
        first_run = True

    # Populate key-value pairs based on extractor type
    if "extractor_name" in dataset:
        new_obj = EXTRACTORS[dataset["extractor_name"]](dataset, new_obj)
    else:
        # TODO: handle scenarios where metadata is not generated by DataLad (or decide not to allow this)
        print("Unrecognized metadata type: non-DataLad)
    
    # Add fields required for UI, but not contained (or not available in required format) in any extractors
    # fields_to_add = ["", "short_name"]
    if "name" in new_obj and "short_name" not in new_obj:
        if len(new_obj["name"])>30:
            new_obj["short_name"] = new_obj["name"][0,30]+'...'
        else:
            new_obj["short_name"] = new_obj["name"]

    # Subdatasets per dataset
    # TODO: check if the subdatasets already exist and decide whether to overwrite or skip. Currently overwritten
    new_obj["children"] = [] if "children" not in new_obj
    subdatasets = [item for item in datasets if "root_dataset_id" in item and item["root_dataset_id"] == dataset["dataset_id"] and item["root_dataset_version"] == dataset["dataset_version"]]
    new_obj["subdatasets"] = []
    for subds in subdatasets:
        new_sub_obj = {}
        new_sub_obj["dataset_id"] = subds["dataset_id"]
        new_sub_obj["dataset_version"] = subds["dataset_version"]
        new_sub_obj["dataset_path"] = subds["dataset_path"]
        new_sub_obj["dirs_from_path"] = subds["dataset_path"].split("/")
        new_obj["subdatasets"].append(new_sub_obj)       
        new_sub_obj["dirs_from_path"]



        dir_obj = {
            "type": "directory"
            "name": ""
            "children": []
        }
        file_obj = {
            "type": "file"
            "name": ""
        }
        ds_obj = {
            "type": "dataset"
            "name": ""
            "dataset_id": ""
            "dataset_version": ""
        }
        new_obj["children"].append
        
        nr_nodes = len(new_sub_obj["dirs_from_path"])
        nodes_list = []
        for n, node in enumerate(new_sub_obj["dirs_from_path"]):
            nodes_list.append(node)
            if n != nr_nodes-1:
                # this is a directory
                nr_nodes

            else:
                # last element, this is a subdataset

            setInDict(dataDict, ["b", "v", "w"], 4)

            # node_exists = next((item for item in metadata["personList"] if item["@id"] == author["@id"]), False)


            


    
    # Files /  Children
    # TODO: figure out if we should create a single json file per dataset file, or if all files are to be listed as children in a nested directory structure as a field in the main dataset object
    # OR a mixture of these. Also figure out how to limit the nested-ness within a single object, only render children up to a max amount in the UI, at which point a pointer should identify which
    # file is to be loaded via HTTP request if the rest of the information is to be rendered.
    # Take into account that a file does not have an id and version, so naming of separate blobs per file would likely be something like md5sum(parent_dataset_id-parent_dataset_version-file_path_relative_to_parent)
    files = [item for item in metadata if item["type"] == "file" and item["dataset_id"] == dataset["dataset_id"] and item["dataset_version"] == dataset["dataset_version"]]



    # Superdatasets
    # 



    # Write object to file
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
