import sys
from argparse import ArgumentParser, Namespace, RawDescriptionHelpFormatter
from pathlib import Path
import json
import os
import hashlib
import shutil


def run_cmd():
    """
    Calls datalad_catalog() with command line arguments
    """
    argument_parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter)
    argument_parser.add_argument(
        "-o", "--outputdir",
        type=str,
        help="Directory to which outputs are written.\
        Default is the '_build' directory inside the\
        'data-browser-from-metadata' rep")
    argument_parser.add_argument(
        "-f", "--force",
        action='store_true',
        help="If content for the user interface already exists in the specified\
        or default directory, force this content to be overwritten. Content\
        overwritten with this flag include the 'artwork' and 'assets'\
        directories and the 'index.html' file. The 'metadata' directory is\
        deleted and recreated by default.")
    argument_parser.add_argument(
        "file_path",
        type=str,
        help="The '.json' file containing all metadata (in the form of an\
        array of JSON objects) from which the user interface will be\
        generated.")
    arguments: Namespace = argument_parser.parse_args()
    print(arguments, file=sys.stderr)
    print("this is the end!")
    # Set parameters for datalad_catalog()
    metadata_file = arguments.file_path
    script_path = os.path.realpath(__file__)
    sep = os.path.sep
    repo_path = sep.join(script_path.split(sep)[0:-2])
    package_path = sep.join(script_path.split(sep)[0:-1])
    if arguments.outputdir:
        out_dir = arguments.outputdir
    else:
        out_dir = os.path.join(repo_path, '_build')
    # Call main function to generate UI
    datalad_catalog(
        metadata_file,
        out_dir,
        repo_path,
        package_path,
        arguments.force)


def datalad_catalog(metadata_file, out_dir, repo_path, package_path,
                    overwrite):
    """
    Generate web-browser-based user interface for browsing metadata of a
    DataLad dataset.

    WORKFLOW:
    Step 1:
    Load JSON data
    Step 2:
    Loop through all metadata objects, map to correct fields, create json
    blob per dataset, containing all data relevant to that dataset,
    including links to children and parent. LOGIC:
        a. Find all objects with type dataset
        b. For each dataset:
        - Find md5sum of id and version.
        - Check if associated file/object has already been created. If yes,
            load object from file. If not, create empty object.
        - Populate key-value pairs based on extractor type (metalad_core,
            metalad_core_dataset, metalad_studyminimeta)
        - Add extra key-value pairs required for UI, but not contained in any
            extractors or not available in required format
        - Find all subdatasets for current dataset. For each subdataset,
            create an object and:
            + add standard dataset fields (id, version, etc)
            + add subdataset and path/directory details to the 'children'
                array of the parent dataset
        - Find all files for current dataset. For each file:
            + add file and path/directory details to the 'children' array of
                the parent dataset
        c. ...
    Step 3:
    From above, create a single json file with an array of superdatasets
    Step 4:
    Create/copy html, js, css from templates.
    ...

    EXAMPLE USAGE:
    > datalad_catalog -o <path-to-output-directory> <path-to-input-file>
    """
    # Create output directories if they do not exist
    metadata_out_dir = setup_metadata_dir(out_dir)
    templates_path = os.path.join(package_path, 'templates')
    # Load data from input file
    # (assume for now that the data were exported by using `datalad meta-dump`,
    # and that all exported objects were added to an array in a json file)
    metadata = load_json_file(metadata_file)
    # Isolate the superdataset, write to file
    super_ds = search_superdataset(metadata)
    write_superdataset(super_ds, metadata_out_dir)
    # Grab all datasets from metadata
    datasets = filter_metadata_objects(metadata,
                                       options_dict={"type": "dataset"})
    # Initialise empty list for appending indices of processed datasets
    processed_datasets = []
    # Loop through datasets
    for i_ds, dataset in enumerate(datasets):
        # Skip iteration if object has already been processed
        blob_hash = md5blob(dataset["dataset_id"], dataset["dataset_version"])
        if blob_hash in processed_datasets:
            continue
        # Process this dataset, other related datasets, subdatasets, and files
        processed_datasets, new_obj = \
            process_dataset(dataset, datasets, processed_datasets,
                            metadata, metadata_out_dir, templates_path)

    # Write parent dataset name and shortname to all subdataset blobs
    for parent_hash in processed_datasets:
        parent_file = os.path.join(metadata_out_dir, parent_hash + ".json")
        parent_ds = load_json_file(parent_file)
        for child_hash in parent_ds["subdataset_blobs"]:
            child_file = os.path.join(metadata_out_dir, child_hash + ".json")
            ds = load_json_file(child_file)
            ds["root_dataset_name"] = parent_ds["name"]
            ds["root_dataset_short_name"] = parent_ds["short_name"]
            with open(child_file, 'w') as f:
                json.dump(ds, f)

    # Copy all remaining components from templates to output directory
    copy_ui_content(repo_path, out_dir, package_path, overwrite)


