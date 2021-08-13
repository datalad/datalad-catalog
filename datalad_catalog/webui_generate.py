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
import shutil

#----------------
# Main functionality
#----------------
def run_cmd():
    """
    Calls datalad_catalog() with command line arguments
    """
    # Parse arguments
    argument_parser = ArgumentParser(
        description=__doc__)
    argument_parser.add_argument(
        "-o", "--outputdir",
        type=str,
        help="Directory to which outputs are written. Default = '_build'")
    argument_parser.add_argument(
        "file_path",
        type=str,
        help="The '.json' file containing all metadata (in the form of an\
        array of JSON objects) from which the user interface will be\
        generated.")
    arguments: Namespace = argument_parser.parse_args(sys.argv[1:])
    print(arguments, file=sys.stderr)
    # Set parameters for datalad_catalog()
    metadata_file = arguments.file_path
    script_path = os.path.realpath(__file__)
    sep = os.path.sep
    repo_path = sep.join(script_path.split(sep)[0:-2])
    package_path = sep.join(script_path.split(sep)[0:-1])
    if arguments.outputdir is True:
        out_dir = arguments.outputdir
    else:
        out_dir = os.path.join(repo_path, '_build')
    # Call main function to generate UI
    datalad_catalog(metadata_file, out_dir, repo_path, package_path)

