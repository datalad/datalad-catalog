# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Serve a catalog via a local http server
"""
from datalad_catalog.constraints import (
    CatalogRequired,
    EnsureWebCatalog,
)
from datalad_catalog.webcatalog import (
    WebCatalog,
)
from datalad_next.commands import (
    build_doc,
    EnsureCommandParameterization,
    eval_results,
    get_status_dict,
    ValidatedInterface,
    Parameter,
    ParameterConstraintContext,
)
from datalad_next.constraints import (
    EnsureInt,
    EnsurePath,
    EnsureRange,
)
import logging
from pathlib import Path
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.serve")


class ServeParameterValidator(EnsureCommandParameterization):
    """"""

    def _validate_combinations(
        self,
        catalog,
        port,
        base,
    ):
        """"""
        # parameter combinations for catalog and base

        if catalog and base:
            if not catalog.location.resolve().is_relative_to(base.resolve()):
                self.raise_for(
                    dict(
                        catalog=catalog,
                        port=port,
                        base=base,
                    ),
                    (
                        f"the catalog location ({catalog.location.resolve()}) should be relative "
                        "to the base path"
                    ),
                )

    def __init__(self):
        all_params = ("catalog", "port", "base")
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                port=EnsureInt() & EnsureRange(1025, 9999),
                base=EnsurePath(),
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
class Serve(ValidatedInterface):
    """Start a local http server to render and test a local catalog.

    Optional arguments include a custom port.
    """

    _validator_ = ServeParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of the existing catalog to be served""",
        ),
        port=Parameter(
            # cmdline argument definitions, incl aliases
            args=("--port",),
            # documentation
            doc="""The port at which the content is served at
            'localhost' (default 8000)""",
        ),
        base=Parameter(
            # cmdline argument definitions, incl aliases
            args=("--base",),
            # documentation
            doc="""The base path that should be served as the 'localhost'
            root, implying that the catalog will be served from a
            subdirectory relative to the base path. Must be a parent
            path of the catalog location.           
            """,
        ),
    )

    _examples_ = [
        dict(
            text=("SERVE the content of the catalog via a local HTTP server"),
            code_py="catalog_serve(catalog='/tmp/my-cat/')",
            code_cmd="datalad catalog-serve -c /tmp/my-cat",
        ),
        dict(
            text=(
                "SERVE the content of the catalog via a local HTTP server "
                "at a custom port, e.g. http://localhost:8001"
            ),
            code_py="catalog_serve(catalog='/tmp/my-cat/', port=8001)",
            code_cmd="datalad catalog-serve -c /tmp/my-cat -p 8001",
        ),
        dict(
            text=(
                "SERVE the content of the catalog via a local HTTP server "
                "at a custom subdirectory, e.g. http://localhost:8000/my-cat"
            ),
            code_py="catalog_serve(catalog='/tmp/my-cat/', base='/tmp')",
            code_cmd="datalad catalog-serve -c /tmp/my-cat --base /tmp",
        ),
    ]

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog: Union[Path, WebCatalog],
        port: int = 8000,
        base=None,
    ):
        res_kwargs = dict(
            action="catalog_serve",
            path=catalog.location,
            basepath=base,
        )
        try:
            catalog.serve(port=port, base=base)
            yield get_status_dict(
                **res_kwargs,
                status="ok",
                message=("Catalog served successfully"),
            )
        except Exception as e:
            yield get_status_dict(
                **res_kwargs,
                status="error",
                message=(f"HTTP server error: {e}"),
                exception=e,
            )