# --------------------
# Function definitions
# --------------------
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


def process_dataset(dataset, all_datasets, processed_datasets,
                    metadata, metadata_out_dir, templates_path):
    """
    Process all metadata items extracted for a dataset on the dataset level
    """

    blob_hash = md5blob(dataset["dataset_id"], dataset["dataset_version"])
    processed_datasets.append(blob_hash)
    # TODO: make sure that this section is called at all the correct places
    # idx_list = find_dataset_objects(all_datasets,
    #                                 dataset["dataset_id"],
    #                                 dataset["dataset_version"])
    # processed_datasets.extend(idx_list)
    # Grab all datasets with the same id and version
    same_datasets = filter_metadata_objects(
        all_datasets,
        options_dict={
            "dataset_id": dataset["dataset_id"],
            "dataset_version": dataset["dataset_version"]
        })
    # Initialise new object from metadata
    # TODO: this call might be unnecessarily checking if a file
    # already exists, follow this up.
    new_obj, blob_file = get_dataset_object(dataset["dataset_id"],
                                            dataset["dataset_version"],
                                            metadata_out_dir)
    # Populate key-value pairs based on extractor type
    for ds_item in same_datasets:
        if "extractor_name" in ds_item:
            new_obj = parse_metadata_object(ds_item, new_obj, templates_path)
        else:
            # TODO: handle scenarios where metadata is not generated by
            # DataLad (or decide not to allow this)
            print("Unrecognized metadata type: non-DataLad")
    # Add missing fields required for UI
    new_obj = add_missing_fields(new_obj, templates_path)
    # Get all subdatasets of current dataset
    subdatasets = filter_metadata_objects(
                    all_datasets,
                    options_dict={
                        "root_dataset_id": dataset["dataset_id"],
                        "root_dataset_version": dataset["dataset_version"]
                    })
    # If subdatasets exist, add them to superdataset list and to
    # main dataset object
    sub_blob_hashes = []
    subdataset_objects = []
    subdataset_keywords = set([])
    for subds in subdatasets:
        sub_blob_hash = md5blob(subds["dataset_id"], subds["dataset_version"])
        if sub_blob_hash not in sub_blob_hashes:
            sub_blob_hashes.append(sub_blob_hash)
        if sub_blob_hash in processed_datasets:
            continue
        # Process this subds, other related datasets, subdatasets, and files
        processed_datasets, subds_obj = \
            process_dataset(subds, all_datasets, processed_datasets,
                            metadata, metadata_out_dir, templates_path)
        subdataset_objects.append(subds_obj)
        subdataset_keywords.update(subds_obj["keywords"])
    # Then populate subdataset details and append to current dataset
    # 'subdatasets' field
    new_obj["subdataset_blobs"] = sub_blob_hashes
    new_obj["subdataset_keywords"] = list(subdataset_keywords)
    new_obj = add_update_subdatasets(dataset_object=new_obj,
                                     subdatasets=subdataset_objects)
    # Find all files with the main object as parent dataset, and add
    # them as children
    files = filter_metadata_objects(
                metadata,
                options_dict={
                    "type": "file",
                    "dataset_id": dataset["dataset_id"],
                    "dataset_version": dataset["dataset_version"]
                })
    new_obj = add_update_files(dataset_object=new_obj, files=files)
    # Write main data object to file
    with open(blob_file, 'w') as fp:
        json.dump(new_obj, fp)

    return processed_datasets, new_obj


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
    if metadata_path.exists() and metadata_path.is_dir():
        shutil.rmtree(metadata_path)
    Path(metadata_path).mkdir(parents=True)
    return metadata_path


