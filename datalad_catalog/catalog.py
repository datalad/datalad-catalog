import json
import logging
import os
import sys
from os.path import (
    abspath,
    curdir,
)
from pathlib import Path
from typing import (
    Optional,
    Dict,
)
from datalad.distribution.dataset import datasetmethod
from datalad.interface.base import (
    Interface,
    build_doc,
)
from datalad.interface.results import get_status_dict
from datalad.interface.utils import eval_results
from datalad.log import log_progress
from datalad.support.constraints import EnsureChoice
from datalad.support.exceptions import InsufficientArgumentsError
from datalad.support.param import Parameter
from jsonschema import (
    Draft202012Validator,
    RefResolver,
    ValidationError,
)

from datalad_catalog.meta_item import MetaItem
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import (
    Node,
    WebCatalog,
)

# Create named logger
lgr = logging.getLogger("datalad.catalog.catalog")

# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Catalog(Interface):
    # first docstring line is used a short description in the cmdline help
    # the rest is put in the verbose help and manpage
    """Generate a user-friendly web-based data catalog from structured
    metadata.

    The ``datalad catalog`` command can be used to ``create`` a new
    catalog, ``add`` and ``remove`` metadata entries to/from an
    existing catalog, or start a a local http server to ``serve`` an
    existing catalog locally. It can also ``validate`` a metadata
    entry (validation is also performed implicitly when adding) and
    set the dataset to be shown by default (``set-super``).

    Metadata can be provided to DataLad Catalog from any number of
    arbitrary metadata sources, as an aggregated set or as individual
    metadata items. DataLad Catalog has a dedicated schema (using the
    JSON Schema vocabulary) against which incoming metadata items are
    validated. This schema allows for standard metadata fields as one
    would expect for datasets of any kind (such as name, doi, url,
    description, license, authors, and more), as well as fields that
    support identification, versioning, dataset context and linkage,
    and file tree specification.

    The output is a set of structured metadata files, as well as a
    Vue.js-based browser interface that understands how to render this
    metadata in the browser. These can be hosted on a platform of
    choice as a static webpage.

    Note: in the catalog website, each dataset entry is displayed
    under ``<main page>/#/dataset/<dataset_id>/<dataset_version>``.
    By default, the main page of the catalog will display a 404 error,
    unless the default dataset is configured with ``datalad catalog
    set-super``.
    """

    # usage examples
    _examples_ = [
        dict(
            text="Create a new catalog from scratch",
            code_py="catalog('create', catalog_dir='/tmp/my-cat')",
            code_cmd="datalad catalog create -c /tmp/my-cat",
        ),
        dict(
            text="Add metadata to an existing catalog",
            code_py=(
                "catalog('add', catalog_dir='/tmp/my-cat', "
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd=(
                "datalad catalog add "
                "-c /tmp/my-cat -m path/to/metadata.jsonl"
            ),
        ),
        dict(
            text=(
                "Set the superdataset of an existing catalog - the first "
                "dataset displayed when navigating to the root URL of the "
                "catalog"
            ),
            code_py=(
                "catalog('set-super', catalog_dir='/tmp/my-cat', "
                "dataset_id='abcd', dataset_version='1234')"
            ),
            code_cmd=(
                "datalad catalog set-super -c /tmp/my-cat -i abcd -v 1234"
            ),
        ),
        dict(
            text=(
                "Serve the content of the catalog via a local HTTP server "
                "at http://localhost:8000"
            ),
            code_py="catalog('serve', catalog_dir='/tmp/my-cat/')",
            code_cmd="datalad catalog serve -c /tmp/my-cat",
        ),
        dict(
            text=(
                "Check if metadata conforms to catalog schema without adding "
                "it to the catalog"
            ),
            code_py="catalog('validate', metadata='path/to/metadata.jsonl')",
            code_cmd="datalad catalog validate -m path/to/metadata.jsonl",
        ),
    ]

    # parameters of the command, must be exhaustive
    _params_ = dict(
        # name of the parameter, must match argument name
        catalog_action=Parameter(
            args=("catalog_action",),
            # documentation
            doc="""This is the subcommand to be executed by datalad-catalog.
            Options include: create, add, remove, serve, set-super, and validate.
            Example: ''""",
            # type checkers, constraint definition is automatically
            # added to the docstring
            constraints=EnsureChoice(
                "create", "add", "remove", "serve", "set-super", "validate"
            ),
        ),
        catalog_dir=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog_dir"),
            # documentation
            doc="""Directory where the catalog is located or will be created.
            Example: ''""",
        ),
        metadata=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-m", "--metadata"),
            # documentation
            doc="""Path to input metadata. Multiple input types are possible:
            - A '.json' file containing an array of JSON objects related to a
             single datalad dataset.
            - A stream of JSON objects/lines
            Example: ''""",
        ),
        dataset_id=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-i", "--dataset_id"),
            # documentation
            doc="""
            Example: ''""",
        ),
        dataset_version=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-v", "--dataset_version"),
            # documentation
            doc="""
            Example: ''""",
        ),
        force=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-f", "--force"),
            # documentation
            doc="""If content for the user interface already exists in the catalog
            directory, force this content to be overwritten. Content
            overwritten with this flag include the 'artwork' and 'assets'
            directories and the 'index.html' and 'config.json' files. Content in
            the 'metadata' directory remain untouched.
            Example: ''""",
            action="store_true",
            default=False,
        ),
        config_file=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-y", "--config-file"),
            # documentation
            doc="""Path to config file in YAML or JSON format. Default config is read
            from datalad_catalog/config/config.json
            Example: ''""",
        ),
    )

    @staticmethod
    # decorator binds the command to the Dataset class as a method
    @datasetmethod(name="catalog")
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog_action: str,
        catalog_dir=None,
        metadata=None,
        dataset_id=None,
        dataset_version=None,
        force: bool = False,
        config_file=None,
    ):
        """
        [summary]

        Args:
            catalog_action (str): [description]
            catalog_dir ([type], optional): [description]. Defaults to None.
            metadata ([type], optional): [description]. Defaults to None.
            dataset_id ([type], optional): [description]. Defaults to None.
            dataset_version ([type], optional): [description]. Defaults to None.
            force (bool, optional): [description]. Defaults to False.

        Raises:
            InsufficientArgumentsError: [description]
            InsufficientArgumentsError: [description]
            InsufficientArgumentsError: [description]

        Yields:
            [type]: [description]
        """

        # TODO: check if schema is valid (move to tests)
        # Draft202012Validator.check_schema(schema)

        # set common result kwargs:
        action = "catalog_%s" % catalog_action
        res_kwargs = dict(action=action)
        # If action is validate, only metadata required
        if catalog_action == "validate":
            yield from _validate_metadata(metadata)
            return

        # Error out if `catalog_dir` argument was not supplied
        if catalog_dir is None:
            yield dict(
                **res_kwargs,
                status="impossible",
                message=(
                    "Datalad catalog %s requires a path to operate on. "
                    "Forgot -c, --catalog_dir?",
                    catalog_action,
                ),
                path=None,
            )
            return
        # now that we have a path, update result kwargs with it
        res_kwargs["path"] = catalog_dir

        # Instantiate WebCatalog class
        ctlg = WebCatalog(catalog_dir, dataset_id, dataset_version, config_file)
        # catalog_path = Path(catalog_dir)
        # catalog_exists = catalog_path.exists() and catalog_path.is_dir()

        # Hanlde case where a non-catalog directory already exists at path
        # argument. Should prevent overwriting
        if ctlg.path_exists() and not ctlg.is_created():
            yield dict(
                **res_kwargs,
                status="error",
                message=(
                    "A non-catalog directory already exists at %s. "
                    "Please supply a different path.",
                    catalog_dir,
                ),
            )
            return

        # Catalog should exist for all actions except create (for create action:
        # unless force flag supplied)
        if not ctlg.is_created():
            if catalog_action != "create":
                yield dict(
                    **res_kwargs,
                    status="impossible",
                    message=(
                        "Catalog does not exist: datalad catalog '%s' can only "
                        "operate on an existing catalog, please supply a path "
                        "to an existing directory with the catalog argument: "
                        "-c, --catalog_dir.",
                        catalog_action,
                    ),
                )
                return
        else:
            if catalog_action == "create":
                if not force:
                    yield dict(
                        **res_kwargs,
                        status="error",
                        message=(
                            "Found existing catalog at %s. Overwriting catalog "
                            "assets (not catalog metadata) is only possible "
                            "when using --force.",
                            catalog_dir,
                        ),
                    )
                    return

        # Call relevant function based on action
        # Action-specific argument parsing as well as results yielding are done within action-functions
        function, args = {
            "create": (
                _create_catalog,
                (
                    ctlg,
                    metadata,
                    dataset_id,
                    dataset_version,
                    force,
                    config_file,
                    res_kwargs,
                ),
            ),
            "serve": (_serve_catalog, (ctlg, res_kwargs)),
            "add": (_add_to_catalog, (ctlg, metadata, res_kwargs)),
            "remove": (
                _remove_from_catalog,
                (ctlg, dataset_id, dataset_version, res_kwargs),
            ),
            "set-super": (
                _set_super_of_catalog,
                (ctlg, dataset_id, dataset_version),
            ),
        }[catalog_action]

        yield from function(*args)


