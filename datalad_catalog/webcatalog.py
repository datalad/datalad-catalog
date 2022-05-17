import sys
import json
from pathlib import Path
import shutil
import hashlib
from . import constants as cnst
import logging
from .utils import read_json_file
from jsonschema import Draft202012Validator, RefResolver
import yaml
lgr = logging.getLogger('datalad.catalog.webcatalog')

# PSEUDOCODE/WORKFLOW:
# 1) Command line call
# 2) Incoming metadata 
# 3) class Catalog(Interface):
#   - parses incoming data and arguments
#   - handles argument errors/warnings
#   - creates or accesses existing catalog via class WebCatalog
#   - calls relevant function based on subcommand: [create / add / remove / serve / set-super
# [create]:
#   - if catalog does not exist, create it
#   - if catalog exists and force flag is True, overwrite assets of existing catalog (not metadata)
#   - if create was called together with metadata, pass on to [add]
# [add]:
#   - handles argument errors/warnings
#   - establishes data input type: incoming stream vs file vs individual objects or other
#   - loops through meta_objects in incoming stream/file:
#       - handles individual objects via class Translator

CATALOG_SCHEMA_IDS = {
    cnst.CATALOG: "https://datalad.org/catalog.schema.json",
    cnst.TYPE_DATASET: "https://datalad.org/catalog.dataset.schema.json",
    cnst.TYPE_FILE: "https://datalad.org/catalog.file.schema.json",
    cnst.AUTHORS: "https://datalad.org/catalog.authors.schema.json",
    # cnst.CHILDREN: "https://datalad.org/catalog.children.schema.json",
    cnst.EXTRACTORS: "https://datalad.org/catalog.extractors.schema.json"
}

