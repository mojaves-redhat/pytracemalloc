:mod:`tracemalloc` --- Trace memory allocations
===============================================

.. module:: tracemalloc
   :synopsis: Trace memory allocations.

The tracemalloc module is a debug tool to trace memory blocks allocated by
Python. It provides the following information:

* Compute the differences between two snapshots to detect memory leaks
* Statistics on allocated memory blocks per filename and per line number:
  total size, number and average size of allocated memory blocks
* Traceback where a memory block was allocated

To trace most memory blocks allocated by Python, the module should be enabled
as early as possible by setting the :envvar:`PYTHONTRACEMALLOC` environment
variable to ``1``, or by using :option:`-X` ``tracemalloc`` command line
option. The :func:`tracemalloc.enable` function can be called at runtime to
start tracing Python memory allocations.

By default, a trace of an allocated memory block only stores the most recent
frame (1 frame). To store 25 frames at startup: set the
:envvar:`PYTHONTRACEMALLOC` environment variable to ``25``, or use the
:option:`-X` ``tracemalloc=25`` command line option. The
:func:`set_traceback_limit` function can be used at runtime to set the limit.

By default, Python memory blocks allocated in the :mod:`tracemalloc` module are
ignored using a filter. Use :func:`clear_filters` to trace also these memory
allocations.

Websites:

* Project homepage: https://pypi.python.org/pypi/pytracemalloc
* Source code: https://github.com/haypo/pytracemalloc
* Documentation: http://pytracemalloc.readthedocs.org/


Status of the module
====================

pytracemalloc 0.9.1 contains patches for Python 2.5, 2.7 and 3.4.

Python 3.4 has a new API to replace memory allocators which can be used to
install hooks on memory allocations: `PEP 445 "Add new APIs to customize Python
memory allocators" <http://www.python.org/dev/peps/pep-0445/>`_. In Python 3.4,
the ``pymalloc`` allocator now also have a counter of allocated memory blocks.

The tracemalloc module was proposed for integration in the Python 3.4 standard
library: `PEP 454 "Add a new tracemalloc module to trace Python memory
allocations" <http://www.python.org/dev/peps/pep-0454/>`_.


Installation
============

Patch Python
------------

To install pytracemalloc, you need a modified Python runtime:

* Download Python source code
* Apply a patch (see below):
  patch -p1 < pythonXXX.patch
* Compile and install Python:
  ./configure && make && sudo make install
* It can be installed in a custom directory. For example:
  ./configure --prefix=/opt/mypython

Patches:

* Python 2.7: patches/2.7/pep445.patch
* Python 3.3: patches/3.3/pep445.patch


Compile and install pytracemalloc
---------------------------------

Dependencies:

* `Python <http://www.python.org>`_ 2.5 - 3.4
* `glib <http://www.gtk.org>`_ version 2
* (optional) `psutil <https://pypi.python.org/pypi/psutil>`_ to get the
  process memory. pytracemalloc is able to read the memory usage of the process
  on Linux without psutil.

Install::

    /opt/mypython/bin/python setup.py install


Examples
========

Display the top 10
------------------

Display the 10 lines allocating the most memory::

    import tracemalloc
    tracemalloc.enable()

    # ... run your application ...

    snapshot = tracemalloc.Snapshot.create()
    top = snapshot.top_by('line')
    stats = top.compare_to(None)

    print("[ Top 10 ]")
    for size_diff, size, count_diff, count, key in stats[:10]:
        filename, lineno = key
        print("%s:%s: %.1f kB" % (filename or "???", lineno or "?", size / 1024))

Example of output of the Python test suite::

    [ Top 10 ]
    <frozen importlib._bootstrap>:704: 6519.4 KB
    <frozen importlib._bootstrap>:274: 709.1 KB
    Lib/linecache.py:127: 616.5 KB
    ???:?: 316.0 KB
    Lib/collections/__init__.py:368: 234.8 KB
    Lib/unittest/case.py:571: 199.5 KB
    Lib/test/test_grammar.py:132: 199.0 KB
    <frozen importlib._bootstrap>:1435: 95.4 KB
    Lib/abc.py:133: 75.1 KB
    <frozen importlib._bootstrap>:1443: 68.2 KB

