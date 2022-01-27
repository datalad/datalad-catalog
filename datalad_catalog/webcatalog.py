import sys
import json
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import hashlib
from . import constants as cnst
import logging
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

# TODO: should webcatalog be a subclass of datalad dataset?
class WebCatalog(object):
    """
    The main catalog class.
    """

    def __init__(self, location: str, main_id: str = None, main_version: str = None, force=False) -> None:
        self.location = Path(location)
        self.main_id = main_id
        self.main_version = main_version
        self.metadata_path = Path(self.location) / 'metadata'

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
        main_file = Path(self.metadata_path) / "super.json"
        with open(main_file, 'w') as f:
            json.dump(main_obj, f)
        return main_file


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
                if overwrite:
                    message = (f"Node instance already has an attribute '{key}'. Overwriting attribute value."
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
            shutil.copy2(src, dest)
        else:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
