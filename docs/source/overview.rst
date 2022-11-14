Overview
********

What is DataLad Catalog?
========================

DataLad Catalog is a free and open source command line tool with a Python API
that allows you to turn structured metadata into a user-friendly, browser-based
data catalog.


.. image:: /_static/datalad_catalog_functionality.svg
   :width: 80%
   :alt: alternate text
   :align: center

|

It is an extension to, and dependent on, `Datalad`_, and is interoperable with 
`Datalad Metalad`_:

- **DataLad** is a distributed data management system that keeps track of
  your data, creates structure, ensures reproducibility, supports collaboration,
  and integrates with widely used data infrastructure.
- **DataLad MetaLad** extends and equips DataLad with a command suite for metadata
  handling. This includes traversing a full data tree (of arbitrarily large size) to 
  conduct metadata extraction (using extractors for various data
  types), metadata aggregation, and also reporting.

By combining the functionality of these three tools, you can:

1. manage the full lifecycle of your data (applying version control and capturing
   provenance records along the way)
2. add and extract detailed metadata records about every single item in a
   multi-level dataset, and
3. convert the metadata into a user-friendly browser application that increases
   the findability and accessibility of your data.

As a bonus, these processes can be applied in a decentralized and collaborative way.

Why use DataLad Catalog?
========================

Working collaboratively with large and distributed datasets poses particular
challenges for FAIR data access, browsing, and usage.

- the **administrative burden of keeping track** of different versions of the
  data, who contributed what, where/how to gain access, and representing this
  information centrally and accessibly can be significant
- **data privacy regulations** might restrict data from being shared or accessed
  across multi-national sites
- **costs of centrally maintained infrastructure** for data hosting and
  web-portal type browsing could be prohibitive

These challenges impede the many possible gains obtainable from distributed data
sharing and access. Decisions might even be made to forego FAIR principles in
favour of saving time, effort and money, leading to the view that these efforts
have seemingly contradicting outcomes.

.. image:: /_static/datacat1_the_challenge.svg

**DataLad Catalog helps counter this** contradiction by focusing on
interoperability with structured, linked, and machine-readable metadata.

Metadata about datasets, their file content, and their links to other datasets
can be used to create abstract representations of datasets that are separate
from the actual data content. This means that data content can be stored
securely while metadata can be shared and operated on widely, thus improving
decentralization and FAIRness.

.. image:: /_static/datacat2_the_opportunity.svg

By combining these features, DataLad Catalog can create a user-friendly
catalog of your dataset and make it publicly available, complete with all
additionally supplied metadata, while you maintain secured and permission-based
access control over your actual file content. This catalog can itself be
maintained and contributed to in a decentralized manner without compromising
metadata integrity.


How does it work?
=================

DataLad Catalog can receive commands to ``create`` a new catalog, ``add`` and
``remove`` metadata entries to/from an existing catalog, ``serve`` an existing
catalog locally, and more. Metadata can be provided to DataLad Catalog from any
number of arbitrary metadata sources, as an aggregated set or as individual
items/objects. DataLad Catalog has a dedicated :doc:`catalog_schema` (using the
`JSON Schema`_ vocabulary) against which incoming metadata items are validated.
This schema allows for standard metadata fields as one would expect for datasets
of any kind (such as ``name``, ``doi``, ``url``, ``description``, ``license``,
``authors``, and more), as well as fields that support identification, versioning,
dataset context and linkage, and file tree specification.

The process of generating a catalog, after metadata entry validation, involves:

1. aggregation of the provided metadata into the catalog filetree
2. generating the assets required to render the user interface in a browser

The output is a set of structured metadata files, as well as a `Vue.js`_-based
browser interface that understands how to render this metadata in the browser.
What is left for the user is to host this content on their platform of choice
and to serve it for the world to see.

For an example of the result, visit our `demo catalog`_.

.. image:: /_static/datacat4_the_catalog.svg



.. note:: A detailed description of these steps can be found in the :doc:`pipeline_description`

.. _DataLad: https://github.com/datalad/datalad
.. _DataLad Metalad: https://github.com/datalad/datalad-metalad
.. _demo catalog: https://datalad.github.io/datalad-catalog/
.. _JSON Schema: https://json-schema.org/
.. _Vue.js: https://vuejs.org/