def copy_ui_content(repo_path, out_dir, package_path, overwrite):
    """
    Copy all content required for the user interface to render

    This includes assets (JS, CSS), artwork and the main html.
    """
    content_paths = {
        "assets": Path(package_path) / 'assets',
        "artwork": Path(repo_path) / 'artwork',
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


def get_md5_details(dataset_id, dataset_version, data_dir):
    """
    Return an md5 hash of a dataset id and version, as well
    as the path for the file representing this dataset object
    """
    blob_hash = md5blob(dataset_id, dataset_version)
    blob_file = os.path.join(data_dir, blob_hash + ".json")
    return blob_hash, blob_file
    

def get_dataset_object(dataset_id, dataset_version, data_dir):
    """
    Get a JSON object pertaining to a UI dataset from file if the file exists,
    else return an empty object.
    """
    blob_hash = md5blob(dataset_id, dataset_version)
    blob_file = os.path.join(data_dir, blob_hash + ".json")
    if os.path.isfile(blob_file):
        return load_json_file(blob_file), blob_file
    else:
        return {}, blob_file


def parse_metadata_object(src_object, dest_object, schema_path):
    """
    Parse a single metadata item )from the list input to `datalad_catalog`),
    using a different parser based on the `extractor_name` field of the item.
    """
    if src_object["extractor_name"] == "metalad_core_dataset":
        schema_file = os.path.join(schema_path, "core_dataset_schema.json")
        dest_object = core_dataset_parse(src_object, dest_object, schema_file)
    elif src_object["extractor_name"] == "metalad_studyminimeta":
        schema_file = os.path.join(schema_path, "studyminimeta_schema.json")
        dest_object = studyminimeta_parse(src_object, dest_object, schema_file)
    elif src_object["extractor_name"] == "metalad_core":
        schema_file = os.path.join(schema_path, "core_schema.json")
        dest_object = core_parse(src_object, dest_object, schema_file)
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
            dataset_object["short_name"] = dataset_object["name"][0, 30]+'...'
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
    for subds in subdatasets:
        # TODO: check if the subdatasets already exist and decide whether
        # to overwrite or skip. Currently overwritten
        new_sub_obj = copy_key_vals(src_object=subds,
                                    dest_object={},
                                    keys=["dataset_id",
                                          "dataset_version",
                                          "dataset_path",
                                          "extraction_time",
                                          "name",
                                          "short_name",
                                          "doi",
                                          "url",
                                          "license",
                                          "authors",
                                          "keywords",
                                          ])
        sep = os.path.sep
        new_sub_obj["dirs_from_path"] = subds["dataset_path"].split(sep)
        if not object_in_list(attribute_key="dataset_id",
                              attribute_val=subds["dataset_id"],
                              search_list=dataset_object["subdatasets"]):
            dataset_object["subdatasets"].append(new_sub_obj)
            print(f"New subds added: obj={new_sub_obj}\n")
        else:
            # subidx = next((i for i, item in
            #                enumerate(dataset_object["subdatasets"])
            #                if item["dataset_id"] == subds["dataset_id"]), -1)
            # dataset_object["subdatasets"][subidx] = new_sub_obj
            print(f"subds replaced: not really, obj={new_sub_obj}\n")
            continue
        # Add subdataset locations as children to parent dataset
        nr_nodes = len(new_sub_obj["dirs_from_path"])
        iter_object = dataset_object["children"]
        idx = -1
        for n, node in enumerate(new_sub_obj["dirs_from_path"]):
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


def core_parse(src_object, dest_object, schema_file):
    """
    Parse metadata output by DataLad's `metalad_core` extractor and
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
                       if "name" in item and item["@name"] == "origin"), False)
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
        print("Error: object where '@type' equals 'CreativeWork' not found in \
               src_object['extracted_metadata']['@graph'] during studyminimeta\
                    extraction")
    metadata["dataset"] = next((item for item
                                in src_object["extracted_metadata"]["@graph"]
                                if "@type" in item
                                and item["@type"] == "Dataset"), False)
    if not metadata["dataset"]:
        print("Error: object where '@type' equals 'Dataset' not found in \
               src_object['extracted_metadata']['@graph'] during studyminimeta\
                    extraction")
    metadata["publicationList"] = \
        next((item for item in src_object["extracted_metadata"]["@graph"]
              if "@id" in item and item["@id"] == "#publicationList"), False)
    if not metadata["publicationList"]:
        print("Error: object where '@id' equals '#publicationList' not found\
               in src_object['extracted_metadata']['@graph'] during\
               studyminimeta extraction")
    else:
        metadata["publicationList"] = metadata["publicationList"]["@list"]
    metadata["personList"] = \
        next((item for item in src_object["extracted_metadata"]["@graph"]
              if "@id" in item and item["@id"] == "#personList"), False)
    if not metadata["personList"]:
        print("Error: object where '@id' equals '#personList' not found in\
               src_object['extracted_metadata']['@graph'] during\
               studyminimeta extraction")
    else:
        metadata["personList"] = metadata["personList"]["@list"]
    # Standard/straightforward fields: copy source to dest values per key
    for key in schema:
        if isinstance(schema[key], list) and len(schema[key]) == 2:
            dest_object[key] = metadata[schema[key][0]][schema[key][1]]
        else:
            dest_object[key] = schema[key]
    # Authors
    for author in metadata["dataset"]["author"]:
        author_details = \
            next((item for item in metadata["personList"]
                  if item["@id"] == author["@id"]), False)
        if not author_details:
            idd = author["@id"]
            print(f"Error: Person details not found in '#personList' for\
                  '@id' = {idd}")
        else:
            dest_object["authors"].append(author_details)
    # Publications
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
