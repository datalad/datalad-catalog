import logging
from datalad_next.commands import (
    Interface,
    build_doc,
)

# Create named logger
lgr = logging.getLogger("datalad.catalog.catalog")


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Catalog(Interface):
    # first docstring line is used a short description in the cmdline help
    # the rest is put in the verbose help and manpage
    """Generate a user-friendly web-based data catalog from structured
    metadata.

    ``datalad catalog`` can be used to ``-create`` a new catalog,
    ``-add`` and ``-remove`` metadata entries to/from an existing catalog,
    start a local http server to ``-serve`` an existing catalog locally.
    It can also ``-validate`` a metadata entry (validation is also
    performed implicitly when adding), ``-set`` dataset properties
    such as the ``home`` page to be shown by default, and ``-get``
    dataset properties such as the ``config``, specific ``metadata``,
    or the ``home`` page.

    Metadata can be provided to DataLad Catalog from any number of
    arbitrary metadata sources, as an aggregated set or as individual
    metadata items. DataLad Catalog has a dedicated schema (using the
    JSON Schema vocabulary) against which incoming metadata items are
    validated. This schema allows for standard metadata fields as one
    would expect for datasets of any kind (such as name, doi, url,
    description, license, authors, and more), as well as fields that
    support identification, versioning, dataset context and linkage,
    and file tree specification.

    The output is a set of structured metadata files, as well as a
    Vue.js-based browser interface that understands how to render this
    metadata in the browser. These can be hosted on a platform of
    choice as a static webpage.

    Note: in the catalog website, each dataset entry is displayed
    under ``<main page>/#/dataset/<dataset_id>/<dataset_version>``.
    By default, the main page of the catalog will display a 404 error,
    unless the default dataset is configured with ``datalad catalog-set
    home``.
    """

    # usage examples
    _examples_ = [
        dict(
            text="CREATE a new catalog from scratch",
            code_py="catalog_create(catalog='/tmp/my-cat')",
            code_cmd="datalad catalog-create -c /tmp/my-cat",
        ),
        dict(
            text="ADD metadata to an existing catalog",
            code_py=(
                "catalog_add(catalog='/tmp/my-cat', "
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd=(
                "datalad catalog-add "
                "-c /tmp/my-cat -m path/to/metadata.jsonl"
            ),
        ),
        dict(
            text=(
                "SET a property of an existing catalog, such as the "
                "home page of an existing catalog - i.e. the first dataset "
                "displayed when navigating to the root URL of the catalog"
            ),
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
                "SERVE the content of the catalog via a local HTTP server "
                "at http://localhost:8001"
            ),
            code_py="catalog_serve(catalog='/tmp/my-cat/', port=8001)",
            code_cmd="datalad catalog-serve -c /tmp/my-cat -p 8001",
        ),
        dict(
            text=(
                "VALIDATE metadata against a catalog schema without adding "
                "it to the catalog"
            ),
            code_py=(
                "catalog_validate(catalog='/tmp/my-cat/',"
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd=(
                "datalad catalog-validate -c /tmp/my-cat/"
                "-m path/to/metadata.jsonl'"
            ),
        ),
        dict(
            text=(
                "GET a property of an existing catalog, "
                "such as the catalog configuration"
            ),
            code_py=("catalog_get(property='config', catalog='/tmp/my-cat/')"),
            code_cmd=("datalad catalog-get -c /tmp/my-cat/ config"),
        ),
        dict(
            text=("REMOVE a specific metadata record from an existing catalog"),
            code_py=(
                "catalog_remove(catalog='/tmp/my-cat', "
                "dataset_id='efgh', dataset_version='5678')"
            ),
            code_cmd=("datalad catalog-remove -c /tmp/my-cat -i efgh -v 5678"),
        ),
        dict(
            text=(
                "TRANSLATE a metalad-extracted metadata item from a particular "
                "source structure into the catalog schema. A dedicated translator "
                "should be provided and exposed as an entry point (e.g. via a DataLad "
                "extension) as part of the 'datalad.metadata.translators' group."
            ),
            code_py=(
                "catalog_translate(catalog='/tmp/my-cat', "
                "metadata='path/to/metadata.jsonl')"
            ),
            code_cmd=(
                "datalad catalog-translate -c /tmp/my-cat -m path/to/metadata.jsonl"
            ),
        ),
        dict(
            text=(
                "RUN A WORKFLOW for recursive metadata extraction (using "
                "datalad-metalad), translating metadata to the catalog schema, "
                "and adding the translated metadata to a new catalog"
            ),
            code_py=(
                "catalog_workflow(mode='new', catalog='/tmp/my-cat/', "
                "dataset='path/to/superdataset', extractor='metalad_core')"
            ),
            code_cmd=(
                "datalad catalog-workflow -t new -c /tmp/my-cat "
                "-d path/to/superdataset -e metalad_core"
            ),
        ),
        dict(
            text=(
                "RUN A WORKFLOW for updating a catalog after registering a "
                "subdataset to the superdataset which the catalog represents. "
                "This workflow includes extraction (using datalad-metalad), "
                "translating metadata to the catalog schema, and adding the "
                "translated metadata to the existing catalog."
            ),
            code_py=(
                "catalog_workflow(mode='update', catalog='/tmp/my-cat/', "
                "dataset='path/to/superdataset', subdataset='path/to/subdataset', "
                "extractor='metalad_core')"
            ),
            code_cmd=(
                "datalad catalog-workflow -t new -c /tmp/my-cat "
                "-d path/to/superdataset -s path/to/subdataset -e metalad_core"
            ),
        ),
    ]

    # parameters of the command, must be exhaustive
    _params_ = dict()

    @staticmethod
    def __call__():
        """ """
        print(Catalog.__doc__)