Snapshots may use a lot of memory, especially snapshots taken with traces. To
display the top 10, snapshots can be removed, only the result of
:meth:`Snapshot.top_by` is needed.


Compute differences
-------------------

Take two snapshots and display the differences::

    import tracemalloc
    tracemalloc.enable()
    snapshot1 = tracemalloc.Snapshot.create()

    # ... call the function leaking memory ...

    snapshot2 = tracemalloc.Snapshot.create()

    top1 = snapshot1.top_by('line')
    top2 = snapshot2.top_by('line')
    stats = top2.compare_to(top1)

    print("[ Top 10 differences ]")
    for size_diff, size, count_diff, count, key in stats[:10]:
        filename, lineno = key
        print("%s:%s: %.1f kB (%+.1f kB)"
              % (filename or "???", lineno or "?",
                 size / 1024, size_diff / 1024))

Example of output of a short script::

    [ Top 10 differences ]
    test.py:4: 0.0 kB (-5.0 kB)
    test.py:8: 0.6 kB (+0.6 kB)

If the system has few free memory, snapshots can be written on disk using the
:meth:`Snapshot.dump` method. The snapshot can then be loaded using the
:meth:`Snapshot.load` method to analyze the snapshot after the application
exited, or on another computer. Using files allow also deeper analysis using
filters or different views: see :meth:`Snapshot.apply_filters` and
:meth:`Snapshot.top_by` methods.


Get the traceback of a memory block
-----------------------------------

Code to display the traceback of the biggest memory block::

    import linecache
    import tracemalloc
    tracemalloc.enable()

    # ... run your application ...

    snapshot = tracemalloc.Snapshot.create(traces=True)
    top = snapshot.top_by('traceback')
    stats = top.compare_to(top)

    size_diff, size, count_diff, count, key = stats[0]
    address, traceback = key
    print("Memory block 0x%x: %.1f kB" % (address, size / 1024))
    for frame in traceback:
        filename, lineno = frame
        if filename and lineno:
            line = linecache.getline(filename, lineno)
            line = line.strip()
        else:
            line = None

        print('  File "%s", line %s' % (filename or "???", lineno or "?"))
        if line:
            print('    ' + line)
    print()

Example of output of the Python test suite (traceback limited to 25 frames)::

    Memory block 0x1725cd0: 768.0 kB
      File "<frozen importlib._bootstrap>", line 704
      File "<frozen importlib._bootstrap>", line 1024
      File "<frozen importlib._bootstrap>", line 922
      File "<frozen importlib._bootstrap>", line 1056
      File "<frozen importlib._bootstrap>", line 607
      File "<frozen importlib._bootstrap>", line 1566
      File "<frozen importlib._bootstrap>", line 1599
      File "Lib/test/support/__init__.py", line 142
        __import__(name)
      File "Lib/test/support/__init__.py", line 206
        _save_and_remove_module(name, orig_modules)
      File "Lib/test/test_decimal.py", line 48
        C = import_fresh_module('decimal', fresh=['_decimal'])
      File "<frozen importlib._bootstrap>", line 274
      File "<frozen importlib._bootstrap>", line 926
      File "<frozen importlib._bootstrap>", line 1056
      File "<frozen importlib._bootstrap>", line 607
      File "<frozen importlib._bootstrap>", line 1566
      File "<frozen importlib._bootstrap>", line 1599
      File "<frozen importlib._bootstrap>", line 1618
      File "Lib/importlib/__init__.py", line 95
        return _bootstrap._gcd_import(name[level:], package, level)
      File "Lib/test/regrtest.py", line 1269
        the_module = importlib.import_module(abstest)
      File "Lib/test/regrtest.py", line 976
        display_failure=not verbose)

.. note::

   This memory block of 768 kB (``0x1725cd0``) is the dictionary of Unicode
   interned strings.


API
===

Main Functions
--------------

.. function:: reset()

   Clear traces and statistics on Python memory allocations.

   See also :func:`disable`.


.. function:: disable()

   Stop tracing Python memory allocations and clear traces and statistics.

   See also :func:`enable` and :func:`is_enabled` functions.


