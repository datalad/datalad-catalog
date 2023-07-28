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
    EnsureCommandParameterization,
    ValidatedInterface,
    Parameter,
    build_doc,
    eval_results,
    get_status_dict,
)
from datalad_next.constraints import (
    EnsureRange,
    EnsureInt,
)
import logging
from pathlib import Path
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.serve")


class ServeParameterValidator(EnsureCommandParameterization):
    """"""

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                port=EnsureInt() & EnsureRange(1025, 9999),
            ),
            joint_constraints=dict(),
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
    ]

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog: Union[Path, WebCatalog],
        port: int = 8000,
    ):
        res_kwargs = dict(
            action="catalog_serve",
            path=catalog.location,
        )
        try:
            catalog.serve(port=port)
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