def datalad_catalog(metadata_file, out_dir, repo_path, package_path):
    """
    Generate web-browser-based user interface for browsing metadata of a
    DataLad dataset.

    WORKFLOW:
    Step 1:
    Load JSON data
    Step 2:
    Loop through all metadata objects, map to correct fields, create json
    blob per dataset, containing all data relevant to that dataset,
    including links to children and parent.
    Step 3:
    From above, create a single json file with an array of superdatasets
    Step 4:
    Create/copy html, js, css from templates.
    ...

    EXAMPLE USAGE:
    > datalad-catalog -o <path-to-output-directory> <path-to-input-file>
    """
    #-------------------
    # Prep and load data
    #-------------------
    # Create output directories if they do not exist
    assets_path = os.path.join(package_path, 'assets')
    artwork_path = os.path.join(repo_path, 'artwork')
    metadata_out_dir = os.path.join(out_dir, 'metadata')
    assets_out_dir = os.path.join(out_dir, 'assets')
    artwork_out_dir = os.path.join(out_dir, 'artwork')
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    Path(metadata_out_dir).mkdir(parents=True, exist_ok=True)
    Path(assets_out_dir).mkdir(parents=True, exist_ok=True)
    Path(artwork_out_dir).mkdir(parents=True, exist_ok=True)
    # Load data from input file
    # (assume for now that the data were exported by using `datalad meta-dump`,
    # and that all exported objects were added to an array in a json file)
    metadata = load_json_file(metadata_file)
    #-----------------------------------------------
    # Parse and translate metadata, generate outputs
    #-----------------------------------------------
    # LOGIC:
    # 1. Find all objects with type dataset
    # 2. For each dataset:
    #   - Find md5sum of id and version.
    #   - Check if associated file/object has already been created. If yes, load object from file. If not, create empty object.
    #   - Populate key-value pairs based on extractor type (metalad_core, metalad_core_dataset, metalad_studyminimeta)
    #   - Add extra key-value pairs required for UI, but not contained in any extractors or not available in required format
    #   - Find all subdatasets for current dataset. For each subdataset, create an object and:
    #       + add standard dataset fields (id, version, etc)
    #       + add subdataset and path/directory details to the 'children' array of the parent dataset
    #   - Find all files for current dataset. For each file:
    #       + add file and path/directory details to the 'children' array of the parent dataset
    #   - ... WIP
    super_datasets = []
    super_dataset_keys = ["type", "dataset_id", "dataset_version", "extraction_time", "short_name", "name", "description", "doi", "url", "license", "authors", "keywords"]
    datasets = [item for item in metadata if item["type"] == "dataset"]
    for dataset in datasets:
        # First check if file for object has already been created. If yes, load object from file. If not, create empty object.
        blob_hash = md5blob(dataset["dataset_id"], dataset["dataset_version"])
        blob_file = os.path.join(metadata_out_dir, blob_hash + ".json")
        if os.path.isfile(blob_file):
            new_obj = load_json_file(blob_file)
        else:
            new_obj = {}
            first_run = True
        # Populate key-value pairs based on extractor type
        if "extractor_name" in dataset:
            if dataset["extractor_name"] == "metalad_core_dataset":
                schema_file = os.path.join(package_path, "templates", "core_dataset_schema.json")
                new_obj = core_dataset_parse(dataset, new_obj, schema_file)
            elif dataset["extractor_name"] == "metalad_studyminimeta":
                schema_file = os.path.join(package_path, "templates", "studyminimeta_schema.json")
                new_obj = studyminimeta_parse(dataset, new_obj, schema_file)
            elif dataset["extractor_name"] == "metalad_core":
                # do nothing for now
                c=1
            else:
                print("Unrecognized metadata type: DataLad-related")
        else:
            # TODO: handle scenarios where metadata is not generated by DataLad (or decide not to allow this)
            print("Unrecognized metadata type: non-DataLad")
        # Add fields required for UI, but not contained (or not available in required format) in any extractors
        # or not yet extracted for specific dataset. 
        # TODO: this is not done in a smart way currently, needs rework
        if "name" not in new_obj and "dataset_path" in new_obj:
            new_obj["name"] = new_obj["dataset_path"].split(os.path.sep)[-1]
        if "name" in new_obj and "short_name" not in new_obj:
            if len(new_obj["name"])>30:
                new_obj["short_name"] = new_obj["name"][0,30]+'...'
            else:
                new_obj["short_name"] = new_obj["name"]
        schema = load_json_file(os.path.join(package_path, "templates", "studyminimeta_empty.json"))
        for key in schema:
            if key not in new_obj:
                new_obj[key] = schema[key]
        if "children" not in new_obj:
            new_obj["children"] = []
        
        # Subdatasets per dataset
        subdatasets = [item for item in datasets if "root_dataset_id" in item and item["root_dataset_id"] == dataset["dataset_id"] and item["root_dataset_version"] == dataset["dataset_version"]]
        # First save superdataset details to tracking list, for writing it to file later
        # TODO: handle extra times this section is called because of multiple metadata
        # objects resulting from different metalad extractors
        # TODO: copy all keys from required super_dataset_keys list
        idx_super = -1
        if len(subdatasets)>0:
            idx_found_super = next((i for i, item in enumerate(super_datasets) if item["dataset_id"] == dataset["dataset_id"]), -1)
            if idx_found_super > -1:
                super_obj = super_datasets[idx_found]
                copy_key_vals(new_obj, super_obj, super_dataset_keys)
                idx_super = idx_found_super
            else:
                super_obj = {}
                super_obj = copy_key_vals(new_obj, super_obj, super_dataset_keys)
                super_datasets.append(super_obj)
                idx_super = len(super_datasets)-1

            if "subdataset_blobs" not in super_datasets[idx_super]:
                super_datasets[idx_super]["subdataset_blobs"] = []

        # Then populate subdataset details and append to current dataset 'subdatasets' field, unless previously done
        new_obj["subdatasets"] = []
        for subds in subdatasets:
            # TODO: check if the subdatasets already exist and decide whether to overwrite or skip. Currently overwritten
            new_sub_obj = {}
            new_sub_obj["dataset_id"] = subds["dataset_id"]
            new_sub_obj["dataset_version"] = subds["dataset_version"]
            new_sub_obj["dataset_path"] = subds["dataset_path"]
            new_sub_obj["dirs_from_path"] = subds["dataset_path"].split(os.path.sep)
            if not any(x["dataset_id"] == subds["dataset_id"] for x in new_obj["subdatasets"]):
                new_obj["subdatasets"].append(new_sub_obj)
            else:
                continue
            # Write subdataset blob to relevant superdataset in list
            blob_hash = md5blob(subds["dataset_id"], subds["dataset_version"])
            if blob_hash not in super_datasets[idx_super]["subdataset_blobs"]:
                super_datasets[idx_super]["subdataset_blobs"].append(blob_hash)

            # Add subdataset locations as children to parent dataset
            nr_nodes = len(new_sub_obj["dirs_from_path"])
            iter_object = new_obj["children"]
            idx = -1
            for n, node in enumerate(new_sub_obj["dirs_from_path"]):
                if n>0:
                    iter_object = iter_object[idx]["children"]
                if n != nr_nodes-1:
                    # this is a directory
                    idx_found = next((i for i, item in enumerate(iter_object) if item["type"] == "directory" and item["name"] == node), -1)
                else:
                    # last element, this is a subdataset
                    idx_found = next((i for i, item in enumerate(iter_object) if item["type"] == "dataset" and item["name"] == node), -1)
                if idx_found < 0:
                    if n != nr_nodes-1:
                        # this is a directory
                        new_node = {
                            "type": "directory",
                            "name": node,
                            "children": []
                        }
                    else:
                        # last element, this is a subdataset
                        new_node = {
                            "type": "dataset",
                            "name": node,
                            "dataset_id": subds["dataset_id"],
                            "dataset_version": subds["dataset_version"]
                        }
                    iter_object.append(new_node)
                    idx = len(iter_object) - 1
                else:
                    idx = idx_found
        
        # Files /  Children
        # TODO: figure out if we should create a single json file per dataset
        # file, or if all files are to be listed as children in a nested directory
        # structure as a field in the main dataset object OR a mixture of these.
        # Also figure out how to limit the nested-ness within a single object, only
        # render children up to a max amount in the UI, at which point a pointer
        # should identify which file is to be loaded via HTTP request if the rest
        # of the information is to be rendered. Take into account that a file does
        # not have an id and version, so naming of separate blobs per file would
        # likely be something like md5sum(parent_dataset_id-parent_dataset_version-file_path_relative_to_parent)
        # For now, add files as children part of the dataset object:
        # find all files belonging to current dataset
        files = [item for item in metadata if item["type"] == "file" and item["dataset_id"] == dataset["dataset_id"] and item["dataset_version"] == dataset["dataset_version"]]
        for file in files:
            # Add subdataset locations as children to parent dataset
            nodes = file["path"].split("/")
            nr_nodes = len(nodes)
            iter_object = new_obj["children"]
            idx = -1
            for n, node in enumerate(nodes):
                if n>0:
                    iter_object = iter_object[idx]["children"]
                if n != nr_nodes-1:
                    # this is a directory
                    idx_found = next((i for i, item in enumerate(iter_object) if item["type"] == "directory" and item["name"] == node), -1)
                else:
                    # last element, this is a file
                    idx_found = next((i for i, item in enumerate(iter_object) if item["type"] == "file" and item["name"] == node), -1)
                if idx_found < 0:
                    if n != nr_nodes-1:
                        # this is a directory
                        new_node = {
                            "type": "directory",
                            "name": node,
                            "children": []
                        }
                    else:
                        # last element, this is a file
                        bytesize = -1
                        if "contentbytesize" in file["extracted_metadata"]:
                            bytesize = file["extracted_metadata"]["contentbytesize"]
                        url = ""
                        if "distribution" in file["extracted_metadata"] and "url" in file["extracted_metadata"]["distribution"]:
                            url = file["extracted_metadata"]["distribution"]["url"]
                        new_node = {
                            "type": "file",
                            "name": node,
                            "contentbytesize": bytesize,
                            "url": url
                        }
                    iter_object.append(new_node)
                    idx = len(iter_object) - 1
                else:
                    idx = idx_found

        # Write object to file
        with open(blob_file, 'w') as fp:
            json.dump(new_obj, fp)

    # Create single file with all superdatasets (datasets.json) for main page browsing
    super_dataset_file = os.path.join(metadata_out_dir, 'datasets.json')
    with open(super_dataset_file, 'w') as f:
        json.dump(super_datasets, f)

    # Write superdataset name and shortname to all subdataset blobs
    for superds in super_datasets:
        for blob_hash in superds["subdataset_blobs"]:
            blob_file = os.path.join(metadata_out_dir, blob_hash + ".json")
            ds = load_json_file(blob_file)
            ds["root_dataset_name"] = superds["name"]
            ds["root_dataset_short_name"] = superds["short_name"]
            with open(blob_file, 'w') as f:
                json.dump(ds, f)

    # Copy all remaining components from templates to output directory 
    # Assets
    assets = ["md5-2.3.0.js", "style.css", "vue_app.js"]
    for asset_fn in assets:
        shutil.copy2(os.path.join(assets_path, asset_fn), assets_out_dir)
    # Artwork
    artworks = ["datalad_logo_wide.svg", "View1.svg"]
    for artwork_fn in artworks:
        shutil.copy2(os.path.join(artwork_path, artwork_fn), artwork_out_dir)
    # Main UI (html)
    shutil.copy2(os.path.join(package_path, 'index.html'), out_dir)

