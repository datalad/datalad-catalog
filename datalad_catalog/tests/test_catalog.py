from typing import Callable, Dict, List, Optional, Tuple
from unittest.mock import (
    call,
    patch,
)

from jsonschema.exceptions import ValidationError

from datalad.support.exceptions import InsufficientArgumentsError
from datalad.tests.utils import (
    assert_equal,
    assert_in,
    assert_raises,
    with_tempfile,
)


from ..catalog import (
    _get_line_count,
    _validate_metadata,
)


def _unwind(
    function: Callable,
    args: Optional[List] = None,
    kwargs: Optional[Dict] = None,
) -> Tuple:
    return tuple(function(*(args or []), **(kwargs or {})))


@with_tempfile(content="\n".join(map(lambda i: str(i), range(10))))
def test_line_count(temp_file: str = ""):
    assert_equal(10, _get_line_count(temp_file))


def test_empty_metadata_detection():
    assert_raises(
        InsufficientArgumentsError,
        _unwind,
        _validate_metadata,
        [None, None, None, None, False, None],
    )


@with_tempfile(content='{"abc": "xyz"}')
def test_schema_violation_detection(metadata_file: str = ""):
    assert_raises(
        ValidationError,
        _unwind,
        _validate_metadata,
        [None, metadata_file, None, None, False, None],
    )


@with_tempfile(content="[]")
def test_metadata_type_mismatch_detection(metadata_file: str = ""):

    with patch("datalad_catalog.catalog.lgr") as lgr_mock:
        assert_raises(
            ValidationError,
            _unwind,
            _validate_metadata,
            [None, metadata_file, None, None, False, None],
        )
        assert_in(
            call(
                "Metadata item not of type dict: metadata items should be "
                "passed to datalad catalog as JSON objects adhering to the "
                "catalog schema."
            ),
            lgr_mock.warning.mock_calls,
        )


# TODO: _validate does not validate semantics of dataset_id
@with_tempfile(
    content="{"
    '   "type": "dataset",'
    '   "dataset_id": "0000",'
    '   "dataset_version": "000",'
    '   "name": "abc"'
    "}"
)
def test_proper_validation(metadata_file: str = ""):
    result = tuple(
        _validate_metadata(None, metadata_file, None, None, False, None)
    )[0]
    assert_equal(result["status"], "ok")
