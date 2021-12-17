from os.path import curdir
from os.path import abspath
import logging
from datalad.interface.base import Interface
from datalad.interface.base import build_doc
from datalad.support.param import Parameter
from datalad.distribution.dataset import datasetmethod
from datalad.interface.utils import eval_results
from datalad.support.constraints import EnsureChoice

from datalad.interface.results import get_status_dict

import sys
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path
import json
import os
import hashlib
import shutil
from typing import (
    Dict,
    List,
    Optional,
    Tuple,
    Union
)
from .webcatalog import WebCatalog, Node, Dataset, Translator
from . import constants as cnst

# create named logger
lgr = logging.getLogger("datalad.catalog.catalog")

# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class Catalog(Interface):
    # first docstring line is used a short description in the cmdline help
    # the rest is put in the verbose help and manpage
    """Generate web-browser-based user interface for browsing metadata of a 
    DataLad dataset.

    (Long description of arbitrary volume.)
    """

    # parameters of the command, must be exhaustive
    _params_ = dict(
        # name of the parameter, must match argument name
        catalog_action=Parameter(
            args=("catalog_action",),
            # documentation
            doc="""The subcommand to be executed by datalad-catalog.
            Options include: create, add, remove, serve, create-sibling-*.
            Example: ''""",
            # type checkers, constraint definition is automatically
            # added to the docstring
            constraints=EnsureChoice('create', 'add', 'remove', 'serve', 'create-sibling')
        ),
        catalog_dir=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog_dir"),
            # documentation
            doc="""Directory where the catalog is located or will be created.
            Example: ''""",
            ),
        metadata=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-m", "--metadata"),
            # documentation
            doc="""Path to input metadata. Multiple input types are possible:
            - A '.json' file containing an array of JSON objects related to a
             single datalad dataset.
            - A stream of JSON objects/lines
            Example: ''""",
            ),
        dataset_id=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-i", "--dataset_id"),
            # documentation
            doc="""
            Example: ''""",
            ),
        dataset_version=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-v", "--dataset_version"),
            # documentation
            doc="""
            Example: ''""",
            ),
        
        force=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-f", "--force"),
            # documentation
            doc="""If content for the user interface already exists in the catalog
            directory, force this content to be overwritten. Content
            overwritten with this flag include the 'artwork' and 'assets'
            directories and the 'index.html' file. Content in the 'metadata' directory 
            remain untouched.
            Example: ''""",
            action="store_true",
            default=False
            ),
    )

    @staticmethod
    # decorator binds the command to the Dataset class as a method
    @datasetmethod(name='catalog')
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog_action: str,
        catalog_dir = None, 
        metadata = None,
        dataset_id = None,
        dataset_version = None,
        force: bool = False):

        # Error out if `catalog_dir` argument was not supplied
        if catalog_dir is None:
            err_msg = f"No catalog directory supplied: Datalad catalog can only operate on a path to a directory (argument: -c, --catalog_dir)"
            yield get_status_dict(
                action=f"catalog {catalog_action}",
                path=abspath(curdir),# reported paths MUST be absolute
                status='error',
                message=err_msg)
            sys.exit(err_msg)

        # Test if catalog already exists at path
        # Instantiate WebCatalog class
        ctlg = WebCatalog(catalog_dir, dataset_id, dataset_version, force) 
        # catalog_path = Path(catalog_dir)
        # catalog_exists = catalog_path.exists() and catalog_path.is_dir()
        # Catalog should exist for all actions except create (for create action: unless force flag supplied)
        if not ctlg.is_created():
            if catalog_action != 'create':
                err_msg = f"Catalog does not exist: datalad catalog {catalog_action} can only operate on an existing catalog, please supply a path to an existing directory (-c, --catalog_dir)"
                yield get_status_dict(
                    action=f"catalog {catalog_action}",
                    path=abspath(curdir),# reported paths MUST be absolute
                    status='error',
                    message=err_msg)
                sys.exit(err_msg)
        else:
            if catalog_action == 'create':
                if not force:
                    err_msg = f"Catalog already exists: overwriting catalog assets (not catalog data!) is only possible when using the force argument (-f, --force)"
                    yield get_status_dict(
                        action=f"catalog {catalog_action}",
                        path=abspath(curdir),# reported paths MUST be absolute
                        status='warning',
                        message=err_msg)
                    sys.exit(err_msg)

        # Call relevant function based on action
        # Action-specific argument parsing as well as results yielding are done within action-functions
        call_action = {
            'create': create_catalog,
            'serve': serve_catalog,
            'add': add_to_catalog,
            'remove': remove_from_catalog,
            'create-sibling': create_sibling_catalog,
        }
        call_action.get(catalog_action, lambda: 'Invalid')(
            ctlg, 
            metadata,
            dataset_id,
            dataset_version,
            force
        )

        # script_path = os.path.realpath(__file__)
        # sep = os.path.sep
        # repo_path = sep.join(script_path.split(sep)[0:-2])
        # package_path = sep.join(script_path.split(sep)[0:-1])
        # if outputdir:
        #     out_dir = outputdir
        # else:
        #     out_dir = curdir


