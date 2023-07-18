# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Add metadata to an existing catalog
"""
from datalad_catalog.constraints import (
    CatalogRequired,
    EnsureWebCatalog,
    metadata_constraint,
)
import datalad_catalog.constants as cnst
from datalad_catalog.webcatalog import WebCatalog
from datalad_next.commands import (
    EnsureCommandParameterization,
    ValidatedInterface,
    Parameter,
    build_doc,
    eval_results,
    get_status_dict,
)
from datalad_next.constraints import (
    EnsurePath,
)
from datalad_next.exceptions import CapturedException

import json
from jsonschema import ValidationError
import logging
from pathlib import Path
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.add")


class AddParameterValidator(EnsureCommandParameterization):
    """"""

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                metadata=metadata_constraint,
                config_file=EnsurePath(lexists=True),
            ),
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Add(ValidatedInterface):
    """Add metadata to an existing catalog

    Optionally, a dataset-level configuration file can be provided
    (defaults to the catalog-level config if not provided)
    """

    _validator_ = AddParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of the existing catalog""",
        ),
        metadata=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-m", "--metadata"),
            # documentation
            doc="""The metadata records to be added to the catalog.
            Multiple input types are possible:
            - a path to a file containing JSON lines
            - JSON lines from STDIN
            - a JSON serialized string""",
        ),
        config_file=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-F", "--config-file"),
            # documentation
            doc="""Path to config file in YAML or JSON format.
            Default config is read from:
            'datalad_catalog/config/config.json'""",
        ),
    )

    _examples_ = [
        dict(
            text="Add metadata from file to an existing catalog",
            code_py=(
                "catalog_add(catalog='/tmp/my-cat', "
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd=(
                "datalad catalog-add "
                "-c /tmp/my-cat -m path/to/metadata.jsonl"
            ),
        ),
        dict(
            text="Add metadata as JSON string to an existing catalog",
            code_py=(
                "catalog_add(catalog='/tmp/my-cat', "
                "metadata=json.dumps({'my':'metadata'}))"
            ),
            code_cmd=(
                "datalad catalog-add " '-c /tmp/my-cat -m \'{"my":"metadata"}\''
            ),
        ),
        dict(
            text="Add metadata as subject to a dataset-level configuration",
            code_py=(
                "catalog_add(catalog='/tmp/my-cat', "
                "config_file='path/to/dataset_config_file.json')"
            ),
            code_cmd=(
                "datalad catalog-add "
                "-c /tmp/my-cat -F path/to/dataset_config_file.json"
            ),
        ),
    ]

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog: Union[Path, WebCatalog],
        metadata,
        config_file=None,
    ):
        # Instantiate WebCatalog class if necessary
        if isinstance(catalog, WebCatalog):
            ctlg = catalog
        else:
            ctlg = WebCatalog(
                location=catalog,
            )

        res_kwargs = dict(
            action="catalog_add",
            path=ctlg.location,
        )

        # input validation allows for a JSON-serialized string
        # handled by EnsureJSON (which seems to return a dict)
        # -> turn this into a list for uniform processing below
        if isinstance(metadata, (str, dict)):
            metadata = [metadata]

        # PROCESS DESCRIPTION FOR "add":
        # 1. Read lines into python dictionaries. For each line:
        #    - Validate the dictionary against the catalog schema
        #    - Instantiate the MetaItem class, which handles translation of a json line into
        #      the Node instances that populate the catalog
        #    - For the MetaItem instance, write all related Node instances to file
        i = 0
        for line in metadata:
            i += 1
            if isinstance(line, CapturedException):
                # the generator encountered an exception for a particular
                # item and is relaying it as per instructions
                # exc_mode='yield'. We report and move on. Outside
                # flow logic will decide if processing continues
                yield get_status_dict(
                    **res_kwargs,
                    status="error",
                    exception=line,
                )
                continue
            # load json object into dict
            if isinstance(line, str):
                meta_dict = json.loads(line.rstrip())
            else:
                meta_dict = line
            # Check if line is a dict
            if not isinstance(meta_dict, dict):
                err_msg = (
                    "Metadata item not of type dict: metadata items should be "
                    "passed to datalad catalog as JSON objects adhering to the "
                    "catalog schema."
                )
                yield get_status_dict(
                    **res_kwargs,
                    status="impossible",
                    message=err_msg,
                )
                continue
            # Validate dict against catalog schema
            try:
                ctlg.schema_validator.validate(meta_dict)
            except ValidationError as e:
                err_msg = f"Schema validation failed in LINE {i}: \n\n{e}"
                yield get_status_dict(
                    **res_kwargs,
                    status="error",
                    message=err_msg,
                    exception=e,
                )
                continue
            # If validation passed, add the record to the catalog
            # This involves translating the record into Node instances
            # and creating/updating their respective metadata files
            try:
                record_props = ctlg.add_record(meta_dict, config_file)
                if record_props.get("action") == "add":
                    success_msg_part1 = (
                        "Metadata record successfully added to catalog"
                    )
                else:
                    success_msg_part1 = (
                        "Metadata record successfully updated in catalog"
                    )
                if record_props.get("type") == "dataset":
                    success_msg_part2 = "dataset:"
                else:
                    success_msg_part2 = "filetree of dataset:"

                yield get_status_dict(
                    **res_kwargs,
                    status="ok",
                    message=(
                        f"{success_msg_part1} "
                        f"({success_msg_part2} dataset_id={meta_dict[cnst.DATASET_ID]}, "
                        f"dataset_version={meta_dict[cnst.DATASET_VERSION]})"
                    ),
                    metadata=meta_dict,
                )
            except Exception as e:
                err_msg = f"Catalog add operation failed in LINE {i}: \n\n{e}"
                yield get_status_dict(
                    **res_kwargs,
                    status="error",
                    message=err_msg,
                    exception=e,
                )
                continue
