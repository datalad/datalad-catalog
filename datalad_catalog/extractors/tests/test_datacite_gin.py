from pathlib import Path

import yaml
from datalad.api import meta_extract
from datalad.distribution.dataset import Dataset
from datalad.tests.utils import (
    assert_equal,
    with_tempfile,
)


datacite_content = """
# Metadata for DOI registration according to DataCite Metadata Schema 4.1.
# For detailed schema description see https://doi.org/10.5438/0014

## Required fields

# The main researchers involved. Include digital identifier (e.g., ORCID)
# if possible, including the prefix to indicate its type.
authors:
  -
    firstname: "GivenName1"
    lastname: "FamilyName1"
    affiliation: "Affiliation1"
    id: "ORCID:0000-0001-2345-6789"
  -
    firstname: "GivenName2"
    lastname: "FamilyName2"
    affiliation: "Affiliation2"
    id: "ResearcherID:X-1234-5678"
  -
    firstname: "GivenName3"
    lastname: "FamilyName3"

# A title to describe the published resource.
title: "Example Title"

# Additional information about the resource, e.g., a brief abstract.
description: |
  Example description
  that can contain linebreaks
  but has to maintain indentation.

# Lit of keywords the resource should be associated with.
# Give as many keywords as possible, to make the resource findable.
keywords:
  - Neuroscience
  - Keyword2
  - Keyword3

# License information for this resource. Please provide the license name and/or a link to the license.
# Please add also a corresponding LICENSE file to the repository.
license:
  name: "Creative Commons CC0 1.0 Public Domain Dedication"
  url: "https://creativecommons.org/publicdomain/zero/1.0/"



## Optional Fields

# Funding information for this resource.
# Separate funder name and grant number by comma.
funding:
  - "DFG, AB1234/5-6"
  - "EU, EU.12345"


# Related publications. reftype might be: IsSupplementTo, IsDescribedBy, IsReferencedBy.
# Please provide digital identifier (e.g., DOI) if possible.
# Add a prefix to the ID, separated by a colon, to indicate the source.
# Supported sources are: DOI, arXiv, PMID
# In the citation field, please provide the full reference, including title, authors, journal etc.
references:
  -
    id: "doi:10.xxx/zzzz"
    reftype: "IsSupplementTo"
    citation: "Citation1"
  -
    id: "arxiv:mmmm.nnnn"
    reftype: "IsSupplementTo"
    citation: "Citation2"
  -
    id: "pmid:nnnnnnnn"
    reftype: "IsReferencedBy"
    citation: "Citation3"


# Resource type. Default is Dataset, other possible values are Software, DataPaper, Image, Text.
resourcetype: Dataset

# Do not edit or remove the following line
templateversion: 1.2
"""


@with_tempfile(mkdir=True)
def test_datacite_extractor(temp_dir_name: str = ""):
    dataset_dir = Path(temp_dir_name) / "dataset"
    dataset = Dataset(dataset_dir).create(result_renderer="disabled")
    (dataset_dir / "datacite.yml").write_text(datacite_content)
    dataset.save(result_renderer="disabled")

    result = meta_extract(
        dataset=str(dataset_dir), extractorname="datacite_gin"
    )
    assert_equal(len(result), 1)
    extracted_metadata = result[0]["metadata_record"]["extracted_metadata"]

    expected_metadata = yaml.load(datacite_content, Loader=yaml.SafeLoader)
    # Adapt expected metadata to modification made by the extractor
    expected_metadata["description"] = expected_metadata["description"].strip()
    expected_metadata["@context"] = extracted_metadata["@context"]

    assert_equal(extracted_metadata, expected_metadata)
