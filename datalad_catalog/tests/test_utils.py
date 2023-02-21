from datalad_catalog.utils import find_duplicate_object_in_list, merge_lists

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


def test_merge_lists():
    """"""
    a = []
    b = None
    c = [{"key1": "valc1"}, {"key1": "valc2"}]
    d = [1, 2, 3]
    e = [4, 3, 5, 9]
    f = ["test"]
    g = [{"key1": "valg1"}, {"key1": "valc2"}]

    a_c = merge_lists(a.copy(), c.copy())
    assert isinstance(a_c, list)
    assert len(a_c) == 2
    assert {"key1": "valc1"} in a_c
    assert {"key1": "valc2"} in a_c
    b_a = merge_lists(None, a.copy())
    assert isinstance(b_a, list)
    assert len(b_a) == 0
    d_e = merge_lists(d.copy(), e.copy())
    assert isinstance(d_e, list)
    assert d_e == [1, 2, 3, 4, 5, 9]
    b_f = merge_lists(None, f.copy())
    assert isinstance(b_f, list)
    assert len(b_f) == 1
    assert "test" in b_f
    c_g = merge_lists(c.copy(), g.copy())
    assert isinstance(c_g, list)
    assert len(c_g) == 3
    assert {"key1": "valc1"} in c_g
    assert {"key1": "valc2"} in c_g
    assert {"key1": "valg1"} in c_g
