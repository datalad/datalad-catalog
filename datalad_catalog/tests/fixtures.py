from pathlib import Path
import pytest
from datalad_catalog.constants import (
    package_path,
    tests_path,
)
from datalad_catalog.webcatalog import WebCatalog


class TestPaths(object):
    """Class to store paths to test data"""

    data_path = tests_path / "data"
    default_config_path = package_path / "config" / "config.json"
    demo_config_path_catalog = data_path / "test_config_file_catalog.json"
    demo_config_path_dataset = data_path / "test_config_file_dataset.json"
    catalog_metadata_dataset1 = (
        data_path / "catalog_metadata_dataset_valid.jsonl"
    )
    catalog_metadata_dataset2 = (
        data_path / "catalog_metadata_dataset_valid2.jsonl"
    )
    catalog_metadata_file1 = data_path / "catalog_metadata_file_valid.jsonl"
    catalog_metadata_file_single = (
        data_path / "catalog_metadata_file_valid_single.jsonl"
    )
    catalog_metadata_valid = data_path / "catalog_metadata_dataset_valid.json"
    catalog_metadata_invalid = (
        data_path / "catalog_metadata_dataset_invalid.json"
    )
    catalog_metadata_valid_invalid = (
        data_path / "catalog_metadata_valid_invalid.jsonl"
    )
    demo_metafile_datacite = data_path / "metadata_datacite_gin.jsonl"
    demo_metafile_datacite_2items = data_path / "metadata_datacite_gin2.jsonl"
    demo_metafile_wrongname = data_path / "metadata_translate_wrongname.jsonl"
    demo_metafile_wrongversion = (
        data_path / "metadata_translate_wrongversion.jsonl"
    )
    demo_metafile_nonsense = data_path / "metadata_translate_nonsense.jsonl"
    workflow_metalad_core = data_path / "metadata_core.json"
    workflow_datacite_gin = data_path / "metadata_datacite_gin.json"
    workflow_metalad_studyminimeta = data_path / "metadata_studyminimeta.json"
    workflow_bids_dataset = data_path / "metadata_bids_dataset.json"
    workflow_config_file = data_path / "test_config_file_workflow.json"


@pytest.fixture
def test_data():
    """Paths to test data"""
    return TestPaths()


@pytest.fixture
def demo_catalog(tmp_path, test_data) -> WebCatalog:
    """A simple WebCatalog instance with no added metadata"""
    catalog_path = tmp_path / "test_catalog"
    catalog = WebCatalog(
        location=catalog_path,
    )
    catalog.create(config_file=str(test_data.demo_config_path_catalog))
    return catalog


@pytest.fixture
def demo_catalog_default_config(tmp_path) -> WebCatalog:
    """A simple WebCatalog instance with no added metadata
    and no config specified"""
    catalog_path = tmp_path / "test_catalog_wo_config"
    catalog = WebCatalog(
        location=catalog_path,
    )
    catalog.create()
    return catalog


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
   volunteered for the audio-only Forrest Gump study. The dataset is structured in
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

# Description:
# 1 - create superdataset with studyminimeta
# 2 - create subdataset with datacite_gin, inside multiple directories in super


@pytest.fixture
def workflow_catalog_path(tmp_path):
    return tmp_path / "workflow_catalog"


@pytest.fixture
def workflow_dataset_path(tmp_path):
    superds_path = tmp_path / "workflow_superdataset"
    superds_path.mkdir()
    studyminimeta = superds_path / ".studyminimeta.yaml"
    with studyminimeta.open("w", encoding="utf-8") as f:
        f.write(studyminimeta_content)
    # studyminimeta.write_text(studyminimeta_content)
    file1 = superds_path / "random_file.txt"
    with file1.open("w", encoding="utf-8") as f:
        f.write("some content")
    # file1.write_text('some content')
    dir1 = superds_path / "some_dir"
    dir1.mkdir()
    file2 = dir1 / "file_in_dir.txt"
    with file2.open("w", encoding="utf-8") as f:
        f.write("some content in file in dir")
    # file2.write_text('some content in file in dir')
    dir2 = dir1 / "subdataset"
    dir2.mkdir()
    datacite = dir2 / "datacite.yml"
    with datacite.open("w", encoding="utf-8") as f:
        f.write(datacitegin_content)
    # datacite.write_text(datacitegin_content)
    file3 = dir2 / "random_file.txt"
    with file3.open("w", encoding="utf-8") as f:
        f.write("some content")
    # file3.write_text('some content')
    return superds_path
