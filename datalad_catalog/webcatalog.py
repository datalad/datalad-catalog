import hashlib
from http.client import FAILED_DEPENDENCY
import json
import logging
import shutil
import sys
from pathlib import Path

import yaml
from jsonschema import (
    Draft202012Validator,
    RefResolver,
)

import datalad_catalog.constants as cnst
from datalad_catalog.utils import (
    find_duplicate_object_in_list,
    read_json_file,
    merge_lists,
)

lgr = logging.getLogger("datalad.catalog.webcatalog")


class WebCatalog(object):
    """
    The main catalog class.
    """

    def __init__(
        self,
        location: str,
        main_id: str = None,
        main_version: str = None,
        config_file: str = None,
        catalog_action: str = None,
    ) -> None:
        self.location = Path(location)
        self.main_id = main_id
        self.main_version = main_version
        self.metadata_path = Path(self.location) / "metadata"
        
        # SCHEMA SETUP
        self.schema_store = self.get_schema_store()
        self.schema_validator = self.get_schema_validator()

        # CONFIG SETUP
        self.catalog_config_path = None
        self.dataset_config_path = None
        self.catalog_config = None
        self.dataset_config = None

        # CONFIG DESCRIPTION
        # WebCatalog can be instantiated for any catalog action (create, add, etc)
        # Config can be specified at catalog level (also functions as default for all datasets)
        # during a "create" action, and at dataset level during an "add" action.
        # If action == create:
        # - if config file is provided, config is set on catalog level from provided file
        # - if config file is NOT provided, config is set on catalog level from default in package
        # - do nothing here wrt dataset-level config
        # If action == add:
        # - config is set on catalog level from existing or default
        # - if config file is provided, config is set on dataset level
        # - if config file is NOT provided, set None (default can be loaded from Node)

        # TODO: testing for the catalog_action assumes that the call was done via CLI and not Python API
        # Need to figure out how to achieve the same without relying on info coming only from CLI
        if catalog_action in ["create", "workflow-new"]:
            # Config file, if specified, belongs to catalog
            self.catalog_config_path = self.get_config_source(
                source_str=config_file, config_level="catalog"
            )
            self.catalog_config = self.get_config(config_level="catalog")
        elif catalog_action in ["add", "workflow-update"]:
            # NOTE: "add" implies that catalog already exists, i.e. .is_created() returns True
            # Config file, if specified, belongs to datasets/files
            # First get default catalog config source and set catalog config attribute
            self.catalog_config_path = self.get_config_source(
                source_str=None, config_level="catalog"
            )
            self.catalog_config = self.get_config(config_level="catalog")
            # Then get/set on the dataset level
            self.dataset_config_path = self.get_config_source(
                source_str=config_file, config_level="dataset"
            )
            if self.dataset_config_path:
                self.dataset_config = self.get_config(config_level="dataset")
        else:
            # For all other actions: do nothing wrt config, even if supplied
            # Must probably still set default if needed?
            self.catalog_config_path = self.get_config_source(
                source_str=None, config_level="catalog"
            )
            self.catalog_config = self.get_config(config_level="catalog")
            self.dataset_config_path = self.get_config_source(
                source_str=None, config_level="dataset"
            )
            if self.dataset_config_path:
                self.dataset_config = self.get_config(config_level="dataset")
            # TODO: this is a silent pass; should probably give warning already in Catalog module
            pass

        # TODO: deal with scenario when config for a dataset should be updated???
        # Arguments = id and version and config file, but what action?
        # If action = add, id and version can be passed, but will be interpreted
        # as main_id and main_version by constructor. Need to deal with multiple
        # actions correctly, possibly introduce new "update action".

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
        Create new catalog directory with assets (JS, CSS), artwork, config, the main html, and html templates
        """
        # TODO: first validate config file (using jsonschema?)
        # Check logo path, if added to config
        if (
            self.catalog_config.get(cnst.LOGO_PATH) is not None
            and not self.get_logo_path().exists()
            # and not Path(self.catalog_config[cnst.LOGO_PATH]).exists()
        ):
            msg = f"Error in config: the specified logo does not exist at path: {self.get_logo_path()}"
            raise FileNotFoundError(msg)

        # Get package-related paths/content
        if not (self.metadata_path.exists() and self.metadata_path.is_dir()):
            Path(self.metadata_path).mkdir(parents=True)

        content_paths = {
            "assets": cnst.catalog_path / "assets",
            "artwork": cnst.catalog_path / "artwork",
            "html": cnst.catalog_path / "index.html",
            "readme": cnst.catalog_path / "README.md",
            "schema": cnst.catalog_path / "schema",
            "templates": cnst.catalog_path / "templates",
        }
        out_dir_paths = {
            "assets": Path(self.location) / "assets",
            "artwork": Path(self.location) / "artwork",
            "html": Path(self.location) / "index.html",
            "readme": Path(self.location) / "README.md",
            "schema": Path(self.location) / "schema",
            "templates": Path(self.location) / "templates",
        }
        for key in content_paths:
            copy_overwrite_path(
                src=content_paths[key], dest=out_dir_paths[key], overwrite=force
            )
        # Copy / write config file
        self.write_config(force)

    def add_dataset():
        """"""
        raise NotImplementedError

    def remove_dataset():
        """"""
        raise NotImplementedError

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

    def get_config_source(
        self, source_str: str = None, config_level: str = "catalog"
    ):
        """"""
        if config_level == "catalog":
            if self.is_created():
                # If catalog already exists, return config if it exists, otherwise default
                catalog_config_path = Path(self.location / "config.json")
                if catalog_config_path.exists():
                    return catalog_config_path
                return cnst.default_config_dir / "config.json"
            else:
                # If catalog does not exist, return config if specified, otherwise default
                if source_str is not None:
                    return Path(source_str)
                else:
                    return cnst.default_config_dir / "config.json"
        if config_level == "dataset":
            if source_str is not None:
                return Path(source_str)
            else:
                # Do not return default here, this will be done on the Node or MetaItem class,
                # where dataset id and version are available.
                return None

    def get_logo_path(self):
        # Returns the absolute path to the logo
        # If none provided via config -> None
        if self.catalog_config.get(cnst.LOGO_PATH) is None:
            return None
        # If the provided path is absolute, return it
        # else assume that the provided path us relative to the
        # parent directory of the config file (within which the
        # logo path was specified)
        if Path(self.catalog_config[cnst.LOGO_PATH]).is_absolute():
            return self.catalog_config[cnst.LOGO_PATH]
        else:
            cfg_dir = self.catalog_config_path.parent
            return cfg_dir / self.catalog_config[cnst.LOGO_PATH]

    def get_config(self, config_level: str = "catalog"):
        """"""
        # Read metadata from file
        cfg_paths = {
            "catalog": self.catalog_config_path,
            "dataset": self.dataset_config_path,
        }
        config_path = cfg_paths[config_level]
        return load_config_file(config_path)

    def write_config(self, force=False):
        """"""
        # Copy content specified by config
        if (
            cnst.LOGO_PATH in self.catalog_config
            and self.catalog_config[cnst.LOGO_PATH]
            and self.catalog_config[cnst.LOGO_PATH]
            != "artwork/catalog_logo.svg"
        ):
            # existing_path = Path(self.catalog_config[cnst.LOGO_PATH])
            existing_path = self.get_logo_path()
            existing_name = existing_path.name
            new_path = Path(self.location) / "artwork" / existing_name
            copy_overwrite_path(
                src=existing_path, dest=new_path, overwrite=force
            )
            self.catalog_config[cnst.LOGO_PATH] = "artwork/" + existing_name
        # Dump json content to file
        new_config_path = Path(self.location) / "config.json"
        with open(new_config_path, "w") as f_config:
            json.dump(self.catalog_config, f_config)

    def get_schema_store(self):
        """Return schema store of catalog instance or package
        whichever is found first"""
        schema_store = {}
        # If catalog has schema files in "<catalog-name>/schema" dir, use them,
        # else use the schema files in the package default schema location
        cat_schema_dir = Path(self.location) / 'schema' 
        if (cat_schema_dir / 'jsonschema_catalog.json').exists():
            schema_dir = cat_schema_dir
        else:
            schema_dir = cnst.schema_dir
        # Now load all schema files into store
        for schema_type, schema_id in cnst.CATALOG_SCHEMA_IDS.items():
            schema_path = schema_dir / f"jsonschema_{schema_type}.json"
            schema = read_json_file(schema_path)
            schema_store[schema[cnst.DOLLARID]] = schema
        return schema_store
    
    def get_schema_validator(self):
        """Return schema validator"""
        if not hasattr(self, 'schema_store'):
            self.schema_store = self.get_schema_store()
        catalog_schema = self.schema_store[cnst.CATALOG_SCHEMA_IDS[cnst.CATALOG]]
        resolver = RefResolver.from_schema(catalog_schema, store=self.schema_store)
        return Draft202012Validator(catalog_schema, resolver=resolver)


class Node(object):
    """
    A node in the directory tree of a catalog dataset, for which a metadata
    file will be created.

    Required arguments:
    catalog -- catalog within which the node exists
    type -- 'directory' | 'dataset'
    dataset_id -- parent dataset id
    dataset_version -- parent dataset version
    """

    _split_dir_length = 3
    _instances = {}

    def __init__(
        self,
        catalog: WebCatalog,
        type: str,
        dataset_id: str,
        dataset_version: str,
        node_path=None,
    ) -> None:
        """
        type = 'directory' | 'dataset'
        """
        # Set main instance variables
        self.parent_catalog = catalog
        self.type = type
        self.dataset_id = dataset_id
        self.dataset_version = dataset_version
        self.node_path = node_path
        self.long_name = self.get_long_name()
        self.md5_hash = self.md5hash(self.long_name)
        self.children = []
        # If corresponding file exists, set attributes
        if self.is_created():
            self.set_attributes_from_file()
        # Get Node config
        self.config = self.get_config()

    def is_created(self) -> bool:
        """
        Check if metadata file for Node exists in catalog
        """
        if self.get_location().exists() and self.get_location().is_file():
            return True
        return False

    def write_attributes_to_file(self):
        """
        Create a catalog metadata file for the Node instance
        """
        # First grab required fields
        file_path = self.get_location()
        parent_path = file_path.parents[0]
        # And set correct attributes for instance of type 'directory': path+name
        if hasattr(self, "node_path") and self.type == "directory":
            setattr(self, "path", str(self.node_path))
            setattr(self, "name", self.node_path.name)
        # Create a dictionary from instance variables
        meta_dict = vars(self)
        # Remove attributes that are irrelevant for the catalog
        keys_to_pop = [
            "node_path",
            "long_name",
            "md5_hash",
            "parent_catalog",
            "config",
        ]
        for key in keys_to_pop:
            meta_dict.pop(key, None)
        # Write the dictionary to file
        parent_path.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(meta_dict, f)

    def load_file(self):
        """Load content from catalog metadata file for current node"""
        try:
            with open(self.get_location()) as f:
                return json.load(f)
        except OSError as err:
            print("OS error: {0}".format(err))
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise

    def set_attributes_from_file(self):
        """Set a Node instance's attributes from its corresponding metadata file

        This overwrites existing attributes on a Node instance, or creates new
        attributes, with values contained in the JSON object in the metadata file
        """
        metadata = self.load_file()
        for key in metadata.keys():
            setattr(self, key, metadata[key])

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

    def get_config(self):
        """Get Node-level config

        In general a Node instance config can be loaded from file
        (e.g. "/metadata/dataset_id/dataset_version/config.json")

        If a config file for the Node instance does not exist:
        - load config content from dataset-level config on the parent
          catalog instance, and also create the file
        - if dataset-level config on the parent catalog instance does not exist,
          inherit/load config from the catalog-level config file.
        """
        # Expected config file path
        dataset_config_path = (
            self.parent_catalog.metadata_path
            / self.dataset_id
            / self.dataset_version
            / "config.json"
        )
        if dataset_config_path.is_file():
            # If dataset-level config file DOES exist, return it
            return load_config_file(dataset_config_path)
        else:
            # If dataset-level config file DOES NOT exist:
            if self.parent_catalog.dataset_config is not None:
                # If dataset-level config IS available on catalog instance: load and create, return
                # First create id and version directories in case they don't exist
                dataset_config_path.parent.mkdir(parents=True, exist_ok=True)
                dataset_config = self.parent_catalog.dataset_config
                with open(dataset_config_path, "w") as f_config:
                    json.dump(dataset_config, f_config)
                return dataset_config
            else:
                # If dataset-level config IS NOT available on catalog instance,
                # only load from catalog-level config file
                return self.parent_catalog.catalog_config

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

    def add_attributes(self, new_attributes: dict, overwrite=False):
        """Add attributes (key-value pairs) to a Node as instance variables"""
        # Get dataset config
        dataset_config = self.config[cnst.PROPERTY_SOURCES][cnst.TYPE_DATASET]
        # Get metadata source of incoming metadata
        # NOTE: this assumes that provided metadata item originates from a single source,
        # and wasn't collated beforehand. TODO: need to investigate and update the implementation
        # if we want to support the addition of metadata items that have previously been constructed
        # from multiple sources
        try:
            data_source_dict = new_attributes[cnst.METADATA_SOURCES][
                cnst.SOURCES
            ][0]
            data_source = data_source_dict[cnst.SOURCE_NAME]
        except:
            data_source_dict = {}
            data_source = None

        # Add metadata source to Node (per-key mapping to source happens below)
        self.add_metadata_source(data_source_dict)
        # Loop through provided keys
        for key in new_attributes.keys():
            new_value = new_attributes[key]
            # Skip metadata_sources key
            if key == cnst.METADATA_SOURCES:
                continue
            # Skip keys with empty values
            if not bool(new_value):
                continue
            # Isolate config rule and source
            key_config = dataset_config.get(key, None)
            config_rule = None
            config_source = None
            if key_config is not None:
                config_rule = key_config.get("rule", None)
                config_source = key_config.get("source", None)
            if config_source and not isinstance(
                config_source, list
            ):  # make all sources a list, except for None
                config_source = [config_source]
            # create new or update existing attribute/variable
            setattr(
                self,
                key,
                self._update_attribute(
                    key,
                    new_value,
                    data_source,
                    config_rule,
                    config_source,
                    overwrite,
                ),
            )

    def _update_attribute(
        self,
        key,
        new_value,
        source_name: str,
        config_rule: str,
        config_source: str,
        overwrite=False,
    ):
        """Create new or update existing attribute/variable of a Node instance

        This function incorporates prioritizing instructions from the user-
        specified or defaulted dataset-level config, reads the source of incoming
        metadata, and decides whether to:
        - create a new instance variable, if none exists
        - merge the existing instance variable value with that of the incoming
          data
        - overwrite the existing instance variable value (if/when applicable)
        """
        # TODO: still need to use overwrite flag where it makes sense to do so

        # Get existing value:
        if hasattr(self, key):
            existing_value = getattr(self, key)
        else:
            existing_value = None

        # Some handling of incorrect config specification:
        # - "rule" can be one of: single / merge / priority / None / empty string
        # - "source" can be: "any" / a list / empty list / empty string
        # If config_rule specified without config_source:
        if not config_source and config_rule in [
            "single",
            "merge",
            "priority",
            None,
        ]:
            if (
                config_rule == "merge"
            ):  # for merge, allow new source to be merged
                config_source = [source_name]
            else:  # for single / priority / None, ignore new source
                config_source = []
        # If config_source specified without config_rule,
        # set config_rule to None (i.e. first-come-first-served)
        if config_source and config_rule not in [
            "single",
            "merge",
            "priority",
            None,
        ]:
            config_rule = None
        # If config_source is "any" it implies the current source is allowed
        if config_source == ["any"]:
            config_source = [source_name]

        # NEXT: decide what to do based on config_rule and config_source:
        if config_rule == "single":
            try:
                if source_name == config_source[0]:
                    self.add_source_map_entry(key, source_name, "replace")
                    return new_value
                else:
                    return existing_value
            except IndexError:
                return existing_value
        elif config_rule == "merge":
            if source_name not in config_source:
                return existing_value
            else:
                if existing_value is None:
                    self.add_source_map_entry(key, source_name, "replace")
                    return new_value
                else:
                    self.add_source_map_entry(key, source_name, "merge")
                    return merge_lists(existing_value, new_value)
        elif config_rule == "priority":
            if source_name not in config_source:
                return existing_value
            else:
                if existing_value is None:
                    self.add_source_map_entry(key, source_name, "replace")
                    return new_value
                else:
                    existing_source = self.get_source_map_entry(key)
                    if existing_source is not None:
                        existing_source = existing_source[0]
                        existing_idx = config_source.index(existing_source)
                        new_idx = config_source.index(source_name)
                        if new_idx < existing_idx:
                            self.add_source_map_entry(
                                key, source_name, "replace"
                            )
                            return new_value
                        else:
                            return existing_value
        else:
            # If config_rule is None or unspecified or something random,
            # ==> first-come-first-served
            if existing_value is None:
                self.add_source_map_entry(key, source_name, "replace")
                return new_value
            else:
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

    def add_metadata_source(self, source_dict: dict):
        """"""
        # Initialise "metadata_sources" attribute if required
        if (
            not hasattr(self, cnst.METADATA_SOURCES)
            or not self.metadata_sources
        ):
            self.metadata_sources = {}
            self.metadata_sources[cnst.KEY_SOURCE_MAP] = {}
            self.metadata_sources[cnst.SOURCES] = []
        # Find the metadata_source element if it already exists in "sources" list
        # NOTE: currently identifying element based on source name and version only
        source_found = next(
            (
                item
                for item in self.metadata_sources[cnst.SOURCES]
                if cnst.SOURCE_NAME in item
                and item[cnst.SOURCE_NAME] == source_dict[cnst.SOURCE_NAME]
                and item[cnst.SOURCE_VERSION]
                == source_dict[cnst.SOURCE_VERSION]
            ),
            False,
        )
        if not source_found:
            # append to source list
            self.metadata_sources[cnst.SOURCES].append(source_dict)
        else:
            pass

    def add_source_map_entry(self, key: str, source_name: str, action: str):
        """"""
        # Initialise "metadata_sources['key_source_map']" attribute if required
        if (
            cnst.KEY_SOURCE_MAP not in self.metadata_sources
            or not self.metadata_sources[cnst.KEY_SOURCE_MAP]
        ):
            self.metadata_sources[cnst.KEY_SOURCE_MAP] = {}
        # Get existing sources, and replace / merge
        sources = self.metadata_sources[cnst.KEY_SOURCE_MAP].get(key, None)
        if not sources:
            self.metadata_sources[cnst.KEY_SOURCE_MAP][key] = [source_name]
        else:
            if action == "replace":
                self.metadata_sources[cnst.KEY_SOURCE_MAP][key] = [source_name]
            if action == "merge":
                self.metadata_sources[cnst.KEY_SOURCE_MAP][key] = list(
                    set(sources + [source_name])
                )

    def get_source_map_entry(self, key: str):
        """"""
        # If "metadata_sources['key_source_map']" doesn't exist, no map:
        if (
            cnst.KEY_SOURCE_MAP not in self.metadata_sources
            or not self.metadata_sources[cnst.KEY_SOURCE_MAP]
        ):
            return None
        # Return none if no key, else key
        return self.metadata_sources[cnst.KEY_SOURCE_MAP].get(key, None)


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


def md5sum_from_id_version_path(dataset_id, dataset_version, path=None):
    """Helper to get md5 hash of concatenated input variables"""
    long_name = dataset_id + "-" + dataset_version
    if path:
        long_name = long_name + "-" + str(path)
    return hashlib.md5(long_name.encode("utf-8")).hexdigest()


def load_config_file(file: Path):
    """Helper to load content from JSON or YAML file"""
    with open(file) as f:
        if file.suffix == ".json":
            return json.load(f)
        if file.suffix in [".yml", ".yaml"]:
            return yaml.safe_load(f)
