from datalad_catalog.utils import find_duplicate_object_in_list

test_list = [
    {"source": "metalad_studyminimeta", "content": ["mini1", "mini2", "mini3"]},
    {"source": "datacite_gin", "content": ["gin1", "gin2"]},
]
test_object_true = {"source": "datacite_gin", "content": ["gin1", "gin2"]}
test_object_half_false = {"source": "metalad_studyminimeta", "content": []}
test_object_false = {"source": "wrong_thing", "content": []}


def test_find_object_in_list():
    keys_to_match = test_object_true.keys()
    obj_found = find_duplicate_object_in_list(
        test_list, test_object_true, keys_to_match
    )
    assert obj_found == test_list[1]


def test_find_no_object_in_list():
    keys_to_match = test_object_false.keys()
    obj_found = find_duplicate_object_in_list(
        test_list, test_object_false, keys_to_match
    )
    assert obj_found is None


def test_find_object_in_list_singlekey():
    keys_to_match = ["source"]
    obj_found = find_duplicate_object_in_list(
        test_list, test_object_half_false, keys_to_match
    )
    assert obj_found == test_list[0]

    keys_to_match = test_object_half_false.keys()
    obj_found = find_duplicate_object_in_list(
        test_list, test_object_half_false, keys_to_match
    )
    assert obj_found is None