def create_catalog(catalog: WebCatalog, metadata, dataset_id, dataset_version, force):
    """
    [summary]
    """    
    # If catalog does not exist, create it
    # If catalog exists and force flag is True, overwrite assets of existing catalog
    if not catalog.is_created():
        catalog.create()
        msg=f"Catalog successfully created at: {catalog.location}"
    else:
        if force:
            catalog.create(force)
            msg=f"Catalog assets successfully overwritten at: {catalog.location}"
    # Yield created/overwitten status message
    yield get_status_dict(
        action='catalog create',
        path=abspath(curdir),
        status='ok',
        message=msg)
    # If metadata was also supplied, add this to the catalog
    if metadata is not None:
        add_to_catalog(catalog, metadata, dataset_id, dataset_version, force)


def add_to_catalog(catalog: WebCatalog, metadata, dataset_id, dataset_version, force):
    """
    [summary]
    """
    if metadata is None:
        err_msg = f"No metadata supplied: Datalad catalog has to be supplied with metadata in the form of a path to a file containing a JSON array, or JSON lines stream (argument: -m, --metadata)"
        yield get_status_dict(
            action='catalog add',
            path=abspath(curdir),# reported paths MUST be absolute
            status='error',
            message=err_msg)
        sys.exit(err_msg)

    # e.g.:
    # {"type": "dataset", "dataset_id": "8b7ce998-96d9-11ea-847b-a0369f287950", "dataset_version": "9a3f93cd0a913148b20bd2ea688fda71bfd632ba"}
    # {"type":"file", "dataset_id":"8b7ce998-96d9-11ea-847b-a0369f287950", "dataset_version":"9a3f93cd0a913148b20bd2ea688fda71bfd632ba", "path":"MovingAverage/OutlierByMovingAverage.m"},
    # 
    # Need to do the following:
    # - 1. establish input type (file, file-with-json-array, file-with-json-lines, command line stdout / stream)
    # - 2. read input based on type
    # - 3. instantiate translator

    # 1 ==> assume file-with-json-array for now
    # Load data from input file
    # (assume for now that the data were exported by using `datalad meta-dump`,
    # and that all exported objects were added to an array in a json file)
    # This metadata should be the dataset and file level metadata of a single dataset
    metadata = load_json_file(metadata)
    for meta_count, meta_object in enumerate(metadata):
        # Get dataset_id, dataset_version
        d_id = meta_object[cnst.DATASET_ID]
        d_version = meta_object[cnst.DATASET_VERSION]
        # get metadata object type (dataset or file)
        if meta_object[cnst.TYPE] == cnst.TYPE_DATASET:
            # If dataset, create special node
            node_object = Dataset.get(dataset_id=d_id, dataset_version=d_version)
            translate = Translator(meta_object, node_object)
        else:
            # If file: create standard node per path part
            f_path = meta_object[cnst.PATH]
            parts_in_path = list(Path(f_path.lstrip('/')).parts)
            nr_of_dirs = len(parts_in_path)-1 # this excludes the last part, which is the actual filename
            incremental_path = Path('')
            previous_path = None
            for part_count, part in enumerate(parts_in_path):

                # Get node path
                incremental_path = incremental_path / part

                # when reaching the last dir (i.e. parent of file)
                if part_count == nr_of_dirs-1:
                    pass
                # when reaching the filename, add it as child to parent node
                elif part_count == nr_of_dirs:
                    # Instantiate/get node object with parent path
                    node_object = Node.get(dataset_id=d_id, dataset_version=d_version, node_path=previous_path)
                    node_object.children.append(


                    )
                    pass
                # for all other parts in the path
                else:
                    # Instantiate/get node object
                    node_object = Node.get(dataset_id=d_id, dataset_version=d_version, node_path=incremental_path)

                # If the accompanying metafile does not exist, create it
                if not node_object.is_created():
                    node_object_content = {} # TODO: load template dictionary
                    with open(node_object.get_location(catalog.metadata_path), 'w') as f:
                        json.dump(node_object_content, f)
                
                
                node_object_content = node_object.load_file()
                
                
                

                
                previous_path = incremental_path

                





