import json
import jq
import logging
from pathlib import Path
from uuid import UUID

from datalad.api import (
    meta_extract,
    meta_conduct,
)
from datalad.distribution.dataset import Dataset
from datalad.local.wtf import _describe_metadata_elements
from datalad.support.exceptions import IncompleteResultsError
from datalad_catalog.translate import (
    Translate,
)
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import WebCatalog
from datalad_catalog.catalog import (
    _add_to_catalog,
)

# metadata_file = Path('datalad_catalog/tests/data/metadata_datacite_gin.json')
# metadata_record = utils.read_json_file(metadata_file)
# translate.Translate(metadata_record).run_translator()

lgr = logging.getLogger("datalad.catalog.workflows")

# DETAILS FOR EXTRACTORS AND TRANSLATORS
extractor_names_dataset = [
    "metalad_core",
    "metalad_studyminimeta",
    "bids_dataset",
    "datacite_gin",
]
extractor_names_file = [
    "metalad_core",
]
required_files = dict(
    metalad_core=[""],
    metalad_studyminimeta=[".studyminimeta.yaml"],
    bids_dataset=["participants.tsv", "dataset_description.json"],
    datacite_gin=["datacite.yml"],
)
translator_map = {
    "metalad_core": {
        "file": "_metaladcore2catalog_file.json",
        "dataset": "_metaladcore2catalog_dataset.json",
    },
    "metalad_studyminimeta": "_studyminimeta2catalog.json",
    "bids_dataset": "_bidsdataset2catalog.json",
    "datacite_gin": "_datacitegin2catalog.json",
}
extractor_map = {
    "metalad_core": "datalad-metalad",
    "metalad_studyminimeta": "datalad-metalad",
    "bids_dataset": "datalad-neuroimaging",
    "datacite_gin": "datalad-catalog",
}
# INTERNAL PATHS
package_path = Path(__file__).resolve().parent
schema_dir = package_path / "schema"


class jsEncoder(json.JSONEncoder):
    """Class to return objects as strings for correct JSON encoding"""

    def default(self, obj):
        if isinstance(obj, UUID) or isinstance(obj, Path):
            # if the obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def super_workflow(dataset_path, catalog: WebCatalog):
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
    ds = Dataset(dataset_path)
    ds.get(
        get_data=False,
        recursive=True,
        recursion_limit=1,
        on_failure="continue",
    )
    # Create catalog
    cat = catalog
    if not cat.is_created():
        cat.create()

    # Call per-dataset workflow
    def _dataset_workflow_inner(ds, refds, **kwargs):
        """Internal function to allow passing"""
        return dataset_workflow(ds, catalog=cat, **kwargs)

    try:
        # for the superdataset and all top-level subdatasets
        for res in ds.foreach_dataset(
            _dataset_workflow_inner,
            recursive=True,
            recursion_limit=1,
            state="any",
            return_type="generator",
            on_failure="continue",
        ):
            # unwind result generator
            for partial_result in res.get("result", []):
                yield partial_result
    except IncompleteResultsError as e:
        lgr.error(
            f"Could not run workflow for all datasets. Inspect errors:\n\n{e}"
        )

    # Set super dataset of catalog
    cat.main_id = ds.id
    # - sync possible adjusted branch
    ds.repo.localsync()
    # - account for possibility of being on adjusted branch:
    cat.main_version = ds.repo.get_hexsha(ds.repo.get_corresponding_branch())
    cat.set_main_dataset()


def update_workflow(superds_path, subds_path, catalog: WebCatalog):
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
    # Install super and subdatasets
    super_ds = Dataset(superds_path)
    sub_ds = Dataset(subds_path)
    # Dataset workflow for super+subdataset
    yield dataset_workflow(super_ds, catalog)
    yield dataset_workflow(sub_ds, catalog)
    # Set super dataset of catalog
    catalog.main_id = super_ds.id
    # - sync possible adjusted branch
    super_ds.repo.localsync()
    # - account for possibility of being on adjusted branch:
    catalog.main_version = super_ds.repo.get_hexsha(
        super_ds.repo.get_corresponding_branch()
    )
    catalog.set_main_dataset()


