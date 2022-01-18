Pipeline Description
********************

Creating a catalog for your data involves the use of several of DataLad's
functionalities and extensions: mainly DataLad, DataLad MetaLad, and 
DataLad Catalog. Below we describe a standard pipeline for building a
user-friendly catalog from your (meta)data.


Step 1 - Create/access a DataLad dataset
========================================

Our fundamental operational unit is a DataLad dataset. In order to generate
a minimal catalog, we have to start with this unit. We do this either by
cloning a DataLad dataset from a known location, or by creating a new dataset.


Clone:

.. code-block:: bash
   
    datalad clone [dataset_location]

Create:
    
.. code-block:: bash
   
    datalad create --force [dataset_location]


Step 2 - Add metadata
=====================

In order to extract arbitrary structured metadata from a DataLad dataset,
this information first has to be added explicitly to the dataset. It can
be added in your preferred location in the dataset tree. For example, here
we add a ``studyminimeta.yaml`` file to the root directory of the dataset:

.. code-block:: bash
   
    cd mydataset
    mv [path/to/studyminimeta.yaml] .

Once the dataset has been updated with metadata, it has to be saved:

.. code-block:: bash
   
    datalad save -m "add metadata to mydataset"

Various metadata formats are recognized by DataLad MetaLad's extractors.
See :doc:`metadata_formats` for an overview and `DataLad Metalad`_'s 
documentation for more detail.


Step 3 - Extract metadata
=========================

With Datalad MetaLad we can extract implicit and explicit metadata from
our dataset. This can be done on the dataset as well as file level through
the use of built-in or custom extractors. MetaLad provides several commands
to streamline this process, especially for large datasets:

- ``meta-add`` adds metadata related to an element (dataset or file) to the
  metadata store
- ``meta-dump`` shows metadata stored in a local or remote dataset
- ``meta-extract`` runs an extractor (see below) on an existing dataset or file
  and emits the resulting metadata to stdout
- ``meta-aggregate`` combines metadata from a number of sub-datasets into the
  root dataset
- ``meta-conduct`` runs pipelines of extractors and adders on locally available
  datatasets/files, in order to automatate metadata extraction and adding tasks

Below are example code snippets that can be run to extract metadata from the
file and dataset level (repectively using the ``metalad_core``, and both the 
``metalad_core`` and ``metalad_studyminimeta`` extractors) and to subsequently
write these metadata objects to disk in JSON format.

From dataset
------------

Extract and add:

.. code-block:: bash

    #!/bin/zsh
    DATASET_PATH="path/to/mydataset"
    PIPELINE_PATH="path/to/extract_dataset_pipeline.json"
    datalad meta-conduct "$PIPELINE_PATH" \
        traverser:"$DATASET_PATH" \
        traverser:dataset \
        traverser:True \
        extractor1:Dataset \
        extractor1:metalad_core \
        extractor2:Dataset \
        extractor2:metalad_studyminimeta \
        adder:True

where the pipeline in ``path/to/extract_dataset_pipeline.json``
looks like this:

.. code-block:: json

    {
      "provider": {
        "module": "datalad_metalad.provider.datasettraverse",
        "class": "DatasetTraverser",
        "name": "traverser",
        "arguments": [],
        "keyword_arguments": {}
      },
      "processors": [
        {
          "module": "datalad_metalad.processor.extract",
          "class": "MetadataExtractor",
          "name": "extractor1",
          "arguments": [],
          "keyword_arguments": {}
        },
        {
          "module": "datalad_metalad.processor.extract",
          "class": "MetadataExtractor",
          "name": "extractor2",
          "arguments": [],
          "keyword_arguments": {}
        },
        {
          "name": "adder",
          "module": "datalad_metalad.processor.add",
          "class": "MetadataAdder",
          "arguments": [],
          "keyword_arguments": {}
        }
      ]
    }

Dump and write to disk:

.. code-block:: bash

    #!/bin/zsh
    DATASET_PATH="path/to/mydataset"
    METADATA_OUT_PATH="path/to/dataset_metadata.json" # empty text file
    datalad meta-dump -d "$DATASET_PATH" -r "*" > "$METADATA_OUT_PATH"

From files
----------

Extract and write to disk:

.. code-block:: bash

    #!/bin/zsh
    DATASET_PATH="path/to/mydataset"
    PIPELINE_PATH="path/to/extract_file_pipeline.json"
    METADATA_OUT_PATH="path/to/file_metadata.json" # empty text file
    # Add starting array bracket
    echo "[" > "$METADATA_OUT_PATH"
    # Extract file-level metadata, add comma
    datalad -f json meta-conduct "$PIPELINE_PATH" \
        traverser:"$DATASET_PATH" \
        traverser:file \
        traverser:True \
        extractor:File \
        extractor:metalad_core \
        | jq '.["pipeline_element"]["result"]["metadata"][0]["metadata_record"]' \
        | jq -c . | sed 's/$/,/' >> "$METADATA_OUT_PATH"
    # Remove last comma
    sed -i '' '$ s/.$//' "$METADATA_OUT_PATH"
    # Add closing array bracket
    echo "]" >> "$METADATA_OUT_PATH"

where the pipeline in ``path/to/extract_file_pipeline.json``
looks like this:

.. code-block:: json

    {
      "provider": {
        "module": "datalad_metalad.provider.datasettraverse",
        "class": "DatasetTraverser",
        "name": "traverser",
        "arguments": [],
        "keyword_arguments": {}
      },
      "processors": [
        {
          "module": "datalad_metalad.processor.extract",
          "class": "MetadataExtractor",
          "name": "extractor",
          "arguments": [],
          "keyword_arguments": {}
        }
      ]
    }

At the end of this process, you have two files with structured metadata that
can be given as arguments to DataLad Catalog in order to generate the catalog.


Step 4 - Run DataLad Catalog
============================

.. note:: Detailed usage instructions for DataLad Catalog can be viewed in
    :doc:`usage` and :doc:`command_line_reference`.

The important subcommands for generating a catalog are:

- ``create`` creates a new catalog with the required assets, taking metadata
  as an optional input argument
- ``add`` adds dataset and/or file level metadata to an existing catalog

To create a catalog from the metadata we generated above, we can run the following:

.. code-block:: bash

    #!/bin/zsh
    DATASET_METADATA_OUT_PATH="path/to/dataset_metadata.json"
    FILE_METADATA_OUT_PATH="path/to/file_metadata.json"
    CATALOG_PATH="path/to/new/catalog"
    datalad catalog create -c "$CATALOG_PATH" -m "$DATASET_METADATA_OUT_PATH"
    datalad catalog add -c "$CATALOG_PATH" -m "$FILE_METADATA_OUT_PATH"


Step 5 - Deploy the catalog
===========================

.. admonition:: TODO
    
    - add/update content


Step 6 - Update the catalog
===========================

.. admonition:: TODO
    
    - add/update content



.. _DataLad Metalad: https://github.com/datalad/datalad-metalad