# Internal functions to execute based on catalog_action parameter
def _create_catalog(
    catalog: WebCatalog,
    metadata,
    dataset_id: str,
    dataset_version: str,
    force: bool,
    config_file: str,
    res_kwargs: Optional[Dict] = None,
):
    """Create the catalog in its specified location.

    If catalog does not exist, it will be created. If catalog exists
    and force flag is True, this will overwrite assets of the existing
    catalog.

    Parameters
    ----------
    catalog : WebCatalog
        an instance of the catalog to be created
    metadata : path-like object, optional
        metadata to be added to the catalog after creation
    force : bool, optional
        if True, will overwrite assets of an existing catalog

    Yields
    ------
    status_dict : dict
        DataLad result record
    """
    msg = ""
    if not catalog.is_created():
        catalog.create()
        msg = ("Catalog successfully created at: %s", catalog.location)
    else:
        if force:
            catalog.create(force)
            msg = (
                "Catalog assets successfully overwritten at: %s",
                catalog.location,
            )
    # Yield created/overwitten status message
    yield get_status_dict(**res_kwargs, status="ok", message=msg)
    # If metadata was also supplied, add this to the catalog
    if metadata is not None:
        yield from _add_to_catalog(catalog, metadata, res_kwargs)


def _add_to_catalog(
    catalog: WebCatalog, metadata, res_kwargs: Optional[Dict] = None
):
    """Add metadata entries to the catalog.

    Reads a specified metadata file and adds the metadata to the
    catalog. Currently supports files in which each line contains a
    json object.

    Parameters
    ----------
    catalog : WebCatalog
        an instance of the catalog to be populated
    metadata : path-like object
        path to a file containing metadata

    Yields
    ------
    status_dict : dict
        DataLad result record

    """
    if metadata is None:
        yield dict(
            **res_kwargs,
            status=impossible,
            message=(
                "No metadata supplied: Datalad catalog has to be supplied with "
                "metadata in the form of a path to a file containing a JSON "
                "array, or JSON lines stream, using the argument: "
                "-m, --metadata."
            ),
        )

    # Then we need to do the following:
    # 1. establish input type (file, file-with-json-array, file-with-json-lines, command line stdout / stream)

    #    - for now: assume file-with-json-array (data exported by `datalad meta-dump` and all exported objects added to an array in file)
    # 2. instantiate translator
    # 3. read input based on type
    #    - for now: load data from input file
    # 4. For each metadata object in input, call translator

    # 2. Instantiate single translator
    # translate = Translator()

    # TODO: Establish input type
    # 3. Read input
    # metadata = read_json_file(metadata)
    # This metadata should be the dataset and file level metadata of a single dataset
    # TODO: insert checks to verify this
    # TODO: decide whether to allow metadata dictionaries from multiple datasets

    with open(metadata) as file:
        i = 0
        for line in file:
            i += 1
            # meta_dict = line.rstrip()
            meta_dict = json.loads(line.rstrip())

            # Check if item/line is a dict
            if not isinstance(meta_dict, dict):
                err_msg = (
                    "Metadata item not of type dict: metadata items should be "
                    "passed to datalad catalog as JSON objects adhering to the "
                    "catalog schema."
                )
                lgr.warning(err_msg)
                # raise TypeError(err_msg)
            # Validate dict against catalog schema
            try:
                catalog.VALIDATOR.validate(meta_dict)
            except ValidationError as e:
                err_msg = f"Schema validation failed in LINE {i}: \n\n{e}"
                raise ValidationError(err_msg) from e
            # If validation passed, translate into catalog files
            MetaItem(catalog, meta_dict)
            # Translator(catalog, meta_dict)

    # TODO: should we write all files here?
    # Set parent catalog of orphans
    orphans = [
        Node._instances[inst]
        for inst in Node._instances
        if not hasattr(Node._instances[inst], "parent_catalog")
        or not Node._instances[inst].parent_catalog
    ]
    for orphan in orphans:
        orphan.parent_catalog = catalog

    # [inst for inst in Node._instances if not hasattr(Node._instances[inst], 'parent_catalog')]
    for blob in Node._instances:
        inst = Node._instances[blob]
        parent_path = inst.get_location().parents[0]
        fn = inst.get_location()
        created = inst.is_created()

        if hasattr(inst, "node_path") and inst.type != "dataset":
            setattr(inst, "path", str(inst.node_path))
        if hasattr(inst, "node_path") and inst.type == "directory":
            setattr(inst, "name", inst.node_path.name)

        meta_dict = vars(inst)
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
                json.dump(vars(inst), f)
        else:
            with open(fn, "r+") as f:
                f.seek(0)
                json.dump(vars(inst), f)
                f.truncate()

    yield get_status_dict(
        res_kwargs,
        status="ok",
        message=("Metadata items successfully added to catalog"),
    )


