Catalog Schema
**************

Metadata submitted to DataLad Catalog has to conform to its own `schema`_, which
uses the vocabulary defined by `JSON Schema`_ (specifically `draft 2020-12`_).

Source files defining the catalog's schema can be found here:

- `catalog`_
- `dataset`_
- `file`_
- `authors`_
- `metadata_sources`_


A rendering of the schema can be accessed at:
https://datalad.github.io/datalad-catalog/display_schema.html


.. _draft 2020-12: https://json-schema.org/specification.html
.. _JSON Schema: https://json-schema.org/
.. _schema: https://datalad.github.io/datalad-catalog/display_schema
.. _catalog: https://raw.githubusercontent.com/datalad/datalad-catalog/main/datalad_catalog/schema/jsonschema_catalog.json
.. _dataset: https://raw.githubusercontent.com/datalad/datalad-catalog/main/datalad_catalog/schema/jsonschema_dataset.json
.. _file: https://raw.githubusercontent.com/datalad/datalad-catalog/main/datalad_catalog/schema/jsonschema_file.json
.. _authors: https://raw.githubusercontent.com/datalad/datalad-catalog/main/datalad_catalog/schema/jsonschema_authors.json
.. _metadata_sources: https://raw.githubusercontent.com/datalad/datalad-catalog/main/datalad_catalog/schema/jsonschema_metadata_sources.json