def remove_from_catalog(catalog: WebCatalog, metadata, dataset_id, dataset_version, force):
    """
    [summary]
    """
    # remove argument checks
    if not dataset_id or not dataset_version:
        err_msg = f"Dataset ID and/or VERSION missing: datalad catalog remove requires both the ID (-i, --dataset_id) and VERSION (-v, --dataset_version) of the dataset to be removed from the catalog"
        yield get_status_dict(
            action=f"catalog remove",
            path=abspath(curdir),# reported paths MUST be absolute
            status='error',
            message=err_msg)
        sys.exit(err_msg)


def serve_catalog(catalog: WebCatalog, metadata, dataset_id, dataset_version, force):
    """
    """

def create_sibling_catalog(catalog: WebCatalog, metadata, dataset_id, dataset_version, force):
    """
    [summary]
    """




def datalad_catalog(metadata, out_dir, repo_path, package_path,
                    overwrite, set_super):
    """
    Generate web-browser-based user interface for browsing metadata of a
    DataLad dataset.

    EXAMPLE USAGE:
    > datalad_catalog -o <path-to-output-directory> -f <path-to-input-file>
    > datalad_catalog -o <path-to-output-directory> -f <path-to-input-file>
    > datalad_catalog -o <path-to-output-directory> -a <data-array>
    """

    # Parse
    act = 0
    actions = ['create', 'add', 'remove', 'serve']
    action = actions[act]

    # Create output directories if they do not exist
    metadata_out_dir = setup_metadata_dir(out_dir)
    templates_path = os.path.join(package_path, 'templates')
    
    # Grab all datasets from metadata
    datasets = filter_metadata_objects(metadata,
                                       options_dict={"type": "dataset"})
    # TODO: test for empty list
    
    # Isolate the incoming dataset id and version
    # TODO: decide whether to warn or error out if multiple source datasets included
    unique_blobs = set([])
    for ds in datasets:
        blob_hash = md5blob(ds["dataset_id"], ds["dataset_version"])
        unique_blobs.add(blob_hash)
    if len(unique_blobs) > 1:
        # Multiple dataset-level metadata items found: error/warning?
        print("Error: dataset-level metadata items found for multiple source \
              datasets. datalad catalog requires all input metadata to be \
              generated from a single dataset.")
        sys.exit("Multiple dataset-level metadata items found")
    else:
        # Single dataset source
        main_dataset_id = datasets[0]["dataset_id"]
        main_dataset_version = datasets[0]["dataset_version"]
    
    # TODO: write main details to file in case -s flag specifies this as catalog super
    if set_super:
        print("Super dataset specified, creating entry")
        write_superdataset(datasets[0], metadata_out_dir)
    
    # Process dataset-level metadata
    new_obj, blob_file = process_dataset(datasets, metadata, metadata_out_dir, templates_path)
    # Add subdatasets to "children" field
    if "subdatasets" in new_obj and isinstance(new_obj["subdatasets"], list) and len(new_obj["subdatasets"]) > 0:
        new_obj = add_update_subdatasets(new_obj, new_obj["subdatasets"])
    # Process file-level metadata
    # Find all files with the main object as parent dataset, and add them as children
    main_dataset_files = filter_metadata_objects(
                metadata,
                options_dict={
                    "type": "file",
                    "dataset_id": main_dataset_id,
                    "dataset_version": main_dataset_version
                })
    # TODO: check if extra files are in incoming data, give warning
    new_obj = add_update_files(dataset_object=new_obj, files=main_dataset_files)

    # Write children array to separate file
    children_hash, children_file = get_md5_details(datasets[0]["dataset_id"],
                                            datasets[0]["dataset_version"],
                                            metadata_out_dir,
                                            children=True)
    children_obj = {}
    children_obj["children"] = new_obj["children"]
    with open(children_file, 'w') as fp1:
        json.dump(children_obj, fp1)
    
    new_obj["children"] = children_hash

    # Write main data object to file
    with open(blob_file, 'w') as fp2:
        json.dump(new_obj, fp2)
    
    # Copy all remaining components from templates to output directory
    copy_ui_content(repo_path, out_dir, package_path, overwrite)


