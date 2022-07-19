from pathlib import Path
from datalad_catalog.utils import read_json_file
from datalad_catalog.workflows import (
    translate_to_catalog,
    get_translation_map
)

import json

package_path = Path(__file__).resolve().parent.parent
tests_path = Path(__file__).resolve().parent
schema_dir = package_path / "schema"

test_data_paths = {
    "metalad_core": tests_path / "data" / "metadata_core.json",
    "datacite_gin": tests_path / "data" / "metadata_datacite_gin.json",
    "metalad_studyminimeta": tests_path / "data" / "metadata_studyminimeta.json",
    "bids_dataset": tests_path / "data" / "metadata_bids_dataset2.json",
}

def test_basic_translations():
    for key in test_data_paths.keys():
        print(f"\n{key}")
        test_data = read_json_file(test_data_paths[key])
        
        mapping_path = schema_dir / get_translation_map(key, "dataset")
        new_obj = translate_to_catalog(test_data, mapping_path)
        print(json.dumps(new_obj))

def test_null_issue():
    test_data = read_json_file(tests_path / "data" / "extracted_meta.json")
    name = test_data["extractor_name"]
    type = test_data["type"]
    mapping_path = schema_dir / get_translation_map(name, type)
    new_obj = translate_to_catalog(test_data, mapping_path)
    print(json.dumps(new_obj))