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

It is an extension to, and dependent on, `Datalad`_ and `Datalad Metalad`_:

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

Data privacy regulations might restrict data from being shared or accessed 
across multi-national sites, and the costs of combined data hosting and
browsing infrastructure could be prohibitive. While free global and
region- or domain-specific data sharing solutions exist, they are unlikely
to provide the full set of features required by the wide range of data types,
data structures, and data security standards in current use. In addition,
centrally maintained infrastructure can be an administrative burden and slow
to update. These challenges impede the many possible gains obtainable from
distributed data sharing and access.

**To counter this, our approach with DataLad and its MetaLad and Catalog extensions
is to improve FAIR data access by focusing on decentralization, modularity,
extensibility and interoperability:**

- DataLad datasets are light-weight representations that are separate from
  actual data content, thus ideal for access and browsing without touching
  actual data.
- DataLad datasets can be structured into modular, nestable, units, each
  with their own version history and provenance records. This is ideal for
  decentralized data management and contributions.
- Adding and extracting metadata is straightforward with DataLad MetaLad, 
  which is extensible through the addition of metadata extractors, on top
  of its built-in file and dataset-level extractors.
- The ability to add generic or custom metadata extractors improves interoperability 
  with global or domain-specific (meta)data standards and formats.
- DataLad Catalog adds user-friendly accessibility on top the above mentioned
  features, while taking care of the complexities of metadata translation
  and aggregation on your behalf.
- Your catalog can be published online using a simple webserver, increasing the
  findability of your data.

By combining these features, DataLad Catalog can create a user-friendly
catalog of your dataset and make it publicly available, complete with all
additionally supplied metadata, while you maintain secured and permission-based
access control over your actual file content. This catalog can itself be
maintained and contributed to in a decentralized manner without compromising
metadata integrity.


How does it work?
=================

With DataLad you can organize your data in modular, representational units 
that are based on, but completely separate from, the actual data. These dataset
representations, that is *DataLad datasets*, are ideally suited for decentralized
access and contribution, with `git`_ providing the underlying version control and
provenance tracking tools, and `git-annex`_ providing the underlying transport
mechanism to obtain actual data files on-demand.

The lightweight DataLad datasets can be hosted on your preferred open or private
infrastructure, while the data remains securely under your control. A DataLad
dataset can be accessed (cloned) from anywhere and by anyone with the required
access permissions, while actual data files can be obtained on-demand. With this
functionality, a distributed network of collaborators can access, provide metadata
for, and extract metadata from a collection of DataLad datasets.

After access, the first step is to add any and all additional metadata to the
DataLad dataset. This could either be standardized metadata such as a `datacite.xml`
file, or a basic README or unstandardized JSON file. This is followed by metadata
extraction from the dataset and its files using DataLad MetaLad together with
built-in or extensible metadata extractors.

When exported, all metadata objects can be passed to DataLad Catalog. This package
translates the DataLad-generated metadata into structured data, which in turn is
required by the `VueJS`_-based data browser interface. DataLad Catalog also
generates the assets for the interface (artwork, CSS, JavaScript and HTML).

The resulting user-friendly catalog can be hosted as a standalone web application
without requiring any prior building steps or complicated infrastructure.

.. note:: A detailed description of these steps can be found in the :doc:`pipeline_description`

.. _DataLad: https://github.com/datalad/datalad
.. _DataLad Metalad: https://github.com/datalad/datalad-metalad
.. _git: https://git-scm.com/
.. _git-annex: https://git-annex.branchable.com/
.. _VueJS: https://vuejs.org/

