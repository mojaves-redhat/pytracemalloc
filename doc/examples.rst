Examples
========

Display the top 10
------------------

Display the 10 files allocating the most memory::

    import tracemalloc

    tracemalloc.start()

    # ... run your application ...

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)


Example of output of the Python test suite::

    [ Top 10 ]
    <frozen importlib._bootstrap>:716: size=4855 KiB, count=39328, average=126 B
    <frozen importlib._bootstrap>:284: size=521 KiB, count=3199, average=167 B
    /usr/lib/python3.4/collections/__init__.py:368: size=244 KiB, count=2315, average=108 B
    /usr/lib/python3.4/unittest/case.py:381: size=185 KiB, count=779, average=243 B
    /usr/lib/python3.4/unittest/case.py:402: size=154 KiB, count=378, average=416 B
    /usr/lib/python3.4/abc.py:133: size=88.7 KiB, count=347, average=262 B
    <frozen importlib._bootstrap>:1446: size=70.4 KiB, count=911, average=79 B
    <frozen importlib._bootstrap>:1454: size=52.0 KiB, count=25, average=2131 B
    <string>:5: size=49.7 KiB, count=148, average=344 B
    /usr/lib/python3.4/sysconfig.py:411: size=48.0 KiB, count=1, average=48.0 KiB

We can see that Python loaded ``4.8 MiB`` data (bytecode and constants) from
modules and that the :mod:`collections` module allocated ``244 KiB`` to build
:class:`~collections.namedtuple` types.

See :meth:`Snapshot.statistics` for more options.


Compute differences
-------------------

Take two snapshots and display the differences::

    import tracemalloc
    tracemalloc.start()
    # ... start your application ...

    snapshot1 = tracemalloc.take_snapshot()
    # ... call the function leaking memory ...
    snapshot2 = tracemalloc.take_snapshot()

    top_stats = snapshot2.compare_to(snapshot1, 'lineno')

    print("[ Top 10 differences ]")
    for stat in top_stats[:10]:
        print(stat)

Example of output before/after running some tests of the Python test suite::

    [ Top 10 differences ]
    <frozen importlib._bootstrap>:716: size=8173 KiB (+4428 KiB), count=71332 (+39369), average=117 B
    /usr/lib/python3.4/linecache.py:127: size=940 KiB (+940 KiB), count=8106 (+8106), average=119 B
    /usr/lib/python3.4/unittest/case.py:571: size=298 KiB (+298 KiB), count=589 (+589), average=519 B
    <frozen importlib._bootstrap>:284: size=1005 KiB (+166 KiB), count=7423 (+1526), average=139 B
    /usr/lib/python3.4/mimetypes.py:217: size=112 KiB (+112 KiB), count=1334 (+1334), average=86 B
    /usr/lib/python3.4/http/server.py:848: size=96.0 KiB (+96.0 KiB), count=1 (+1), average=96.0 KiB
    /usr/lib/python3.4/inspect.py:1465: size=83.5 KiB (+83.5 KiB), count=109 (+109), average=784 B
    /usr/lib/python3.4/unittest/mock.py:491: size=77.7 KiB (+77.7 KiB), count=143 (+143), average=557 B
    /usr/lib/python3.4/urllib/parse.py:476: size=71.8 KiB (+71.8 KiB), count=969 (+969), average=76 B
    /usr/lib/python3.4/contextlib.py:38: size=67.2 KiB (+67.2 KiB), count=126 (+126), average=546 B

We can see that Python has loaded ``8.2 MiB`` of module data (bytecode and
constants), and that this is ``4.4 MiB`` more than had been loaded before the
tests, when the previous snapshot was taken. Similarly, the :mod:`linecache`
module has cached ``940 KiB`` of Python source code to format tracebacks, all
of it since the previous snapshot.

If the system has little free memory, snapshots can be written on disk using
the :meth:`Snapshot.dump` method to analyze the snapshot offline. Then use the
:meth:`Snapshot.load` method reload the snapshot.


Get the traceback of a memory block
-----------------------------------

Code to display the traceback of the biggest memory block::

    import tracemalloc

    # Store 25 frames
    tracemalloc.start(25)

    # ... run your application ...

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('traceback')

    # pick the biggest memory block
    stat = top_stats[0]
    print("%s memory blocks: %.1f KiB" % (stat.count, stat.size / 1024))
    for line in stat.traceback.format():
        print(line)