class WebCatalog(object):
    """
    The main catalog class.
    """

    # Get package-related paths
    package_path = Path(__file__).resolve().parent
    templates_path = package_path / 'templates'
    # Set up schema store and validator
    SCHEMA_STORE = {}
    for schema_type, schema_id in CATALOG_SCHEMA_IDS.items():
        schema_path = templates_path / f"jsonschema_{schema_type}.json"
        schema = read_json_file(schema_path)
        SCHEMA_STORE[schema['$id']] = schema
    CATALOG_SCHEMA = SCHEMA_STORE[CATALOG_SCHEMA_IDS[cnst.CATALOG]]
    RESOLVER = RefResolver.from_schema(CATALOG_SCHEMA, store=SCHEMA_STORE)
    VALIDATOR = Draft202012Validator(CATALOG_SCHEMA, resolver=RESOLVER)

    def __init__(self, location: str, main_id: str = None, main_version: str = None, config_file: str = None) -> None:
        self.location = Path(location)
        self.main_id = main_id
        self.main_version = main_version
        self.metadata_path = Path(self.location) / 'metadata'
        self.config_path = self.set_config_source(config_file)
        self.config = self.get_config()

    def path_exists(self) -> bool:
        """
        Check if directory exists at location (could be a catalog or any other directory)
        """
        catalog_path = Path(self.location)
        if catalog_path.exists() and catalog_path.is_dir():
            return True
        return False

    def is_created(self) -> bool:
        """
        Check if directory exists at location, and if main subdirectories also
        exist. This identifies the location as a datalad catalog.
        """

        is_created = self.path_exists()
        out_dir_paths = {
            "assets": Path(self.location) / 'assets',
            "artwork": Path(self.location) / 'artwork',
            "html": Path(self.location) / 'index.html',
        }
        for key in out_dir_paths:
            is_created = is_created and out_dir_paths[key].exists()
        return is_created

    def create(self, force=False):
        """
        Create new catalog directory with assets (JS, CSS), artwork, config and the main html
        """

        # Get package-related paths/content
        package_path = Path(__file__).resolve().parent

        if not (self.metadata_path.exists() and self.metadata_path.is_dir()):
            Path(self.metadata_path).mkdir(parents=True)

        content_paths = {
            "assets": Path(package_path) / 'assets',
            "artwork": Path(package_path) / 'artwork',
            "html": Path(package_path) / 'index.html',
            "config": self.config_path,
        }
        out_dir_paths = {
            "assets": Path(self.location) / 'assets',
            "artwork": Path(self.location) / 'artwork',
            "html": Path(self.location) / 'index.html',
            "config": Path(self.location) / 'config.yml',
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
        main_file = Path(self.metadata_path) / "super.json"
        with open(main_file, 'w') as f:
            json.dump(main_obj, f)
        return main_file

    def set_config_source(self, source_str=None):
        """"""        
        # If no source_str provided, determine
        if self.is_created():
            # If catalog already exists, return config if it exists, otherwise None
            config_path = Path(self.location / 'config.yml')
            if config_path.exists():
                return config_path
            # TODO: if catalog exists without config file, should one be created from default?
            return None
        else:
            # If catalog does not exist, return config if specified, otherwise default
            if source_str is not None:
                return Path(source_str)
            else:
                return Path(self.templates_path / 'config.yml')

    def get_config(self):
        """"""
        # Read metadata from file
        with open(self.config_path, "rt") as input_stream:
            # print(yaml.safe_load(input_stream))
            return yaml.safe_load(input_stream)



class Node(object):
    """
    A node in the directory tree of a catalog dataset, for which a metadata
    file will be created.

    Required arguments:
    type -- 'directory' | 'dataset'
    dataset_id -- parent dataset id
    dataset_version -- parent dataset version
    path -- path of node relevant to parent dataset
    """

    _split_dir_length = 3
    _instances = {}

    def __init__(self, type=None, dataset_id=None, dataset_version=None, node_path=None) -> None:
        """
        type = 'directory' | 'dataset'
        """
        self.dataset_id= dataset_id
        self.dataset_version = dataset_version
        self.node_path = node_path
        self.long_name = self.get_long_name()
        self.md5_hash = self.md5hash(self.long_name)
        self.type = type
        self.file_name = None
        # Children type: file, node(directory), dataset
        self.children = []
        self._instances[self.md5_hash] = self
        self.parent_catalog = None

    def is_created(self) -> bool:
        """
        Check if node exists in metadata of catalog
        """
        if self.get_location().exists() and self.get_location().is_file():
            return True
        return False

    def create_file(self):
        """
        Create catalog metadata file for current node
        """
        node_fn = self.get_location()

    def load_file(self):
        """
        Load content from catalog metadata file for current node
        """
        try:
            with open(self.get_location()) as f:
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
            long_name = long_name + "-" + str(self.node_path)
        return long_name

    def get_location(self):
        """
        Get node file location from  dataset id, dataset version, and node path
        using a file system structure similar to RIA stores
        """
        # /metadata/dataset_id/dataset_verion/id_version_hash.json
        if not hasattr(self, 'node_path') and self.type=='dataset':
            self.node_path=None

        if not hasattr(self, 'md5_hash'):
            self.long_name = self.get_long_name()
            self.md5_hash = self.md5hash(self.long_name)

        hash_path_left, hash_path_right = self.split_dir_name(self.md5_hash)
        node_fn = self.parent_catalog.metadata_path / self.dataset_id / \
            self.dataset_version / hash_path_left / hash_path_right
        node_fn = node_fn.with_suffix('.json')
        return node_fn

    def md5hash(self, txt):
        """
        Create md5 hash of the input string
        """
        txt_hash = hashlib.md5(txt.encode('utf-8')).hexdigest()
        return txt_hash

    def split_dir_name(self, dir_name):
        """
        Split a string into two parts

        Args:
            dir_name ([type]): [description]

        Returns:
            [type]: [description]
        """
        path_left = dir_name[:self._split_dir_length]
        path_right = dir_name[self._split_dir_length:]
        return path_left, path_right

    def add_attribrutes(self, new_attributes: dict, overwrite=True):
        """"""
        for key in new_attributes.keys():
            if hasattr(self, key):
                # Only overwrite if flag is True AND the new property actually has content
                # This prevents existing content from being overwritten by empty arrays/dicts
                # TODO: this should be replaced by the enhancement to allow multiple sources of
                # content (i.e. from multiple extractors) for the same attribute.
                if overwrite and bool(new_attributes[key]):
                    message = (f"Node instance already has an attribute '{key}'. Overwriting attribute value with non-zero/null content."
                        "To prevent overwriting, set 'overwrite' argument to False")
                    lgr.warning(message)
                    setattr(self, key, new_attributes[key])
            else:
                setattr(self, key, new_attributes[key])

    def add_child(self, meta_dict: dict):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        child_found = next((item for item in self.children
                        if item[cnst.TYPE] == meta_dict[cnst.TYPE]
                        and item[cnst.NAME] == meta_dict[cnst.NAME]), False)
        if not child_found:
            self.children.append(meta_dict)
        else:
            pass

    def add_extractor(self, extractor_dict: dict):
        """"""
        if not hasattr(self, 'extractors_used') or not self.extractors_used:
            self.extractors_used = []

        extractor_found = next((item for item in self.extractors_used
                        if item[cnst.EXTRACTOR_NAME] == extractor_dict[cnst.EXTRACTOR_NAME]
                        and item[cnst.EXTRACTOR_VERSION] == extractor_dict[cnst.EXTRACTOR_VERSION]), False)
        if not extractor_found:
            self.extractors_used.append(extractor_dict)
        else:
            pass

    def write_to_file(self):
        """"""
        parent_path = self.get_location().parents[0]
        fn = self.get_location()
        created = self.is_created()

        # if hasattr(self, 'node_path') and self.type != 'dataset':
        #     setattr(self, 'path', str(self.node_path))
        # if hasattr(self, 'node_path') and self.type == 'directory':
        #     setattr(self, 'name', self.node_path.name)
        
        meta_dict = vars(self)
        keys_to_pop = ['node_path', 'long_name', 'md5_hash', 'file_name', 'parent_catalog']
        for key in keys_to_pop:
            meta_dict.pop(key, None)

        if not created:
            parent_path.mkdir(parents=True, exist_ok=True)
            with open(fn, 'w') as f:
                json.dump(vars(self), f)
        else:
            with open(fn, "r+") as f:
                f.seek(0)
                json.dump(vars(self), f)
                f.truncate()


def getNode(type, dataset_id, dataset_version, path=None):
    """"""
    name = dataset_id + '-' + dataset_version
    if path:
        name = name + '-' + str(path)
    md5_hash = hashlib.md5(name.encode('utf-8')).hexdigest()

    if md5_hash in Node._instances.keys():
        return Node._instances[md5_hash] 
    else:
        return Node(type, dataset_id, dataset_version, path)


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