def dataset_workflow(ds: Dataset, catalog, **kwargs):
    """Run a dataset-specific catalog generation workflow.

    This includes:
      - dataset- and file-level metadata extraction
      - extracted metadata translation
      - adding translated metadata to a catalog"""
    # 1. Run dataset-level extraction
    extracted_file = Path(ds.path) / "extracted_meta.json"
    for name in extractor_names_dataset:
        if (
            name not in _getAvailableExtractors().keys()
            and check_required_files(ds, name)
        ):
            warning_msg = (
                f"Extractor '{name}' not available. Please install "
                f"{extractor_map[name]} to include additional metadata."
            )
            lgr.warning(warning_msg)
            continue
        if check_required_files(ds, name):
            metadata_record = extract_dataset_level(ds, name)
            write_jsonline_to_file(extracted_file, metadata_record)
    # 2. Run file-level extraction, add output to same file
    # - Not implemented yet
    # 3. Run translation
    translated_file = Path(ds.path) / "translated_meta.json"
    with open(extracted_file) as file:
        for line in file:
            meta_dict = json.loads(line.rstrip())
            try:
                # extr_name = meta_dict["extractor_name"]
                # extr_type = meta_dict["type"]
                # mapping_path = schema_dir / get_translation_map(
                #     extr_name, extr_type
                # )
                write_jsonline_to_file(
                    translated_file,
                    Translate(
                        meta_dict, get_all_translators()
                    ).run_translator(),
                )
            except Exception as e:
                lgr.error("Failed to translate line due to error: %s", str(e))
                continue
    # 4. Add translated metadata to catalog
    return _add_to_catalog(catalog, translated_file, dict())


def extract_dataset_level(dataset, extractor_name):
    """Extract dataset-level metadata using metalad and a specific extractor"""
    res = meta_extract(
        extractorname=extractor_name,
        dataset=dataset,
        result_renderer="disabled",
    )
    return res[0]["metadata_record"]


def conduct_extract_file_level(dataset):
    """NOT IMPLEMENTED YET"""


def extract_file_level(file):
    """NOT IMPLEMENTED YET"""


def check_required_files(dataset: Dataset, extractor_name: str):
    for fn in required_files[extractor_name]:
        f_path = Path(dataset.path) / fn
        if not f_path.exists():
            return False
    return True


def write_jsonline_to_file(filename, line):
    """Write a single JSON line to file"""
    with open(filename, "a") as f:
        json.dump(line, f, cls=jsEncoder)
        f.write("\n")


def translate_to_catalog(meta_obj, mapping_path):
    """Transforms JSON to JSON using JQ bindings and a translation map

    A translation map should:
    - be a JSON object written to file
    - be placed in the 'datalad_catalog/schema/' directory
    - contain 'variables' and 'properties' keys (respectively, dict and array of dicts)

    Variables are mapped directly from the input object (meta_obj).
    Properties are mapped from whichever variable is defined as its 'input'.
    Mapping strings can be constructed using jq syntax: https://stedolan.github.io/jq/
    """
    mapping_dict = read_json_file(Path(mapping_path))
    # Create data variables
    data_vars = dict()
    for key in mapping_dict["variables"].keys():
        data_vars[key] = jq.first(mapping_dict["variables"][key], meta_obj)
    # Map
    new_obj = dict()
    for prop in mapping_dict["properties"]:
        if prop["program"] is None:
            new_obj[prop["name"]] = prop["input"]
        else:
            new_obj[prop["name"]] = jq.first(
                prop["program"], data_vars[prop["input"]]
            )
    # Return translated dict
    return new_obj


def get_translation_map(extractor_name, extractor_type):
    """Get the mapping file name from for a specific extractor"""
    try:
        mapping_file = translator_map[extractor_name]
        if isinstance(mapping_file, dict):
            mapping_file = mapping_file[extractor_type]
        return mapping_file
    except Exception as e:
        raise (e)


def _getKnownExtractors():
    # returns all extractors known to datalad-metalad
    return _describe_metadata_elements("datalad.metadata.extractors")


def _getAvailableExtractors():
    # returns all extractors known to datalad-metalad, with no load errors
    extractor_dict = _getKnownExtractors()
    return {
        name: extractor_dict[name]
        for name in extractor_dict.keys()
        if extractor_dict[name].get("load_error", None) is None
    }
