# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Print the dataset-version tree of a catalog
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
)
from datalad_next.uis import ui_switcher
import logging
from pathlib import Path
from time import gmtime, strftime
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.serve")


class TreeParameterValidator(EnsureCommandParameterization):
    """"""

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
            ),
            joint_constraints=dict(),
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Tree(ValidatedInterface):
    """Print the tree of datasets and their respective versions
    contained in a catalog
    """

    _validator_ = TreeParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of the existing catalog""",
        ),
    )

    _examples_ = [
        dict(
            text=("Print a catalog metadata tree"),
            code_py="catalog_tree(catalog='/tmp/my-cat/')",
            code_cmd="datalad catalog-tree -c /tmp/my-cat",
        ),
    ]

    @staticmethod
    def custom_result_renderer(res, **kwargs):
        """This result renderer dumps the value of the 'output' key
        in the result record in JSON-line format -- only if status==ok"""
        ui = ui_switcher.ui
        if res["result_type"] == "dataset":
            if res["i"] == 0:
                ui.message(res["catalog_name"])
                ui.message(".")
            ds_prefix = "└──" if res["i"] + 1 == res["N_datasets"] else "├──"
            ui.message(f"{ds_prefix} DS[{res['i']}]: {res['dataset_name']}")
            indent = "    " if res["i"] + 1 == res["N_datasets"] else "│   "
            ui.message(f"{indent}ID: {res['d']}; ALIAS: {res['dataset_alias']}")
            ui.message(f"{indent}Versions:")
        elif res["result_type"] == "version":
            indent = "    " if res["i"] + 1 == res["N_datasets"] else "│   "
            version_prefix = (
                "└──" if res["j"] + 1 == res["N_ds_versions"] else "├──"
            )
            postfix = ""
            if (
                res["d"] == res["homepage"]["id"]
                and res["dataset_version"] == res["homepage"]["version"]
            ):
                postfix = " (HOMEPAGE)"
            ui.message(
                f"{indent}{version_prefix} {res['dataset_version']} (Updated: {strftime('%a, %d %b %Y %H:%M:%S +0000', gmtime(res['updated_at']))}){postfix}"
            )
        else:
            ui.message("│")

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog: Union[Path, WebCatalog],
    ):
        res_kwargs = dict(
            action="catalog_tree",
            path=catalog.location,
        )
        report = catalog.get_catalog_report()
        res_kwargs["catalog_name"] = catalog.location.name
        res_kwargs["homepage"] = {
            "id": report.get("homepage_id"),
            "version": report.get("homepage_version"),
        }
        all_datasets = report.get("datasets")
        N_datasets = len(all_datasets)
        res_kwargs["N_datasets"] = N_datasets
        for i, d in enumerate(all_datasets):
            res_kwargs["i"] = i
            res_kwargs["d"] = d

            found_dv = next(
                (dv for dv in report.get("versions") if dv["dataset_id"] == d),
                "",
            )
            res_kwargs["dataset_name"] = found_dv["dataset_name"]
            res_kwargs["dataset_alias"] = found_dv.get("alias", None)
            res_kwargs["result_type"] = "dataset"
            yield get_status_dict(status="ok", **res_kwargs)

            current_ds_versions = [
                dsv for dsv in report.get("versions") if dsv["dataset_id"] == d
            ]
            res_kwargs["N_ds_versions"] = len(current_ds_versions)
            for j, cdsv in enumerate(current_ds_versions):
                res_kwargs["j"] = j
                res_kwargs["dataset_version"] = cdsv.get("dataset_version")
                res_kwargs["updated_at"] = cdsv.get("updated_at")
                res_kwargs["result_type"] = "version"
                yield get_status_dict(status="ok", **res_kwargs)

            if not i + 1 == N_datasets:
                res_kwargs["result_type"] = ""
                yield get_status_dict(status="ok", **res_kwargs)
