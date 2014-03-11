#!/usr/bin/env python
"""
Script to trace Python memory allocations when running a Python program.

Usage: python tracemalloc_runner.py /path/to/program [arg1 arg2 ...]
"""
filename_pattern = "/tmp/tracemalloc-%d-%04d.pickle"  # % (pid, counter)
snapshot_delay = 5
nframes = 25

# The first step is to start tracing memory allocations
import tracemalloc
tracemalloc.start(nframes)

import atexit
import gc
import os
import pickle
import runpy
import signal
import sys
import threading
import time

class TakeSnapshot(threading.Thread):
    daemon = True

    def __init__(self):
        threading.Thread.__init__(self)
        self.counter = 1

    def take_snapshot(self):
        filename = (filename_pattern
                    % (os.getpid(), self.counter))
        print("Write snapshot into %s..." % filename)
        gc.collect()
        snapshot = tracemalloc.take_snapshot()
        with open(filename, "wb") as fp:
            # Pickle version 2 can be read by Python 2 and Python 3
            pickle.dump(snapshot, fp, 2)
        snapshot = None
        print("Snapshot written into %s" % filename)
        self.counter += 1

    def run(self):
        self.take_snapshot()
        if hasattr(signal, 'pthread_sigmask'):
            # Available on UNIX with Python 3.3+
            signal.pthread_sigmask(signal.SIG_BLOCK, range(1, signal.NSIG))
        while True:
            time.sleep(snapshot_delay)
            self.take_snapshot()

print("Start thread taking snapshots every %.1f seconds" % snapshot_delay)
print("Filename pattern: %s" % filename_pattern)
thread = TakeSnapshot()
thread.start()
atexit.register(thread.take_snapshot)

del sys.argv[0]
runpy.run_path(sys.argv[0])
