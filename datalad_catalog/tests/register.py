from datalad.tests.utils import assert_result_count


def register(tmp_path):
    import datalad.api as da
    assert hasattr(da, 'catalog_cmd')
    assert_result_count(
        da.catalog_cmd('create', catalog_dir=tmp_path / 'test_catalog'),
        1,
        action='demo')

