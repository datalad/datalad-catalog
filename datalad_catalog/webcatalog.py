import sys
import json
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import hashlib
from . import constants as cnst

# Reminders:
# Instance method
# @classmethod
# @staticmethod
# @property




# PSEUDOCODE/WORKFLOW:
# 1) Command line call
# 2) Incoming metadata 
# 3) class Catalog(Interface):
#   - parses incoming data and arguments
#   - handles argument errors/warnings
#   - creates or accesses existing catalog via class WebCatalog
#   - decides how to handle incoming stream vs individual objects
#   - handles individual objects via class Translator





class WebCatalog:
    """
    The main catalog class. This is also a datalad dataset
    """

    def __init__(self, location: Path, main_id: str = None, main_version: str = None) -> None:
        self.location = location
        self.main_id = main_id
        self.main_version = main_version

    def is_created(self) -> bool:
        """
        Check if catalog directory exists at location
        """
        catalog_path = Path(self.location)
        if catalog_path.exists() and catalog_path.is_dir():
            return True
        return False

    def create(self, force=False, config=None):
        """
        Create new catalog directory with assets (JS, CSS), artwork and the main html
        """

        metadata_path = Path(self.location) / 'metadata'
        if not (metadata_path.exists() and metadata_path.is_dir()):
            Path(metadata_path).mkdir(parents=True)

        content_paths = {
            "assets": Path(cnst.PACKAGE_PATH) / 'assets',
            "artwork": Path(cnst.PACKAGE_PATH) / 'artwork',
            "html": Path(cnst.PACKAGE_PATH) / 'index.html',
        }
        out_dir_paths = {
            "assets": Path(self.location) / 'assets',
            "artwork": Path(self.location) / 'artwork',
            "html": Path(self.location) / 'index.html',
        }
        for key in content_paths:
            copy_overwrite_path(src=content_paths[key],
                                dest=out_dir_paths[key],
                                overwrite=force)

    def add_dataset():
        """"""
    
    def remove_dataset():
        """"""
    
    def set_main_dataset(self):
        """
        Save self.main_id and self.main_version to the "super.json" file
        in order to link the main dataset to the catalog.

        If "super.json" file already exists:
            - currently overwrites
            - TODO: provide warning (and instructions for how to overwrite?)
        """
        main_obj = {
            cnst.DATASET_ID: self.main_id,
            cnst.DATASET_VERSION: self.main_version
        }
        main_file = Path(self.location) / 'metadata' / "super.json"
        with open(main_file, 'w') as f:
            json.dump(main_obj, f)
        return main_file

    def serve():
        """Start local webserver, open catalog html"""

    def add_sibling():
        """For hosting catalog on e.g. GitHub"""


class Node:
    """
    A node in the directory tree of a catalog dataset, for which a metadata
    file will be created.

    Required arguments:
    id -- parent dataset id
    version -- parent dataset version
    path -- path of node relevant to parent dataset
    """

    def __init__(self, id=None, version=None, path=None) -> None:
        """
        
        """
        self.id = id
        self.version = version
        self.path = path
        self.long_name = self.get_long_name()
        self.md5_hash = self.md5hash(self.long_name)
        self.node_type = cnst.DIRECTORY
        self.file_name = None
        self.children = []
        
        # Children type: file, directory, dataset
        self.children = []

    def create_file(self):
        """
        Create catalog metadata file for current node
        """

    def load_file(self):
        """
        Load content from catalog metadata file for current node
        """
        try:
            with open(self.long_name) as f:
                return json.load(f)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def get_long_name(self):
        """
        Concatenate dataset id, dataset version, and node path

        """
        long_name = self.dataset_id + "-" + self.dataset_version
        if self.node_path:
            long_name = long_name + f"-{self.node_path}"
        return long_name

    def add_missing_fields(self, meta_object, node_object):
        """"""

    def md5hash(self, txt):
        """
        Create md5 hash of the input string
        """
        txt_hash = hashlib.md5(txt.encode('utf-8')).hexdigest()
        return txt_hash


