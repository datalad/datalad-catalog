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
from datalad_catalog.webcatalog import WebCatalog
from datalad_catalog.meta_item import MetaItem
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
from datalad_next.exceptions import (
    CapturedException
)

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
                catalog=CatalogRequired()&EnsureWebCatalog(),
                metadata=metadata_constraint,
                config_file=EnsurePath(lexists=True),
            ),
            joint_constraints=dict(),
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
            doc="""Path to input metadata. Multiple input types are possible:
            - A '.json' file containing an array of JSON objects related to a
             single datalad dataset.
            - A stream of JSON objects/lines""",
        ),
        config_file=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-F", "--config-file"),
            # documentation
            doc="""Path to config file in YAML or JSON format. Default config is read
            from datalad_catalog/config/config.json""",
        ),
    )

    _examples_ = [
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
                config_file=config_file,
                catalog_action='add',
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
                    status='error',
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
                    status='impossible',
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
                    status='error',
                    message=err_msg,
                    exception=e,                  
                )
                continue
            # If validation passed, translate into Node instances and their files
            # TODO: implement instance method catalog.add() to be used here
            meta_item = MetaItem(catalog, meta_dict)
            meta_item.write_nodes_to_files()
            yield get_status_dict(
                **res_kwargs,
                status="ok",
                message=("Metadata item successfully added to catalog"),
            )