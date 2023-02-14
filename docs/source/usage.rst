Usage
*****

DataLad Catalog can be used from the command line or with its Python API.
You can access detailed usage information in the :doc:`command_line_reference`
or the :doc:`python_module_reference` respectively.

The overall catalog generation process actually starts several steps before the
involvement of ``datalad-catalog``. Steps include:

1. curating data into datasets (a group of files in an hierarchical tree)
2. adding metadata to datasets and files (the process for this and the resulting
   metadata formats and content vary widely depending on domain, file types,
   data availability, and more)
3. extracting the metadata using an automated tool to output metadata items into
   a standardized and queryable set
4. translating the metadata into the catalog schema

These steps can follow any arbitrarily specified procedures and can use any
arbitrarily specified tools to get the job done. Once they are completed, the
``datalad-catalog`` tool can be used for catalog generation and customization.


Create a catalog
================

To create a new catalog, start by running ``datalad catalog create``

.. code-block:: bash

   datalad catalog create --catalog_dir /tmp/my-cat

This will create a catalog with the following structure:

- artwork: images that make the catalog pretty
- assets: mainly the JavaScript and CSS code that underlie the user interface of
  the catalog
- metadata: where metadata content for any datasets and files rendered by the
  catalog will be contained
- index.html: the main HTML content rendered in the browser

Add metadata
============

To add metadata to an existing catalog, run ``datalad catalog add``, specifying
the location of the metadata to add. The DataLad Catalog accepts metadata in the
form of json lines, i.e. a text file (typically ``.json``, ``.jsonl``, or
``.txt``) where each line is a single, correctly formatted JSON object. The correct
format for the added metadata is specified by the :doc:`catalog_schema`.

.. code-block:: bash

   datalad catalog add --catalog_dir /tmp/my-cat --metadata path/to/metadata.jsonl


The ``metadata`` directory is now populated.

Metadata validation
-------------------
To check if metadata is valid before adding it to a catalog, ``datalad catalog
validate`` can be run to check if the metadata conforms to the :doc:`catalog_schema`.

.. code-block:: bash

   datalad catalog validate --metadata path/to/metadata.jsonl

Note: the validator runs internally whenever ``datalad catalog add`` is called, so
there is no need to run validation explicitly unless desired.

Set the main dataset (homepage)
===============================

Setting a main dataset is necessary in order to indicate which dataset will be
shown on the catalog homepage. To set the main dataset, run ``datalad
catalog set-super``, specifying the dataset id and version.

.. code-block:: bash

   datalad catalog set-super --catalog_dir /tmp/my-cat --dataset_id abcd --dataset_version 1234

Normally, the main dataset is a superdataset that contains other datasets from
the catalog.

View the catalog
=================

To serve the content of a catalog via a local HTTP server for viewing or
testing, run ``datalad catalog serve``.

.. code-block:: bash

   datalad catalog serve --catalog_dir /tmp/my-cat

Once the content is served, the catalog can be viewed by visiting the local URL.

Update
======

Catalog content can be updated using the ``add`` or ``remove`` commands. To add
content, simply re-run ``datalad catalog add``, providing the path to the new
metadata.

.. code-block:: bash

   datalad catalog add --catalog_dir /tmp/my-cat --metadata path/to/new/metadata.jsonl

If a newly added dataset or version of a dataset was added incorrectly,
``datalad catalog remove`` can be used to get rid of the incorrect addition.

.. code-block:: bash

   datalad catalog remove --dataset_id abcd --dataset_version 1234

Configuration
=============

A useful feature of the catalog process is to be able to configure certain
properties according to your preferences. This is done with help of a config
file (in either ``JSON`` or ``YAML`` format) and the ``-y/--config-file`` flag.
A config file can be passed during catalog creation in order to set the config
on the catalog level:

.. code-block:: bash

   datalad catalog create --catalog_dir /tmp/my-custom-cat --config-file path/to/custom_config.json

A config file can also be passed when adding metadata in order to set the config
on the dataset-level:

.. code-block:: bash

   datalad catalog add --catalog_dir /tmp/my-custom-cat --metadata path/to/metadata.jsonl --config-file path/to/custom_dataset_config.json

In the latter case, the config will be set for all new dataset entries corresponding
to metadata source objects in the metadata provided to the ``add`` operation.

If no config file is specified on the catalog level, a default config file is used.
The catalog-level config also serves as the default config on the dataset level,
which is used if no config file is specified on the dataset-level.

For detailed information on how to structure and use config files, please refer to
the dedicated documentation in :doc:`catalog_config`.


Translate
=========

``datalad-catalog`` can translate a metadata item originating from a particular
source structure and extracted using ``datalad-metalad`` into the catalog schema.
Before translation from a specific source will work, an extractor-specific translator
should be provided and exposed as an entry point (via a DataLad extension) as part of the
``datalad.metadata.translators`` group. Translate metadata as follows:

.. code-block:: bash

   datalad catalog translate --metadata path/to/extracted/metadata.jsonl

This command will output the translated objects as JSON lines to ``stdout``, which can 
be saved to disk and later used, for example, for catalog entry generation.

Workflows
=========

Several subprocesses need to be run in order to create a new catalog with multiple entries,
or in order to update an existing catalog with new entries. These processes can include:

- tracking datasets that are intended to be entries in a catalog as subdatasets of a DataLad super-dataset
- extracting (and temporarily storing) metadata from the super- and subdatasets
- translating extracted metadata (and temporarily storing it)
- creating a catalog
- adding translated metadata to the catalog
- updating the catalog's superdataset (i.e. homepage) if the DataLad superdataset version changed

It is evident that these steps can become quite cumbersome and even resource intensive if run
at scale. Therefore, in order to streamline these processes, to automate them as much as possible,
and to shift the effort away from the user, ``datalad-catalog`` can run workflows for catalog 
generation and updates. It builds on top of the following functionality:

- *DataLad datasets* and nesting for maintaining a super-/subdataset hierarchy.
- ``datalad-metalad``'s metadata extraction functionality
- ``datalad-catalog``'s metadata translation functionality
- ``datalad-catalog`` for maintaining a catalog

``workflow-new``
----------------

To run a workflow from scratch on a dataset and all of its subdatasets:

.. code-block:: bash

   datalad catalog workflow-new --catalog_dir /tmp/my-cat --dataset-path path/to/super/dataset

This workflow will:
1. Clone the super-dataset and all its first-level subdatasets
2. Create the catalog if it does not yet exists
3. Run dataset-level metadata extraction on the super- and subdatasets
4. Translate all extracted metadata to the catalog schema
5. Add the translated metadata as entries to the catalog
6. Set the catalog's super-dataset to the *id* and *version* of the DataLad super-dataset.

``workflow-update``
-------------------
To run a workflow for updating an existing catalog after registering a new subdataset
to the superdataset which the catalog represents:

.. code-block:: bash

   datalad catalog workflow-new --catalog_dir /tmp/my-cat --dataset-path path/to/super/dataset

This workflow assumes:
- The subdataset has already been added as a submodule to the parent dataset
- The parent dataset already contains the subdataset commit

This workflow will:
1. Clone the super-dataset and new subdataset
2. Run dataset-level metadata extraction on the super-dataset and new subdataset
3. Translate all extracted metadata to the catalog schema
4. Add the translated metadata as entries to the catalog
5. Reset the catalog's super-dataset to the latest *id* and *version* of the DataLad super-dataset.
