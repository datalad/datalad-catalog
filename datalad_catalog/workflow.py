# emacs: -*- mode: python; py-indent-offset: 4; tab-width: 4; indent-tabs-mode: nil -*-
# ex: set sts=4 ts=4 sw=4 et:
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
#
#   See COPYING file distributed along with the datalad package for the
#   copyright and license terms.
#
# ## ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ##
"""Run a workflow to create or update a catalog
"""

from datalad.distribution.dataset import Dataset
from datalad.support.exceptions import IncompleteResultsError
from datalad_catalog.constraints import (
    CatalogRequired,
    EnsureWebCatalog,
)
from datalad_catalog.webcatalog import (
    WebCatalog,
)
from datalad_catalog.add import Add
from datalad_catalog.translate import MetaTranslate
from datalad_catalog.utils import (
    get_available_entrypoints,
    write_jsonline_to_file,
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
    EnsureBool,
    EnsureChoice,
    EnsureInt,
    EnsureListOf,
    EnsurePath,
    EnsureStr,
)
from datalad_next.constraints.dataset import EnsureDataset
import logging
from pathlib import Path
from typing import Union


__docformat__ = "restructuredtext"

lgr = logging.getLogger("datalad.catalog.workflow")


class WorkflowParameterValidator(EnsureCommandParameterization):
    """"""

    def _check_extractors(self, extractor):
        # Parameter is required
        if extractor is None:
            lgr.info(
                msg="No extractors provided, using the default 'metalad_core' extractor"
            )
            extractor = ["metalad_core"]
        extractor = EnsureListOf(EnsureStr(extractor))
        available_extractors = get_available_entrypoints(
            group="datalad.metadata.extractors"
        )
        available_extractor_names = available_extractors.keys()
        for extr in extractor:
            if extr not in available_extractor_names:
                self.raise_for(
                    extractor,
                    f"unknown extractor name provided: {extr}",
                )
        return extractor

    def __init__(self):
        super().__init__(
            param_constraints=dict(
                catalog=CatalogRequired() & EnsureWebCatalog(),
                mode=EnsureChoice("new", "update"),
                dataset=EnsureDataset(installed=True, require_id=True),
                subdataset=EnsureDataset(installed=True, require_id=True),
                recursive=EnsureBool(),
                recursion_limit=EnsureInt(),
                extractor=EnsureListOf(EnsureStr()),
                config_file=EnsurePath(lexists=True),
                force=EnsureBool(),
            ),
            joint_constraints=dict(),
        )


