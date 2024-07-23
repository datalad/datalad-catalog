Metadata source specification
*****************************

This metadata source specification defines how to structure a collection of metadata records
that together form the source material for a ``datalad-catalog`` catalog instance.

The specification benefits both users and developers in that it separates metadata formats
from the tooling that processes it:

- users can create and maintain such specification-compliant metadata collections without
  having to employ ``datalad-catalog`` tooling
- both generic and format-specific tooling can be developed and deployed, either as part of
  ``datalad-catalog`` or as custom extensions, to transform specification-compliant metadata
  collections into a state renderable by a catalog


High-level design
=================

The metadata source specification supports:

1. **Per-catalog versioned customizations**: the top-level functional unit of the source
   specification is a catalog instance, which can be customized via a versioned configuration
   file as defined in the section :doc:`catalog_config`. This means a specification-compliant
   collection of records can specify the (version-specific) "look and feel" of a catalog,
   in addition to its displayed content.
2. **Multi-dataset, multi-version records**: the source specification has a filesystem layout
   with a directory for each unique dataset identifier, which in turn has a subdirectory for
   each unique version identifier of a given dataset. This ensures a modular setup within which
   records for multiple versions of the same dataset can coexist.
3. **Multi-format metadata records**: the specification places no restrictions on the number
   and type of metadata records in a collection for a given dataset version, since in reality
   metadata often originate from a variety of sources and exist in a variety of formats.
   The transformation of different record formats into ``datalad-catalog``-compatible records
   is conveniently shifted into the tooling domain, and is not part of the specification itself.


The specification
=================

The following filesystem layout and record naming scheme should be adhered to for
a given collection of records:

.. code-block::

   .
   ├── config/
   │   └── <config-version-id>/
   │       └── config.json
   └── records/
       └── <dataset-id>/
           ├── config.json
           └── <dataset-version-id>/
               └── <format-id>


``config/``
-----------

This directory should contain the catalog-level configuration file(s), one per version,
with the name ``config.json``.

``<config-version-id>``
-----------------------

This directory name specifies the version of the configuration file,
and should have a unique string value.

``records/``
------------

All metadata records for all versions of all datasets should be placed in the appropriate
relative location within this directory.


``<dataset-id>/``
-----------------

All metadata records for all versions of *a specific dataset* should be placed in this
directory. ``<dataset-id>`` should be a unique string identifying the dataset, avoiding
white space and special characters.


``<dataset-version-id>/``
-------------------------

All metadata records for *a specific version* of *a specific dataset* should be placed
in this directory. ``<dataset-version-id>`` should be a unique string identifying the version,
avoiding white space and special characters.

``<format-id>``
---------------

This should be a unique filename of a single record, with identifying characters that
can be parsed in order to match the specific file format with a specific reader or processing
tool. There is no restriction on the number of files contained in a given ``<dataset-version-id>``
directory, they should just all be unique.


An example
==========

This is an example record collection:

.. code-block::

   .
   ├── config/
   │   ├── v1/
   │   │   └── config.json
   │   └── v2/
   │       └── config.json
   └── records/
       └── myDatasetA/
       │   ├── v0.1.1/
       │   │   └── datacite.json
       │   └── v0.1.2/
       │       ├── studyminimeta.yaml
       │       └── datacite.json
       └── myDatasetB/
           ├── config.json
           └── latest/
               ├── dataset_description.json
               ├── tabby.tsv
               ├── data-package.json
               ├── LICENSE
               └── citations.cff


.. note::
   
   **TO DO**: Construct and point to an actual specification-compliant collection of records


.. note::
   
   **TO DO**: Point to the toolset description of how such a collection can be transformed
   into a set of ``datalad-catalog``-compatible records