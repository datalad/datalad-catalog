import pytest
from datalad.support.exceptions import InsufficientArgumentsError
from datalad.tests.utils_pytest import assert_in_results

from datalad_catalog.catalog import Catalog
from datalad_catalog.webcatalog import WebCatalog

# catalog_paths = [
#     'assets/md5-2.3.0.js',
#     'assets/vue_app.js',
#     'assets/style.css',
#     'artwork',
#     'index.html']

catalog_paths = [
    "assets/md5-2.3.0.js",
    "assets/vue_app.js",
    "assets/style.css",
    "artwork",
    "index.html",
    "config.json",
    "README.md",
]


def test_create(tmp_path):
    """
    Test if catalog is created successfully given a path as single argument,
    where path does not yet exist
    """
    catalog_path = tmp_path / "test_catalog"
    test_catalog = Catalog()
    test_catalog("create", catalog_dir=catalog_path)

    assert catalog_path.exists()
    assert catalog_path.is_dir()

    for p in catalog_paths:
        pth = catalog_path / p
        assert pth.exists()


def test_create_at_existing_noncatalog(tmp_path):
    """
    Test if error is raised when create action is used on an existing
    non-catalog directory
    """
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    test_catalog = Catalog()
    assert_in_results(
        test_catalog(
            "create",
            catalog_dir=dir_path,
            on_failure="ignore",
            return_type="list",
        ),
        action="catalog_create",
        status="error",
        message=(
            "A non-catalog directory already exists at %s. "
            "Please supply a different path.",
            dir_path,
        ),
        path=dir_path,
    )


def test_create_at_existing_catalog_noforce(tmp_path):
    """
    Test if error is raised when create action is used on an existing catalog
    """
    catalog_path = tmp_path / "test_catalog"
    test_catalog = Catalog()
    test_catalog("create", catalog_dir=catalog_path)

    new_catalog_path = catalog_path
    new_test_catalog = Catalog()

    assert_in_results(
        new_test_catalog(
            "create",
            catalog_dir=new_catalog_path,
            on_failure="ignore",
            return_type="list",
        ),
        action="catalog_create",
        status="error",
        message=(
            "Found existing catalog at %s. Overwriting catalog "
            "assets (not catalog metadata) is only possible "
            "when using --force.",
            new_catalog_path,
        ),
        path=new_catalog_path,
    )


def test_create_at_existing_catalog_force(tmp_path):
    """
    Test if catalog is created when create action is used on an existing catalog,
    together with force flag
    """
    catalog_path = tmp_path / "test_catalog2"
    test_catalog = Catalog()
    test_catalog("create", catalog_dir=catalog_path)

    new_catalog_path = catalog_path
    new_test_catalog = Catalog()
    new_test_catalog("create", catalog_dir=new_catalog_path, force=True)

    assert new_catalog_path.exists()
    assert new_catalog_path.is_dir()

    for p in catalog_paths:
        pth = new_catalog_path / p
        assert pth.exists()
