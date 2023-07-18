# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Utility for getting various properties of a catalog
"""
from datalad_catalog.constraints import (
    CatalogRequired,
    EnsureWebCatalog,
)
from datalad_catalog.utils import jsEncoder
from datalad_catalog.webcatalog import (
    WebCatalog,
)
from datalad_next.commands import (
    EnsureCommandParameterization,
    ValidatedInterface,
    Parameter,
    build_doc,
    eval_results,
    get_status_dict,
    ParameterConstraintContext,
)
from datalad_next.constraints import (
    EnsureChoice,
    EnsureStr,
)
from datalad_next.uis import ui_switcher
import logging
import json
from pathlib import Path
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.get")


class GetParameterValidator(EnsureCommandParameterization):
    """"""

    def _validate_combinations(
        self,
        catalog,
        property,
        dataset_id,
        dataset_version,
        record_type,
        record_path,
    ):
        """"""
        # parameter combinations for getting metadata
        if property == "metadata":
            # always require both dataset_id and dataset_version
            if not dataset_id or not dataset_version:
                self.raise_for(
                    dict(
                        catalog=catalog,
                        property=property,
                        dataset_id=dataset_id,
                        dataset_version=dataset_version,
                        record_type=record_type,
                        record_path=record_path,
                    ),
                    (
                        "both the 'dataset_id' and 'dataset_version' arguments are required "
                        "when retrieving metadata"
                    ),
                )
            # require record_type if record_path is specified
            if record_path and not record_type:
                self.raise_for(
                    dict(
                        catalog=catalog,
                        property=property,
                        dataset_id=dataset_id,
                        dataset_version=dataset_version,
                        record_type=record_type,
                        record_path=record_path,
                    ),
                    (
                        "the 'record_type' argument is required when specifying a specific "
                        "'record_path'"
                    ),
                )

            # require record_path for record_type in ('directory', 'file')
            if record_type in ("directory", "file") and not record_path:
                self.raise_for(
                    dict(
                        catalog=catalog,
                        property=property,
                        dataset_id=dataset_id,
                        dataset_version=dataset_version,
                        record_type=record_type,
                        record_path=record_path,
                    ),
                    (
                        "a relative path is required (argument 'record_path') when "
                        "specifying 'record_type' as 'directory' or 'file'"
                    ),
                )
        # parameter combinations for getting config
        if property == "config":
            # require both dataset_id and dataset_version, or neither
            if (dataset_id and not dataset_version) or (
                dataset_version and not dataset_id
            ):
                self.raise_for(
                    dict(
                        catalog=catalog,
                        property=property,
                        dataset_id=dataset_id,
                        dataset_version=dataset_version,
                        record_type=record_type,
                        record_path=record_path,
                    ),
                    (
                        "both the 'dataset_id' and 'dataset_version' arguments are required "
                        "when retrieving dataset-level configuration; neither are required "
                        "when retrieving catalog-level configuration"
                    ),
                )

    def __init__(self):
        all_params = (
            "catalog",
            "property",
            "dataset_id",
            "dataset_version",
            "record_type",
            "record_path",
        )
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                property=EnsureChoice("home", "config", "metadata", "tree"),
                dataset_id=EnsureStr(),
                dataset_version=EnsureStr(),
                record_type=EnsureChoice("dataset", "directory", "file"),
                record_path=EnsureStr(),
            ),
            joint_constraints={
                ParameterConstraintContext(
                    all_params, "validate-parameter-combinations"
                ): self._validate_combinations,
            },
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Get(ValidatedInterface):
    """Utility for getting various properties of a catalog, based on the specified
    property ('home', 'config', 'metadata', 'tree')

    Used to get the catalog home page, get config at catalog- or dataset-level,
    or get the metadata for a specific dataset/version.
    """

    _validator_ = GetParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of the existing catalog""",
        ),
        property=Parameter(
            args=("property",),
            doc="""The property to get in the catalog.
            Should be one of 'home', 'config', 'metadata' or 'tree'.""",
        ),
        dataset_id=Parameter(
            args=("-i", "--dataset_id"),
            doc="""The unique identifier of the dataset for
            which metadata or config has been requested.""",
        ),
        dataset_version=Parameter(
            args=("-v", "--dataset_version"),
            doc="""The unique version of the dataset for
            which metadata or config has been requested.""",
        ),
        record_type=Parameter(
            args=("--record_type",),
            doc="""The type of record in a catalog for which
            metadata has been requested. Should be one of
            'dataset' (default), 'directory', or 'file'.""",
        ),
        record_path=Parameter(
            args=("--record_path",),
            doc="""The relative path of record in a catalog
            for which metadata has been requested. Required
            if 'record_type' is 'directory' or 'file'.""",
        ),
    )

    _examples_ = [
        dict(
            text=("Get the configuration of an existing catalog"),
            code_py=("catalog_get(property='config', catalog='/tmp/my-cat/')"),
            code_cmd=("datalad catalog-get -c /tmp/my-cat/ config"),
        ),
        dict(
            text=("Get the home page details of an existing catalog"),
            code_py=("catalog_get(property='home', catalog='/tmp/my-cat/')"),
            code_cmd=("datalad catalog-get -c /tmp/my-cat/ home"),
        ),
        dict(
            text=(
                "Get metadata of a specific dataset from an existing catalog"
            ),
            code_py=(
                "catalog_get(property='metadata', catalog='/tmp/my-cat', "
                "dataset_id='abcd', dataset_version='1234')"
            ),
            code_cmd=(
                "datalad catalog-get -c /tmp/my-cat -i abcd -v 1234 metadata"
            ),
        ),
        dict(
            text=(
                "Get metadata of a specific directory node in a dataset from "
                "an existing catalog"
            ),
            code_py=(
                "catalog_get(property='metadata', catalog='/tmp/my-cat', "
                "dataset_id='abcd', dataset_version='1234', "
                "record_type='directory', record_path='relative/path/to/directory')"
            ),
            code_cmd=(
                "datalad catalog-get -c /tmp/my-cat -i abcd -v 1234 "
                "--record_type directory --record_path relative/path/to/directory "
                "metadata"
            ),
        ),
    ]

    @staticmethod
    def custom_result_renderer(res, **kwargs):
        """This result renderer dumps the value of the 'output' key
        in the result record in JSON-line format -- only if status==ok"""
        ui = ui_switcher.ui
        ui.message(
            json.dumps(
                res.get("output"),
                separators=(",", ":"),
                indent=None,
                cls=jsEncoder,
            )
        )

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog: Union[Path, WebCatalog],
        property: str,
        dataset_id: str = None,
        dataset_version: str = None,
        record_type: str = None,
        record_path: str = None,
    ):
        res_kwargs = dict(
            action="catalog_get",
            action_property=property,
            path=catalog.location,
        )
        # ui = ui_switcher.ui

        # TODO: add property schema, schema:store, schema:version, schema:catalog, schema:dataset, etc
        # Yield error for get-operations that haven't been implemented yet
        if property in ("tree"):
            msg = f"catalog-get for property={property} is not yet implemented"
            yield get_status_dict(**res_kwargs, status="error", message=msg)
        # Get catalog home page
        if property == "home":
            try:
                home_spec = catalog.get_main_dataset()
                msg = (
                    f"Home page found: dataset_id={home_spec['dataset_id']}, "
                    f"dataset_version={home_spec['dataset_version']}"
                )
                yield get_status_dict(
                    **res_kwargs, status="ok", message=msg, output=home_spec
                )
            except Exception as e:
                msg = "No home page has been set for the catalog"
                yield get_status_dict(
                    **res_kwargs,
                    status="impossible",
                    message=msg,
                    exception=e,
                    output=None,
                )
        # Get catalog metadata for dataset/directory/file
        if property == "metadata":
            # set default record_type
            if record_type is None:
                record_type = "dataset"
            record = catalog.get_record(
                dataset_id=dataset_id,
                dataset_version=dataset_version,
                record_type=record_type,
                relpath=record_path,
            )
            if record is None:
                msg = (
                    "The catalog does not contain a metadata record "
                    "with the specified properties"
                )
                sts = "impossible"
            else:
                msg = "Metadata record retrieved"
                sts = "ok"
            yield get_status_dict(
                **res_kwargs, status=sts, message=msg, output=record
            )
            # if record:
            #     ui.message(json.dumps(record, cls=jsEncoder))
        # Get catalog-level or dataset-level config
        if property == "config":
            if dataset_id and dataset_version:
                # config level is dataset
                # get config from Node
                dataset_node = catalog.get_record(
                    dataset_id=dataset_id,
                    dataset_version=dataset_version,
                    record_type="dataset",
                    relpath=None,
                )
                if dataset_node is None:
                    msg = (
                        "The catalog does not contain a dataset "
                        "with the specified 'dataset_id' and 'dataset_version'"
                    )
                    sts = "impossible"
                else:
                    msg = "Dataset-level configuration retrieved"
                    sts = "ok"
                yield get_status_dict(
                    **res_kwargs,
                    status=sts,
                    message=msg,
                    output=dataset_node["config"],
                )
                # ui.message(json.dumps(dataset_node["config"], cls=jsEncoder))
            else:
                try:
                    cfg = catalog.get_config()
                    msg = f"Catalog-level configuration retrieved"
                    yield get_status_dict(
                        **res_kwargs, status="ok", message=msg, output=cfg
                    )
                    # ui.message(json.dumps(cfg, cls=jsEncoder))
                except Exception as e:
                    msg = "Catalog-level configuration has not been set"
                    yield get_status_dict(
                        **res_kwargs,
                        status="impossible",
                        message=msg,
                        exception=e,
                        output=None,
                    )
