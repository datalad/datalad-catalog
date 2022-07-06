import pytest
from datalad.support.exceptions import InsufficientArgumentsError
from datalad.tests.utils import assert_in_results

from datalad_catalog.catalog import Catalog
from datalad_catalog.webcatalog import WebCatalog


def test_catalog_no_argument():
    """
    Test if error is raised when no argument is supplied
    """
    with pytest.raises(TypeError):
        ctlg = Catalog()
        ctlg()


def test_catalog_wrong_action_argument():
    """
    Test if error is raised when wrong action argument is supplied
    """
    ctlg = Catalog()
    # TODO: This test is wrong, the package lacks proper handling of wrong
    # TODO: subcommands. Needs redoing after code is fixed!
    assert_in_results(
        ctlg("wrong_action", on_failure="ignore"),
        action="catalog_wrong_action",
        status="impossible",
        message=(
            "Datalad catalog %s requires a path to operate on. "
            "Forgot -c, --catalog_dir?",
            "wrong_action",
        ),
        path=None,
    )


def test_catalog_no_path_argument():
    """
    Test if error is raised when -c/--catalog_dir argument is not supplied
    """
    ctlg = Catalog()
    assert_in_results(
        ctlg("create", on_failure="ignore"),
        action="catalog_create",
        status="impossible",
        message=(
            "Datalad catalog %s requires a path to operate on. "
            "Forgot -c, --catalog_dir?",
            "create",
        ),
        path=None,
    )


def test_catalog_nonexisting_noncreate(tmp_path):
    """
    Test if error is raised when non-create action is used on a non-existing catalog
    """
    catalog_path = tmp_path / "test_catalog"
    ctlg = Catalog()
    assert_in_results(
        ctlg("add", catalog_dir=catalog_path, on_failure="ignore"),
        action="catalog_add",
        status="impossible",
        message=(
            "Catalog does not exist: datalad catalog '%s' can only "
            "operate on an existing catalog, please supply a path "
            "to an existing directory with the catalog argument: "
            "-c, --catalog_dir.",
            "add",
        ),
        path=catalog_path,
    )
