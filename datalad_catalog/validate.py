# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Validate metadata against the catalog schema
"""
import datalad_catalog.constants as cnst
from datalad_catalog.constraints import (
    EnsureWebCatalog,
    metadata_constraint,
)
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import WebCatalog
from jsonschema import (
    Draft202012Validator,
    RefResolver,
    ValidationError,
)
from datalad_next.commands import (
    EnsureCommandParameterization,
    ValidatedInterface,
    Parameter,
    build_doc,
    eval_results,
    get_status_dict,
)
from datalad_next.exceptions import CapturedException
import json
import logging
from pathlib import Path


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.validate")


class ValidateParameterValidator(EnsureCommandParameterization):
    """"""

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog=EnsureWebCatalog(),
                metadata=metadata_constraint,
            ),
            joint_constraints=dict(),
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Validate(ValidatedInterface):
    """Validate metadata against the catalog schema

    The schema version is determined from the catalog, if provided.
    Otherwise from the latest supported version of the package installation.
    """

    _validator_ = ValidateParameterValidator()

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
    )

    _examples_ = [
        dict(
            text=(
                "Validate metadata against a catalog schema without adding "
                "it to the catalog"
            ),
            code_py=(
                "catalog_validate(catalog='/tmp/my-cat/',"
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd=(
                "datalad catalog-validate -c /tmp/my-cat/"
                "-m path/to/metadata.jsonl'"
            ),
        ),
    ]

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        metadata,
        catalog=None,
    ):
        res_kwargs = dict(
            action="catalog_validate",
            path=catalog.location if bool(catalog) else Path.cwd(),
        )
        # turn non-iterable into a list for uniform processing below
        if isinstance(metadata, (str, dict)):
            metadata = [metadata]
        # Get schema store from 1) catalog or 2) package data
        schema_store = get_schema_store(catalog)
        # Get subsequent Draft202012Validator validator
        schema_validator = get_schema_validator(schema_store)
        # Validate items in metadata
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
                schema_validator.validate(meta_dict)
                yield get_status_dict(
                    **res_kwargs,
                    status="ok",
                )
            except ValidationError as e:
                err_msg = f"Schema validation failed for item {i}: {e}"
                yield get_status_dict(
                    **res_kwargs,
                    status="error",
                    message=err_msg,
                    exception=e,
                )
                continue


def get_schema_store(catalog: WebCatalog = None):
    """Get the applicable schema store containing schemas against
    which incoming metadata should be validated

    If the catalog argument is provided, first retrieve the catalog-specific
    schema store; else, retrieve the package default (i.e. latest) schema store
    """
    if catalog is None:
        schema_store = {}
        # get store from package schema path
        for schema_type, schema_id in cnst.CATALOG_SCHEMA_IDS.items():
            schema_path = cnst.schema_dir / f"jsonschema_{schema_type}.json"
            schema = read_json_file(schema_path)
            schema_store[schema[cnst.DOLLARID]] = schema
    else:
        schema_store = catalog.get_schema_store()
    return schema_store


def get_schema_validator(schema_store: dict):
    """Return schema validator"""
    catalog_schema = schema_store[cnst.CATALOG_SCHEMA_IDS[cnst.CATALOG]]
    resolver = RefResolver.from_schema(catalog_schema, store=schema_store)
    return Draft202012Validator(catalog_schema, resolver=resolver)
