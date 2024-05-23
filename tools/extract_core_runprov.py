"""
The extract_core_runprov.py script:

- takes paths to a DataLad dataset and to a catalog as arguments
- extracts core metadata as well as runprov metadata from the dataset
- translates these records to catalog-ready records
- adds the records to the catalog
"""

from argparse import ArgumentParser
import json
from pathlib import Path

from datalad_catalog.extractors import (
    catalog_core,
    catalog_runprov,
)
from datalad_catalog.constraints import EnsureWebCatalog
from datalad_next.constraints.dataset import EnsureDataset


def get_metadata_records(dataset):
    """"""
    # first get core dataset-level metadata
    core_record = catalog_core.get_catalog_metadata(dataset)
    # then get runprov dataset-level metadata
    runprov_record = catalog_runprov.get_catalog_metadata(
        source_dataset=dataset,
        process_type='dataset')
    # return both
    return core_record, runprov_record


def add_to_catalog(records, catalog):
    from datalad.api import  (
        catalog_add,
        catalog_set,
    )
    # Add metadata to the catalog
    for r in records:
        catalog_add(
            catalog=catalog,
            metadata=json.dumps(r),
        )    


if __name__ == "__main__":

    parser = ArgumentParser()
    parser.add_argument(
        "dataset_path", type=str, help="Path to the datalad dataset",
    )
    parser.add_argument(
        "catalog_path", type=str, help="Path to the catalog",
    )
    args = parser.parse_args()
    # Ensure is a dataset
    ds = EnsureDataset(
        installed=True, purpose="extract metadata", require_id=True
    )(args.dataset_path).ds
    # Ensure is a catalog
    catalog = EnsureWebCatalog()(args.catalog_path)
    core_record, runprov_record = get_metadata_records(ds)
    
    print(json.dumps(core_record))
    print("\n")
    print(json.dumps(runprov_record))

    # Add metadata to catalog
    add_to_catalog([core_record, runprov_record], catalog)