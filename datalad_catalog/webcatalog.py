import json
import logging
from pathlib import Path
import os
from jsonschema import (
    Draft202012Validator,
    RefResolver,
)

import datalad_catalog.constants as cnst
from datalad_catalog.meta_item import MetaItem
from datalad_catalog.node import Node
from datalad_catalog.utils import (
    copy_overwrite_path,
    dir_exists,
    load_config_file,
    md5hash,
    md5sum_from_id_version_path,
    read_json_file,
    split_string,
)

lgr = logging.getLogger("datalad.catalog.webcatalog")


class WebCatalog(object):
    """
    The main catalog class.
    """

    def __init__(
        self,
        location: str,
    ) -> None:
        self.location = Path(location)
        self.metadata_path = Path(self.location) / "metadata"
        # The following attributes should be reset on create:
        # STATE
        self.is_valid_catalog = self.is_created()
        # SCHEMA SETUP
        self.schema_store = self.get_schema_store()
        self.schema_validator = self.get_schema_validator()
        # CONFIG SETUP
        self.config = self.get_config()

    def is_created(self) -> bool:
        """
        Check if directory exists at location, and if main subdirectories also
        exist, as well as config. This identifies the location as a valid catalog.
        """
        is_created = dir_exists(self.location)
        out_dir_paths = {
            "assets": Path(self.location) / "assets",
            "artwork": Path(self.location) / "artwork",
            "html": Path(self.location) / "index.html",
            "config": Path(self.location) / "config.json",
        }
        for key in out_dir_paths:
            is_created = is_created and out_dir_paths[key].exists()
        return is_created

    def create(self, config_file: str = None, force: bool = False):
        """Create new catalog directory with assets (JS, CSS),
        artwork, config, the main html, and html templates
        """
        # TODO: validate config file
        # First determine where to get config from
        if config_file:
            self.config_path = Path(config_file)
        else:
            self.config_path = cnst.default_config_dir / "config.json"
        # Load config from source file
        self.config = load_config_file(self.config_path)
        # Check logo path, if added to config
        if (
            self.config.get(cnst.LOGO_PATH) is not None
            and not self.get_logo_path().exists()
        ):
            msg = f"Error in config: the specified logo does not exist at path: {self.get_logo_path()}"
            raise FileNotFoundError(msg)
        # Create package-related paths/content
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
        # Reset STATE and SCHEMA
        self.is_valid_catalog = self.is_created()
        self.schema_store = self.get_schema_store()
        self.schema_validator = self.get_schema_validator()

    def get_record(
        self,
        dataset_id: str,
        dataset_version: str,
        record_type: str = "dataset",
        relpath: str = None,
    ):
        """Find the metadata record of a dataset, directory, or file in a catalog."""
        # EnsureChoice
        if record_type not in ("dataset", "directory", "file"):
            error_msg = "Argument 'record_type' must be one of 'dataset', 'directory', 'file'"
            raise ValueError(error_msg)

        if record_type in ("directory", "file") and relpath == None:
            error_msg = (
                "A relative path is required (argument 'relpath') "
                "for records of type 'directory' or 'file'"
            )
            raise ValueError(error_msg)
        # set the correct node_type and node_path
        node_type = record_type if record_type != "file" else "directory"
        if node_type == "dataset":
            node_path = None
        else:
            node_path = Path(relpath)
            if record_type == "file":
                node_path = node_path.parent
        # get node instance
        node_instance = Node(
            catalog=self,
            type=node_type,
            dataset_id=dataset_id,
            dataset_version=dataset_version,
            node_path=node_path,
        )
        if node_instance.is_created():
            if record_type == "file":
                children = [
                    c for c in node_instance.children if c["path"] == relpath
                ]
                return children[0] if len(children) > 0 else None
            else:
                return vars(node_instance)
        else:
            return None

    def add_record(self, metadata_record: dict, config_file: str = None):
        """Add a validated metadata record to the catalog

        This translates the record into a MetaItem instance
        with multiple Node instances, and then creates or updates
        the metadata file of each Node instance.

        If a config file is provided, the record is created/updated
        by taking the specified dataset-level config into account.
        Such a config file will also be saved in a dedicated
        dataset-specific location
        """
        # First see if related dataset record already exists
        existing_record = self.get_record(
            dataset_id=metadata_record[cnst.DATASET_ID],
            dataset_version=metadata_record[cnst.DATASET_VERSION],
        )
        # First translate the record into a MetaItem instance
        # that has multiple Node instances
        meta_item = MetaItem(
            catalog=self, meta_item=metadata_record, config_file=config_file
        )
        # Then create/update their respective metadata files
        meta_item.write_nodes_to_files()
        # Return a value specifying whether the record
        # was created or updated, for reporting
        return dict(
            action="update" if existing_record else "add",
            type=metadata_record.get(cnst.TYPE),
        )

    def get_main_dataset(self):
        super_path = Path(self.metadata_path) / "super.json"
        if not (super_path.exists() and super_path.is_file()):
            error_msg = f"File does not exist at path: {super_path}"
            raise FileNotFoundError(error_msg)
        return read_json_file(super_path)

    def set_main_dataset(self, dataset_id, dataset_version):
        """
        Save dataset_id and dataset_version to the "super.json" file
        in order to link the main dataset to the catalog.

        If "super.json" file already exists:
            - currently overwrites
        """
        main_obj = {
            cnst.DATASET_ID: dataset_id,
            cnst.DATASET_VERSION: dataset_version,
        }
        main_file = Path(self.metadata_path) / "super.json"
        with open(main_file, "w") as f:
            json.dump(main_obj, f)
        return main_file

    def get_logo_path(self):
        # Returns the absolute path to the logo
        # If none provided via config -> None
        if self.config.get(cnst.LOGO_PATH) is None:
            return None
        # If the provided path is absolute, return it
        # else assume that the provided path is relative to the
        # parent directory of the config file (within which the
        # logo path was specified)
        if Path(self.config[cnst.LOGO_PATH]).is_absolute():
            return self.config[cnst.LOGO_PATH]
        else:
            cfg_dir = self.config_path.parent
            return cfg_dir / self.config[cnst.LOGO_PATH]

    def get_config(self):
        """"""
        # Read config from file
        config_path = self.location / "config.json"
        if not config_path.exists():
            return None
        return load_config_file(config_path)

    def write_config(self, force=False):
        """"""
        # Copy content specified by config
        if (
            cnst.LOGO_PATH in self.config
            and self.config[cnst.LOGO_PATH]
            and self.config[cnst.LOGO_PATH] != "artwork/catalog_logo.svg"
        ):
            existing_path = self.get_logo_path()
            existing_name = existing_path.name
            new_path = Path(self.location) / "artwork" / existing_name
            copy_overwrite_path(
                src=existing_path, dest=new_path, overwrite=force
            )
            self.config[cnst.LOGO_PATH] = "artwork/" + existing_name
        # Dump json content to file
        new_config_path = Path(self.location) / "config.json"
        with open(new_config_path, "w") as f:
            json.dump(self.config, f)

    def get_schema_store(self):
        """Return schema store of catalog instance, or of package
        if the former is not found"""
        schema_store = {}
        # If catalog has schema files in "<catalog-name>/schema" dir, use them,
        # else use the schema files in the package default schema location
        cat_schema_dir = Path(self.location) / "schema"
        if (cat_schema_dir / "jsonschema_catalog.json").exists():
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
        if not hasattr(self, "schema_store"):
            self.schema_store = self.get_schema_store()
        catalog_schema = self.schema_store[
            cnst.CATALOG_SCHEMA_IDS[cnst.CATALOG]
        ]
        resolver = RefResolver.from_schema(
            catalog_schema, store=self.schema_store
        )
        return Draft202012Validator(catalog_schema, resolver=resolver)

    def serve(
        self,
        host: str = "localhost",
        port: int = 8000,
        base: str = None,
    ):
        """Serve a catalog via a local http server"""

        if base and not self.location.resolve().is_relative_to(
            Path(base).resolve()
        ):
            error_msg = "The catalog location should be relative to the supplied base path "
            raise ValueError(error_msg)
        if base:
            base_path = Path(base).resolve()
            relpath = str(self.location.resolve().relative_to(base_path))
            os.chdir(base_path)
        else:
            relpath = ""
            os.chdir(self.location)

        from http.server import SimpleHTTPRequestHandler
        import socketserver
        from datalad.ui import ui
        import datalad.support.ansi_colors as ac

        class CustomHandler(SimpleHTTPRequestHandler):
            # Redirect all '/dataset' URLs to '/index.html'
            def do_GET(self):
                if self.path.startswith(f"/{relpath}/dataset"):
                    self.path = f"/{relpath}/index.html"
                # Continue with the default behavior
                return SimpleHTTPRequestHandler.do_GET(self)

        try:
            with socketserver.TCPServer((host, port), CustomHandler) as httpd:
                ui.message(
                    "\nServing catalog at: http://{h}:{p}/{s} - navigate to this "
                    "address in your browser to test the catalog locally - press "
                    "CTRL+C to stop local testing\n".format(
                        h=ac.color_word(host, ac.BOLD),
                        p=ac.color_word(port, ac.BOLD),
                        s=ac.color_word(relpath, ac.BOLD),
                    )
                )
                httpd.serve_forever()
        except Exception as e:
            lgr.error(
                msg="Unable to serve at the desired host and port", exc_info=e
            )
            raise (e)

    def get_dataset_versions(self):
        """Function to get all dataset-versions from a catalog,
        including several data points from each specific dataset-version
        metadata file. This means that each dataset-level metadata file
        in the catalog is read, which might take some time.
        """
        dataset_versions = []

        for dv in self.metadata_path.glob("*/*"):
            """"""
            if not dv.is_dir():
                continue
            ds_id_path = dv.parent.relative_to(self.metadata_path)
            ds_id = str(ds_id_path)
            ds_version_path = dv.relative_to(self.metadata_path)
            ds_version = dv.name
            n = Node(
                catalog=self,
                type="dataset",
                dataset_id=ds_id,
                dataset_version=ds_version,
                node_path=None,
            )
            name = alias_path = alias = None
            if hasattr(n, "name"):
                name = n.name
            if hasattr(n, "alias"):
                alias = n.alias
                alias_path = str(
                    (Path(alias) / md5hash(alias)).with_suffix(".json")
                )
            dataset_versions.append(
                {
                    "dataset_name": name,
                    "dataset_id": ds_id,
                    "dataset_version": ds_version,
                    "concept_path": str(
                        (ds_id_path / md5hash(ds_id)).with_suffix(".json")
                    ),
                    "metadata_path": str(
                        n.get_location().relative_to(self.metadata_path)
                    ),
                    "alias": alias,
                    "alias_path": alias_path,
                    "updated_at": n.get_last_updated(),
                }
            )
        return dataset_versions

    def get_catalog_report(self):
        """Summarize output from self.get_dataset_versions and
        some more additional stats
        """
        files = list(self.metadata_path.rglob("*.json"))
        ds_versions = self.get_dataset_versions()
        ds_ids = list(set([dsv["dataset_id"] for dsv in ds_versions]))
        homepage = self.get_main_dataset()
        homepage_node = Node(
            catalog=self,
            type="dataset",
            dataset_id=homepage.get("dataset_id"),
            dataset_version=homepage.get("dataset_version"),
            node_path=None,
        )
        return {
            "catalog_location": str(self.location.resolve()),
            "homepage_id": homepage.get("dataset_id"),
            "homepage_version": homepage.get("dataset_version"),
            "homepage_path": str(
                homepage_node.get_location().relative_to(self.location)
            ),
            "dataset_count": len(ds_ids),
            "version_count": len(ds_versions),
            "metadata_file_count": len(files),
            "datasets": ds_ids,
            "versions": ds_versions,
        }
