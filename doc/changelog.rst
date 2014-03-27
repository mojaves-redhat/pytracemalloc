Changelog
=========

Version 1.0 (2014-03-05)
------------------------

- Python issue #20616: Add a format() method to tracemalloc.Traceback.
- Python issue #20354: Fix alignment issue in the tracemalloc module on 64-bit
  platforms. Bug seen on 64-bit Linux when using "make profile-opt".
- Fix slicing traces and fix slicing a traceback.

Version 1.0beta1 (2013-12-14)
-----------------------------

- A trace of a memory block can now contain more than 1 frame, a whole
  traceback instead of just the most recent frame
- The malloc hook API has been proposed as the PEP 445. The PEP has been
  accepted and implemented in Python 3.4.
- The tracemalloc module has been proposed as the PEP 454. After many reviews,
  the PEP has been accepted and the code has been merged into Python 3.4.
- The code has been almost fully rewritten from scratch between the version
  0.9.1 and 1.0. The tracemalloc has now a completly different API:

  * DisplayTop, TakeSnapshot and DisplayGarbage classes have been removed
  * Rename enable/disable to start/stop
  * start() now takes an optional nframe parameter which is the maximum number
    of frames stored in a trace of a memory block
  * Raw traces are accesible in Snapshot.traces
  * The get_process_memory() has been removed, but new functions are added
    like get_traced_memory()

- The glib hashtable has been replaced by a builtin hashtable based on the
  libcfu library. The glib dependency has been removed so it should be easier
  to install the module (ex: on Windows).

Version 0.9.1 (2013-06-01)
--------------------------

- Add ``PYTRACEMALLOC`` environment variable to trace memory allocation as
  early as possible at Python startup
- Disable the timer while calling its callback to not call the callback
  while it is running
- Fix pythonXXX_track_free_list.patch patches for zombie frames
- Use also MiB, GiB and TiB units to format a size, not only B and KiB

Version 0.9 (2013-05-31)
------------------------

- Tracking free lists is now the recommended method to patch Python
- Fix code tracking Python free lists and python2.7_track_free_list.patch
- Add patches tracking free lists for Python 2.5.2 and 3.4.

Version 0.8.1 (2013-03-23)
--------------------------

- Fix python2.7.patch and python3.4.patch when Python is not compiled in debug
  mode (without --with-pydebug)
- Fix :class:`DisplayTop`: display "0 B" instead of an empty string if the size is zero
  (ex: trace in user data)
- setup.py automatically detects which patch was applied on Python

Version 0.8 (2013-03-19)
------------------------

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
------------------------

- First public version