#-----------------
# Helper functions
#-----------------
def md5blob(identifier='', version=''):
    """
    Create md5sum of an identifier and version number (joined by a
    dash), to serve as a filename for a json blob.
    """
    blob_string = identifier + "-" + version
    blob_hash = hashlib.md5(blob_string.encode('utf-8')).hexdigest()
    return blob_hash

def load_json_file(filename):
    """
    Load contents of a JSON file into a dict or list of dicts
    """
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        print("Exception occurred: ", sys.exc_info()[0])

def core_parse(src_object, dest_object, schema_file):
    """
    Parse metadata output by DataLad's `metalad_core` extractor and
    translate into JSON structure from which UI is generated.
    """

def core_dataset_parse(src_object, dest_object, schema_file):
    """
    Parse metadata output by DataLad's `metalad_core_dataset`
    extractor and translate into JSON structure from which UI is
    generated.
    """
    # Load schema/template dictionary, where each key represents the exact
    # same key in the destination object, and each associated value
    # represents the key in the source object which value is to be copied.
    schema = load_json_file(schema_file)
    # Copy source to destination values, per key
    for key in schema:
        if schema[key] in src_object:
            dest_object[key] = src_object[schema[key]]
    return dest_object

def studyminimeta_parse(src_object, dest_object, schema_file):
    """
    Parse metadata output by DataLad's `metalad_studyminimeta`
    extractor and translate into JSON structure from which UI is
    generated.
    """
    # Load schema/template dictionary, where each key represents the exact
    # same key in the destination object, and each associated value
    # represents the key in the source object which value is to be copied.
    #TODO: request to add fields to metalad_studyminimeta extractor in metalad:
    # - license, DOI,...
    schema = load_json_file(schema_file)    
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
        if isinstance(schema[key], list) and len(schema[key])==2:
            dest_object[key] = metadata[schema[key][0]][schema[key][1]]
        else:
            dest_object[key] = schema[key]
    # Authors
    for author in metadata["dataset"]["author"]:
        author_details = next((item for item in metadata["personList"] if item["@id"] == author["@id"]), False)
        if not author_details:
            idd = author["@id"]
            print(f"Error: Person details not found in '#personList' for '@id' = {idd}")
        else:
            dest_object["authors"].append(author_details)
    # Publications
    for pub in metadata["publicationList"]:
        new_pub = {"type" if k == "@type" else k:v for k,v in pub.items()}
        new_pub = {"doi" if k == "sameAs" else k:v for k,v in new_pub.items()}
        new_pub["publication"] = {"type" if k == "@type" else k:v for k,v in new_pub.items()}
        if "@id" in new_pub:
            new_pub.pop("@id")
        if "@id" in new_pub["publication"]:
            new_pub["publication"].pop("@id")
        for i, author in enumerate(new_pub["author"]):
            author_details = next((item for item in metadata["personList"] if item["@id"] == author["@id"]), False)
            if not author_details:
                idd = author["@id"]
                print(f"Error: Person details not found in '#personList' for @id = {idd}")
            else:
                new_pub["author"][i] = author_details
        dest_object["publications"].append(new_pub)
    
    return dest_object

def copy_key_vals(src_object, dest_object, keys):
    """
    For each key in a list, copy each corresponding key-value pair from
    a source dictionary to a destination dictionary, provided that the
    key-value pair exists in the source dictionary
    """
    for key in keys:
        if key in src_object:
            dest_object[key] = src_object[key]
    return dest_object

#------------
# MOAR TODOS!
#------------
# TODO: figure out logging
# TODO: figure out testing
# TODO: figure out installation / building process
# TODO: figure out automated updates to serving content somewhere
# TODO: figure out CI
# TODO: figure out what to do when a dataset belongs to multiple super-datasets
# TODO: if not provided, calculate directory/dataset size by accumulating children file sizes