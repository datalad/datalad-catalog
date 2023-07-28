from datalad_catalog.translate import (
    MetaTranslate,
)
from datalad.tests.utils_pytest import (
    assert_in_results,
    assert_result_count,
)
from datalad_next.constraints.exceptions import CommandParametrizationError
import pytest
import os

catalog_translate = MetaTranslate()


def test_arg_combinations(demo_catalog):
    """Test various incorrect combinations of arguments"""
    # no arguments
    with pytest.raises(CommandParametrizationError):
        catalog_translate()
    # only catalog (no further positional/optional args)
    with pytest.raises(CommandParametrizationError):
        catalog_translate(catalog=demo_catalog)
    # fake metadata argument
    with pytest.raises(CommandParametrizationError):
        catalog_translate("huh?", catalog=demo_catalog)


def test_correct_translation(demo_catalog, test_data):
    """With and without the catalog argument"""
    res = catalog_translate(
        catalog=demo_catalog,
        metadata=test_data.demo_metafile_datacite,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_translate",
        status="ok",
        path=demo_catalog.location,
    )
    res = catalog_translate(
        metadata=test_data.demo_metafile_datacite,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_translate",
        status="ok",
        path=os.getcwd(),
    )


def test_translator_not_found(demo_catalog, test_data):
    # Wrong name
    res = catalog_translate(
        catalog=demo_catalog,
        metadata=test_data.demo_metafile_wrongname,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_translate",
        status="error",
        path=demo_catalog.location,
    )
    # Wrong version
    res = catalog_translate(
        catalog=demo_catalog,
        metadata=test_data.demo_metafile_wrongversion,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_translate",
        status="error",
        path=demo_catalog.location,
    )
    # Nonsense metadata
    res = catalog_translate(
        catalog=demo_catalog,
        metadata=test_data.demo_metafile_nonsense,
        on_failure="ignore",
        return_type="list",
    )
    assert_in_results(
        res,
        action="catalog_translate",
        status="error",
        path=demo_catalog.location,
    )


def test_multiline_translation(demo_catalog, test_data):
    """This runs on two lines of metadata requiring the same translator,
    which should be instantiated only once"""
    res = catalog_translate(
        catalog=demo_catalog,
        metadata=test_data.demo_metafile_datacite_2items,
        on_failure="ignore",
        return_type="list",
    )
    assert_result_count(
        res,
        2,
        action="catalog_translate",
        status="ok",
    )
