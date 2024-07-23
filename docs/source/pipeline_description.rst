Pipeline Description
********************

.. warning::

   This section describes a functioning but outdated view of generating a catalog
   entry from a DataLad dataset using ``datalad-metalad`` extractors and 
   ``datalad-catalog`` translators. This will soon be updated to suggest a 
   metadata ingestion pipeline using the :doc:`metadata_source_spec` and
   dedicated toolset.


The DataLad ecosystem provides a complete set of free and open source tools
that, together, provide full control over dataset access and distribution,
version control, provenance tracking, metadata addition, extraction, and
aggregation, as well as catalog generation.

DataLad itself can be used for decentralised management of data as lightweight,
portable and extensible representations. DataLad MetaLad can extract structured
high- and low-level metadata and associate it with these datasets or with
individual files. Then at the end of this workflow, DataLad Catalog can turn the
structured metadata into a user-friendly data browser.

Importantly, DataLad Catalog can operate independently as well. Since it
provides its own schema in a standard vocabulary, any metadata that conforms to
this schema can be submitted to the tool in order to generate a catalog.
Metadata items do not necessarily have to be derived from DataLad datasets, and
the metadata extraction does not have to be conducted via DataLad MetaLad.

Even so, the provided set of tools can be particularly powerful when used
together in a distributed (meta)data management pipeline. Below is an example
for building a catalog using the full DataLad toolset; from data management, to
metadata handling, to the end result of catalog generation.

.. image:: /_static/datacat3_the_toolset.svg

An example end-to-end pipeline
==============================

Step 1 - Create/access a DataLad dataset
----------------------------------------

Our fundamental operational unit is a DataLad dataset. In order to generate
a minimal catalog, we have to start with this unit. We do this either by
cloning a DataLad dataset from a known location, or by creating a new dataset.
See the `DataLad Handbook`_ for more information on working with DataLad datasets.


Clone:

.. code-block:: bash
   
    datalad clone [dataset_location]

Create:
    
.. code-block:: bash
   
    datalad create --force [dataset_location]


Step 2 - Add metadata
---------------------

In order to extract arbitrary structured metadata from a DataLad dataset,
this information first has to be added explicitly to the dataset. It can
be added in your preferred location in the dataset tree. For example, here
we add a ``.studyminimeta.yaml`` file to the root directory of the dataset:

.. code-block:: bash
   
    cd mydataset
    mv [path/to/studyminimeta.yaml] .

Once the dataset has been updated with metadata, it has to be saved:

.. code-block:: bash
   
    datalad save -m "add metadata to mydataset"

Various metadata formats can be recognized by DataLad MetaLad's extraction process.
See :doc:`metadata_formats` for an overview and `DataLad Metalad`_'s
documentation for more detail.


Step 3 - Extract metadata
-------------------------

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
  datatasets/files, in order to automate metadata extraction and adding tasks

Below are example code snippets that can be run to extract metadata from the
file and dataset level (respectively using the ``metalad_core``, and both the
``metalad_core`` and ``metalad_studyminimeta`` extractors) and to subsequently
write these metadata objects to disk in JSON format.

From dataset
############

Extract and add:

.. code-block:: bash

    #!/bin/zsh
    DATASET_PATH="path/to/mydataset"
    PIPELINE_PATH="path/to/extract_dataset_pipeline.json"
    datalad meta-conduct "$PIPELINE_PATH" \
        traverser.top_level_dir=$DATASET_PATH \
        traverser.item_type=dataset \
        traverser.traverse_sub_datasets=True \
        extractor1.extractor_type=dataset \
        extractor1.extractor_name=metalad_core \
        extractor2.extractor_type=dataset \
        extractor2.extractor_name=metalad_studyminimeta \
        adder.aggregate=True

where the pipeline in ``path/to/extract_dataset_pipeline.json``
looks like this:

