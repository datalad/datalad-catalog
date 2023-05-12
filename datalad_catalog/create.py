# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Interface for creating a catalog
"""
from datalad.distribution.dataset import datasetmethod
from datalad.interface.base import (
    build_doc,
    eval_results,
)
from datalad_next.commands import (
    EnsureCommandParameterization,
    ValidatedInterface,
    # Parameter,
    build_doc,
    # datasetmethod,
    # eval_results,
    # generic_result_renderer,
    # get_status_dict,
)
from datalad_next.constraints import (
    EnsureBool,
    EnsureChoice,
    EnsureGeneratorFromFileLike,
    EnsureJSON,
    EnsureNone,
    EnsurePath,
    EnsureStr,
)
from datalad_next.constraints.dataset import EnsureDataset
from datalad.support.param import Parameter
import logging
from pathlib import Path


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.create")


class CreateParameterValidator(EnsureCommandParameterization):
    """"""

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog_dir=EnsurePath(),
                metadata=EnsureGeneratorFromFileLike(EnsureJSON()),
                config_file=EnsurePath(lexists=True),
            ),
            joint_constraints=dict(),
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Create(ValidatedInterface):
    """Create a user-friendly web-based data catalog from structured
    metadata.
    ...
    """

    _validator_ = CreateParameterValidator()

    _params_ = dict(
        catalog_dir=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog_dir"),
            # documentation
            doc="""Directory where the catalog is located or will be created.""",
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
            args=("-y", "--config-file"),
            # documentation
            doc="""Path to config file in YAML or JSON format. Default config is read
            from datalad_catalog/config/config.json""",
        ),
        force=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-f", "--force"),
            # documentation
            doc="""If content for the user interface already exists in the catalog
            directory, force this content to be overwritten. Content
            overwritten with this flag include the 'artwork' and 'assets'
            directories and the 'index.html' and 'config.json' files. Content in
            the 'metadata' directory remain untouched.""",
            action="store_true",
            default=False,
        ),
    )

    _examples_ = [
        dict(
            text="Create a new catalog from scratch",
            code_py="catalog('create', catalog_dir='/tmp/my-cat')",
            code_cmd="datalad catalog create -c /tmp/my-cat",
        ),
    ]

    @staticmethod
    # decorator binds the command to the Dataset class as a method
    @datasetmethod(name="catalog_create")
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog_dir: Path = None,
        metadata=None,
        config_file=None,
        force: bool = False,
    ):
        res_kwargs = dict(
            action="catalog_create",
            path=catalog_dir,
        )
