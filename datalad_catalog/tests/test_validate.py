from datalad.tests.utils_pytest import (
    assert_in_results,
    assert_result_count,
)
from datalad_catalog.validate import Validate
from datalad_next.constraints.exceptions import CommandParametrizationError

from pathlib import Path
import pytest

catalog_validate = Validate()

# TODO: add test to ensure that correct schema is used
# 1) if catalog is supplied as argument or not
# 2) if catalog has schema folder or not.


def test_no_args(demo_catalog, test_data):
    """The metadata argument is required, catalog is optional"""
    with pytest.raises(CommandParametrizationError):
        catalog_validate()

    with pytest.raises(CommandParametrizationError):
        catalog_validate(catalog=demo_catalog)


def test_validation_failure(demo_catalog, test_data):
    """Validate catalog metadata from a json serialized string

    Provided metadata does not include all required fields for a dataset
    """
    mdata = '{"dataset_id": "deabeb9b-7a37-4062-a1e0-8fcef7909609", "dataset_version": "0321dbde969d2f5d6b533e35b5c5c51ac0b15758", "type": "dataset"}'
    res = catalog_validate(
        catalog=demo_catalog,
        metadata=mdata,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_validate",
        status="error",
        path=demo_catalog.location,
    )


def test_validate_from_file_faulty(demo_catalog, test_data):
    """Validate catalog metadata from a file with json lines
    where at least one line is not valid json"""
    res = catalog_validate(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_valid_invalid,
        on_failure="ignore",
        return_type="list",
    )
    assert_result_count(
        res,
        2,
        action="catalog_validate",
        status="ok",
        path=demo_catalog.location,
    )
    assert_in_results(
        res,
        action="catalog_validate",
        status="error",
        path=demo_catalog.location,
    )


def test_validate_without_catalog(demo_catalog, test_data):
    """Validate  metadata from a file with json lines,
    and no catalog argument"""
    res = catalog_validate(
        metadata=test_data.catalog_metadata_valid_invalid,
        on_failure="ignore",
        return_type="list",
    )
    assert_result_count(
        res,
        2,
        action="catalog_validate",
        status="ok",
        path=Path.cwd(),
    )
    assert_in_results(
        res,
        action="catalog_validate",
        status="error",
        path=Path.cwd(),
    )
