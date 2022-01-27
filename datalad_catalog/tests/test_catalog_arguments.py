
from ..catalog import Catalog
from ..webcatalog import WebCatalog
import pytest
from datalad.support.exceptions import InsufficientArgumentsError

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
    with pytest.raises(ValueError):
        ctlg = Catalog()
        ctlg('wrong_action')

def test_catalog_no_path_argument():
    """
    Test if error is raised when -c/--catalog_dir argument is not supplied
    """
    partial_error_msg = "--catalog_dir"
    with pytest.raises(InsufficientArgumentsError, match=partial_error_msg):
        ctlg = Catalog()
        ctlg('create')

def test_catalog_nonexisting_noncreate(tmp_path):
    """
    Test if error is raised when non-create action is used on a non-existing catalog
    """
    catalog_path = tmp_path / "test_catalog"

    partial_error_msg = "can only operate on an existing catalog"
    with pytest.raises(InsufficientArgumentsError, match=partial_error_msg):
        ctlg = Catalog()
        ctlg('add', catalog_dir=catalog_path)