.. function:: enable()

   Start tracing Python memory allocations.

   See also :func:`disable` and :func:`is_enabled` functions.


.. function:: get_stats()

   Get statistics on traced Python memory blocks as a dictionary ``{filename
   (str): {line_number (int): stats}}`` where *stats* in a
   ``(size: int, count: int)`` tuple, *filename* and *line_number* can
   be ``None``.

   *size* is the total size in bytes of all memory blocks allocated on the
   line, or *count* is the number of memory blocks allocated on the line.

   Return an empty dictionary if the :mod:`tracemalloc` module is disabled.

   See also the :func:`get_traces` function.


.. function:: get_traced_memory()

   Get the current size and maximum size of memory blocks traced by the
   :mod:`tracemalloc` module as a tuple: ``(size: int, max_size: int)``.


.. function:: get_tracemalloc_memory()

   Get the memory usage in bytes of the :mod:`tracemalloc` module used
   internally to trace memory allocations.
   Return a tuple: ``(size: int, free: int)``.

   * *size*: total size of bytes allocated by the module,
     including *free* bytes
   * *free*: number of free bytes available to store new traces


.. function:: is_enabled()

    ``True`` if the :mod:`tracemalloc` module is tracing Python memory
    allocations, ``False`` otherwise.

    See also :func:`disable` and :func:`enable` functions.


Trace Functions
---------------

When Python allocates a memory block, :mod:`tracemalloc` attachs a "trace" to
it to store information on it: its size in bytes and the traceback where the
allocation occured.

The following functions give access to these traces. A trace is a ``(size: int,
traceback)`` tuple. *size* is the size of the memory block in bytes.
*traceback* is a tuple of frames sorted from the most recent to the oldest
frame, limited to :func:`get_traceback_limit` frames. A frame is
a ``(filename: str, lineno: int)`` tuple where *filename* and *lineno* can be
``None``.

Example of trace: ``(32, (('x.py', 7), ('x.py', 11)))``.  The memory block has
a size of 32 bytes and was allocated at ``x.py:7``, line called from line
``x.py:11``.


.. function:: get_object_address(obj)

   Get the address of the main memory block of the specified Python object.

   A Python object can be composed by multiple memory blocks, the function only
   returns the address of the main memory block. For example, items of
   :class:`dict` and :class:`set` containers are stored in a second memory block.

   See also :func:`get_object_trace` and :func:`gc.get_referrers` functions.

   .. note::

      The builtin function :func:`id` returns a different address for objects
      tracked by the garbage collector, because :func:`id` returns the address
      after the garbage collector header.


.. function:: get_object_trace(obj)

   Get the trace of a Python object *obj* as a ``(size: int, traceback)`` tuple
   where *traceback* is a tuple of ``(filename: str, lineno: int)`` tuples,
   *filename* and *lineno* can be ``None``.

   The function only returns the trace of the main memory block of the object.
   The *size* of the trace is smaller than the total size of the object if the
   object is composed by more than one memory block. For example, items of
   :class:`dict` and :class:`set` containers are stored in a second memory
   block.

   Return ``None`` if the :mod:`tracemalloc` module did not trace the
   allocation of the object.

   See also :func:`get_object_address`, :func:`get_trace`,
   :func:`gc.get_referrers` and :func:`sys.getsizeof` functions.


.. function:: get_trace(address)

   Get the trace of a memory block allocated by Python. Return a tuple:
   ``(size: int, traceback)``, *traceback* is a tuple of ``(filename: str,
   lineno: int)`` tuples, *filename* and *lineno* can be ``None``.

   Return ``None`` if the :mod:`tracemalloc` module did not trace the
   allocation of the memory block.

   See also :func:`get_object_trace`, :func:`get_stats` and :func:`get_traces`
   functions.


.. function:: get_traceback_limit()

   Get the maximum number of frames stored in the traceback of a trace.

   By default, a trace of an allocated memory block only stores the most recent
   frame: the limit is ``1``. This limit is enough to get statistics using
   :func:`get_stats`.

   Use the :func:`set_traceback_limit` function to change the limit.


