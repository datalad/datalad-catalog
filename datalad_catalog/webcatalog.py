import sys
import json
from pathlib import Path
import shutil
import hashlib
from . import constants as cnst
import logging
from .utils import read_json_file, find_duplicate_object_in_list
from jsonschema import Draft202012Validator, RefResolver
import yaml

lgr = logging.getLogger("datalad.catalog.webcatalog")

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
    cnst.EXTRACTORS: "https://datalad.org/catalog.extractors.schema.json",
}


class WebCatalog(object):
    """
    The main catalog class.
    """

    # Get package-related paths
    package_path = Path(__file__).resolve().parent
    templates_path = package_path / "templates"
    # Set up schema store and validator
    SCHEMA_STORE = {}
    for schema_type, schema_id in CATALOG_SCHEMA_IDS.items():
        schema_path = templates_path / f"jsonschema_{schema_type}.json"
        schema = read_json_file(schema_path)
        SCHEMA_STORE[schema["$id"]] = schema
    CATALOG_SCHEMA = SCHEMA_STORE[CATALOG_SCHEMA_IDS[cnst.CATALOG]]
    RESOLVER = RefResolver.from_schema(CATALOG_SCHEMA, store=SCHEMA_STORE)
    VALIDATOR = Draft202012Validator(CATALOG_SCHEMA, resolver=RESOLVER)

    def __init__(
        self,
        location: str,
        main_id: str = None,
        main_version: str = None,
        config_file: str = None,
    ) -> None:
        self.location = Path(location)
        self.main_id = main_id
        self.main_version = main_version
        self.metadata_path = Path(self.location) / "metadata"
        self.config_path = self.get_config_source(config_file)
        if self.config_path is not None:
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
            "assets": Path(self.location) / "assets",
            "artwork": Path(self.location) / "artwork",
            "html": Path(self.location) / "index.html",
        }
        for key in out_dir_paths:
            is_created = is_created and out_dir_paths[key].exists()
        return is_created

    def create(self, force=False):
        """
        Create new catalog directory with assets (JS, CSS), artwork, config and the main html
        """

        # TODO: first validate config file (using jsonschema?)
        # Check logo path, if added to config
        if cnst.LOGO_PATH in self.config and self.config[cnst.LOGO_PATH]:
            if not Path(self.config[cnst.LOGO_PATH]).exists():
                msg = f"Error in config: the specified logo does not exist at path: {self.config[cnst.LOGO_PATH]}"
                raise FileNotFoundError(msg)

        # Get package-related paths/content
        if not (self.metadata_path.exists() and self.metadata_path.is_dir()):
            Path(self.metadata_path).mkdir(parents=True)

        content_paths = {
            "assets": Path(self.package_path) / "assets",
            "artwork": Path(self.package_path) / "artwork",
            "html": Path(self.package_path) / "index.html",
        }
        out_dir_paths = {
            "assets": Path(self.location) / "assets",
            "artwork": Path(self.location) / "artwork",
            "html": Path(self.location) / "index.html",
        }
        for key in content_paths:
            copy_overwrite_path(
                src=content_paths[key], dest=out_dir_paths[key], overwrite=force
            )

        # Copy / write config file
        self.write_config(force)

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
            cnst.DATASET_VERSION: self.main_version,
        }
        main_file = Path(self.metadata_path) / "super.json"
        with open(main_file, "w") as f:
            json.dump(main_obj, f)
        return main_file

    def get_config_source(self, source_str=None):
        """"""
        # If no source_str provided, determine
        if self.is_created():
            # If catalog already exists, return config if it exists, otherwise None
            config_path = Path(self.location / "config.json")
            if config_path.exists():
                return config_path
            # TODO: if catalog exists without config file, should one be created from default?
            return None
        else:
            # If catalog does not exist, return config if specified, otherwise default
            if source_str is not None:
                return Path(source_str)
            else:
                return Path(self.templates_path / "config.json")

    def get_config(self):
        """"""
        # Read metadata from file
        with open(self.config_path) as f:
            if self.config_path.suffix == ".json":
                return json.load(f)
            if self.config_path.suffix in [".yml", ".yaml"]:
                return yaml.safe_load(f)

    def write_config(self, force=False):
        """"""

        # Copy content specified by config
        if (
            cnst.LOGO_PATH in self.config
            and self.config[cnst.LOGO_PATH]
            and self.config[cnst.LOGO_PATH] != "artwork/catalog_logo.svg"
        ):
            existing_path = Path(self.config[cnst.LOGO_PATH])
            existing_name = existing_path.name
            new_path = Path(self.location) / "artwork" / existing_name
            copy_overwrite_path(
                src=existing_path, dest=new_path, overwrite=force
            )
            self.config[cnst.LOGO_PATH] = "artwork/" + existing_name

        new_config_path = Path(self.location) / "config.json"
        with open(new_config_path, "w") as f_config:
            json.dump(self.config, f_config)


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

    def __init__(
        self, type=None, dataset_id=None, dataset_version=None, node_path=None
    ) -> None:
        """
        type = 'directory' | 'dataset'
        """
        self.dataset_id = dataset_id
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
        Get node file location from dataset id, dataset version, and node path
        using a file system structure similar to RIA stores. Format:
        "/metadata/dataset_id/dataset_version/id_version_hash.json"
        """
        # /metadata/dataset_id/dataset_version/id_version_hash.json
        if not hasattr(self, "node_path") and self.type == "dataset":
            self.node_path = None

        if not hasattr(self, "md5_hash"):
            self.long_name = self.get_long_name()
            self.md5_hash = self.md5hash(self.long_name)

        hash_path_left, hash_path_right = self.split_dir_name(self.md5_hash)
        node_fn = (
            self.parent_catalog.metadata_path
            / self.dataset_id
            / self.dataset_version
            / hash_path_left
            / hash_path_right
        )
        node_fn = node_fn.with_suffix(".json")
        return node_fn

    def md5hash(self, txt):
        """
        Create md5 hash of the input string
        """
        txt_hash = hashlib.md5(txt.encode("utf-8")).hexdigest()
        return txt_hash

    def split_dir_name(self, dir_name):
        """
        Split a string into two parts

        Args:
            dir_name ([type]): [description]

        Returns:
            [type]: [description]
        """
        path_left = dir_name[: self._split_dir_length]
        path_right = dir_name[self._split_dir_length :]
        return path_left, path_right

    def add_attribrutes(
        self, new_attributes: dict, catalog: WebCatalog, overwrite=False
    ):
        """Add attributes (key-value pairs) to a Node as instance variables"""
        # Get config
        dataset_config = catalog.config[cnst.PROPERTY_SOURCE][cnst.TYPE_DATASET]
        # Get extractor / source. TODO: rework the extractors_used property, see https://github.com/datalad/datalad-catalog/issues/68
        try:
            data_source = new_attributes[cnst.EXTRACTORS_USED][0][
                cnst.EXTRACTOR_NAME
            ]
        except:
            data_source = None
        # Loop through provided keys
        for key in new_attributes.keys():
            # Add extractor
            if key == cnst.EXTRACTORS_USED:
                self.add_extractor(new_attributes[cnst.EXTRACTORS_USED][0])
                continue
            # Skip keys with empty values
            if not bool(new_attributes[key]):
                continue
            # create new or update existing attribute/variable
            setattr(
                self,
                key,
                self._update_attribute(
                    key, new_attributes, dataset_config, data_source, overwrite
                ),
            )

    def _update_attribute(
        self,
        key,
        new_attributes: dict,
        dataset_config: dict,
        data_source,
        overwrite=False,
    ):
        """Create new or update existing attribute/variable of a Node instance

        This function incorporates prioritizing instructions from the user-
        specified or default dataset-level config, reads the source of incoming
        metadata, and decides whether to:
        - create a new instance variable, if none exists
        - merge the existing instance variable value with that of the incoming
          data
        - overwrite the existing instance variable value (if/when applicable)
        -
        """
        # TODO: still need to use overwrite flag where it makes sense to do so

        # Extract config, existing, and new attribute values

        config_source = dataset_config.get(key, None)
        existing_value = None
        if hasattr(self, key):
            existing_value = getattr(self, key)
        new_value = new_attributes[key]

        # Decide what to do based on config. Options include:
        # 1. list of names of data sources (e.g. ["metalad_studyminimeta", "datacite_gin"])
        # 2. name of data source (e.g. extractor such as "metalad_core")
        # 3. "merge"
        # 4. "" (empty string) or None/null

        # 1. List of names of data sources
        if isinstance(config_source, list):
            """"""
            # Construct dict element for multisource list
            new_object = {"source": data_source, "content": new_value}
            new_list = [new_object]
            # If attribute does not exist yet, create it
            if existing_value is None:
                return new_list
            else:
                # Otherwise, merge into existing list
                # If an object with the same "source" value already exists,
                # replace value of the "content" key of existing object
                existing_object = find_duplicate_object_in_list(
                    existing_value, new_object, [cnst.SOURCE]
                )
                if existing_object is not None:
                    existing_object[cnst.CONTENT] = new_value
                    return existing_value
                else:
                    # Otherwise, merge new list into existing list
                    return existing_value + new_list
        # If data from a single source should be used
        elif config_source == data_source:
            return new_value
        # If data from multiple sources should be merged
        elif config_source == "merge":
            if existing_value is None:
                return new_value
            else:
                # First ensure that both existing and new values are lists
                if not isinstance(existing_value, list):
                    existing_value = [existing_value]
                if not isinstance(new_value, list):
                    new_value = [new_value]
                # Then determine type of variable in list and handle accordingly
                if isinstance(new_value[0], (str, int)):
                    return list(set(existing_value + new_value))
                if isinstance(new_value[0], object):
                    for new_object in new_value:
                        existing_object = find_duplicate_object_in_list(
                            existing_value, new_object, new_object.keys()
                        )
                        if existing_object is None:
                            existing_value.append(new_object)
                        else:
                            continue
                    return existing_value

        # If config has empty string or none/null or does not exist
        elif not bool(config_source):
            if existing_value is None:
                return new_value
            else:
                return existing_value
        else:
            # If a non priority source is present
            if (config_source != data_source) and (existing_value is None):
                return new_value
            else:
                # TODO: figure out if this is expected/ideal behaviour or not
                return existing_value

    def add_child(self, meta_dict: dict):
        """
        [summary]

        Returns:
            [type]: [description]
        """
        child_found = next(
            (
                item
                for item in self.children
                if item[cnst.TYPE] == meta_dict[cnst.TYPE]
                and item[cnst.NAME] == meta_dict[cnst.NAME]
            ),
            False,
        )
        if not child_found:
            self.children.append(meta_dict)
        else:
            pass

    def add_extractor(self, extractor_dict: dict):
        """"""
        if not hasattr(self, "extractors_used") or not self.extractors_used:
            self.extractors_used = []

        extractor_found = next(
            (
                item
                for item in self.extractors_used
                if item[cnst.EXTRACTOR_NAME]
                == extractor_dict[cnst.EXTRACTOR_NAME]
                and item[cnst.EXTRACTOR_VERSION]
                == extractor_dict[cnst.EXTRACTOR_VERSION]
            ),
            False,
        )
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
        keys_to_pop = [
            "node_path",
            "long_name",
            "md5_hash",
            "file_name",
            "parent_catalog",
        ]
        for key in keys_to_pop:
            meta_dict.pop(key, None)

        if not created:
            parent_path.mkdir(parents=True, exist_ok=True)
            with open(fn, "w") as f:
                json.dump(vars(self), f)
        else:
            with open(fn, "r+") as f:
                f.seek(0)
                json.dump(vars(self), f)
                f.truncate()


def getNode(type, dataset_id, dataset_version, path=None):
    """"""
    name = dataset_id + "-" + dataset_version
    if path:
        name = name + "-" + str(path)
    md5_hash = hashlib.md5(name.encode("utf-8")).hexdigest()

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
