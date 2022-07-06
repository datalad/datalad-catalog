Installation
************

You can install and run DataLad Catalog on all major operating systems
by following the steps below in the command line.

Step 1 - Setup and activate a virtual environment
=================================================

With your virtual environment manager of choice, create a virtual
environment and ensure you have a recent version of Python installed.
Then activate the environment.


With `venv`_:

.. code-block:: bash

    python -m venv my_catalog_env
    source my_catalog_env/bin/activate


With `miniconda`_:

.. code-block:: bash
   
    conda create -n my_catalog_env python=3.9
    conda activate my_catalog_env


Step 2 - Clone the repo and install the package
===============================================

.. code-block:: bash

    git clone https://github.com/datalad/datalad-catalog.git
    cd datalad-catalog
    pip install -e .

Congratulations! You have now installed DataLad Catalog!


Dependencies
============

Because this is an extension to ``datalad`` and builds on metadata handling
functionality, the installation process also installed `datalad`_ and
`datalad-metalad`_ as dependencies, although these do not have to be used as the
only sources of metadata for a catalog.

While the catalog generation process does not expect data to be structured as
DataLad datasets, it can still be very useful to do so when building a full
(meta)data management pipeline from raw data to catalog publishing. For complete
instructions on how to install ``datalad`` and ``git-annex``, please refer to the
`DataLad Handbook`_.

Similarly, the metadata input to ``datalad-catalog`` can come from any source as
long as it conforms to the catalog schema. While the catalog does not expect
metadata originating only from ``datalad-metalad``'s extractors, this tool has
advanced metadata handling capabilities that will integrate seamlessly with
DataLad datasets and the catalog generation process.

.. _venv: https://github.com/pypa/virtualenv
.. _miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _datalad: https://github.com/datalad/datalad
.. _datalad-metalad: https://github.com/datalad/datalad-metalad
.. _DataLad Handbook: https://handbook.datalad.org/en/latest/intro/installation.html