.. function:: get_traces()

   Get traces of all memory blocks allocated by Python. Return a dictionary:
   ``{address (int): trace}``, *trace* is a ``(size: int, traceback)`` tuple,
   *traceback* is a tuple of ``(filename: str, lineno: int)`` tuples,
   *filename* and *lineno* can be None.

   Return an empty dictionary if the :mod:`tracemalloc` module is disabled.

   See also :func:`get_object_trace`, :func:`get_stats` and :func:`get_trace`
   functions.


.. function:: set_traceback_limit(nframe: int)

   Set the maximum number of frames stored in the traceback of a trace.

   Storing the traceback of each memory allocation has an important overhead on
   the memory usage. Use the :func:`get_tracemalloc_memory` function to measure
   the overhead and the :func:`add_filter` function to select which memory
   allocations are traced.

   Use the :func:`get_traceback_limit` function to get the current limit.

   The :envvar:`PYTHONTRACEMALLOC` environment variable and the :option:`-X`
   ``tracemalloc=NFRAME`` command line option can be used to set a limit at
   startup.


Filter Functions
----------------

.. function:: add_filter(filter)

   Add a new filter on Python memory allocations, *filter* is a :class:`Filter`
   instance.

   All inclusive filters are applied at once, a memory allocation is only
   ignored if no inclusive filters match its trace. A memory allocation is
   ignored if at least one exclusive filter matchs its trace.

   The new filter is not applied on already collected traces. Use the
   :func:`reset` function to ensure that all traces match the new
   filter.

.. function:: add_inclusive_filter(filename_pattern: str, lineno: int=None, traceback: bool=False)

   Add an inclusive filter: helper for the :func:`add_filter` function creating
   a :class:`Filter` instance with the :attr:`~Filter.include` attribute set to
   ``True``.

   The ``*`` joker character can be used in *filename_pattern* to match any
   substring, including empty string.

   Example: ``tracemalloc.add_inclusive_filter(tracemalloc.__file__)`` only
   includes memory blocks allocated by the :mod:`tracemalloc` module.


.. function:: add_exclusive_filter(filename_pattern: str, lineno: int=None, traceback: bool=False)

   Add an exclusive filter: helper for the :func:`add_filter` function creating
   a :class:`Filter` instance with the :attr:`~Filter.include` attribute set to
   ``False``.

   The ``*`` joker character can be used in *filename_pattern* to match any
   substring, including empty string.

   Example: ``tracemalloc.add_exclusive_filter(tracemalloc.__file__)`` ignores
   memory blocks allocated by the :mod:`tracemalloc` module.


.. function:: clear_filters()

   Clear the filter list.

   See also the :func:`get_filters` function.


.. function:: get_filters()

   Get the filters on Python memory allocations.
   Return a list of :class:`Filter` instances.

   By default, there is one exclusive filter to ignore Python memory blocks
   allocated by the :mod:`tracemalloc` module.

   See also the :func:`clear_filters` function.


Filter
------

.. class:: Filter(include: bool, filename_pattern: str, lineno: int=None, traceback: bool=False)

   Filter to select which memory allocations are traced. Filters can be used to
   reduce the memory usage of the :mod:`tracemalloc` module, which can be read
   using the :func:`get_tracemalloc_memory` function.

   The ``*`` joker character can be used in *filename_pattern* to match any
   substring, including empty string. The ``.pyc`` and ``.pyo`` file extensions
   are replaced with ``.py``. On Windows, the comparison is case insensitive
   and the alternative separator ``/`` is replaced with the standard separator
   ``\``.

   .. attribute:: include

      If *include* is ``True``, only trace memory blocks allocated in a file
      with a name matching :attr:`filename_pattern` at line number
      :attr:`lineno`.

      If *include* is ``False``, ignore memory blocks allocated in a file with
      a name matching :attr:`filename_pattern` at line number
      :attr:`lineno`.

   .. attribute:: lineno

      Line number (``int``) of the filter. If *lineno* is is ``None`` or less
      than ``1``, the filter matches any line number.

   .. attribute:: filename_pattern

      Filename pattern (``str``) of the filter.

   .. attribute:: traceback

      If *traceback* is ``True``, all frames of the traceback are checked. If
      *traceback* is ``False``, only the most recent frame is checked.

      This attribute is ignored if the traceback limit is less than ``2``.
      See the :func:`get_traceback_limit` function.