# --------------------
# Function definitions
# --------------------

def process_dataset(datasets, metadata, metadata_out_dir, templates_path):
    """
    Process all metadata items extracted for a dataset on the dataset level
    """

    # blob_hash = md5blob(datasets[0]["dataset_id"], datasets[0]["dataset_version"])
    
    new_obj, blob_file = get_dataset_object(datasets[0]["dataset_id"],
                                            datasets[0]["dataset_version"],
                                            metadata_out_dir)
    # Populate key-value pairs based on extractor type
    for ds_item in datasets:
        if "extractor_name" in ds_item:
            new_obj = parse_metadata_object(ds_item, new_obj, templates_path)
        else:
            # TODO: handle scenarios where metadata is not generated by
            # DataLad (or decide not to allow this)
            print("Unrecognized metadata type: non-DataLad")
    # Add missing fields required for UI
    new_obj = add_missing_fields(new_obj, templates_path)
    # # Get all subdatasets of current dataset
    # subdatasets = filter_metadata_objects(
    #                 all_datasets,
    #                 options_dict={
    #                     "root_dataset_id": dataset["dataset_id"],
    #                     "root_dataset_version": dataset["dataset_version"]
    #                 })
    # # If subdatasets exist, add them to superdataset list and to
    # # main dataset object
    # sub_blob_hashes = []
    # subdataset_objects = []
    # subdataset_keywords = set([])
    # for subds in subdatasets:
    #     sub_blob_hash = md5blob(subds["dataset_id"], subds["dataset_version"])
    #     if sub_blob_hash not in sub_blob_hashes:
    #         sub_blob_hashes.append(sub_blob_hash)
    #     if sub_blob_hash in processed_datasets:
    #         continue
    #     # Process this subds, other related datasets, subdatasets, and files
    #     processed_datasets, subds_obj = \
    #         process_dataset(subds, all_datasets, processed_datasets,
    #                         metadata, metadata_out_dir, templates_path)
    #     subdataset_objects.append(subds_obj)
    #     subdataset_keywords.update(subds_obj["keywords"])
    # # Then populate subdataset details and append to current dataset
    # # 'subdatasets' field
    # new_obj["subdataset_blobs"] = sub_blob_hashes
    # new_obj["subdataset_keywords"] = list(subdataset_keywords)
    # new_obj = add_update_subdatasets(dataset_object=new_obj,
    #                                  subdatasets=subdataset_objects)
    # # Find all files with the main object as parent dataset, and add
    # # them as children
    # files = filter_metadata_objects(
    #             metadata,
    #             options_dict={
    #                 "type": "file",
    #                 "dataset_id": dataset["dataset_id"],
    #                 "dataset_version": dataset["dataset_version"]
    #             })
    # new_obj = add_update_files(dataset_object=new_obj, files=files)
    # # Write main data object to file
    # with open(blob_file, 'w') as fp:
    #     json.dump(new_obj, fp)

    return new_obj, blob_file


def md5blob(identifier='', version='', children=False):
    """
    Create md5sum of an identifier and version number (joined by a
    dash), to serve as a filename for a json blob.
    """
    blob_string = identifier + "-" + version
    if children:
        blob_string = blob_string + "-children"
    blob_hash = hashlib.md5(blob_string.encode('utf-8')).hexdigest()
    return blob_hash


def load_json_file(filename):
    """
    Load contents of a JSON file into a dict or list of dicts
    """
    try:
        with open(filename) as f:
            return json.load(f)
    except OSError as err:
        print("OS error: {0}".format(err))
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def copy_key_vals(src_object, dest_object, keys=[], overwrite=True):
    """
    For each key in a list, copy each corresponding key-value pair from
    a source dictionary to a destination dictionary, provided that the
    key-value pair exists in the source dictionary and that it doesn't
    exist in the destination dictionary. If it does, only copy if the
    overwrite boolean is specified as True (default).
    """
    # If an empty list is provided, use all keys from src_object
    if not keys:
        keys = src_object.keys()
    for key in keys:
        if key in src_object:
            if key not in dest_object or overwrite:
                dest_object[key] = src_object[key]
    return dest_object


