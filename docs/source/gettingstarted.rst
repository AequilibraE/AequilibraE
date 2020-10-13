
Getting Started
===============

This page describes how to get started with AequilibraE.

.. note::
   Although AequilibraE is under intense development, we try to avoid making
   breaking changes to the API. In any case, you should check for new features
   and possible API changes often.

.. index:: installation

Installation
------------

1. Install `Python 3.5, 3.6 or 3.7 <www.python.org>`__. We recommend Python
   3.7 as of late 2019.

2. Install AequilibraE

::

  pip install aequilibrae

.. _dependencies:

Dependencies
~~~~~~~~~~~~

Aequilibrae relies on a series of compiled libraries, such as NumPy and Scipy.
If you are working on Windows and have trouble installing any of the
requirements, you can look at
`Christoph Gohlke's wonderful repository <https://www.lfd.uci.edu/~gohlke/pythonlibs/>`_
of compiled Python packages for windows.

OMX support
+++++++++++
AequilibraE also supports OMX starting on version 0.5.3, but that comes with a
few extra dependencies. Installing **openmatrix** solves all those dependencies:

::

  pip install openmatrix

.. _installing_spatialite_on_windows:

Spatialite
++++++++++

Although the presence of Spatialite is rather obiquitous in the GIS ecosystem,
it has to be installed separately from Python or AequilibraE.

Windows
^^^^^^^
Spatialite does not have great support on Python for Windows. For this reason,
it is necessary to download Spatialite for Windows and inform AequilibraE of its
location.

One can download the appropriate version of the latest SpatiaLite release
directly from its `project page <https://www.gaia-gis.it/gaia-sins/>`_ .

After unpacking the zip file into its own folder (say D:/spatialite), one can
update the AequilibraE parameter file with the location of spatialite by using
the *Parameters* module as follows:

::

  from aequilibrae import Parameters

  fldr = 'D:/spatialite'

  p = Parameters()
  p.parameters['system']['spatialite_path'] =  fldr
  p.writeback()

It is not possible to use Spatialite with AequilibraE on windows by simply
editing environment variables.

Ubuntu Linux
^^^^^^^^^^^^

On Ubuntu it is possible to install Spatialite by simply using apt-get

::

  sudo apt-get install libsqlite3-mod-spatialite
  sudo apt-get install -y libspatialite-dev


MacOS
^^^^^

On MacOS one can use brew as per
`this answer on StackOverflow <https://stackoverflow.com/a/48370444/1480643>`_.

::

  brew install libspatialite

Hardware requirements
---------------------

AequilibraE's requirements depend heavily of the size of the model you are using
for computation. The most important
things to keep an eye on are:

* Number of zones on your model (size of the matrices you are dealing with)

* Number of matrices (classes you are dealing with)

* Number of links and nodes on your network (far less likely to create trouble)

Substantial testing has been done with large real-world models (up to 8,000
zones) and memory requirements did not exceed the traditional 32Gb found in most
modelling computers these days. In most cases 16Gb of RAM is enough even for
large models (2,000+ zones).  Parallelization is fully implemented for graph
computation, and can make use of as many CPUs as there are available in the
system when doing traffic assignment.
