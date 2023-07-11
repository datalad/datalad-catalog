import pytest
from pathlib import Path
from jsonschema import (
    Draft202012Validator,
    RefResolver,
    ValidationError,
)
from datalad_catalog.utils import read_json_file

# Setup schema parameters
package_path = Path(__file__).resolve().parent.parent
schema_dir = package_path / "catalog" / "schema"
schemas = ["dataset", "file", "authors", "metadata_sources"]
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


def test_dataset_valid(test_data):
    """"""
    RESOLVER = RefResolver.from_schema(dataset_schema, store=schema_store)
    Draft202012Validator(dataset_schema, resolver=RESOLVER).validate(
        read_json_file(test_data.catalog_metadata_valid)
    )


def test_dataset_invalid(test_data):
    """"""
    RESOLVER = RefResolver.from_schema(dataset_schema, store=schema_store)
    with pytest.raises(ValidationError):
        Draft202012Validator(dataset_schema, resolver=RESOLVER).validate(
            read_json_file(test_data.catalog_metadata_invalid)
        )