class Dataset(Node):
    """
    A dataset is a top-level node, and has additional properties that pertain
    to datasets 
    """

    def __init__(self, id: str=None, version: str=None) -> None:
        self.path = ''
        self.node_type = cnst.TYPE_DATASET
        self.long_name = self.get_long_name(self.id, self.version, self.path)
        self.md5_hash = self.md5hash(self.long_name)
        self.children = []
    
    def create_file(self):
        """
        Create catalog metadata file for current node
        """

    def load_file(self):
        """
        Load content from catalog metadata file for current node
        """

    def add_metadata(self):
        """
        """




class Translator():
    """
    Parse a single metadata item from the list input to `datalad_catalog`,
    using a different parser based on the `extractor_name` field of the item.
    Uses subclasses for extractor-specific parsing.
    """
    # Dictionary to select relevant class based on the extractor used to
    # generate the incoming metadata object
    translatorSelector = {
        cnst.EXTRACTOR_CORE: CoreTranslator,
        cnst.EXTRACTOR_CORE_DATASET: CoreDatasetTranslator,
        cnst.EXTRACTOR_STUDYMINIMETA: StudyminimetaTranslator,
    }

    # Get package-related paths/content
    package_path = Path(__file__).resolve().parent
    templates_path = package_path / 'templates'

    def __init__(self, meta_object, node_object) -> None:
        try:
            
            newTranslator = self.translatorSelector.get(meta_object[cnst.EXTRACTOR_NAME])(meta_object, node_object)
        except:
            # TODO: handle unrecognised extractors
            pass

    def load_schema(self, meta_object, node_object):
        schema = load_json_file(self.schema_file)
        # Copy source to destination values, per key
        for key in schema:
            if schema[key] in meta_object:
                node_object[key] = meta_object[schema[key]]
        return node_object
    


