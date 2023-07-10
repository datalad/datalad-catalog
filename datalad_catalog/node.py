import json
import logging
import sys
import datalad_catalog.constants as cnst
from datalad_catalog.utils import (
    load_config_file,
    md5hash,
    merge_lists,
)

lgr = logging.getLogger("datalad.catalog.node")


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
        catalog,
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
        self.md5_hash = md5hash(self.long_name)
        self.children = []

        # Defaults for config
        self.config = None
        self.config_source = None  # 'catalog' or 'dataset'

        # If Node metadata file exists, set attributes and config
        if self.is_created():
            self.set_attributes_from_file()
            cfg = self.get_config()
            self.config = cfg["config"]
            self.config_source = cfg["source"]

    def is_created(self) -> bool:
        """
        Check if metadata file for Node exists in catalog
        """
        if self.get_location().exists() and self.get_location().is_file():
            return True
        return False

    def create(self):
        """"""
        # Assumes that Node has been populated with attributes,
        # including config attribute (only applicable for dataset Node)
        if self.type == "dataset":
            if self.config is None:
                msg = (
                    "config has not been set for this node",
                    "neither from catalog- nor dataset-level",
                )
                raise ValueError(msg)
            # create config file if necessary, i.e. if a config file
            # does not already exist and if the config_source is 'dataset'
            dataset_config_path = (
                self.parent_catalog.metadata_path
                / self.dataset_id
                / self.dataset_version
                / "config.json"
            )
            if (
                not dataset_config_path.is_file()
                and self.config_source == "dataset"
            ):
                # First create id and version directories in case they don't exist
                dataset_config_path.parent.mkdir(parents=True, exist_ok=True)
                with open(dataset_config_path, "w") as f:
                    json.dump(self.config, f)
        # write attributes to file
        self.write_attributes_to_file()

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
            "config_source",
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
            self.md5_hash = md5hash(self.long_name)

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

    def get_config(self, config_file: str = None):
        """Get Node-level config

        In general a Node instance config can be loaded from file
        (e.g. "/metadata/dataset_id/dataset_version/config.json")

        If a config file for the Node instance does not exist:
        - if config file is passed, load its content
        - if no config file is passed, inherit/load config from the
          catalog-level config.
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
            return dict(
                source="dataset", config=load_config_file(dataset_config_path)
            )
        else:
            # If dataset-level config file DOES NOT exist:
            if config_file is not None:
                # If config file passed: load and return
                return dict(
                    source="dataset", config=load_config_file(config_file)
                )
            else:
                # If config file is not passed,
                # only load from catalog-level config file
                return dict(source="catalog", config=self.parent_catalog.config)

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

    def add_attributes(
        self, new_attributes: dict, config_file: str = None, overwrite=False
    ):
        """Add attributes (key-value pairs) to a Node as instance variables
        This is the point where a config is necessary"""
        # Get dataset config
        cfg = self.get_config(config_file)
        self.config = cfg.get("config", None)
        self.config_source = cfg["source"]
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
