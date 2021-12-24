from datalad.tests.utils import assert_result_count
from datalad_catalog.webcatalog import Node, getNode
from nose.tools import (
    assert_equal,
    assert_false,
    assert_greater,
    assert_greater_equal,
    assert_in as in_,
    assert_in,
    assert_is,
    assert_is_none,
    assert_is_not,
    assert_is_not_none,
    assert_not_equal,
    assert_not_in,
    assert_not_is_instance,
    assert_raises,
    assert_true,
    eq_,
    make_decorator,
    ok_,
    raises,
)


def assert_instances_equal():
    """
    Assert that two instances with identical variables, one created via class
    instantiation and one created via getNode method, are the same object
    """
    node_instance_1 = Node(dataset_id='123', dataset_version='v1')
    node_instance_2 = getNode(dataset_id='123', dataset_version='v1')
    assert_equal(node_instance_1, node_instance_2)

