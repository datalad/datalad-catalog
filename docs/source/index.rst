DataLad Catalog
***************

.. image:: https://readthedocs.org/projects/datalad-catalog/badge/?version=latest
   :target: http://docs.datalad.org/projects/catalog/en/latest/?badge=latest
   :alt: Documentation Status

Welcome to the user and technical documentation of DataLad Catalog,
a DataLad extension that allows you to create a user-friendly data
browser from structured metadata.

.. image:: /_static/datacat0_hero_wo_subtitle.svg
   :alt: datacat logo
   :align: center

|


Acknowledgements
================

This software was developed with support from the German Federal Ministry of
Education and Research (BMBF 01GQ1905), the US National Science Foundation
(NSF 1912266), and the Deutsche Forschungsgemeinschaft (DFG, German Research
Foundation) under grant SFB 1451 (`431549029`_, INF project).

.. _431549029: https://gepris.dfg.de/gepris/projekt/431549029


NOTE: Future development
========================

We're working on a newer, leaner, more modular, and more interoperable solution
to the same challenge that the current ``datalad-catalog`` aims to address.
This new development is taking place within the broader context of making
DataLad datasets interoperable with linked and semantic (meta)data. For more
background, see `this issue`_. To keep up to date, follow progress at
`psychoinformatics-de/datalad-concepts`_, `psychoinformatics-de/shacl-vue`_, and
in the `new development branch`_. Because of this redirected focus, ``datalad-catalog``
itself will be downscaled by focusing on maintenance and assessing the priority
of new features on a case-by-case basis.


.. _this issue: https://github.com/psychoinformatics-de/datalad-concepts/issues/115
.. _psychoinformatics-de/datalad-concepts: https://github.com/psychoinformatics-de/datalad-concepts
.. _psychoinformatics-de/shacl-vue: https://github.com/psychoinformatics-de/shacl-vue
.. _new development branch: https://github.com/datalad/datalad-catalog/tree/revolution

Demo
====

See our `demo catalog`_, hosted via Netlify. This catalog was generated
from the `studyforrest dataset`_.

.. image:: /_static/datalad_catalog_demo.svg
   :align: center

|

Index
=====

.. toctree::
   :maxdepth: 1

   overview
   installation
   usage
   metadata_source_spec
   pipeline_description
   metadata_formats
   catalog_schema
   catalog_config
   resources
   contributing
   command_line_reference
   python_module_reference
   changelog



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. |---| unicode:: U+02014 .. em dash

.. _demo catalog: https://datalad-catalog.netlify.app/
.. _studyforrest dataset: https://www.studyforrest.org/