Example of output of the Python test suite (traceback limited to 25 frames)::

    903 memory blocks: 870.1 KiB
      File "<frozen importlib._bootstrap>", line 716
      File "<frozen importlib._bootstrap>", line 1036
      File "<frozen importlib._bootstrap>", line 934
      File "<frozen importlib._bootstrap>", line 1068
      File "<frozen importlib._bootstrap>", line 619
      File "<frozen importlib._bootstrap>", line 1581
      File "<frozen importlib._bootstrap>", line 1614
      File "/usr/lib/python3.4/doctest.py", line 101
        import pdb
      File "<frozen importlib._bootstrap>", line 284
      File "<frozen importlib._bootstrap>", line 938
      File "<frozen importlib._bootstrap>", line 1068
      File "<frozen importlib._bootstrap>", line 619
      File "<frozen importlib._bootstrap>", line 1581
      File "<frozen importlib._bootstrap>", line 1614
      File "/usr/lib/python3.4/test/support/__init__.py", line 1728
        import doctest
      File "/usr/lib/python3.4/test/test_pickletools.py", line 21
        support.run_doctest(pickletools)
      File "/usr/lib/python3.4/test/regrtest.py", line 1276
        test_runner()
      File "/usr/lib/python3.4/test/regrtest.py", line 976
        display_failure=not verbose)
      File "/usr/lib/python3.4/test/regrtest.py", line 761
        match_tests=ns.match_tests)
      File "/usr/lib/python3.4/test/regrtest.py", line 1563
        main()
      File "/usr/lib/python3.4/test/__main__.py", line 3
        regrtest.main_in_temp_cwd()
      File "/usr/lib/python3.4/runpy.py", line 73
        exec(code, run_globals)
      File "/usr/lib/python3.4/runpy.py", line 160
        "__main__", fname, loader, pkg_name)

We can see that the most memory was allocated in the :mod:`importlib` module to
load data (bytecode and constants) from modules: ``870 KiB``. The traceback is
where the :mod:`importlib` loaded data most recently: on the ``import pdb``
line of the :mod:`doctest` module. The traceback may change if a new module is
loaded.


Pretty top
----------

Code to display the 10 lines allocating the most memory with a pretty output,
ignoring ``<frozen importlib._bootstrap>`` and ``<unknown>`` files::

    import os
    import tracemalloc

    def display_top(snapshot, group_by='lineno', limit=10):
        snapshot = snapshot.filter_traces((
            tracemalloc.Filter(False, "<frozen importlib._bootstrap>"),
            tracemalloc.Filter(False, "<unknown>"),
        ))
        top_stats = snapshot.statistics(group_by)

        print("Top %s lines" % limit)
        for index, stat in enumerate(top_stats[:limit], 1):
            frame = stat.traceback[0]
            # replace "/path/to/module/file.py" with "module/file.py"
            filename = os.sep.join(frame.filename.split(os.sep)[-2:])
            print("#%s: %s:%s: %.1f KiB"
                  % (index, filename, frame.lineno,
                     stat.size / 1024))

        other = top_stats[limit:]
        if other:
            size = sum(stat.size for stat in other)
            print("%s other: %.1f KiB" % (len(other), size / 1024))
        total = sum(stat.size for stat in top_stats)
        print("Total allocated size: %.1f KiB" % (total / 1024))

    tracemalloc.start()

    # ... run your application ...

    snapshot = tracemalloc.take_snapshot()
    display_top(snapshot, 10)

Example of output of the Python test suite::

    2013-11-08 14:16:58.149320: Top 10 lines
    #1: collections/__init__.py:368: 291.9 KiB
    #2: Lib/doctest.py:1291: 200.2 KiB
    #3: unittest/case.py:571: 160.3 KiB
    #4: Lib/abc.py:133: 99.8 KiB
    #5: urllib/parse.py:476: 71.8 KiB
    #6: <string>:5: 62.7 KiB
    #7: Lib/base64.py:140: 59.8 KiB
    #8: Lib/_weakrefset.py:37: 51.8 KiB
    #9: collections/__init__.py:362: 50.6 KiB
    #10: test/test_site.py:56: 48.0 KiB
    7496 other: 4161.9 KiB
    Total allocated size: 5258.8 KiB

See :meth:`Snapshot.statistics` for more options.


Thread to write snapshots into files every minutes
--------------------------------------------------

Create a daemon thread writing snapshots every minutes into
``/tmp/tracemalloc-PPP-CCCC.pickle`` where ``PPP`` is the identifier of the
process and ``CCCC`` is a counter::

    import pickle, gc, os, signal, threading, time, tracemalloc

    class TakeSnapshot(threading.Thread):
        daemon = True

        def run(self):
            if hasattr(signal, 'pthread_sigmask'):
                # Available on UNIX with Python 3.3+
                signal.pthread_sigmask(signal.SIG_BLOCK, range(1, signal.NSIG))
            counter = 1
            while True:
                time.sleep(60)
                filename = ("/tmp/tracemalloc-%d-%04d.pickle"
                            % (os.getpid(), counter))
                print("Write snapshot into %s..." % filename)
                gc.collect()
                snapshot = tracemalloc.take_snapshot()
                with open(filename, "wb") as fp:
                    # Pickle version 2 can be read by Python 2 and Python 3
                    pickle.dump(snapshot, fp, 2)
                snapshot = None
                print("Snapshot written into %s" % filename)
                counter += 1

    # save 25 frames
    tracemalloc.start(25)
    TakeSnapshot().start()