def setup_metadata_dir(out_dir):
    """
    Setup the 'metadata' directory for saving output files
    """
    # If the metadata directory already exists, remove it with its contents
    metadata_path = Path(out_dir) / 'metadata'
    if not (metadata_path.exists() and metadata_path.is_dir()):
        Path(metadata_path).mkdir(parents=True)
    
    return metadata_path


def copy_ui_content(repo_path, out_dir, package_path, overwrite):
    """
    Copy all content required for the user interface to render

    This includes assets (JS, CSS), artwork and the main html.
    """
    content_paths = {
        "assets": Path(package_path) / 'assets',
        "artwork": Path(package_path) / 'artwork',
        "html": Path(package_path) / 'index.html',
    }
    out_dir_paths = {
        "assets": Path(out_dir) / 'assets',
        "artwork": Path(out_dir) / 'artwork',
        "html": Path(out_dir) / 'index.html',
    }
    for key in content_paths:
        copy_overwrite_path(src=content_paths[key],
                            dest=out_dir_paths[key],
                            overwrite=overwrite)


def copy_overwrite_path(src, dest, overwrite):
    """
    Copy or overwrite a directory or file
    """
    isFile = src.is_file()
    if dest.exists() and not overwrite:
        pass
    else:
        if isFile:
            shutil.copy2(src, dest)
        else:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)


def get_md5_details(dataset_id, dataset_version, data_dir, children=False):
    """
    Return an md5 hash of a dataset id and version, as well
    as the path for the file representing this dataset object
    """
    blob_hash = md5blob(dataset_id, dataset_version, children)
    blob_file = os.path.join(data_dir, blob_hash + ".json")
    return blob_hash, blob_file
    

def get_dataset_object(dataset_id, dataset_version, data_dir, children=False):
    """
    Get a JSON object pertaining to a UI dataset from file if the file exists,
    else return an empty object.
    """
    blob_hash = md5blob(dataset_id, dataset_version, children)
    blob_file = os.path.join(data_dir, blob_hash + ".json")
    if os.path.isfile(blob_file):
        return load_json_file(blob_file), blob_file
    else:
        return {}, blob_file


def parse_metadata_object(src_object, dest_object, schema_path):
    """
    Parse a single metadata item from the list input to `datalad_catalog`,
    using a different parser based on the `extractor_name` field of the item.
    """
    if src_object["extractor_name"] == "metalad_core_dataset":
        schema_file = os.path.join(schema_path, "core_dataset_schema.json")
        dest_object = core_dataset_parse(src_object, dest_object, schema_file)
    elif src_object["extractor_name"] == "metalad_studyminimeta":
        schema_file = os.path.join(schema_path, "studyminimeta_schema.json")
        dest_object = studyminimeta_parse(src_object, dest_object, schema_file)
    elif src_object["extractor_name"] == "metalad_core" and src_object["type"] == "dataset":
        schema_file = os.path.join(schema_path, "core_schema_for_dataset.json")
        dest_object = core_parse_dataset(src_object, dest_object, schema_file)
    elif src_object["extractor_name"] == "metalad_core" and src_object["type"] == "file":
        schema_file = os.path.join(schema_path, "core_schema_for_file.json")
        dest_object = core_parse_file(src_object, dest_object, schema_file)
    else:
        print("Unrecognized metadata type: DataLad-related")
    return dest_object


def filter_metadata_objects(metadata_list, options_dict):
    """
    Filter a list of objects by multiple key-value pairs
    """
    for key in options_dict:
        metadata_list = [item for item in metadata_list if key in item
                         and item[key] == options_dict[key]]
    return metadata_list


def find_dataset_objects(datasets, dataset_id, dataset_version):
    """
    Find indices of specific elements in a list of dataset objects,
    given specific key-value pairs
    """
    idx_list = [idx for idx, item in enumerate(datasets)
                if "dataset_id" in item
                and item["dataset_id"] == dataset_id
                and "dataset_version" in item
                and item["dataset_version"] == dataset_version]
    return idx_list


