from datalad.tests.utils_pytest import (
    assert_in_results,
    assert_result_count,
)
from datalad_catalog.add import Add

import io
import json
import pytest


from datalad_next.constraints.exceptions import CommandParametrizationError

catalog_add = Add()


def test_no_args(demo_catalog, test_data):
    """Both the catalog and metadata arguments are required"""
    with pytest.raises(CommandParametrizationError):
        catalog_add()

    with pytest.raises(CommandParametrizationError):
        catalog_add(catalog=demo_catalog)

    with pytest.raises(CommandParametrizationError):
        catalog_add(metadata=test_data.catalog_metadata_dataset1)


def test_add_from_file(demo_catalog, test_data):
    """Add catalog metadata from a file with json line(s)"""
    res = catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset1,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_add",
        status="ok",
        path=demo_catalog.location,
    )
    res2 = catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset2,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res2,
        action="catalog_add",
        status="ok",
        path=demo_catalog.location,
    )


def test_add_from_file_faulty(demo_catalog, test_data):
    """Add catalog metadata from a file with json lines
    where at least one line is not valid json"""
    res = catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_valid_invalid,
        on_failure="ignore",
        return_type="list",
    )
    assert_result_count(
        res,
        2,
        action="catalog_add",
        status="ok",
        path=demo_catalog.location,
    )
    assert_in_results(
        res,
        action="catalog_add",
        status="error",
        path=demo_catalog.location,
    )


def test_add_from_stdin(monkeypatch, demo_catalog):
    """Add catalog metadata from stdin"""
    mdata1 = '{"dataset_id": "deabeb9b-7a37-4062-a1e0-8fcef7909609", "dataset_version": "0321dbde969d2f5d6b533e35b5c5c51ac0b15758", "type": "dataset", "name": "test_name"}'
    mdata2 = '{"dataset_id": "3344ffv5-7a37-4062-a1e0-8fcef7909609", "dataset_version": "8888dbde969d2f5d6b533e35b5c5c51ac0b15758", "type": "dataset", "name": "test_name"}'
    content = io.StringIO(json.dumps(mdata1) + "\n" + json.dumps(mdata2))
    monkeypatch.setattr("sys.stdin", content)
    res = catalog_add(
        catalog=demo_catalog,
        metadata="-",
        on_failure="ignore",
        return_type="list",
    )
    assert_result_count(
        res,
        2,
        action="catalog_add",
        status="ok",
        path=demo_catalog.location,
    )


def test_add_from_json_str(demo_catalog, test_data):
    """Add catalog metadata from a json serialized string"""
    mdata = '{"dataset_id": "deabeb9b-7a37-4062-a1e0-8fcef7909609", "dataset_version": "0321dbde969d2f5d6b533e35b5c5c51ac0b15758", "type": "dataset", "name": "test_name"}'
    res = catalog_add(
        catalog=demo_catalog,
        metadata=mdata,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_add",
        status="ok",
        path=demo_catalog.location,
    )
