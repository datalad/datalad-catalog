from pathlib import Path
from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
)
from unittest.mock import (
    call,
    patch,
)

from datalad.support.exceptions import InsufficientArgumentsError
from datalad.tests.utils import (
    assert_equal,
    assert_in,
    assert_raises,
    with_tempfile,
)
from jsonschema.exceptions import ValidationError

from datalad_catalog.catalog import (
    Catalog,
    _get_line_count,
    _validate_metadata,
)

minimal_metadata = (
    "{"
    '   "type": "dataset",'
    '   "dataset_id": "0000",'
    '   "dataset_version": "000",'
    '   "name": "abc"'
    "}"
)

default_kwargs = {
    "catalog_dir": ".",
    "metadata": minimal_metadata,
    "dataset_id": "0000-0000-0000",
    "dataset_version": "abcdef",
    "force": False,
    "config_file": "catalog.conf",
}

result_template = {"status": "ok", "path": "/catalog"}


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
        [
            None,
        ],
    )


@with_tempfile(content='{"abc": "xyz"}')
def test_schema_violation_detection(metadata_file: str = ""):
    assert_raises(
        ValidationError,
        _unwind,
        _validate_metadata,
        [
            metadata_file,
        ],
    )


@with_tempfile(content="[]")
def test_metadata_type_mismatch_detection(metadata_file: str = ""):

    with patch("datalad_catalog.catalog.lgr") as lgr_mock:
        assert_raises(
            ValidationError,
            _unwind,
            _validate_metadata,
            [
                metadata_file,
            ],
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
@with_tempfile(content=minimal_metadata)
def test_proper_validation(metadata_file: str = ""):
    result = tuple(_validate_metadata(metadata_file))[0]
    assert_equal(result["status"], "ok")


@with_tempfile(mkdir=True)
@with_tempfile(content="key: value")
def test_catalog_action_routing(temp_dir: str = "", config_file: str = ""):
    # expect that every mocked action handler is called
    with patch("datalad_catalog.catalog._validate_metadata") as f1, patch(
        "datalad_catalog.catalog._create_catalog"
    ) as f2, patch("datalad_catalog.catalog._serve_catalog") as f3, patch(
        "datalad_catalog.catalog._add_to_catalog"
    ) as f4, patch(
        "datalad_catalog.catalog._remove_from_catalog"
    ) as f5, patch(
        "datalad_catalog.catalog._set_super_of_catalog"
    ) as f6:

        for mock, name in zip(
            (f1, f2, f3, f4, f5, f6), (f"f{i}" for i in range(1, 7))
        ):
            mock.return_value = iter([{**result_template, "action": name}])

        results = []
        for action, create_dir in (
            ("create", False),
            ("validate", False),
            ("add", True),
            ("remove", True),
            ("set-super", True),
            ("serve", True),
        ):

            test_catalog_path = Path(temp_dir) / "test_catalog"

            if create_dir:
                try:
                    test_catalog_path.mkdir()
                    (test_catalog_path / "assets").mkdir()
                    (test_catalog_path / "artwork").mkdir()
                    (test_catalog_path / "index.html").write_text("")
                except FileExistsError:
                    pass
            else:
                try:
                    test_catalog_path.unlink()
                except FileNotFoundError:
                    pass

            results.append(
                tuple(
                    Catalog()(
                        **{
                            **default_kwargs,
                            "catalog_action": action,
                            "config_file": config_file,
                            "catalog_dir": str(test_catalog_path),
                            "result_renderer": "disabled",
                        }
                    )
                )[0]["action"]
            )

        for i in range(1, 7):
            assert_in(f"f{i}", results)