class CoreTranslator(Translator):
    """
    Parse metadata output by DataLad's `metalad_core` extractor and
    translate into JSON structure from which UI is generated.
    """

    typeSelector = {
        cnst.TYPE_DATASET: dataset_translator,
        cnst.TYPE_FILE: file_translator,
    }

    def __init__(self, meta_object, node_object) -> None:
        """"""
        # node_object = self.typeSelector.get(cnst.TYPE)()
        # Assign schema file for dataset/file
        self.type = meta_object[cnst.TYPE]
        if meta_object[cnst.TYPE] == cnst.TYPE_DATASET:
            self.schema_file = self.package_path / cnst.SCHEMA_CORE_FOR_DATASET
        else:
            self.schema_file = self.package_path / cnst.SCHEMA_CORE_FOR_FILE
        # Load basic fields for dataset/file from schema
        node_object = self.load_schema(self, meta_object, node_object)
        # Populate URL field (common to file and dataset?)
        ds_info = next((item for item in meta_object[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
                        # TODO: CHECK IF THIS ONLY GETS RUL FIELD FOR DATASET!!!
        if ds_info and cnst.DISTRIBUTION in ds_info:
            origin = next((item for item in ds_info[cnst.DISTRIBUTION]
                        if cnst.NAME in item and item[cnst.NAME] == cnst.ORIGIN), False)
            if origin:
                node_object[cnst.URL] = origin[cnst.URL]
        # Add dataset-specific fields
        if self.type == cnst.TYPE_DATASET:
            node_object = self.dataset_translator(self, meta_object, node_object)
        # Add extractor type to 

    def dataset_translator(self, meta_object, node_object):
        """
        Parse dataset-level metadata output by DataLad's `metalad_core` extractor
        """
        ds_info = next((item for item in meta_object[cnst.EXTRACTED_METADATA][cnst.ATGRAPH]
                        if cnst.ATTYPE in item and item[cnst.ATTYPE] == cnst.DATASET), False)
        # Populate subdatasets field
        node_object[cnst.SUBDATASETS] = []
        if ds_info and cnst.HASPART in ds_info:
            for subds in ds_info[cnst.HASPART]:
                sub_dict = {
                    cnst.DATASET_ID: subds[cnst.IDENTIFIER].strip(cnst.STRIPDATALAD),
                    cnst.DATASET_VERSION: subds[cnst.ATID].strip(cnst.STRIPDATALAD),
                    cnst.DATASET_PATH: subds[cnst.NAME],
                    cnst.DIRSFROMPATH: list(Path(subds[cnst.NAME]).parts)
                }
                node_object[cnst.SUBDATASETS].append(sub_dict)

        # Populate extractor field
        extractor_dict = {
            cnst.EXTRACTOR_NAME: meta_object[cnst.EXTRACTOR_NAME],
            cnst.EXTRACTOR_VERSION: subds[cnst.ATID].strip(cnst.STRIPDATALAD),
            cnst.DATASET_PATH: subds[cnst.NAME],
            cnst.DIRSFROMPATH: list(Path(subds[cnst.NAME]).parts)
        }
        "extractor_name": "metalad_core", "extractor_version": "1", "extraction_parameter": {}, "extraction_time": 1636623469.594389,
        return node_object


class StudyminimetaTranslator(Translator):
    """"""

    def __init__(self, meta_object, node_object) -> None:
        self.schema_file = self.package_path / cnst.SCHEMA_STUDYMINIMETA

#     metadata = {}
#     # Extract core objects/lists from src_object
#     metadata["study"] = next((item for item
#                               in src_object["extracted_metadata"]["@graph"]
#                               if "@type" in item
#                               and item["@type"] == "CreativeWork"), False)
#     if not metadata["study"]:
#         print("Warning: object where '@type' equals 'CreativeWork' not found in \
# src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    
#     metadata["dataset"] = next((item for item
#                                 in src_object["extracted_metadata"]["@graph"]
#                                 if "@type" in item
#                                 and item["@type"] == "Dataset"), False)
#     if not metadata["dataset"]:
#         print("Warning: object where '@type' equals 'Dataset' not found in \
# src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
    
#     metadata["publicationList"] = \
#         next((item for item in src_object["extracted_metadata"]["@graph"]
#               if "@id" in item and item["@id"] == "#publicationList"), False)
#     if not metadata["publicationList"]:
#         print("Warning: object where '@id' equals '#publicationList' not found \
# in src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
#     else:
#         metadata["publicationList"] = metadata["publicationList"]["@list"]
    
#     metadata["personList"] = \
#         next((item for item in src_object["extracted_metadata"]["@graph"]
#               if "@id" in item and item["@id"] == "#personList"), False)
#     if not metadata["personList"]:
#         print("Warning: object where '@id' equals '#personList' not found in \
# src_object['extracted_metadata']['@graph'] during studyminimeta extraction")
#     else:
#         metadata["personList"] = metadata["personList"]["@list"]
    
#     # Standard/straightforward fields: copy source to dest values per key
#     for key in schema:
#         if isinstance(schema[key], list) and len(schema[key]) == 2:
#             if schema[key][0] in metadata \
#                and schema[key][1] in metadata[schema[key][0]]:
#                 dest_object[key] = metadata[schema[key][0]][schema[key][1]]
#         else:
#             dest_object[key] = schema[key]
#     # Description
#     dest_object["description"] = dest_object["description"].replace('<', '')
#     dest_object["description"] = dest_object["description"].replace('>', '')
#     # Authors
#     for author in metadata["dataset"]["author"]:
#         author_details = \
#             next((item for item in metadata["personList"]
#                   if item["@id"] == author["@id"]), False)
#         if not author_details:
#             idd = author["@id"]
#             print(f"Error: Person details not found in '#personList' for '@id'={idd}")
#         else:
#             dest_object["authors"].append(author_details)
#     # Publications
#     if metadata["publicationList"]:
#         for pub in metadata["publicationList"]:
#             new_pub = {"type" if k == "@type" else k: v for k, v in pub.items()}
#             new_pub = {"doi" if k == "sameAs"
#                     else k: v for k, v in new_pub.items()}
#             new_pub["publication"] = {"type" if k == "@type"
#                                     else k: v for k, v in new_pub.items()}
#             if "@id" in new_pub:
#                 new_pub.pop("@id")
#             if "@id" in new_pub["publication"]:
#                 new_pub["publication"].pop("@id")
#             for i, author in enumerate(new_pub["author"]):
#                 author_details = \
#                     next((item for item in metadata["personList"]
#                         if item["@id"] == author["@id"]), False)
#                 if not author_details:
#                     idd = author["@id"]
#                     print(f"Error: Person details not found in '#personList' for\
#                         @id = {idd}")
#                 else:
#                     new_pub["author"][i] = author_details
#             dest_object["publications"].append(new_pub)
#     return dest_object


class CoreDatasetTranslator(Translator):
    """"""

    def __init__(self, meta_object, node_object) -> None:
        pass




def copy_overwrite_path(src: Path, dest: Path, overwrite: bool = False):
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