# Decoration auto-generates standard help
@build_doc
# All extension commands must be derived from Interface
class Workflow(ValidatedInterface):
    """Run a workflow to create or update a catalog

    This functionality requires the installation of datalad-metalad as well
    as any datalad extensions providing relevant translators for the extracted
    metadata items.

    It will run a workflow of metadata extraction, translation, and catalog (entry)
    generation, given a DataLad dataset hierarchy and a specified workflow type:
    new/update.
    """

    _validator_ = WorkflowParameterValidator()

    _params_ = dict(
        catalog=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-c", "--catalog"),
            # documentation
            doc="""Location of the existing catalog""",
        ),
        mode=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-t", "--type"),
            # documentation
            doc="""Which type of workflow to run: one of ['new', 'update']""",
        ),
        dataset=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-d", "--dataset"),
            # documentation
            doc="""The datalad dataset on which to run the workflow""",
        ),
        subdataset=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-s", "--subdataset"),
            # documentation
            doc="""The datalad subdataset on which to run the update workflow""",
        ),
        recursive=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-r", "--recursive"),
            # documentation
            doc="""Specifies whether to recurse into subdatasets or not during
            workflow execution""",
            action="store_true",
            default=False,
        ),
        recursion_limit=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-R", "--recursion_limit"),
            # documentation
            doc="""Specifies how many levels to recurse down into the hierarchy
            when recursing into subdatasets""",
            default=0,
        ),
        extractor=Parameter(
            # cmdline argument definitions, incl aliases
            args=("-e", "--extractor"),
            nargs="+",
            # documentation
            doc="""Which extractors to use during metadata extraction of a workflow.
            Multiple can be provided. If none are provided, the default extractor
            'metalad_core' is used. Any extractor name passed as an argument should
            first be known to the current installation via datalad's entrypoint
            mechanism.""",
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
            text=(
                "Run a workflow for recursive metadata extraction (using "
                "the 'metalad_core' extractor), translating metadata to the latest"
                "catalog schema, and adding the translated metadata to a new catalog"
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
                "Run a workflow for updating a catalog after registering a "
                "subdataset to the superdataset which the catalog represents. "
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

    @staticmethod
    # generic handling of command results (logging, rendering, filtering, ...)
    @eval_results
    # signature must match parameter list above
    # additional generic arguments are added by decorators
    def __call__(
        catalog: Union[Path, WebCatalog],
        mode: str,
        dataset: Dataset,
        subdataset: Dataset = None,
        recursive=False,
        recursion_limit=None,
        extractor=["metalad_core"],
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
            action="catalog_workflow",
            action_mode=mode,
            path=catalog.location,
        )
        if mode == "new":
            yield from super_workflow(
                ds=dataset,
                cat=catalog,
                extractors=extractor,
                config_file=config_file,
                force=force,
                **res_kwargs,
            )
        if mode == "update":
            yield from update_workflow(
                superds=dataset,
                subds=subdataset,
                catalog=catalog,
                extractors=extractor,
                **res_kwargs,
            )


def super_workflow(
    ds: Dataset,
    cat: WebCatalog,
    extractors: list,
    config_file=None,
    force=False,
    **kwargs,
):
    """Run a workflow from scratch on a dataset and all its subdatasets

    The workflow includes:
    - Recursively installing the super- and subdatasets
    - Creating the catalog if it does not yet exists
    - Running several steps on the super- and subdatasets:
      - dataset- and file-level metadata extraction
      - extracted metadata translation
      - adding translated metadata to the catalog
    - Setting the super-dataset of catalog
    """
    # Install super and subdatasets
    ds.get(
        get_data=False,
        recursive=True,
        recursion_limit=1,
        on_failure="continue",
    )
    # Create catalog if required
    if not cat.is_created():
        cat.create(config_file, force)

    # Call per-dataset workflow
    def _dataset_workflow_inner(ds, refds, **kwargs):
        """Internal function to allow passing"""
        return dataset_workflow(
            ds, catalog=cat, extractors=extractors, **kwargs
        )

    try:
        # for the superdataset and all top-level subdatasets
        for res in ds.foreach_dataset(
            _dataset_workflow_inner,
            recursive=True,
            recursion_limit=1,
            state="any",
            return_type="generator",
            on_failure="ignore",
        ):
            # unwind result generator
            for partial_result in res.get("result", []):
                yield partial_result
    except IncompleteResultsError as e:
        msg = f"Could not run workflow for all datasets. Inspect errors:\n\n{e}"
        yield get_status_dict(
            **kwargs, status="impossible", message=msg, exception=e
        )
    # Set super dataset of catalog
    main_id = ds.id
    # - sync possible adjusted branch
    ds.repo.localsync()
    # - account for possibility of being on adjusted branch:
    main_version = ds.repo.get_hexsha(ds.repo.get_corresponding_branch())
    cat.set_main_dataset(main_id, main_version)
    yield get_status_dict(
        **kwargs,
        status="ok",
        message="Workflow-new successfully completed",
    )


def update_workflow(
    superds: Dataset,
    subds: Dataset,
    catalog: WebCatalog,
    extractors: list,
    **kwargs,
):
    """Run an update workflow on a specific subdataset and its parent

    The workflow includes running several steps on the super- and subdataset:
    - dataset- and file-level metadata extraction
    - extracted metadata translation
    - adding translated metadata to the catalog

    It then resets the catalog's superdataset to the latest id and version of
    the parent dataset.

    This workflow assumes:
    - The subdataset has already been added as a submodule to the parent dataset
    - The parent dataset already contains the subdataset commit
    """
    # Dataset workflow for super+subdataset
    yield dataset_workflow(
        superds,
        catalog,
        extractors,
    )
    yield dataset_workflow(
        subds,
        catalog,
        extractors,
    )
    # Set super dataset of catalog
    main_id = superds.id
    # - sync possible adjusted branch
    superds.repo.localsync()
    # - account for possibility of being on adjusted branch:
    main_version = superds.repo.get_hexsha(
        superds.repo.get_corresponding_branch()
    )
    catalog.set_main_dataset(main_id, main_version)
    yield get_status_dict(
        **kwargs,
        status="ok",
        message="Workflow-update successfully completed",
    )


def dataset_workflow(ds: Dataset, catalog, extractors, **kwargs):
    """Run a dataset-specific catalog generation workflow.

    This includes:
      - dataset- and file-level metadata extraction
      - extracted metadata translation
      - adding translated metadata to a catalog"""
    # 1. Run dataset-level extraction
    extracted_file = Path(ds.path) / "extracted_meta.json"
    for name in extractors:
        # these are hacks to deal with extractors no yielding
        # results in an ideal way
        # TODO
        if (
            name == "metalad_studyminimeta"
            and not (Path(ds.path) / ".studyminimeta.yaml").exists()
        ):
            continue
        if (
            name == "datacite_gin"
            and not (Path(ds.path) / "datacite.yml").exists()
        ):
            continue
        metadata_record = extract_dataset_level(ds, name)
        write_jsonline_to_file(extracted_file, metadata_record)
    # 2. Run file-level extraction, add output to same file
    # - Not implemented yet
    # 3. Run translation
    translated_file = Path(ds.path) / "translated_meta.json"
    catalog_translate = MetaTranslate()
    res = catalog_translate(
        catalog=catalog,
        metadata=extracted_file,
        result_renderer="disabled",
    )
    for r in res:
        write_jsonline_to_file(
            translated_file,
            r.get("translated_metadata"),
        )
    # 4. Add translated metadata to catalog
    catalog_add = Add()
    return catalog_add(
        catalog=catalog,
        metadata=translated_file,
    )


def extract_dataset_level(dataset, extractor_name):
    """Extract dataset-level metadata using metalad and a specific extractor"""
    from datalad.api import (
        meta_extract,
    )

    res = meta_extract(
        extractorname=extractor_name,
        dataset=dataset,
        result_renderer="disabled",
    )
    return res[0]["metadata_record"]


def conduct_extract_file_level(dataset):
    raise NotImplementedError


def extract_file_level(file):
    raise NotImplementedError