def _remove_from_catalog(
    catalog: WebCatalog,
    dataset_id: str,
    dataset_version: str,
    res_kwargs: Optional[Dict] = None,
):
    """Remove a dataset from the catalog.

    Parameters
    ----------
    dataset_id : str
        dataset id of the dataset to be removed
    dataset_version : str
        dataset version of the dataset to be removed

    Yields
    ------
    status_dict : dict
        DataLad result record
    """
    assert catalog  # to indicate that catalog will be used when implemented
    if not dataset_id or not dataset_version:
        yield get_status_dict(
            **res_kwargs,
            status="error",
            message=(
                "Dataset ID and/or VERSION missing: datalad catalog remove "
                "requires both the ID (-i, --dataset_id) and VERSION (-v, "
                "--dataset_version) of the dataset to be removed from the "
                "catalog"
            ),
        )
        sys.exit(err_msg)


def _serve_catalog(
    catalog: WebCatalog,
    res_kwargs: Optional[Dict] = None,
):
    """Start a local http server for viewing/testing a local catalog.

    Parameters
    ----------
    catalog : WebCatalog
        the catalog to be served

    Yields
    ------
    status_dict : dict
        DataLad result record
    """
    os.chdir(catalog.location)
    import http.server
    import socketserver
    from datalad.ui import ui
    import datalad.support.ansi_colors as ac

    PORT = 8000
    HOSTNAME = "localhost"
    # HOSTNAME = '127.0.0.1'
    Handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer((HOSTNAME, PORT), Handler) as httpd:
        ui.message(
            "\nServing catalog at: http://{host}:{port}/ - navigate to this "
            "address in your browser to test the catalog locally - press "
            "CTRL+C to stop local testing\n".format(
                host=ac.color_word(HOSTNAME, ac.BOLD),
                port=ac.color_word(PORT, ac.BOLD),
            )
        )
        httpd.serve_forever()

    yield get_status_dict(**res_kwargs, status="ok", message=("Dataset served"))