GroupedStats
------------

.. class:: GroupedStats(timestamp: datetime.datetime, traceback_limit: int, stats: dict, group_by: str, cumulative=False, metrics: dict=None)

   Top of allocated memory blocks grouped by *group_by* as a dictionary.

   The :meth:`Snapshot.top_by` method creates a :class:`GroupedStats` instance.

   .. method:: compare_to(old_stats: GroupedStats=None, sort=True)

      Compare to an older :class:`GroupedStats` instance.

      Return a list of ``(size_diff, size, count_diff, count, key)`` tuples.
      *size_diff*, *size*, *count_diff* and *count* are ``int``. The key type
      depends on the :attr:`group_by` attribute: see the
      :meth:`Snapshot.top_by` method.

      The result is sorted in the biggest to the smallest by
      ``abs(size_diff)``, *size*, ``abs(count_diff)``, *count* and then by
      *key*. Set the *sort* paramter to ``False`` to get the list unsorted and
      use your own sort method.

      ``None`` values are replaced with an empty string for filenames or zero
      for line numbers, because :class:`str` and :class:`int` cannot be
      compared to ``None``.

   .. attribute:: cumulative

      If ``True``, size and count of memory blocks of all frames of the
      traceback of a trace were cumulated, not only the most recent frame.

   .. attribute:: metrics

      Dictionary storing metrics read when the snapshot was created:
      ``{name (str): metric}`` where *metric* type is :class:`Metric`.

   .. attribute:: group_by

      Determine how memory allocations were grouped: see
      :meth:`Snapshot.top_by()` for the available values.

   .. attribute:: stats

      Dictionary ``{key: stats}`` where the *key* type depends on the
      :attr:`group_by` attribute and *stats* is a ``(size: int, count: int)``
      tuple.

      See the :meth:`Snapshot.top_by` method.

   .. attribute:: traceback_limit

      Maximum number of frames stored in the traceback of :attr:`traces`,
      result of the :func:`get_traceback_limit` function.

   .. attribute:: timestamp

      Creation date and time of the snapshot, :class:`datetime.datetime`
      instance.


Metric
------

.. class:: Metric(name: str, value: int, format: str)

   Value of a measure read when a snapshot is taken.

   Example of metrics: Resident Set Size (RSS) memory of a process, memory in
   bytes used by Python, number of Python objects, etc.

   .. attribute:: name

      Name of the metric (``str``).

   .. attribute:: value

      Value of the metric.

   .. attribute:: format

      Format of the metric used to display a metric (``str``, ex: ``'size'``).


Snapshot
--------

