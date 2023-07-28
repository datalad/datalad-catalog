# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Create a new catalog
"""
from datalad_catalog.constraints import (
    CatalogRequired,
    EnsureWebCatalog,
)
from datalad_catalog.webcatalog import (
    WebCatalog,
)
from datalad_catalog.add import Add
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
    EnsurePath,
)
import logging
from pathlib import Path
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.create")


class CreateParameterValidator(EnsureCommandParameterization):
    """"""

    def _check_force(self, catalog, force):
        """"""
        if catalog.is_created() and not force:
            self.raise_for(
                dict(catalog=catalog, force=force),
                "the force flag should be True to overwrite the assets of an existing catalog",
            )

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                config_file=EnsurePath(lexists=True),
                force=EnsureBool(),
            ),
            joint_constraints={
                ParameterConstraintContext(
                    ("catalog", "force"), "force-when-existing"
                ): self._check_force,
            },
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Create(ValidatedInterface):
    """Create a user-friendly web-based data catalog, with or without
    metadata.

    If the catalog does not exist at the specified location, it will be
    created. If the catalog exists and the force flag is True, this will
    overwrite assets of the existing catalog, while catalog metadata
    remain unchanged.

    Parameters
    ----------
    catalog : path-like object | WebCatalog instance
        an instance of the catalog to be created
    metadata : path-like object, optional
        metadata to be added to the catalog after creation
    force : bool, optional
        if True, will overwrite assets of an existing catalog

    Yields
    ------
    status_dict : dict
        DataLad result record
    """

    _validator_ = CreateParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Directory where the catalog is located or will be created.""",
        ),
        metadata=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-m", "--metadata"),
            # documentation
            doc="""The metadata records to be added to the catalog.
            Multiple input types are possible:
            - a path to a file containing JSON lines
            - JSON lines from STDIN
            - a JSON serialized string""",
        ),
        config_file=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-F", "--config-file"),
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
            code_py="catalog_create(catalog='/tmp/my-cat')",
            code_cmd="datalad catalog-create -c /tmp/my-cat",
        ),
        dict(
            text=(
                "Create a new catalog at a location where a directory "
                "already exists. This will overwrite all catalog content "
                "except for metadata."
            ),
            code_py="catalog_create(catalog='/tmp/my-cat', force=True)",
            code_cmd="datalad catalog-create -c /tmp/my-cat --force",
        ),
        dict(
            text=("Create a new catalog and add metadata"),
            code_py=(
                "catalog_create(catalog='/tmp/my-cat', "
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd="datalad catalog-create -c /tmp/my-cat -m path/to/metadata.jsonl",
        ),
        dict(
            text=("Create a new catalog with a custom configuration"),
            code_py=(
                "catalog_create(catalog='/tmp/my-cat', "
                "config_file='path/to/custom_config_file.json')"
            ),
            code_cmd="datalad catalog-create -c /tmp/my-cat -F path/to/custom_config_file.json",
        ),
    ]

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        # catalog: str,
        catalog: Union[Path, WebCatalog],
        metadata=None,
        config_file=None,
        force: bool = False,
    ):
        # Instantiate WebCatalog class if necessary
        if isinstance(catalog, WebCatalog):
            ctlg = catalog
        else:
            ctlg = WebCatalog(
                location=catalog,
            )

        res_kwargs = dict(
            action="catalog_create",
            path=ctlg.location,
        )
        # Determine message based on catalog state and force flag
        msg = ""
        if not ctlg.is_created():
            msg = ("Catalog successfully created at: %s", ctlg.location)
        else:
            if force:
                msg = (
                    "Catalog assets successfully overwritten at: %s",
                    ctlg.location,
                )

        ctlg.create(config_file, force)

        # Yield created/overwritten status message
        yield get_status_dict(**res_kwargs, status="ok", message=msg)

        # If metadata was also supplied, add this to the catalog
        # Assume that config applies to catalog level since it was
        # provide with 'create', i.e. no need to send to 'add'
        # Dataset-level will inherit from catalog config in any case.
        if metadata is not None:
            catalog_add = Add()
            yield from catalog_add(
                catalog=catalog,
                metadata=metadata,
                config_file=None,
            )
