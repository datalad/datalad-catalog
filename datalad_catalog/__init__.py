"""DataLad Catalog extension"""

__docformat__ = 'restructuredtext'

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
            'datalad_catalog.webui_generate',
            # name of the command class implementation in above module
            'Catalog',
            # optional name of the command in the cmdline API
            'catalog',
            # optional name of the command in the Python API
            'catalog_cmd'
        ),
    ]
)


from datalad import setup_package
from datalad import teardown_package

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
