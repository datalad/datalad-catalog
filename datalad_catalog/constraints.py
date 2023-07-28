# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Utility constraints
"""
from datalad_catalog.webcatalog import (
    WebCatalog,
)

from datalad_catalog.utils import dir_exists

from datalad_next.constraints import (
    AnyOf,
    Constraint,
    EnsureGeneratorFromFileLike,
    EnsureJSON,
    WithDescription,
)

__docformat__ = "restructuredtext"


# metadata input via the Add/Create/Validate/Translate commands can be any of:
# - a path to a file containing JSON lines
# - valid JSON lines from STDIN
# - a JSON serialized string
metadata_constraint = WithDescription(
    AnyOf(
        WithDescription(
            EnsureJSON(),
            error_message="not valid JSON content",
        ),
        EnsureGeneratorFromFileLike(EnsureJSON(), exc_mode="yield"),
    ),
    error_message="No constraint satisfied:\n{__itemized_causes__}",
)


# Custom constraint classes
class EnsureWebCatalog(Constraint):
    """"""

    def __call__(self, value) -> WebCatalog:
        # Test for instance of WebCatalog or Path
        if isinstance(value, WebCatalog):
            ctlg = value
        else:
            ctlg = WebCatalog(
                location=str(value),
            )
        # Return the catalog instance if the path does not exist yet
        if not dir_exists(ctlg.location):
            return ctlg
        # Raise error of the path exists but does not have a catalog structure
        if dir_exists(ctlg.location) and not ctlg.is_created():
            self.raise_for(
                value, "should not be a path to a non-catalog directory"
            )
        # Otherwise return catalog instance
        return ctlg


class CatalogRequired(Constraint):
    """"""

    def __call__(self, value):
        # Parameter is required
        if value is None:
            self.raise_for(
                value, "should either be a path or a WebCatalog instance"
            )
        return value