.. code-block:: json

    {
      "provider": {
        "module": "datalad_metalad.pipeline.provider.datasettraverse",
        "class": "DatasetTraverser",
        "name": "traverser",
        "arguments": {}  
      },
      "processors": [
        {
          "module": "datalad_metalad.pipeline.processor.extract",
          "class": "MetadataExtractor",
          "name": "extractor1",
          "arguments": {}    
        },
        {
          "module": "datalad_metalad.pipeline.processor.extract",
          "class": "MetadataExtractor",
          "name": "extractor2",
          "arguments": {}    
        },
        {
          "name": "adder",
          "module": "datalad_metalad.pipeline.processor.add",
          "class": "MetadataAdder",
          "arguments": {}    
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
##########

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
        traverser.top_level_dir=$DATASET_PATH \
        traverser.item_type=file \
        traverser.traverse_sub_datasets=True \
        extractor.extractor_type=file \
        extractor.extractor_name=metalad_core \
        | jq '.["pipeline_element"]["result"]["metadata"][0]["metadata_record"]' \
        | jq -c . | sed 's/$/,/' >> "$METADATA_OUT_PATH"
    # Remove last comma
    sed -i '' '$ s/.$//' "$METADATA_OUT_PATH"
    # Add closing array bracket
    echo "]" >> "$METADATA_OUT_PATH"

where the pipeline in ``path/to/extract_file_pipeline.json``
looks like this:

.. code-block:: javascript

    {
      "provider": {
        "module": "datalad_metalad.pipeline.provider.datasettraverse",
        "class": "DatasetTraverser",
        "name": "traverser",
        "arguments": {}
      },
      "processors": [
        {
          "module": "datalad_metalad.pipeline.processor.extract",
          "class": "MetadataExtractor",
          "name": "extractor",
          "arguments": {}
        }
      ]
    }

At the end of this process, you have two files with structured metadata that
can eventually be provided to ``datalad-catalog`` in order to generate the catalog
and its entries.


Step 4 - Translate the metadata
-------------------------------

Before the extracted metadata can be provided to ``datalad-catalog``, it needs to be
in a format/structure that will validate successfully against the catalog schema.
Extracted metadata will typically be structured according to whatever schema was
specified by the extractor, and information in such a schema will have to be translated
to the catalog schema. For this purpose, ``datalad-catalog`` provides a ``catalog-translate``
command together with dedicated translators for specific metadata extractors.
See :doc:`metadata_formats` and the :doc:`usage` instructions for more information.

To translate the extracted metadata, we do the following:

.. code-block:: bash
   
    datalad catalog-translate -m [path/to/dataset_metadata.json] > [path/to/translated_dataset_metadata.json]
    datalad catalog-translate -m [path/to/file_metadata.json] > [path/to/translated_file_metadata.json]


Step 5 - Run DataLad Catalog
----------------------------

.. note:: Detailed usage instructions for DataLad Catalog can be viewed in
    :doc:`usage` and :doc:`command_line_reference`.

The important subcommands for generating a catalog are:

- ``catalog-create`` creates a new catalog with the required assets, taking metadata
  as an optional input argument
- ``catalog-add`` adds dataset and/or file level metadata to an existing catalog

To create a catalog from the metadata we generated above, we can run the following:

.. code-block:: bash

    #!/bin/zsh
    TRANSLATED_DATASET_METADATA_OUT_PATH="path/to/translated_dataset_metadata.json"
    TRANSLATED_FILE_METADATA_OUT_PATH="path/to/translated_file_metadata.json"
    CATALOG_PATH="path/to/new/catalog"
    datalad catalog-create -c "$CATALOG_PATH" -m "$TRANSLATED_DATASET_METADATA_OUT_PATH"
    datalad catalog-add -c "$CATALOG_PATH" -m "$TRANSLATED_FILE_METADATA_OUT_PATH"


Step 6 - Next steps
-------------------

Congratulations! You now have a catalog with multiple entries!

This catalog can be served locally (``datalad catalog-serve``) to view/test it, deployed
to an open or/restricted cloud server in order to make it available to the public or 
colleagues/collaborators (e.g. via Netlify in the case of publicly available catalogs),
and updated with new entries in future (with a ``datalad catalog-add``).

Happy cataloging!

.. _DataLad Handbook: https://handbook.datalad.org/en/latest/basics/basics-datasets.html
.. _DataLad Metalad: https://github.com/datalad/datalad-metalad
