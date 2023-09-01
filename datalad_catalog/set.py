# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Utility for setting various properties of a catalog
"""

import datalad_catalog.constants as cnst
from datalad_catalog.constraints import (
    EnsureWebCatalog,
    CatalogRequired,
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
    EnsureChoice,
    EnsureStr,
)
import logging
from pathlib import Path
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.set")


class SetParameterValidator(EnsureCommandParameterization):
    """"""

    def _validate_combinations(
        self,
        catalog,
        property,
        dataset_id,
        dataset_version,
    ):
        """"""
        # parameter combinations for setting homepage
        if property == "home":
            # require both dataset_id and dataset_version
            if not dataset_id or not dataset_version:
                self.raise_for(
                    dict(
                        catalog=catalog,
                        property=property,
                        dataset_id=dataset_id,
                        dataset_version=dataset_version,
                    ),
                    (
                        "both the 'dataset_id' and 'dataset_version' arguments are required "
                        "when setting the catalog home page"
                    ),
                )
        # if property == 'config':

    def __init__(self):
        all_params = ("catalog", "property", "dataset_id", "dataset_version")
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                property=EnsureChoice("home", "config"),
                dataset_id=EnsureStr(),
                dataset_version=EnsureStr(),
                reckless=EnsureChoice("overwrite"),
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
class Set(ValidatedInterface):
    """Utility for setting various properties of a catalog, based on the
    specified property ('home' or 'config')

    Used to set the catalog home page, or to reset config at catalog- or dataset-level.
    (Note: the latter is not fully supported yet and will yield an error result)
    """

    _validator_ = SetParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of the existing catalog""",
        ),
        property=Parameter(
            args=("property",),
            doc="""The property to set in the catalog.
            Should be one of 'home' or 'config'.""",
        ),
        dataset_id=Parameter(
            args=("-i", "--dataset_id"),
            doc="""The unique identifier of a dataset.""",
        ),
        dataset_version=Parameter(
            args=("-v", "--dataset_version"),
            doc="""The unique version of a dataset.""",
        ),
        reckless=Parameter(
            args=("--reckless",),
            doc="""Set the property in a potentially unsafe way.
            Supported modes are:
            ["overwrite"]: if the property is already set, overwrite it""",
        ),
    )

    _examples_ = [
        dict(
            text=("Set the home page of an existing catalog"),
            code_py=(
                "catalog_set(property='home', catalog='/tmp/my-cat', "
                "dataset_id='abcd', dataset_version='1234')"
            ),
            code_cmd=(
                "datalad catalog-set -c /tmp/my-cat -i abcd -v 1234 home"
            ),
        ),
        dict(
            text=(
                "Set a new home page of an existing catalog, where the home page "
                "has previously been set "
            ),
            code_py=(
                "catalog_set(property='home', catalog='/tmp/my-cat', "
                "dataset_id='efgh', dataset_version='5678', reckless='overwrite')"
            ),
            code_cmd=(
                "datalad catalog-set -c /tmp/my-cat -i efgh -v 5678 --reckless "
                "overwrite home"
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
        property: str,
        dataset_id: str = None,
        dataset_version: str = None,
        reckless: str = None,
    ):
        res_kwargs = dict(
            action="catalog_set",
            action_property=property,
            path=catalog.location,
        )

        # Yield error for set-operations that haven't been implemented yet
        if property in ("config"):
            msg = f"catalog-set for property={property} is not yet implemented"
            yield get_status_dict(**res_kwargs, status="error", message=msg)

        # Set catalog home page
        if property == "home":
            # First check if a corresponding record with dataset id and version is
            # actually in the catalog
            existing_record = catalog.get_record(dataset_id, dataset_version)
            if existing_record is None:
                if reckless != "overwrite":
                    msg = (
                        f"No dataset record found in catalog for: dataset_id="
                        f"{dataset_id}, dataset_version={dataset_version}."
                        " Home page should not be set to a nonexisting dataset."
                        " To ignore this check and continue to set the home page,"
                        " use '--reckless overwrite'."
                    )
                    yield get_status_dict(
                        **res_kwargs,
                        status="impossible",
                        message=msg,
                        home=None,
                    )

            success_msg = (
                f"Home page successfully set to: dataset_id={dataset_id}, "
                f"dataset_version={dataset_version}."
            )
            success_home_spec = {
                cnst.DATASET_ID: dataset_id,
                cnst.DATASET_VERSION: dataset_version,
            }
            # Check if home is already set
            try:
                home_spec = catalog.get_main_dataset()
                # if home already set and reckless specified, overwrite
                if reckless == "overwrite":
                    catalog.set_main_dataset(dataset_id, dataset_version)
                    yield get_status_dict(
                        **res_kwargs,
                        status="ok",
                        message=success_msg,
                        home=success_home_spec,
                    )
                else:
                    # if home already set and no reckless mode, yield impossible
                    msg = (
                        f"Home page already set: dataset_id={home_spec[cnst.DATASET_ID]}, "
                        f"dataset_version={home_spec[cnst.DATASET_VERSION]}."
                        "To overwrite this property, use '--reckless overwrite'"
                    )
                    yield get_status_dict(
                        **res_kwargs,
                        status="impossible",
                        message=msg,
                        home=home_spec,
                    )
            except FileNotFoundError:
                # if home not set, set it
                catalog.set_main_dataset(dataset_id, dataset_version)
                yield get_status_dict(
                    **res_kwargs,
                    status="ok",
                    message=success_msg,
                    home=success_home_spec,
                )
