API
===

The version of the module is ``tracemalloc.__version__`` (string), example:
``"0.9.1"``.

Functions
---------

.. function:: clear_traces()

   Clear traces of memory blocks allocated by Python.

   See also :func:`stop`.


.. function:: get_object_traceback(obj)

   Get the traceback where the Python object *obj* was allocated.
   Return a :class:`Traceback` instance, or ``None`` if the :mod:`tracemalloc`
   module is not tracing memory allocations or did not trace the allocation of
   the object.

   See also :func:`gc.get_referrers` and :func:`sys.getsizeof` functions.


.. function:: get_traceback_limit()

   Get the maximum number of frames stored in the traceback of a trace.

   The :mod:`tracemalloc` module must be tracing memory allocations to
   get the limit, otherwise an exception is raised.

   The limit is set by the :func:`start` function.


.. function:: get_traced_memory()

   Get the current size and peak size of memory blocks traced by the
   :mod:`tracemalloc` module as a tuple: ``(current: int, peak: int)``.


.. function:: get_tracemalloc_memory()

   Get the memory usage in bytes of the :mod:`tracemalloc` module used to store
   traces of memory blocks.
   Return an :class:`int`.


.. function:: is_tracing()

    ``True`` if the :mod:`tracemalloc` module is tracing Python memory
    allocations, ``False`` otherwise.

    See also :func:`start` and :func:`stop` functions.


.. function:: start(nframe: int=1)

   Start tracing Python memory allocations: install hooks on Python memory
   allocators. Collected tracebacks of traces will be limited to *nframe*
   frames. By default, a trace of a memory block only stores the most recent
   frame: the limit is ``1``. *nframe* must be greater or equal to ``1``.

   Storing more than ``1`` frame is only useful to compute statistics grouped
   by ``'traceback'`` or to compute cumulative statistics: see the
   :meth:`Snapshot.compare_to` and :meth:`Snapshot.statistics` methods.

   Storing more frames increases the memory and CPU overhead of the
   :mod:`tracemalloc` module. Use the :func:`get_tracemalloc_memory` function
   to measure how much memory is used by the :mod:`tracemalloc` module.

   The :envvar:`PYTHONTRACEMALLOC` environment variable
   (``PYTHONTRACEMALLOC=NFRAME``) can be used to start tracing at startup.

   See also :func:`stop`, :func:`is_tracing` and :func:`get_traceback_limit`
   functions.


.. function:: stop()

   Stop tracing Python memory allocations: uninstall hooks on Python memory
   allocators. Also clears all previously collected traces of memory blocks
   allocated by Python.

   Call :func:`take_snapshot` function to take a snapshot of traces before
   clearing them.

   See also :func:`start`, :func:`is_tracing` and :func:`clear_traces`
   functions.


.. function:: take_snapshot()

   Take a snapshot of traces of memory blocks allocated by Python. Return a new
   :class:`Snapshot` instance.

   The snapshot does not include memory blocks allocated before the
   :mod:`tracemalloc` module started to trace memory allocations.

   Tracebacks of traces are limited to :func:`get_traceback_limit` frames. Use
   the *nframe* parameter of the :func:`start` function to store more frames.

   The :mod:`tracemalloc` module must be tracing memory allocations to take a
   snapshot, see the the :func:`start` function.

   See also the :func:`get_object_traceback` function.


Filter
------

.. class:: Filter(inclusive: bool, filename_pattern: str, lineno: int=None, all_frames: bool=False)

   Filter on traces of memory blocks.

   See the :func:`fnmatch.fnmatch` function for the syntax of
   *filename_pattern*. The ``'.pyc'`` and ``'.pyo'`` file extensions are
   replaced with ``'.py'``.

   Examples:

   * ``Filter(True, subprocess.__file__)`` only includes traces of the
     :mod:`subprocess` module
   * ``Filter(False, tracemalloc.__file__)`` excludes traces of the
     :mod:`tracemalloc` module
   * ``Filter(False, "<unknown>")`` excludes empty tracebacks

   .. attribute:: inclusive

      If *inclusive* is ``True`` (include), only trace memory blocks allocated
      in a file with a name matching :attr:`filename_pattern` at line number
      :attr:`lineno`.

      If *inclusive* is ``False`` (exclude), ignore memory blocks allocated in
      a file with a name matching :attr:`filename_pattern` at line number
      :attr:`lineno`.

   .. attribute:: lineno

      Line number (``int``) of the filter. If *lineno* is ``None``, the filter
      matches any line number.

   .. attribute:: filename_pattern

      Filename pattern of the filter (``str``).

   .. attribute:: all_frames

      If *all_frames* is ``True``, all frames of the traceback are checked. If
      *all_frames* is ``False``, only the most recent frame is checked.

      This attribute has no effect if the traceback limit is ``1``.  See the
      :func:`get_traceback_limit` function and :attr:`Snapshot.traceback_limit`
      attribute.


Frame
-----

.. class:: Frame

   Frame of a traceback.

   The :class:`Traceback` class is a sequence of :class:`Frame` instances.

   .. attribute:: filename

      Filename (``str``).

   .. attribute:: lineno

      Line number (``int``).


