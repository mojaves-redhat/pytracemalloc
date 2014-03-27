:mod:`tracemalloc` --- Trace memory allocations
===============================================

.. module:: tracemalloc
   :synopsis: Trace memory allocations.

.. image:: tiger.jpg
   :alt: Tiger
   :align: right
   :target: http://www.flickr.com/photos/haypo/7199655050/

The tracemalloc module is a debug tool to trace memory blocks allocated by
Python. It provides the following information:

* Traceback where an object was allocated
* Statistics on allocated memory blocks per filename and per line number:
  total size, number and average size of allocated memory blocks
* Compute the differences between two snapshots to detect memory leaks

To trace most memory blocks allocated by Python, the module should be started
as early as possible by setting the :envvar:`PYTHONTRACEMALLOC` environment
variable to ``1``. The :func:`tracemalloc.start` function can be called at runtime to
start tracing Python memory allocations.

By default, a trace of an allocated memory block only stores the most recent
frame (1 frame). To store 25 frames at startup: set the
:envvar:`PYTHONTRACEMALLOC` environment variable to ``25``.

Websites:

* `Project homepage
  <http://pytracemalloc.readthedocs.org/>`_ (this documentation)
* `Entry in the Python Cheeseshop (PyPI)
  <https://pypi.python.org/pypi/pytracemalloc>`_
* `Source code at Github
  <https://github.com/haypo/pytracemalloc>`_
* `Statistics on the project at Ohloh
  <https://www.ohloh.net/p/pytracemalloc/>`_
* `Qt graphical interface: tracemallocqt
  <https://bitbucket.org/haypo/tracemallocqt/>`_

The tracemalloc module has been integrated in Python 3.4: read `tracemalloc
module documentation <http://docs.python.org/dev/library/tracemalloc.html>`_.

Table of Contents
=================

.. toctree::
   :maxdepth: 2

   install
   examples
   api
   tracemallocqt
   changelog


Status of the module
====================

pytracemalloc 1.0 contains patches for Python 2.7 and 3.3. The version 1.0 has
been tested on Linux with Python 2.7 and 3.3: unit tests passed.


Similar Projects
================

Python projects:

* `Meliae: Python Memory Usage Analyzer
  <https://pypi.python.org/pypi/meliae>`_
* `Guppy-PE: umbrella package combining Heapy and GSL
  <http://guppy-pe.sourceforge.net/>`_
* `PySizer <http://pysizer.8325.org/>`_: developed for Python 2.4
* `memory_profiler <https://pypi.python.org/pypi/memory_profiler>`_
* `pympler <http://code.google.com/p/pympler/>`_
* `memprof <http://jmdana.github.io/memprof/>`_:
  based on sys.getsizeof() and sys.settrace()
* `Dozer <https://pypi.python.org/pypi/Dozer>`_: WSGI Middleware version of
  the CherryPy memory leak debugger
* `objgraph <http://mg.pov.lt/objgraph/>`_
* `caulk <https://github.com/smartfile/caulk/>`_

Perl projects:

* `Devel::MAT
  <https://metacpan.org/release/Devel-MAT>`_ by Paul Evans
* `Devel::Size
  <http://search.cpan.org/~nwclark/Devel-Size/lib/Devel/Size.pm>`_ by  Dan Sugalski
* `Devel::SizeMe
  <http://search.cpan.org/~timb/Devel-SizeMe/lib/Devel/SizeMe.pm>`_ by Dan Sugalski
