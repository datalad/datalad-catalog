"""
With this script you can do the following for an existing catalog:
- create aliases for datasets from a tsv file (TODO)
- create alias and concept id metadata files for all datasets
"""
from argparse import ArgumentParser
import json
from datalad_catalog.constraints import EnsureWebCatalog
from datalad_catalog.utils import md5hash

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
    # Get report
    report = catalog.get_catalog_report()

    # Write metadata for all datasets
    # assumes that datasets have aliases set
    for d in report.get("datasets", []):
        # Get latest version
        current_ds_versions = [
            dsv for dsv in report.get("versions") if dsv["dataset_id"] == d
        ]
        sorted_versions = sorted(
            current_ds_versions,
            key=lambda d: d.get("updated_at"),
            reverse=True,
        )

        # Dict for metadata
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

        # Create alias metadata
        dataset_alias_path = (
            catalog.metadata_path
            / sorted_versions[0]["alias"]
            / md5hash(sorted_versions[0]["alias"])
        ).with_suffix(".json")
        dataset_alias_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dataset_alias_path, "w") as f:
            json.dump(redirect_dict, f)