def _set_super_of_catalog(
    catalog: WebCatalog,
    dataset_id: str,
    dataset_version: str,
):
    """Set the catalog's main dataset (shown on home page).

    This sets which dataset will be shown on the catalog home page.
    This would normally be a superdataset containing other datasets
    from the catalog (acting as en entry page), but in practice this
    could be any of the datasets.

    Parameters
    ----------
    catalog : WebCatalog
        the catalog to be configured
    dataset_id : str
        id of the dataset chosen to be the main dataset
    dataset_version : str
        version of the dataset chosen to be the main dataset

    Yields
    ------
    status_dict : dict
        DataLad result record
    """
    err_msg = (
        "Dataset ID and/or VERSION missing: datalad catalog set-super requires "
        "both the ID (-i, --dataset_id) and VERSION (-v, --dataset_version) of "
        "the dataset that is to be used as the catalog's super dataset"
    )
    if not dataset_id or not dataset_version:
        raise InsufficientArgumentsError(err_msg)

    catalog.set_main_dataset()

    yield get_status_dict(
        action="catalog_set_super",
        path=abspath(curdir),
        status="ok",
        message=("Superdataset successfully set for catalog"),
    )


def _validate_metadata(metadata: str):
    """Validate supplied metadata entries against catalog schema.

    Parameters
    ----------
    metadata : path-like object
        metadata to be validated

    Yields
    ------
    status_dict : dict
        DataLad result record
    """
    # First check metadata was supplied via -m flag
    if metadata is None:
        err_msg = (
            "No metadata supplied: datalad catalog has to be supplied with "
            "metadata in the form of a path to a file containing a JSON array, "
            "or JSON lines stream, using the argument: -m, --metadata."
        )
        raise InsufficientArgumentsError(err_msg)

    # Setup schema parameters
    package_path = Path(__file__).resolve().parent
    config_dir = package_path / "config"
    schema_dir = package_path / "schema"
    schemas = ["catalog", "dataset", "file", "authors", "extractors"]
    schema_store = {}
    for s in schemas:
        schema_path = schema_dir / str("jsonschema_" + s + ".json")
        schema = read_json_file(schema_path)
        schema_store[schema["$id"]] = schema

    # Access the schema against which incoming metadata items will be validated
    catalog_schema = schema_store["https://datalad.org/catalog.schema.json"]
    RESOLVER = RefResolver.from_schema(catalog_schema, store=schema_store)
    num_lines = _get_line_count(metadata)

    # Open metadata file and validate line by line
    with open(metadata) as file:
        i = 0
        for line in file:
            i += 1
            log_progress(
                lgr.info,
                "catalog_validate",
                f"Start validation of metadata in {metadata}",
                total=num_lines,
                update=i,
                label="metadata validation against catalog schema",
                unit=" Lines",
            )
            meta_dict = json.loads(line.rstrip())
            # Check if item/line is a dict
            if not isinstance(meta_dict, dict):
                err_msg = (
                    "Metadata item not of type dict: metadata items should be "
                    "passed to datalad catalog as JSON objects adhering to the "
                    "catalog schema."
                )
                lgr.warning(err_msg)
            # Validate dict against schema
            try:
                Draft202012Validator(
                    catalog_schema, resolver=RESOLVER
                ).validate(meta_dict)
            except ValidationError as e:
                err_msg = (
                    f"Schema validation failed in LINE {i}/{num_lines}: \n\n{e}"
                )
                raise ValidationError(err_msg) from e

    yield get_status_dict(
        action="catalog_validate",
        path=Path(metadata),
        status="ok",
        message=("Metadata successfully validated"),
    )


def _get_line_count(file: str) -> int:
    """A helper function to get a file line count"""
    return sum(1 for _ in open(file))