.. class:: Snapshot(timestamp: datetime.datetime, traceback_limit: int, stats: dict=None, traces: dict=None, metrics: dict=None)

   Snapshot of statistics and traces of memory blocks allocated by Python.

   .. method:: add_metric(name: str, value: int, format: str)

      Helper to add a :class:`Metric` instance to :attr:`Snapshot.metrics`.
      Return the newly created :class:`Metric` instance.

      Raise an exception if the name is already present in
      :attr:`Snapshot.metrics`.


   .. method:: apply_filters(filters)

      Apply filters on the :attr:`traces` and :attr:`stats` dictionaries,
      *filters* is a list of :class:`Filter` instances.


   .. classmethod:: create(traces=False)

      Take a snapshot of statistics and traces of memory blocks allocated by
      Python.

      If *traces* is ``True``, :func:`get_traces` is called and its result
      is stored in the :attr:`Snapshot.traces` attribute. This attribute
      contains more information than :attr:`Snapshot.stats` and uses more
      memory and more disk space. If *traces* is ``False``,
      :attr:`Snapshot.traces` is set to ``None``.

      Tracebacks of traces are limited to :attr:`traceback_limit` frames. Call
      :func:`set_traceback_limit` before calling :meth:`~Snapshot.create` to
      store more frames.

      The :mod:`tracemalloc` module must be enabled to take a snapshot, see the
      the :func:`enable` function.

   .. method:: dump(filename)

      Write the snapshot into a file.

      Use :meth:`load` to reload the snapshot.


   .. method:: get_metric(name, default=None)

      Get the value of the metric called *name*. Return *default* if the metric
      does not exist.


   .. classmethod:: load(filename, traces=True)

      Load a snapshot from a file.

      If *traces* is ``False``, don't load traces.

      See also :meth:`dump`.


   .. method:: top_by(group_by: str, cumulative: bool=False)

      Compute top statistics grouped by *group_by* as a :class:`GroupedStats`
      instance:

      =====================  ========================  ================================
      group_by               description               key type
      =====================  ========================  ================================
      ``'filename'``         filename                  ``str``
      ``'line'``             filename and line number  ``(filename: str, lineno: int)``
      ``'address'``          memory block address      ``int``
      ``'traceback'``        traceback                 ``(address: int, traceback)``
      =====================  ========================  ================================

      The ``traceback`` type is a tuple of ``(filename: str, lineno: int)``
      tuples, *filename* and *lineno* can be ``None``.

      If *cumulative* is ``True``, cumulate size and count of memory blocks of
      all frames of the traceback of a trace, not only the most recent frame.
      The *cumulative* parameter is set to ``False`` if *group_by* is
      ``'address'``, or if the traceback limit is less than ``2``.


   .. attribute:: metrics

      Dictionary storing metrics read when the snapshot was created:
      ``{name (str): metric}`` where *metric* type is :class:`Metric`.

   .. attribute:: stats

      Statistics on traced Python memory, result of the :func:`get_stats`
      function.

   .. attribute:: traceback_limit

      Maximum number of frames stored in the traceback of :attr:`traces`,
      result of the :func:`get_traceback_limit` function.

   .. attribute:: traces

      Traces of Python memory allocations, result of the :func:`get_traces`
      function, can be ``None``.

   .. attribute:: timestamp

      Creation date and time of the snapshot, :class:`datetime.datetime`
      instance.


Changelog
=========

Development version:

- Rewrite the API to prepare the PEP 454
- Split the project into two parts: pytracemalloc and pytracemalloctext:
  https://github.com/haypo/pytracemalloctext
- Remove the dependency to the glib library: tracemalloc now has its own
  implementation of hash table, based on the cfuhash library

Version 0.9.1 (2013-06-01)

- Add ``PYTRACEMALLOC`` environment variable to trace memory allocation as
  early as possible at Python startup
- Disable the timer while calling its callback to not call the callback
  while it is running
- Fix pythonXXX_track_free_list.patch patches for zombie frames
- Use also MiB, GiB and TiB units to format a size, not only B and KiB

Version 0.9 (2013-05-31)

- Tracking free lists is now the recommended method to patch Python
- Fix code tracking Python free lists and python2.7_track_free_list.patch
- Add patches tracking free lists for Python 2.5.2 and 3.4.

Version 0.8.1 (2013-03-23)

- Fix python2.7.patch and python3.4.patch when Python is not compiled in debug
  mode (without --with-pydebug)
- Fix :class:`DisplayTop`: display "0 B" instead of an empty string if the size is zero
  (ex: trace in user data)
- setup.py automatically detects which patch was applied on Python

Version 0.8 (2013-03-19)

- The top uses colors and displays also the memory usage of the process
- Add :class:`DisplayGarbage` class
- Add :func:`get_process_memory` function
- Support collecting arbitrary user data using a callback:
  :meth:`Snapshot.create`, :class:`DisplayTop` and :class:`TakeSnapshot` have
  has an optional user_data_callback parameter/attribute
- Display the name of the previous snapshot when comparing two snapshots
- Command line (``-m tracemalloc``):

  * Add ``--color`` and ``--no-color`` options
  * ``--include`` and ``--exclude`` command line options can now be specified
    multiple times

- Automatically disable tracemalloc at exit
- Remove :func:`get_source` and :func:`get_stats` functions: they are now
  private

Version 0.7 (2013-03-04)

- First public version


Similar Projects
================

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