def add_missing_fields(dataset_object, schema_path):
    """
    Add fields to a dataset object that are required for UI but are not yet
    contained in the object, i.e. not available in any Datalad extractor output
    or not yet parsed for the specific dataset
    """
    if "name" not in dataset_object and "dataset_path" in dataset_object:
        dataset_object["name"] = dataset_object["dataset_path"]. \
                                 split(os.path.sep)[-1]
    if "name" in dataset_object and "short_name" not in dataset_object:
        if len(dataset_object["name"]) > 30:
            dataset_object["short_name"] = dataset_object["name"][0:30]+'...'
        else:
            dataset_object["short_name"] = dataset_object["name"]

    schema = load_json_file(os.path.join(schema_path,
                                         "studyminimeta_empty.json"))
    for key in schema:
        if key not in dataset_object:
            dataset_object[key] = schema[key]

    if "children" not in dataset_object:
        dataset_object["children"] = []

    if "subdatasets" not in dataset_object:
        dataset_object["subdatasets"] = []

    return dataset_object


def add_update_superdatasets(dataset_object, super_datasets):
    """
    Update a specific superdataset in a list. If the dataset does not exist in
    the list, create it and append to the list.
    """
    super_dataset_keys = ["type", "dataset_id", "dataset_version",
                          "extraction_time", "short_name", "name",
                          "description", "doi", "url", "license",
                          "authors", "keywords"]
    # Find index if dataset already exists in the `super_datasets` list
    idx_super_found = next((i for i, item in enumerate(super_datasets)
                            if item["dataset_id"] ==
                            dataset_object["dataset_id"]), -1)
    # If dataset found, get object, copy key-value pairs
    # If dataset not found, copy key-value pairs to new object, append to list
    if idx_super_found > -1:
        super_obj = super_datasets[idx_super_found]
        copy_key_vals(dataset_object, super_obj, super_dataset_keys)
        idx_super = idx_super_found
    else:
        super_obj = {}
        super_obj = copy_key_vals(dataset_object,
                                  super_obj,
                                  super_dataset_keys)
        super_datasets.append(super_obj)
        idx_super = len(super_datasets)-1
    # Add empty list for subdataset info to be added later
    if "subdataset_blobs" not in super_datasets[idx_super]:
        super_datasets[idx_super]["subdataset_blobs"] = []

    return idx_super, super_datasets


def object_in_list(attribute_key, attribute_val, search_list):
    """
    Returns True if an object with an attribute equal to a specific value
    exists in a list, else returns False.
    """
    return any(x[attribute_key] == attribute_val for x in search_list)


def add_update_subdatasets(dataset_object, subdatasets):
    """
    For each subdataset in a list, add subdataset locations as children to
    parent dataset
    """
    print(subdatasets)
    print(dataset_object["children"])
    for subds in subdatasets:
        # Add subdataset locations as children to parent dataset
        nr_nodes = len(subds["dirs_from_path"])
        iter_object = dataset_object["children"]
        idx = -1
        for n, node in enumerate(subds["dirs_from_path"]):
            if n > 0:
                iter_object = iter_object[idx]["children"]
            if n != nr_nodes-1:
                # this is a directory
                idx_found = next((i for i, item in enumerate(iter_object)
                                  if item["type"] == "directory"
                                  and item["name"] == node), -1)
            else:
                # last element, this is a subdataset
                idx_found = next((i for i, item in enumerate(iter_object)
                                  if item["type"] == "dataset"
                                  and item["name"] == node), -1)
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
    return dataset_object


def add_update_files(dataset_object, files):
    """
    For each file in a list, add file locations as children to parent dataset
    """
    for file in files:
        nodes = file["path"].split("/")
        nr_nodes = len(nodes)
        iter_object = dataset_object["children"]
        idx = -1
        for n, node in enumerate(nodes):
            if n > 0:
                iter_object = iter_object[idx]["children"]
            if n != nr_nodes-1:
                # this is a directory
                idx_found = next((i for i, item in enumerate(iter_object)
                                  if item["type"] == "directory"
                                  and item["name"] == node), -1)
            else:
                # last element, this is a file
                idx_found = next((i for i, item in enumerate(iter_object)
                                  if item["type"] == "file"
                                  and item["name"] == node), -1)
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
                        bytesize = \
                            file["extracted_metadata"]["contentbytesize"]
                    url = ""
                    if "distribution" in file["extracted_metadata"] \
                       and "url" in file["extracted_metadata"]["distribution"]:
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
    return dataset_object


