from pathlib import Path
from datalad_catalog.utils import read_json_file
from datalad_catalog.webcatalog import (
    WebCatalog,
)
from datalad_catalog.workflows import (
    translate_to_catalog,
    get_translation_map,
    super_workflow,
)
from datalad.tests.utils_pytest import (
    with_tree,
    with_tempfile,
    assert_equal,
    assert_repo_status,
)
from datalad.api import (
    create,
    Dataset
)

import json
import pytest

package_path = Path(__file__).resolve().parent.parent
tests_path = Path(__file__).resolve().parent
schema_dir = package_path / "schema"

test_data_paths = {
    "metalad_core": tests_path / "data" / "metadata_core.json",
    "datacite_gin": tests_path / "data" / "metadata_datacite_gin.json",
    "metalad_studyminimeta": tests_path / "data" / "metadata_studyminimeta.json",
    "bids_dataset": tests_path / "data" / "metadata_bids_dataset2.json",
}

studyminimeta_content = """\
#<!-- METADATA START --> # DO NOT DELETE THIS LINE
# All example text is surrounded with <ex> and </ex>. Please replace the example
# text including the <ex> and </ex> with your data. Delete all non-applicable
# lines and sections.

# Attention: indentation is important and must be preserved!

# information on the study the to-be-archived dataset was created for

# mandatory information on to-be-archived dataset
dataset:
  # short name or label
  name: StudyForrest

  # current location of the dataset
  location: https://github.com/psychoinformatics-de/studyforrest-data

  # summary of purpose and content of the dataset
  description:
    "The StudyForrest project centers around the use of the movie Forrest Gump, which provides complex sensory input
    that is both reproducible and is also richly laden with real-life-like content and contexts. Since its initial release,
    the StudyForrest dataset has grown and been extended substantially, and now encompasses many hours of fMRI scans,
    structural brain scans, eye-tracking data, and extensive annotations of the movie."

  # optional list of employed standard and format
  # for automatic generation of rich metadata records
  # (see handbook for full list)

  # optional list of keyword/phrase
  keyword:
    - human
    - fMRI
    - task

  # minimum of one dataset author required
  author:
    - g@fz-juelich.de

  # optional list of entities that funded the creation of
  # the dataset. This might also be a single value.
    - BMBF, 01GQ1411
    - NSF, 1429999

# one or more publications on or using the dataset, optional
publication:
  - title: "The effect of acquisition resolution on orientation decoding from V1: comparison of 3T and 7T"
    author:
      - a@fz-juelich.de
      - b@fz-juelich.de
      - c@fz-juelich.de
      - d@fz-juelich.de
      - e@fz-juelich.de
      - f@fz-juelich.de
      - g@fz-juelich.de
    # when published
    year: 2018
    # all other properties are optional
    # highly recommended to provide a DOI
    doi: https://doi.org/10.1101/305417
    # journal name or publication venue label
    publication: bioRxiv

  - title: "Spatial band-pass filtering aids decoding musical genres from auditory cortex 7T fMRI"
    author:
      - a@fz-juelich.de
      - f@fz-juelich.de
      - g@fz-juelich.de
    # when published
    year: 2018
    # all other properties are optional
    # highly recommended to provide a DOI
    doi: https://doi.org/10.12688/f1000research.13689.2
    # journal name or publication venue label
    publication: F1000Research

# person information, one record for every email-key used above
person:
  a@fz-juelich.de:
     given_name: Ayan
     last_name: Sengupta
  
  b@fz-juelich.de:
     given_name: Oliver
     last_name: Speck
  
  c@fz-juelich.de:
     given_name: Renat
     last_name: Yakupov
  
  d@fz-juelich.de:
     given_name: Martin
     last_name: Kanowski
  
  e@fz-juelich.de:
     given_name: Claus
     last_name: Tempelmann
  
  f@fz-juelich.de:
     given_name: Stefan
     last_name: Pollmann
  
  g@fz-juelich.de:
     given_name: Michael
     last_name: Hanke
     orcid-id: 0000-0001-6398-6370

#<!-- METADATA END -->  # DO NOT DELETE THIS LINE

"""

