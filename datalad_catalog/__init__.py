"""DataLad Catalog extension"""

__docformat__ = "restructuredtext"

# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "DataLad Catalog command suite",
    [
        # specification of a command, any number of commands can be defined
        (
            # importable module that contains the command implementation
            "datalad_catalog.catalog",
            # name of the command class implementation in above module
            "Catalog",
            # optional name of the command in the cmdline API
            "catalog",
            # optional name of the command in the Python API
            "catalog",
        ),
        (
            "datalad_catalog.create",
            "Create",
            "catalog-create",
            "catalog_create",
        ),
        (
            "datalad_catalog.add",
            "Add",
            "catalog-add",
            "catalog_add",
        ),
        (
            "datalad_catalog.validate",
            "Validate",
            "catalog-validate",
            "catalog_validate",
        ),
        (
            "datalad_catalog.serve",
            "Serve",
            "catalog-serve",
            "catalog_serve",
        ),
        (
            "datalad_catalog.get",
            "Get",
            "catalog-get",
            "catalog_get",
        ),
        (
            "datalad_catalog.set",
            "Set",
            "catalog-set",
            "catalog_set",
        ),
        (
            "datalad_catalog.remove",
            "Remove",
            "catalog-remove",
            "catalog_remove",
        ),
        (
            "datalad_catalog.translate",
            "MetaTranslate",
            "catalog-translate",
            "catalog_translate",
        ),
        (
            "datalad_catalog.workflow",
            "Workflow",
            "catalog-workflow",
            "catalog_workflow",
        ),
    ],
)


from datalad import setup_package
from datalad import teardown_package

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