Snapshot
--------

.. class:: Snapshot

   Snapshot of traces of memory blocks allocated by Python.

   The :func:`take_snapshot` function creates a snapshot instance.

   .. method:: compare_to(old_snapshot: Snapshot, group_by: str, cumulative: bool=False)

      Compute the differences with an old snapshot. Get statistics as a sorted
      list of :class:`StatisticDiff` instances grouped by *group_by*.

      See the :meth:`statistics` method for *group_by* and *cumulative*
      parameters.

      The result is sorted from the biggest to the smallest by: absolute value
      of :attr:`StatisticDiff.size_diff`, :attr:`StatisticDiff.size`, absolute
      value of :attr:`StatisticDiff.count_diff`, :attr:`Statistic.count` and
      then by :attr:`StatisticDiff.traceback`.


   .. method:: dump(filename)

      Write the snapshot into a file.

      Use :meth:`load` to reload the snapshot.


   .. method:: filter_traces(filters)

      Create a new :class:`Snapshot` instance with a filtered :attr:`traces`
      sequence, *filters* is a list of :class:`Filter` instances.  If *filters*
      is an empty list, return a new :class:`Snapshot` instance with a copy of
      the traces.

      All inclusive filters are applied at once, a trace is ignored if no
      inclusive filters match it. A trace is ignored if at least one exclusive
      filter matchs it.


   .. classmethod:: load(filename)

      Load a snapshot from a file.

      See also :meth:`dump`.


   .. method:: statistics(group_by: str, cumulative: bool=False)

      Get statistics as a sorted list of :class:`Statistic` instances grouped
      by *group_by*:

      =====================  ========================
      group_by               description
      =====================  ========================
      ``'filename'``         filename
      ``'lineno'``           filename and line number
      ``'traceback'``        traceback
      =====================  ========================

      If *cumulative* is ``True``, cumulate size and count of memory blocks of
      all frames of the traceback of a trace, not only the most recent frame.
      The cumulative mode can only be used with *group_by* equals to
      ``'filename'`` and ``'lineno'``.

      The result is sorted from the biggest to the smallest by:
      :attr:`Statistic.size`, :attr:`Statistic.count` and then by
      :attr:`Statistic.traceback`.


   .. attribute:: traceback_limit

      Maximum number of frames stored in the traceback of :attr:`traces`:
      result of the :func:`get_traceback_limit` when the snapshot was taken.

   .. attribute:: traces

      Traces of all memory blocks allocated by Python: sequence of
      :class:`Trace` instances.

      The sequence has an undefined order. Use the :meth:`Snapshot.statistics`
      method to get a sorted list of statistics.


Statistic
---------

.. class:: Statistic

   Statistic on memory allocations.

   :func:`Snapshot.statistics` returns a list of :class:`Statistic` instances.

   See also the :class:`StatisticDiff` class.

   .. attribute:: count

      Number of memory blocks (``int``).

   .. attribute:: size

      Total size of memory blocks in bytes (``int``).

   .. attribute:: traceback

      Traceback where the memory block was allocated, :class:`Traceback`
      instance.


StatisticDiff
-------------

.. class:: StatisticDiff

   Statistic difference on memory allocations between an old and a new
   :class:`Snapshot` instance.

   :func:`Snapshot.compare_to` returns a list of :class:`StatisticDiff`
   instances. See also the :class:`Statistic` class.

   .. attribute:: count

      Number of memory blocks in the new snapshot (``int``): ``0`` if
      the memory blocks have been released in the new snapshot.

   .. attribute:: count_diff

      Difference of number of memory blocks between the old and the new
      snapshots (``int``): ``0`` if the memory blocks have been allocated in
      the new snapshot.

   .. attribute:: size

      Total size of memory blocks in bytes in the new snapshot (``int``):
      ``0`` if the memory blocks have been released in the new snapshot.

   .. attribute:: size_diff

      Difference of total size of memory blocks in bytes between the old and
      the new snapshots (``int``): ``0`` if the memory blocks have been
      allocated in the new snapshot.

   .. attribute:: traceback

      Traceback where the memory blocks were allocated, :class:`Traceback`
      instance.


Trace
-----

.. class:: Trace

   Trace of a memory block.

   The :attr:`Snapshot.traces` attribute is a sequence of :class:`Trace`
   instances.

   .. attribute:: size

      Size of the memory block in bytes (``int``).

   .. attribute:: traceback

      Traceback where the memory block was allocated, :class:`Traceback`
      instance.


Traceback
---------

.. class:: Traceback

   Sequence of :class:`Frame` instances sorted from the most recent frame to
   the oldest frame.

   A traceback contains at least ``1`` frame. If the ``tracemalloc`` module
   failed to get a frame, the filename ``"<unknown>"`` at line number ``0`` is
   used.

   When a snapshot is taken, tracebacks of traces are limited to
   :func:`get_traceback_limit` frames. See the :func:`take_snapshot` function.

   The :attr:`Trace.traceback` attribute is an instance of :class:`Traceback`
   instance.



