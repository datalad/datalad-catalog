from pathlib import Path
from datalad_catalog.catalog import Catalog
from datalad_catalog.translate import (
    Translate,
    TranslatorNotFoundError,
)
from datalad_catalog.utils import read_json_file
from datalad.tests.utils import (
    assert_in_results,
    assert_raises,
    assert_result_count,
)


tests_path = Path(__file__).resolve().parent
data_path = tests_path / "data"
demo_metafile_datacite = data_path / "metadata_datacite_gin.jsonl"
demo_metafile_datacite_2items = data_path / "metadata_datacite_gin2.jsonl"
demo_metafile_wrongname = data_path / "metadata_translate_wrongname.jsonl"
demo_metafile_wrongversion = data_path / "metadata_translate_wrongversion.jsonl"
demo_metafile_nonsense = data_path / "metadata_translate_nonsense.jsonl"


def test_correct_translation():
    """"""
    ctlg = Catalog()
    assert_in_results(
        ctlg("translate", metadata=demo_metafile_datacite),
        action="catalog_translate",
        status="ok",
    )


def test_correct_translation_with_class():
    meta_dict = read_json_file(demo_metafile_datacite)
    Translate(meta_dict).run_translator()


def test_translator_not_found():
    ctlg = Catalog()
    # Wrong name
    assert_raises(
        TranslatorNotFoundError,
        ctlg,
        "translate",
        metadata=demo_metafile_wrongname,
    )
    # Wrong version
    assert_raises(
        TranslatorNotFoundError,
        ctlg,
        "translate",
        metadata=demo_metafile_wrongversion,
    )
    # Nonsense metadata
    assert_raises(
        TranslatorNotFoundError,
        ctlg,
        "translate",
        metadata=demo_metafile_nonsense,
    )


def test_multiline_translation():
    ctlg = Catalog()
    assert_result_count(
        ctlg("translate", metadata=demo_metafile_datacite_2items),
        2,
        action="catalog_translate",
        status="ok",
    )
