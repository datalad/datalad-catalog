"""
With this script you can do the following for an existing catalog:
- create aliases for datasets from a tsv file
- create alias and concept id metadata files for all datasets
"""

from argparse import ArgumentParser
import csv
import json
from pathlib import Path
from datalad.api import (
    catalog_add,
)
from datalad_catalog.constraints import EnsureWebCatalog
from datalad_catalog.utils import md5hash
from datalad_catalog.schema_utils import get_metadata_item


def add_aliases(alias_path, catalog):
    alias_path = Path(alias_path)
    ids_processed = []
    with alias_path.open(newline="") as tsvfile:
        reader = csv.DictReader(tsvfile, delimiter="\t")
        for i, row in enumerate(reader):
            meta_item = get_metadata_item(
                item_type="dataset",
                dataset_id=row["dataset_id"],
                dataset_version=row["dataset_version"],
                source_name="automated_alias_entry",
                source_version="0.1.0",
                required_only=True,
                exclude_keys=[],
            )
            meta_item["alias"] = row["alias"]
            catalog_add(
                catalog=catalog,
                metadata=json.dumps(meta_item),
            )
            ids_processed.append(row["dataset_id"])

    return ids_processed


def create_metadata_files(catalog, ids_to_process):
    # Get report
    report = catalog.get_catalog_report()
    # Write metadata for all datasets
    # - assumes that datasets have aliases set
    for d in report.get("datasets", []):
        if d not in ids_to_process:
            continue
        # Get latest version
        current_ds_versions = [
            dsv for dsv in report.get("versions") if dsv["dataset_id"] == d
        ]
        sorted_versions = sorted(
            current_ds_versions,
            key=lambda d: d.get("updated_at"),
            reverse=True,
        )
        # Dict for id concept metadata
        redirect_dict = {
            "type": "redirect",
            "dataset_id": d,
            "dataset_version": sorted_versions[0]["dataset_version"],
        }
        # Create id concept metadata
        dataset_concept_path = (
            catalog.metadata_path / d / md5hash(d)
        ).with_suffix(".json")
        dataset_concept_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dataset_concept_path, "w") as f:
            json.dump(redirect_dict, f)
        # Dict for alias metadata
        redirect_dict = {
            "type": "redirect",
            "dataset_id": d,
        }
        # Create alias metadata
        dataset_alias_path = (
            catalog.metadata_path
            / sorted_versions[0]["alias"]
            / md5hash(sorted_versions[0]["alias"])
        ).with_suffix(".json")
        dataset_alias_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dataset_alias_path, "w") as f:
            json.dump(redirect_dict, f)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--catalog",
        type=str,
        help="Path to the catalog",
    )
    parser.add_argument(
        "--aliases",
        type=str,
        help="Path to tsv file with dataset ids and aliases",
    )
    args = parser.parse_args()
    # Ensure is a catalog
    catalog = EnsureWebCatalog()(args.catalog)

    # If aliases are provided, first set them in metadata
    ids_processed = []
    if args.aliases:
        ids_processed = add_aliases(args.aliases, catalog)

    create_metadata_files(catalog, ids_processed)
