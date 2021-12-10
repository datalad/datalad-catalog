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
        self.node_type = cnst.DATASET
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
    """"""
    # Dictionary to select relevant class based on the extractor used to
    # generate the incoming metadata object
    translatorSelector = {
        cnst.EXTRACTOR_CORE: CoreTranslator,
        cnst.EXTRACTOR_CORE_DATASET: CoreDatasetTranslator,
        cnst.EXTRACTOR_CORE_FILE: CoreFileTranslator,
        cnst.EXTRACTOR_STUDYMINIMETA: StudyminimetaTranslator,
    }

    def __init__(self) -> None:
        pass


class CoreTranslator(ABC):
    """"""

    def __init__(self) -> None:
        pass


class StudyminimetaTranslator(ABC):
    """"""

    def __init__(self) -> None:
        pass


class CoreDatasetTranslator(ABC):
    """"""

    def __init__(self) -> None:
        pass


class CoreFileTranslator(ABC):
    """"""

    def __init__(self) -> None:
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





