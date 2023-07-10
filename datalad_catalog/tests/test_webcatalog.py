from datalad_catalog.add import Add

from pathlib import Path
import pytest


def test_get_record(demo_catalog, test_data):
    """"""
    # correct id and version and files
    ds_id = "deabeb9b-7a37-4062-a1e0-8fcef7909609"
    ds_v = "0321dbde969d2f5d6b533e35b5c5c51ac0b15758"
    file1 = "MRI_raw_data/Control/Baseline/GV_T3_14_1_1_2_20190809_134721/8/pdata/1/2dseq"
    file2 = "derivatives/fmriprep/sub-CSI1/anat/sub-CSI1_T1w_preproc.nii.gz"
    # Test unknown record type
    with pytest.raises(ValueError):
        demo_catalog.get_record(
            dataset_id=ds_id,
            dataset_version=ds_v,
            record_type="bla",
        )
    # Test wrong None path with record type 'file'
    with pytest.raises(ValueError):
        demo_catalog.get_record(
            dataset_id=ds_id,
            dataset_version=ds_v,
            record_type="file",
        )
    # Now add useful dataset-level and file
    catalog_add = Add()
    res_dataset = catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_dataset1,
        on_failure="ignore",
        return_type="list",
    )
    res_file = catalog_add(
        catalog=demo_catalog,
        metadata=test_data.catalog_metadata_file1,
        on_failure="ignore",
        return_type="list",
    )
    # Test existing dataset record
    ds_rec = demo_catalog.get_record(
        dataset_id=ds_id,
        dataset_version=ds_v,
        record_type="dataset",
    )
    assert "dataset_id" in ds_rec
    assert ds_rec["dataset_id"] == ds_id
    assert "dataset_version" in ds_rec
    assert ds_rec["dataset_version"] == ds_v
    # pp.pprint(ds_rec)
    # Test nonexisting dataset record
    ds_rec = demo_catalog.get_record(
        dataset_id="ljkhbjg",
        dataset_version="sdffdfsafd",
        record_type="dataset",
    )
    assert ds_rec is None
    # Test existing directory record
    dir_path = str(Path(file1).parent)
    ds_rec = demo_catalog.get_record(
        dataset_id=ds_id,
        dataset_version=ds_v,
        record_type="directory",
        relpath=dir_path,
    )
    assert "dataset_id" in ds_rec
    assert ds_rec["dataset_id"] == ds_id
    assert "dataset_version" in ds_rec
    assert ds_rec["dataset_version"] == ds_v
    assert "path" in ds_rec
    assert ds_rec["path"] == dir_path
    # Test nonexisting directory record
    ds_rec = demo_catalog.get_record(
        dataset_id=ds_id,
        dataset_version=ds_v,
        record_type="directory",
        relpath="MRI_raw_data/Control/yackity-yack",
    )
    assert ds_rec is None
    # Test existing file record
    ds_rec = demo_catalog.get_record(
        dataset_id=ds_id,
        dataset_version=ds_v,
        record_type="file",
        relpath=file2,
    )
    assert "dataset_id" in ds_rec
    assert ds_rec["dataset_id"] == ds_id
    assert "dataset_version" in ds_rec
    assert ds_rec["dataset_version"] == ds_v
    assert "path" in ds_rec
    assert ds_rec["path"] == file2
    # Test nonexisting file record
    ds_rec = demo_catalog.get_record(
        dataset_id=ds_id,
        dataset_version=ds_v,
        record_type="file",
        relpath="derivatives/fmriprep/sub-CSI1/anat/blah.txt",
    )
    assert ds_rec is None
