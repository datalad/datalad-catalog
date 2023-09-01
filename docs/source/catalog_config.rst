Catalog Configuration
*********************

A useful feature of the catalog process is to be able to configure certain
properties according to your preferences. This is done with help of a config
file (in either ``JSON`` or ``YAML`` format) and the ``-F/--config-file`` flag.
A config file can be passed during catalog creation in order to set the config
on the catalog level, or when adding metadata in order to set the config
on the dataset-level.

As an example, ``datalad-catalog``'s default config file can be viewed `here`_.

Catalog-level configuration
===========================

Via the catalog-level config (provided during ``catalog-create``) you can specify
the following properties:

- the catalog name
- a path to a logo file to be used in the rendered catalog header
- the HEX color code to be used for links in the rendered catalog
- the HEX color code to be used when a cursor hovers over links in the rendered catalog
- default rules for rendering metadata on a dataset level (see detailed specification below)

The catalog-level configuration file will be located at: ``path-to-catalog/config.json``.

Dataset-level configuration
===========================

The dataset-level config (provided during ``catalog-add``) can specify the exact same content,
although then the catalog-level properties mentioned above will be ignored.

This configuration file will be located at: ``path-to-catalog/metadata/<dataset_id>/<dataset_version>/config.json``.

This configuration file will be created for all dataset-level metadata items in the metadata
provided to the ``catalog-add`` operation. For each dataset, this file will override the default
config specified on the catalog level.

Inheritance rules
=================

- If not specified by the user on the catalog-level, a default built-in config file is used.
- The catalog-level config serves as the default for dataset-level config.
- If not specified on the dataset-level by the user, the rendering rules will be inherited from the catalog level.

Prioritizing rendered metadata properties
=========================================

``datalad-catalog`` can generate metadata entries that originate from various sources. Through
the particular mechanism of catalog entry generation, this information from multiple sources
ends up in a single metadata entry in a catalog. It follows that one might want to prioritize
information coming from a particular source over another. For example, if metadata from
the ``metalad_core`` as well as the ``metalad_studyminimeta`` extractors both provide information
that maps to the ``authors`` property of a dataset in a catalog, which one should end up being
displayed in the catalog? Or should they be merged? How can I apply a rule to automate such
prioritization? And can these rules be set per catalog property?

To cater to these challenges, the catalog's configuration file can specify specific *rules* and
how they should be applied in relation to various *sources* of metadata. These rules
and sources can be specified *per property* of a file and a dataset.

Here is an example config structure:

.. code-block:: javascript

   config = {
       ...
       "property_sources": {
           "dataset": {
               ...
               "description": {
                   "rule": "single",
                   "source": ["metalad_studyinimeta"]
               },
               "authors": {
                   "rule": "priority",
                   "source": ["metalad_studyinimeta", "bids_dataset", "datacite_gin"]
               },
               "keywords": {
                   "rule": "merge",
                   "source": "any"
               },
               "publications": {
                   "rule": "merge",
                   "source": ["metalad_studyinimeta", "bids_dataset"]
               },
               ...
           },
           "file": {}
       }
       ...
   }

Rules
-----

A rule can be:

- ``single``: only save metadata from a single specified source
- ``merge``: merge specified sources together
- ``priority``: save only one source from a list of sources, where the sources are prioritised based on the order in which they appear in the list

If no rule is specified, the default rule is "first-come-first-served".

Sources
-------

A source is generally a list of strings, with the list containing:

- a single element, when the ``single`` rule is specified
- multiple elements, when the ``merge`` or ``priority`` rules are specified

The source can also be ``any``, meaning that any sources are allowed.

How it works
------------

When metadata from a specific source is added to a catalog, the config is loaded
(either from the file specified on the dataset level, or inherited from the catalog level)
and this provides the specification (rules and sources) according to which all key-value pairs
of the incoming metadata dictionary is evaluated and populated into the catalog metadata.

The catalog metadata for a dataset keeps track of which sources supplied the values for which keys
in the metadata dictionary. This is done in order to allow metadata to be updated according to the
config-specified rules and sources.

As an example, let's say a dataset in a catalog has the property ``dataset_name`` with a current
value supplied by ``source_B``. And let's say the config specifies that the ``dataset_name`` property
can be populated by a number of sources in order of priority ``["source_A", "source_B", "source_C"]``.
Now, if a catalog update is made that supplies a new value for ``dataset_name`` from ``source_A``,
this should result in the new value for ``dataset_name`` being populated from ``source_A``,
and in this source information being tracked.

The tracking process is done in the ``metadata_sources`` of the metadata entry for the
specific dataset in the catalog. For example (before the metadata update):

.. code-block:: javascript

   {
     "type": "dataset",
     "dataset_id": "....",
     "name": "value_from_source_B",
     ...
     "metadata_sources": {
       "key_source_map": {
         "type": ["metalad_core"],
         "dataset_id": ["metalad_core"],
         "name": ["source_B"],
         ...
       },
       "sources": [
         {
           "source_name": "metalad_core",
           "source_version": "0.0.1",
           "source_parameter": {},
           "source_time": 1643901350.65269,
           "agent_name": "John Doe",
           "agent_email": "email@example.com"
         },
         {
           "source_name": "source_B",
           "source_version": "2",
           "source_parameter": {},
           "source_time": 1643901350.65269,
           "agent_name": "John Doe",
           "agent_email": "email@example.com"
         },
       ]
     }
   }

As can be seen in the above object, the structure of ``metadata_sources``, 

- ``metadata_sources["sources"]`` contains a list of metadata sources (with extra info such as version, agent, etc) that have provided content for this particular metadata record.
- ``metadata_sources["key_source_map"]`` provides a mapping of which metadata sources were used to provide content for which specific keys in the metadata record.


.. _here: https://raw.githubusercontent.com/datalad/datalad-catalog/main/datalad_catalog/config/config.json