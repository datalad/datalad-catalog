import sys
import json
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import hashlib
from . import constants as cnst
import logging
lgr = logging.getLogger('datalad.catalog.webcatalog')

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
#   - calls relevant function based on subcommand: [create / add / remove / serve / create-sibling]
# [create]:
#   - if catalog does not exist, create it
#   - if catalog exists and force flag is True, overwrite assets of existing catalog (not metadata)
#   - if create was called together with metadata, pass on to [add]
# [add]:
#   - handles argument errors/warnings
#   - establishes data input type: incoming stream vs file vs individual objects or other
#   - loops through meta_objects in incoming stream/file:
#       - handles individual objects via class Translator


# class Singleton(type):
#     """
#     This singleton design pattern is used as a metaclass by classes that 
#     """
#     _instances = {}
#     def __call__(cls, *args, **kwargs):
#         if cls not in cls._instances:
#             cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
#         return cls._instances[cls]

# TODO: should webcatalog be a subclass of datalad dataset???
class WebCatalog(object):
    """
    The main catalog class. This is also a datalad dataset
    """

    def __init__(self, location: Path, main_id: str = None, main_version: str = None) -> None:
        self.location = location
        self.main_id = main_id
        self.main_version = main_version
        self.metadata_path = Path(self.location) / 'metadata'

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

        # Get package-related paths/content
        package_path = Path(__file__).resolve().parent

        if not (self.metadata_path.exists() and self.metadata_path.is_dir()):
            Path(self.metadata_path).mkdir(parents=True)

        content_paths = {
            "assets": Path(package_path) / 'assets',
            "artwork": Path(package_path) / 'artwork',
            "html": Path(package_path) / 'index.html',
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


class Node(object):
    """
    A node in the directory tree of a catalog dataset, for which a metadata
    file will be created.

    Required arguments:
    dataset_id -- parent dataset id
    dataset_version -- parent dataset version
    path -- path of node relevant to parent dataset
    """

    _split_dir_length = 3
    _instances = {}

    # # Begin Flyweight
    # _unique_instances = WeakValueDictionary()
    # @classmethod
    # def _flyweight_id_from_args(cls, *args, **kwargs):
    #     id = kwargs.pop('id')
    #     return id, args, kwargs
    # # End Flyweight

    @classmethod
    def get(cls, *args, **kwargs):
        id = kwargs.pop('dataset_id')
        version = kwargs.pop('dataset_version')
        path = None
        if 'node_path' in kwargs:
            path = kwargs.pop('node_path')
        name = id + '-' + version
        if path:
            name = name + '-' + path
        md5_hash = hashlib.md5(name.encode('utf-8')).hexdigest()
        return cls._instances[md5_hash] if md5_hash in cls._instances.keys() else cls(dataset_id=id, dataset_version=version, node_path=path)

    def __init__(self, dataset_id=None, dataset_version=None, node_path=None) -> None:
        """
        node_type = 'directory' | 'dataset'
        """
        self.dataset_id= dataset_id
        self.dataset_version = dataset_version
        self.node_path = node_path
        self.long_name = self.get_long_name()
        self.md5_hash = self.md5hash(self.long_name)
        self.node_type = cnst.DIRECTORY
        self.file_name = None
        # Children type: file, node(directory), dataset
        self.children = []
        self._instances[self.md5_hash] = self
        

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
            long_name = long_name + "-" + self.node_path
        return long_name

    def get_location(self, metadata_dir):
        """
        Get node file location from  dataset id, dataset version, and node path
        using a file system structure similar to RIA stores
        """
        # /metadata/dataset_id/dataset_verion/id_version_hash.json
        hash_path_left, hash_path_right = self.split_dir_name(self.md5_hash)
        node_fn = Path(metadata_dir) / self.dataset_id / self.dataset_version / \
            hash_path_left / hash_path_right + '.json'
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

    def addAttribrutes(self, new_attributes: dict, overwrite=True):
        """"""
        for key in new_attributes.keys():
            if hasattr(self, key) and overwrite:
                message = f"Node instance already has an attribute '{key}'. Overwriting attribute value. \
                    To prevent overwriting, set 'overwrite' argument to False"
                lgr.warning(message)
            else:
                self.key = new_attributes[key]

    def add_child(self, meta_dict: dict):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        child_found = next((item for item in self.children
                        if item[cnst.TYPE] == meta_dict[cnst.TYPE]
                        and item[cnst.NAME] == meta_dict[cnst.NAME]), False)
        if child_found:
            message = f"Node child of type '{meta_dict[cnst.TYPE]}' \
                and name '{meta_dict[cnst.NAME]}' already exists."
            lgr.warning(message)
        else:
            self.children.append(meta_dict)
        example_file = {
            "type": "file",
            "name": "",
            "contentbytesize": int,
            "url": "",
        }
        example_directory = {
            "type": "directory",
            "name": "",
        }
        example_dataset = {
            "type": "dataset",
            "name": "dataset_name",
            "dataset_id": "",
            "dataset_version": "",
        }


def getNode(node_type, dataset_id, dataset_version, path=None):
    """"""
    name = dataset_id + '-' + dataset_version
    if path:
        name = name + '-' + path
    md5_hash = hashlib.md5(name.encode('utf-8')).hexdigest()

    if md5_hash in Node._instances.keys():
        return Node._instances[md5_hash] 
    else:
        if node_type == "dataset":
            return Node(dataset_id, dataset_version, path)
        else:
            return Dataset(dataset_id, dataset_version)


class Dataset(Node):
    """
    A dataset is a top-level node, and has additional properties that are
    specific to datasets 
    """

    def __init__(self, dataset_id: str=None, dataset_version: str=None, node_path: str=None) -> None:
        self.dataset_id= dataset_id
        self.dataset_version = dataset_version
        self.node_path = None
        self.long_name = self.get_long_name()
        self.md5_hash = self.md5hash(self.long_name)
        self.node_type = cnst.TYPE_DATASET
        self.file_name = None
        # Children type: file, node(directory), dataset
        self.children = []
        self._instances[self.md5_hash] = self


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