datacitegin_content = """\
# Metadata for DOI registration according to DataCite Metadata Schema 4.1.
# For detailed schema description see https://doi.org/10.5438/0014

authors:
  - firstname: Michael
    lastname: Hanke
    id: "ORCID:0000-0001-6398-6370"

  - firstname: Nico
    lastname: Adelhöfer
    
  - firstname: Falko R.
    lastname: Kaule

  - firstname: Laura
    lastname: Waite
    id: "ORCID:0000-0003-2213-7465"

  - firstname: Christian
    lastname: Mönch
    id: "ORCID:0000-0002-3092-0612"


title: "Simultaneous fMRI/eyetracking while movie watching, plus visual localizers"


description: |
  "Extension of the dataset published in Hanke et al.
   (2014; doi:10.1038/sdata.2014.3) with additional acquisitions for 15 of
   the original 20 participants. These additions include: retinotopic mapping,
   a localizer paradigm for higher visual areas (FFA, EBA, PPA), and another
   2h movie recording with 3T full-brain BOLD fMRI with simultaneous 1000 Hz
   eyetracking.

   This is an extension of the studyforrest project, all participants previously
   volunteered for the audio-only Forrest Gump study. The datset is structured in
   BIDS format, details of the files and metadata can be found at:

     Ayan Sengupta, Falko R. Kaule, J. Swaroop Guntupalli, Michael B. Hoffmann,
     Christian Häusler, Jörg Stadler, Michael Hanke. `An extension of the
     studyforrest dataset for vision research
     <http://biorxiv.org/content/early/2016/03/31/046573>`_. (submitted for
     publication)

     Michael Hanke, Nico Adelhöfer, Daniel Kottke, Vittorio Iacovella,
     Ayan Sengupta, Falko R. Kaule, Roland Nigbur, Alexander Q. Waite,
     Florian J. Baumgartner & Jörg Stadler. `Simultaneous fMRI and eye gaze
     recordings during prolonged natural stimulation – a studyforrest extension
     <http://biorxiv.org/content/early/2016/03/31/046581>`_. (submitted for
     publication)

   For more information about the project visit: http://studyforrest.org

   We acknowledge the support of the Combinatorial NeuroImaging Core
   Facility at the Leibniz Institute for Neurobiology in Magdeburg, and
   the German federal state of Saxony-Anhalt, Project: Center for
   Behavioral Brain Sciences. This research was, in part, also supported
   by the German Federal Ministry of Education and Research (BMBF) as
   part of a US-German collaboration in computational neuroscience (CRCNS),
   co-funded by the BMBF and the US National Science Foundation
   (BMBF 01GQ1112; NSF 1129855). Work on the data-sharing technology
   employed for this research was supported by US-German CRCNS project,
   co-funded by the BMBF and the US National Science Foundation
   (BMBF 01GQ1411; NSF 1429999)."


funding:
  - "BMBF, 01GQ1112"
  - "NSF, 1129855"
  - "BMBF, 01GQ1411"
  - "NSF, 1429999"


keywords:
  - Neuroscience
  - Studyforrest
  - BIDS


license:
  name: "Open Data Commons Public Domain Dedication and License (PDDL)"
  url: "https://opendatacommons.org/licenses/pddl/"


# Related publications. reftype might be: IsSupplementTo, IsDescribedBy, IsReferencedBy.
# Please provide digital identifier (e.g., DOI) if possible.
# Add a prefix to the ID, separated by a colon, to indicate the source.
# Supported sources are: DOI, arXiv, PMID
# In the citation field, please provide the full reference, including title, authors, journal etc.
references:
  - id: "doi:10.1038/sdata.2016.93"
    reftype: "IsSupplementTo"
    citation: "Sengupta, A., Kaule, F. R., Guntupalli, J. S., Hoffmann, M. B., Häusler, C., Stadler, J., Hanke, M. (2016). A studyforrest extension, retinotopic mapping and localization of higher visual areas. Scientific Data, 3, 160093."

  - id: "doi:10.1038/sdata.2016.92"
    reftype: "IsSupplementTo"
    citation: "Hanke, M, Adelhöfer, N, Kottke, D, Iacovella, V, Sengupta, A, Kaule, FR, Nigbur, R, Waite, AQ, Baumgartner, F, Stadler, J (2016). A studyforrest extension, simultaneous fMRI and eye gaze recordings during prolonged natural stimulation. Scientific Data, 3, 160092."


# Resource type. Default is Dataset, other possible values are Software, Image, Text.
resourcetype: Dataset


# Do not edit or remove the following line
templateversion: 1.2

"""