def core_parse_dataset(src_object, dest_object, schema_file):
    """
    Parse dataset-level metadata output by DataLad's `metalad_core` extractor from
    translate into JSON structure from which UI is generated.
    """
    # Load schema/template dictionary, where each key represents the exact
    # same key in the destination object, and each associated value
    # represents the key in the source object which value is to be copied.
    schema = load_json_file(schema_file)
    # Copy source to destination values, per key
    for key in schema:
        if schema[key] in src_object:
            dest_object[key] = src_object[schema[key]]
    # Populate URL field
    ds_info = next((item for item in src_object["extracted_metadata"]["@graph"]
                    if "@type" in item and item["@type"] == "Dataset"), False)
    if ds_info and "distribution" in ds_info:
        origin = next((item for item in ds_info["distribution"]
                       if "name" in item and item["name"] == "origin"), False)
        if origin:
            dest_object["url"] = origin["url"]
    # Populate subdatasets field
    sep = os.path.sep
    dest_object["subdatasets"] = []
    if ds_info and "hasPart" in ds_info:
        for subds in ds_info["hasPart"]:
            sub_dict = {
                "dataset_id": subds["identifier"].strip("datalad:"),
                "dataset_version": subds["@id"].strip("datalad:"),
                "dataset_path": subds["name"],
                "dirs_from_path": subds["name"].split(sep)
            }
            dest_object["subdatasets"].append(sub_dict)
    return dest_object

