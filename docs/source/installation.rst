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
   
    conda create -n my_catalog_env python=3.11
    conda activate my_catalog_env


Step 2 - Install via `PyPI`_
============================

.. code-block:: bash

    pip install datalad-catalog


Congratulations! You have now installed DataLad Catalog!


Optional - Clone the repo and install the package
=================================================

If you want to access the latest, unreleased version of the software or 
contribute to the code, access the repository via `GitHub`_:

.. code-block:: bash

    git clone https://github.com/datalad/datalad-catalog.git
    cd datalad-catalog
    pip install -e .


Dependencies
============

Because this is an extension to ``datalad`` and builds on metadata handling
functionality, the installation process also installed `datalad`_ and
`datalad-metalad`_ as dependencies, although these do not have to be used as the
only sources of metadata for a catalog. In addition `datalad-next`_ is installed
in order to use the latest improvements and patches to the ``datalad`` core package.

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

In order to translate metadata extracted using ``datalad-metalad`` into the
catalog schema, ``datalad-catalog`` provides translation modules that are
dependent on `jq`_.

.. _datalad: https://github.com/datalad/datalad
.. _GitHub: https://github.com/datalad/datalad-catalog
.. _datalad-metalad: https://github.com/datalad/datalad-metalad
.. _datalad-next: https://github.com/datalad/datalad-next
.. _DataLad Handbook: https://handbook.datalad.org/en/latest/intro/installation.html
.. _jq: https://stedolan.github.io/jq/
.. _miniconda: https://docs.conda.io/en/latest/miniconda.html
.. _PyPI: https://pypi.org/project/datalad-catalog/
.. _venv: https://github.com/pypa/virtualenv