super_ds_tree = {
    'superdataset': {
        '.studyminimeta.yaml': studyminimeta_content,
        'random_file.txt': 'some content',
        'some_dir': {
            'file_in_dir.txt': 'some content in file in dir',
        }
    }
}


catalog_paths = [
    "assets/md5-2.3.0.js",
    "assets/vue_app.js",
    "assets/style.css",
    "artwork",
    "index.html",
    "config.json",
    "README.md",
]


# def test_basic_translations():
#     """Test the output of translations using jq-bindings

#     The outputs are for manual inspection: use pytest -s.
#     """
#     for key in test_data_paths.keys():
#         print(f"\n{key}")
#         test_data = read_json_file(test_data_paths[key])
        
#         mapping_path = schema_dir / get_translation_map(key, "dataset")
#         new_obj = translate_to_catalog(test_data, mapping_path)
        # print(json.dumps(new_obj))


# Description:
# 1 - create superdataset with studyminimeta
# 2 - create subdataset with datacite_gin, inside multiple directories in super
# 3 - run workflow

super_ds_tree = {
    'superdataset': {
        '.studyminimeta.yaml': studyminimeta_content,
        'random_file.txt': 'some content',
        'some_dir': {
            'file_in_dir.txt': 'some content in file in dir',
            'subdataset': {
                'datacite.yml': datacitegin_content,
                'random_file.txt': 'some content',
            }
        }
    }
}
@with_tree(tree=super_ds_tree)
@with_tempfile(mkdir=True)
def test_workflow_new(super_path=None, cat_path=None):
    ckwa=dict(result_renderer='disabled')
    # Create super and subdataset, save all
    sub_ds = create(super_path + "/some_dir/subdataset",  force=True, **ckwa)
    sub_ds.save(to_git=True, **ckwa)
    super_ds = create(super_path, force=True, **ckwa)
    super_ds.save(to_git=True, **ckwa)
    assert_repo_status(super_ds.path)
    # Create catalog
    cat = WebCatalog(location=cat_path)
    cat.create(force=True)
    # Create catalog
    cat_path = Path(cat_path)
    cat = WebCatalog(location=cat_path)
    cat.create(force=True)
    assert cat_path.exists()
    assert cat_path.is_dir()
    for p in catalog_paths:
        pth = cat_path / p
        assert pth.exists()
    # Run workflow
    tuple(super_workflow(super_ds.path, cat))
    # Test workflow outputs
    meta_path = cat_path / "metadata"
    assert meta_path.exists()
    dataset_details = {
        "super_ds": get_id_and_version(super_ds),
        "sub_ds": get_id_and_version(sub_ds),
    }
    for ds in dataset_details.values():
        pth = meta_path / str(ds[0]) / str(ds[1])
        assert pth.exists()
    super_file = cat_path / "metadata" / "super.json"
    assert super_file.exists()
    assert super_file.is_file()
    assert_equal(
    json.dumps(read_json_file(super_file), sort_keys=True, indent=2),
    f"""\
{{
  "dataset_id": {dataset_details["super_ds"][0]},
  "dataset_version": {dataset_details["super_ds"][1]},
}}""")


def get_id_and_version(dataset: Dataset, var_to_string=False):
    """Helper to get a DataLad dataset's id and version
    """
    id = dataset.id
    # sync possible adjusted branch and account for
    # possibility of being on adjusted branch
    dataset.repo.localsync()
    version = dataset.repo.get_hexsha(
        dataset.repo.get_corresponding_branch()
    )
    if var_to_string:
        return str(id), str(version)
    return id, version