def core_parse_file(src_object, dest_object, schema_file):
    """
    Parse file-level metadata output by DataLad's `metalad_core` extractor and
    translate into JSON structure from which UI is generated.
    """
    # Load schema/template dictionary, where each key represents the exact
    # same key in the destination object, and each associated value
    # represents the key in the source object which value is to be copied.
    schema = load_json_file(schema_file)
    # Copy source to destination values, per key
    for key in schema:
        if schema[key] in src_object:
            dest_object[key] = src_object[schema[key]]
    # Populate URL field
    ds_info = next((item for item in src_object["extracted_metadata"]["@graph"]
                    if "@type" in item and item["@type"] == "Dataset"), False)
    if ds_info and "distribution" in ds_info:
        origin = next((item for item in ds_info["distribution"]
                       if "name" in item and item["name"] == "origin"), False)
        if origin:
            dest_object["url"] = origin["url"]
    return dest_object


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
    # TODO: request add fields to metalad_studyminimeta extractor in metalad:
    # - license, DOI,...
    schema = load_json_file(schema_file)
    metadata = {}
    # Extract core objects/lists from src_object
    metadata["study"] = next((item for item
                              in src_object["extracted_metadata"]["@graph"]
                              if "@type" in item
                              and item["@type"] == "CreativeWork"), False)
    if not metadata["study"]:
        print("Warning: object where '@type' equals 'CreativeWork' not found in \
src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    
    metadata["dataset"] = next((item for item
                                in src_object["extracted_metadata"]["@graph"]
                                if "@type" in item
                                and item["@type"] == "Dataset"), False)
    if not metadata["dataset"]:
        print("Warning: object where '@type' equals 'Dataset' not found in \
src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    
    metadata["publicationList"] = \
        next((item for item in src_object["extracted_metadata"]["@graph"]
              if "@id" in item and item["@id"] == "#publicationList"), False)
    if not metadata["publicationList"]:
        print("Warning: object where '@id' equals '#publicationList' not found \
in src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    else:
        metadata["publicationList"] = metadata["publicationList"]["@list"]
    
    metadata["personList"] = \
        next((item for item in src_object["extracted_metadata"]["@graph"]
              if "@id" in item and item["@id"] == "#personList"), False)
    if not metadata["personList"]:
        print("Warning: object where '@id' equals '#personList' not found in \
src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    else:
        metadata["personList"] = metadata["personList"]["@list"]
    
    # Standard/straightforward fields: copy source to dest values per key
    for key in schema:
        if isinstance(schema[key], list) and len(schema[key]) == 2:
            if schema[key][0] in metadata \
               and schema[key][1] in metadata[schema[key][0]]:
                dest_object[key] = metadata[schema[key][0]][schema[key][1]]
        else:
            dest_object[key] = schema[key]
    # Description
    dest_object["description"] = dest_object["description"].replace('<', '')
    dest_object["description"] = dest_object["description"].replace('>', '')
    # Authors
    for author in metadata["dataset"]["author"]:
        author_details = \
            next((item for item in metadata["personList"]
                  if item["@id"] == author["@id"]), False)
        if not author_details:
            idd = author["@id"]
            print(f"Error: Person details not found in '#personList' for '@id'={idd}")
        else:
            dest_object["authors"].append(author_details)
    # Publications
    if metadata["publicationList"]:
        for pub in metadata["publicationList"]:
            new_pub = {"type" if k == "@type" else k: v for k, v in pub.items()}
            new_pub = {"doi" if k == "sameAs"
                    else k: v for k, v in new_pub.items()}
            new_pub["publication"] = {"type" if k == "@type"
                                    else k: v for k, v in new_pub.items()}
            if "@id" in new_pub:
                new_pub.pop("@id")
            if "@id" in new_pub["publication"]:
                new_pub["publication"].pop("@id")
            for i, author in enumerate(new_pub["author"]):
                author_details = \
                    next((item for item in metadata["personList"]
                        if item["@id"] == author["@id"]), False)
                if not author_details:
                    idd = author["@id"]
                    print(f"Error: Person details not found in '#personList' for\
                        @id = {idd}")
                else:
                    new_pub["author"][i] = author_details
            dest_object["publications"].append(new_pub)
    return dest_object


def search_superdataset(metadata):
    """
    Find the main superdataset from the list of input metadata.
    Throw errors if zero or multiple superdatasets are found.
    Create file to save details of single superdataset
    """
    super_datasets = [item for item in metadata if "type" in item
                      and item["type"] == "dataset"
                      and "root_dataset_id" not in item]
    if len(super_datasets) == 0:
        # No superdatasets found: error
        print("Error: no superdataset found in input. datalad_catalog\
              requires all input metadata to be generated from a single\
              superdataset.")
        sys.exit("No superdatasets found")

    unique_supers = set([])
    for ds in super_datasets:
        blob_hash = md5blob(ds["dataset_id"], ds["dataset_version"])
        unique_supers.add(blob_hash)

    if len(unique_supers) > 1:
        # Multiple superdatasets found: error
        print("Error: multiple superdatasets found in input. datalad_catalog\
              requires all input metadata to be generated from a single\
              superdataset.")
        sys.exit("Multiple superdatasets found")
    else:
        # Single superdataset found
        return super_datasets[0]


def write_superdataset(superds, metadata_out_dir):
    """
    """
    suberds_obj = {"dataset_id": superds["dataset_id"],
                   "dataset_version": superds["dataset_version"]}
    superds_file = os.path.join(metadata_out_dir, "super.json")
    with open(superds_file, 'w') as f:
        json.dump(suberds_obj, f)
# ------------
# MOAR TODOS!
# ------------
# TODO: IMPORTANT FOR CURRENT UPDATE:
    # add fields to objects in subdatasets array, which in turn is a field of
    #   the main superdataset object:
    #   -extraction_time, name, short_name, doi, url, license, authors,keywords
# TODO: figure out logging
# TODO: figure out testing
# TODO: figure out installation / building process
# TODO: figure out automated updates to serving content somewhere
# TODO: figure out CI
# TODO: figure out what to do when a dataset belongs to multiple super-datasets
# TODO: if not provided, calculate directory/dataset size by accumulating
# children file sizes
# TODO: figure out if we should create a single json file per dataset
    # file, or if all files are to be listed as children in a nested directory
    # structure as a field in the main dataset object OR a mixture of these.
    # Also figure out how to limit the nested-ness within a single object, only
    # render children up to a max amount in the UI, at which point a pointer
    # should identify which file is to be loaded via HTTP request if the rest
    # of the information is to be rendered. Take into account that a file does
    # not have an id and version, so naming of separate blobs per file would
    # likely be something like:
    # md5sum(parent_dataset_id-parent_dataset_version-file_path_relative_to_parent)
    # For now, add files as children part of the dataset object

# NOTE: replace string properties with global variable / enum, e.g.: obj["property"] ==> obj[global_var.prop], where global_var.prop = "property"
