tracemallocqt: GUI to analyze snapshots
=======================================

tracemallocqt is graphical interface to analyze :mod:`tracemalloc` snapshots.
It uses the Qt toolkit.

* `tracemallocqt project at Bitbucket <https://bitbucket.org/haypo/tracemallocqt>`_

Usage
-----

Analyze a single snapshot::

    ./tracemallocqt.py snapshot.pickle

Compare two snapshots::

    ./tracemallocqt.py snapshot1.pickle snapshot2.pickle

You can pass more snapshots and then use the checkbox to select which snapshots
are compared. The snpashots are sorted by the modification time of the files.


Installation
------------

There is no release yet, you have to clone the Mercurial repository::

    hg clone https://bitbucket.org/haypo/tracemallocqt

tracemallocqt works on Python 2 and 3 and requires PyQt4 or PySide.


Screenshots
-----------

Traces grouped by line number
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: tracemallocqt_lineno.png
   :alt: Screenshot of tracemallocqt: traces grouped by line number

Traces grouped by traceback
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. image:: tracemallocqt_traceback.png
   :alt: Screenshot of tracemallocqt: traces grouped by traceback

