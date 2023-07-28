# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Remove metadata from an existing catalog
"""
from datalad_catalog.constraints import (
    CatalogRequired,
    EnsureWebCatalog,
)
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
    EnsureBool,
    EnsureStr,
)
import logging
from pathlib import Path
import shutil
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.remove")


class RemoveParameterValidator(EnsureCommandParameterization):
    """"""

    def _validate_combinations(
        self,
        catalog,
        dataset_id,
        dataset_version,
        reckless,
    ):
        """"""
        # always require both dataset_id and dataset_version
        if not dataset_id or not dataset_version:
            self.raise_for(
                dict(
                    catalog=catalog,
                    dataset_id=dataset_id,
                    dataset_version=dataset_version,
                    reckless=reckless,
                ),
                (
                    "both the 'dataset_id' and 'dataset_version' arguments are required "
                    "in order to remove metadata from the catalog"
                ),
            )

        if not reckless:
            self.raise_for(
                dict(
                    catalog=catalog,
                    dataset_id=dataset_id,
                    dataset_version=dataset_version,
                    reckless=reckless,
                ),
                (
                    "This will remove potentially useful metadata from the catalog, "
                    "use the 'reckless' flag to ignore this warning and continue "
                    "with metadata removal."
                ),
            )

    def __init__(self):
        all_params = (
            "catalog",
            "dataset_id",
            "dataset_version",
            "reckless",
        )
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                dataset_id=EnsureStr(),
                dataset_version=EnsureStr(),
                force=EnsureBool(),
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
class Remove(ValidatedInterface):
    """Remove metadata from an existing catalog

    This will remove metadata corresponding to a specified
    dataset_id and dataset_version from an existing catalog.

    This command has to be called with the reckless flag to
    ignore a warning message.
    """

    _validator_ = RemoveParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of the existing catalog""",
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
        reckless=Parameter(
            args=("--reckless",),
            doc="""Remove the dataset in a potentially unsafe way.
            A standard catalog-remove call without this flag
            will provide a warning and do nothing else""",
            action="store_true",
            default=False,
        ),
    )

    _examples_ = [
        dict(
            text=("REMOVE a specific metadata record from an existing catalog"),
            code_py=(
                "catalog_remove(catalog='/tmp/my-cat', "
                "dataset_id='efgh', dataset_version='5678', reckless=True)"
            ),
            code_cmd=(
                "datalad catalog-remove -c /tmp/my-cat -i efgh -v 5678 --reckless"
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
        dataset_id: str,
        dataset_version: str,
        reckless: bool = False,
    ):
        # Instantiate WebCatalog class if necessary
        if isinstance(catalog, WebCatalog):
            ctlg = catalog
        else:
            ctlg = WebCatalog(
                location=catalog,
            )
        res_kwargs = dict(
            action="catalog_remove",
            path=ctlg.location,
        )

        existing_record = ctlg.get_record(dataset_id, dataset_version)
        if existing_record is None:
            msg = (
                f"No dataset record found in catalog for: dataset_id="
                f"{dataset_id}, dataset_version={dataset_version}."
            )
            yield get_status_dict(
                **res_kwargs,
                status="impossible",
                message=msg,
            )
            return

        if reckless:
            id_path = Path(catalog.location) / "metadata" / dataset_id
            version_path = id_path / dataset_version
            shutil.rmtree(version_path)
            # remove id directory if it is empty
            if not any(id_path.iterdir()):
                shutil.rmtree(id_path)
            success_msg = (
                f"Metadata record successfully removed (dataset_id={dataset_id}, "
                f"dataset_version={dataset_version})"
            )
            yield get_status_dict(
                **res_kwargs,
                status="ok",
                message=success_msg,
            )
            return
        else:
            msg = (
                "This will remove potentially useful metadata from the catalog, "
                "use the 'reckless' flag to ignore this warning and continue "
                "with metadata removal."
            )
            yield get_status_dict(
                **res_kwargs,
                status="error",
                message=msg,
            )
            return
