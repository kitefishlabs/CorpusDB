.. CorpusDB documentation master file, created by
   sphinx-quickstart on Mon Feb 11 22:42:35 2013.
   

CorpusDB
********
*Corpus-based processing for Python and SuperCollider*

Introduction
============
CorpusDB is a collection of Python classes for maintaining a database describing a corpus of sound files. There are three essential parts to this database: representation of the sounds, metadata derived from analysis of the sounds, and tools to access that data. CorpusDB relies on scsynth, by way of its command line interface (using Python's subprocess module). Furthermore, important relationships between sound files are encoded in the database, namely parent/child relationships that can be used to define source sound-processed sound relationships.

More on the architecture and design of CorpusDB can be found in the `design <design.html>`_ document.

Why CorpusDB?
-------------

There are some great tools out there for MIR, and also for corpus-based concatenative synthesis. (See Bibliography, whenever it gets written.) CorpusDB has its own unique characteristics and potential uses:

* Composition - organizing sound files for systematic material generation or transformation
* Analysis - can be used to support purely analytical tasks.
* Synthesis - sounds can be synthesized directly rather than sampled
* Trees/Nodes - structure allows for relationships between source sounds and derivations
* Interoperability - data can be easily processed and displayed with Numpy, Bregman and other tools
* Generative - serves as a perfect tool for tracking and representing sounds and sound-making algorithms in a generative system
* CBPSC - the sclang companion project to CorpusDB; to be kept synced with CorpusDB for complete interoperability.

Dependencies
============

* `SuperCollider <http:supercollider.sourceforge.net>`_
* Download `sc3-plugins <http://sourceforge.net/projects/sc3-plugins/files/OSX_3.6/SC3ExtPlugins-universal.dmg/download>`_ and install.
* jsonpickle - `pypi.python.org/pypi/jsonpickle <http://pypi.python.org/pypi/jsonpickle>`_.
* `Scipy Superpack <https://github.com/fonnesbeck/ScipySuperpack>`_ 

Optional, but highly recommended
--------------------------------
* `Bregman MIR Toolkit <http://digitalmusics.dartmouth.edu/bregman/>`_.
* SC-0.3.1 - `pypi.python.org/pypi/SC/0.3.1 <http://pypi.python.org/pypi/SC/0.3.1>`_. - not used in the core classes, but can be used to play sounds in real time.

MacPorts
--------

You may also wish to use MacPorts' Python. Use Python 2.7, and get numpy, matplotlib, scipy, ipython, etc. Be sure to select the proper version of python, then install the optional libraries.


Installation
============

Unzip, ``cd``, and install: ``sudo python setup.py install`` Do the same for SC-0.3.1 and jsonpickle.

If you do not have admin (sudo) privileges, you can install in your home path using the --prefix "$HOME" option to setup.py

Tutorials
=========
TBA

CorpusDB Modules
================
.. toctree::
   :maxdepth: 2

   corpusdb - database of sound files and metadata <corpusdb>
   sftree - representation of sounds and processed versions as nodes in tree <sftree>
   nrtoscparser - convert synth parameters into non-realtime (NRT) synthesis .osc files <nrtoscparser>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

