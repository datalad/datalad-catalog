Installation
************

You can install and run DataLad Catalog on all major operating systems
by following the steps below in the command line.

Step 1 - Setup and activate a virtual environment
=================================================

With your virtual environment manager of choice, create a virtual
environment and ensure you have a recent version of Python installed.
Then activate the environment.


With `virtualenv`_:

.. code-block:: bash

    virtualenv mycatalogenv
    source mycatalogenv/bin/activate


With `miniconda`_:

.. code-block:: bash
   
    conda create -n mycatalogenv python=3.9
    conda activate mycatalogenv


Step 2 - Clone the repo and install the package
===============================================

.. code-block:: bash

    git clone https://github.com/datalad/datalad-catalog.git
    cd datalad-catalog
    pip install -e .

Congratulations! You have now installed DataLad Catalog!


Dependencies
============

.. admonition:: TODO

    - Confirm and list all dependencies
    - Provide separate installation instructions where needed
    - Describe DataLad installation process in short, git-annex
    - Separate usage dependencies from development dependencies

DataLad Catalog has the following core dependencies:

- datalad
- datalad-metalad
- sphinx (for documentation)
- pytest (for testing)

.. _virtualenv: https://github.com/pypa/virtualenv
.. _miniconda: https://docs.conda.io/en/latest/miniconda.html
