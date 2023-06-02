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
from datalad_next.constraints import (
    Constraint,
)

import logging
from pathlib import Path


__docformat__ = "restructuredtext"


class EnsureWebCatalog(Constraint):
    """"""
    def __call__(self, value) -> WebCatalog:

        if value is None:
            self.raise_for(value, "should either be a path or a WebCatalog instance")

        # Test for instance of WebCatalog or Path
        if isinstance(value, WebCatalog):
            ctlg = value
        else:
            ctlg = WebCatalog(
                location=str(value),
            )
        # Return the catalog instance if the path does not exist yet
        if not ctlg.path_exists():
            return ctlg
        # Raise error of the path exists but does not have a catalog structure
        if ctlg.path_exists() and not ctlg.is_created():
            self.raise_for(value, "should not be a path to a non-catalog directory")
        # Otherwise return catalog instance
        return ctlg
