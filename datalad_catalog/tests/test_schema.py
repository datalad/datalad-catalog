import pytest
from pathlib import Path
from datalad.support.exceptions import InsufficientArgumentsError
from jsonschema import (
    Draft202012Validator,
    RefResolver,
    ValidationError,
    validate,
)

from datalad_catalog.catalog import Catalog
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import WebCatalog

# Setup schema parameters
package_path = Path(__file__).resolve().parent.parent
schema_dir = package_path / "schema"
schemas = ["dataset", "file", "authors", "extractors"]
schema_store = {}
for s in schemas:
    schema_path = schema_dir / str("jsonschema_" + s + ".json")
    schema = read_json_file(schema_path)
    schema_store[schema["$id"]] = schema
dataset_schema = schema_store["https://datalad.org/catalog.dataset.schema.json"]


def test_schema():
    """"""
    for s in schema_store.values():
        Draft202012Validator.check_schema(s)


def test_dataset_valid():
    """"""
    test_metadata = read_json_file(
        package_path / "tests/data/catalog_metadata_valid.json"
    )
    RESOLVER = RefResolver.from_schema(dataset_schema, store=schema_store)
    Draft202012Validator(dataset_schema, resolver=RESOLVER).validate(
        test_metadata
    )


def test_dataset_invalid():
    """"""
    test_metadata_invalid = read_json_file(
        package_path / "tests/data/catalog_metadata_invalid.json"
    )
    RESOLVER = RefResolver.from_schema(dataset_schema, store=schema_store)
    with pytest.raises(ValidationError):
        Draft202012Validator(dataset_schema, resolver=RESOLVER).validate(
            test_metadata_invalid
        )
