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

   datalad catalog create --catalog-dir /tmp/my-cat

This will create a catalog with the following structure:

- artwork: images that make the catalog pretty
- assets: mainly the JavaScript and CSS code that underlie the user interface of
  the catalog
- metadata: where metadata content for any datasets and files rendered by the
  catalog will be contained

Add metadata
============

To add metadata to an existing catalog, run ``datalad catalog add``, specifying
the location of the metadata to add. The DataLad Catalog accepts metadata in the
form of json lines, i.e. a text file (typically ``.json``, ``.jsonl``, or
``.txt``) where each line is a single, correctly formatted JSON object.

.. code-block:: bash

   datalad catalog add --catalog-dir /tmp/my-cat --metadata path/to/metadata.jsonl


The ``metadata`` directory is now populated.

Metadata validation
-------------------
To check if metadata is valid before adding it to a catalog, ``datalad catalog
validate`` can be run to check if the metadata conforms to the Catalog schema.

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

   datalad catalog set-super --catalog-dir /tmp/my-cat --dataset_id abcd --dataset_version 1234

Normally, the main dataset is a superdataset that contains other datasets from
the catalog.

View the catalog
=================

To serve the content of a catalog via a local HTTP server for viewing or
testing, run ``datalad catalog serve``.

.. code-block:: bash

   datalad catalog serve --catalog-dir /tmp/my-cat

Once the content is served, the catalog can be viewed by visiting the local URL.

Update
======

Catalog content can be updated using the ``add`` or ``remove`` commands. To add
content, simply re-run ``datalad catalog add``, providing the path to the new
metadata.

.. code-block:: bash

   datalad catalog add --catalog-dir /tmp/my-cat --metadata path/to/new/metadata.jsonl

If a newly added dataset or version of a dataset was added incorrectly,
``datalad catalog remove`` can be used to get rid of the incorrect addition.

.. code-block:: bash

   datalad catalog remove --dataset_id abcd --dataset_version 1234

Configuration
=============

A useful feature of the catalog process is to be able to configure certain
properties according to your preferences. This is done with help of a config
file (in either ``JSON`` or ``YAML`` format) and the ``-y/--config-file`` flag during
catalog creation.

.. code-block:: bash

   datalad catalog create --catalog-dir /tmp/my-custom-cat --config-file path/to/custom_config.json

If no config file is specified, a default config file is used.
