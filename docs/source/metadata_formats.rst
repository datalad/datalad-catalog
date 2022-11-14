Metadata Types and Formats
**************************

What is metadata?
=================

Metadata describe the files in your dataset, as well as its overall content.
Implicit metadata include basic descriptions of the data itself (such as the names,
types, sizes, and relative locations of all files in your dataset), while explicit
metadata items (such as a description of your dataset, its contributors and project
specifications) can be added to your dataset as you see fit. MetaLad provides functionality
for adding metadata items of arbitrary size, format, and amount, and does not impose
restrictions in this regard.

Many standards exist for specifying and structuring metadata. Some examples include:

- **DataCite**: The `DataCite Metadata Schema`_ is a list of core metadata properties
  chosen for an accurate and consistent identification of a resource for citation
  and retrieval purposes, along with recommended use instructions.
- **XMP**: The `Extensible Metadata Platform`_ is an ISO standard for the creation,
  processing and interchange of standardized and custom metadata for digital documents
  and data sets. It also provides guidelines for embedding XMP information into popular
  image, video and document file formats, such as JPEG and PDF.
- **Frictionless Data**: The `Frictionless Data Package`_ is a container format for
  describing a coherent collection of data in a single 'package', providing the basis
  for convenient delivery, installation and management of datasets.

Standardized file formats may also contain format-specific information (such as bit rate
and duration for audio files, or resolution and color mode for image files), while domain-
standard files (such as `Digital Imaging and Communications in Medicine`_, i.e. DICOM)
also supply embedded or sidecar metadata.

.. note:: In order to create a user-friendly catalog, DataLad Catalog should receive 
    structured metadata adhering to a specified :doc:`catalog_schema` as input. This means
    that structured metadata first has to be extracted from your DataLad dataset.


Metadata Extractors
===================

To simplify the process of generating structured metadata, DataLad MetaLad provides
several extractors, as well as functionality for running these extractors on the level
of a dataset or files. If an extractor for a specific data or metadata type is not
available, these can be added via a DataLad extension.


``metalad_core``
----------------

For extracting implicit metadata from a DataLad dataset and its files (i.e. without
first having to add specific metadata content to the dataset) MetaLad has the built-in
``metalad_core`` extractor.

.. admonition:: TODO

    - add short descriptions of fields extracted with ``metalad_core``

``metalad_studyminimeta``
-------------------------

.. admonition:: TODO

    - add short description the extractor, and extracted fields


``more...``
----------------

.. _DataCite Metadata Schema: https://en.wikipedia.org/wiki/Extensible_Metadata_Platform
.. _Extensible Metadata Platform: https://en.wikipedia.org/wiki/Extensible_Metadata_Platform
.. _Frictionless Data Package: https://specs.frictionlessdata.io/data-package/
.. _Digital Imaging and Communications in Medicine: https://www.dicomstandard.org/
