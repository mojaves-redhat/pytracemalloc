import contextlib
import datetime
import os
import sys
import tracemalloc
import unittest
from unittest.mock import patch
from test.script_helper import assert_python_ok
from test import support
try:
    import threading
except ImportError:
    threading = None

PYTHON34 = (sys.version_info >= (3, 4))
EMPTY_STRING_SIZE = sys.getsizeof(b'')

def get_frames(nframe, lineno_delta):
    frames = []
    frame = sys._getframe(1)
    for index in range(nframe):
        code = frame.f_code
        lineno = frame.f_lineno + lineno_delta
        frames.append((code.co_filename, lineno))
        lineno_delta = 0
        frame = frame.f_back
        if frame is None:
            break
    return tuple(frames)

def allocate_bytes(size):
    nframe = tracemalloc.get_traceback_limit()
    bytes_len = (size - EMPTY_STRING_SIZE)
    frames = get_frames(nframe, 1)
    data = b'x' * bytes_len
    return data, frames

def create_snapshots():
    traceback_limit = 2

    timestamp = datetime.datetime(2013, 9, 12, 15, 16, 17)
    stats = {
        'a.py': {2: (30, 3),
                 5: (2, 1)},
        'b.py': {1: (66, 1)},
        None: {None: (7, 1)},
    }
    traces = {
        0x10001: (10, (('a.py', 2), ('b.py', 4))),
        0x10002: (10, (('a.py', 2), ('b.py', 4))),
        0x10003: (10, (('a.py', 2), ('b.py', 4))),

        0x20001: (2, (('a.py', 5), ('b.py', 4))),

        0x30001: (66, (('b.py', 1),)),

        0x40001: (7, ((None, None),)),
    }
    snapshot = tracemalloc.Snapshot(timestamp, traceback_limit,
                                    stats, traces)
    snapshot.add_metric('process_memory.rss', 1024, 'size')
    snapshot.add_metric('tracemalloc.size', 100, 'size')
    snapshot.add_metric('my_data', 8, 'int')

    timestamp2 = datetime.datetime(2013, 9, 12, 15, 16, 50)
    stats2 = {
        'a.py': {2: (30, 3),
                 5: (5002, 2)},
        'c.py': {578: (400, 1)},
    }
    traces2 = {
        0x10001: (10, (('a.py', 2), ('b.py', 4))),
        0x10002: (10, (('a.py', 2), ('b.py', 4))),
        0x10003: (10, (('a.py', 2), ('b.py', 4))),

        0x20001: (2, (('a.py', 5), ('b.py', 4))),
        0x20002: (5000, (('a.py', 5), ('b.py', 4))),

        0x30001: (400, (('c.py', 30),)),
    }
    snapshot2 = tracemalloc.Snapshot(timestamp2, traceback_limit,
                                     stats2, traces2)
    snapshot2.add_metric('process_memory.rss', 1500, 'size')
    snapshot2.add_metric('tracemalloc.size', 200, 'size')
    snapshot2.add_metric('my_data', 10, 'int')

    return (snapshot, snapshot2)


class TestTracemallocEnabled(unittest.TestCase):
    def setUp(self):
        if tracemalloc.is_enabled():
            self.skipTest("tracemalloc must be disabled before the test")

        tracemalloc.clear_filters()
        tracemalloc.add_exclusive_filter(tracemalloc.__file__)
        tracemalloc.set_traceback_limit(1)
        tracemalloc.enable()

    def tearDown(self):
        tracemalloc.disable()
        tracemalloc.clear_filters()

    def test_get_tracemalloc_memory(self):
        data = [allocate_bytes(123) for count in range(1000)]
        size, free = tracemalloc.get_tracemalloc_memory()
        self.assertGreaterEqual(size, 0)
        self.assertGreaterEqual(free, 0)
        self.assertGreater(size, free)

        tracemalloc.reset()
        size2, free2 = tracemalloc.get_tracemalloc_memory()
        self.assertLessEqual(size2, size)

    def test_get_trace(self):
        tracemalloc.reset()
        obj_size = 12345
        obj, obj_frames = allocate_bytes(obj_size)
        address = tracemalloc.get_object_address(obj)
        trace = tracemalloc.get_trace(address)
        self.assertIsInstance(trace, tuple)
        size, traceback = trace
        self.assertEqual(size, obj_size)
        self.assertEqual(traceback, obj_frames)

    def test_get_object_trace(self):
        tracemalloc.reset()
        obj_size = 12345
        obj, obj_frames = allocate_bytes(obj_size)
        trace = tracemalloc.get_object_trace(obj)
        self.assertIsInstance(trace, tuple)
        size, traceback = trace
        self.assertEqual(size, obj_size)
        self.assertEqual(traceback, obj_frames)

    def test_set_traceback_limit(self):
        obj_size = 10

        nframe = tracemalloc.get_traceback_limit()
        self.addCleanup(tracemalloc.set_traceback_limit, nframe)

        self.assertRaises(ValueError, tracemalloc.set_traceback_limit, -1)

        tracemalloc.reset()
        tracemalloc.set_traceback_limit(0)
        obj, obj_frames = allocate_bytes(obj_size)
        trace = tracemalloc.get_object_trace(obj)
        size, traceback = trace
        self.assertEqual(len(traceback), 0)
        self.assertEqual(traceback, obj_frames)

        tracemalloc.reset()
        tracemalloc.set_traceback_limit(1)
        obj, obj_frames = allocate_bytes(obj_size)
        trace = tracemalloc.get_object_trace(obj)
        size, traceback = trace
        self.assertEqual(len(traceback), 1)
        self.assertEqual(traceback, obj_frames)

        tracemalloc.reset()
        tracemalloc.set_traceback_limit(10)
        obj2, obj2_frames = allocate_bytes(obj_size)
        trace = tracemalloc.get_object_trace(obj2)
        size, traceback = trace
        self.assertEqual(len(traceback), 10)
        self.assertEqual(traceback, obj2_frames)

    def test_get_traces(self):
        tracemalloc.reset()
        obj_size = 12345
        obj, obj_frames = allocate_bytes(obj_size)

        traces = tracemalloc.get_traces()
        address = tracemalloc.get_object_address(obj)
        self.assertIn(address, traces)
        trace = traces[address]

        self.assertIsInstance(trace, tuple)
        size, traceback = trace
        self.assertEqual(size, obj_size)
        self.assertEqual(traceback, obj_frames)

    def test_get_traces_intern_traceback(self):
        # dummy wrappers to get more useful and identical frames in the traceback
        def allocate_bytes2(size):
            return allocate_bytes(size)
        def allocate_bytes3(size):
            return allocate_bytes2(size)
        def allocate_bytes4(size):
            return allocate_bytes3(size)

        # Ensure that two identical tracebacks are not duplicated
        tracemalloc.reset()
        tracemalloc.set_traceback_limit(4)
        obj_size = 123
        obj1, obj1_frames = allocate_bytes4(obj_size)
        obj2, obj2_frames = allocate_bytes4(obj_size)

        traces = tracemalloc.get_traces()

        address1 = tracemalloc.get_object_address(obj1)
        address2 = tracemalloc.get_object_address(obj2)
        trace1 = traces[address1]
        trace2 = traces[address2]
        size1, traceback1 = trace1
        size2, traceback2 = trace2
        self.assertEqual(traceback2, traceback1)
        self.assertIs(traceback2, traceback1)

    def test_get_traced_memory(self):
        # get the allocation location to filter allocations
        size = 12345
        obj, frames = allocate_bytes(size)
        filename, lineno = frames[0]
        tracemalloc.add_inclusive_filter(filename, lineno)

        # allocate one object
        tracemalloc.reset()
        obj, obj_frames = allocate_bytes(size)
        self.assertEqual(tracemalloc.get_traced_memory(), (size, size))

        # destroy the object
        obj = None
        self.assertEqual(tracemalloc.get_traced_memory(), (0, size))

        # reset() must reset traced memory counters
        tracemalloc.reset()
        self.assertEqual(tracemalloc.get_traced_memory(), (0, 0))

        # allocate another object
        tracemalloc.reset()
        obj, obj_frames = allocate_bytes(size)
        self.assertEqual(tracemalloc.get_traced_memory(), (size, size))

        # disable() rests also traced memory counters
        tracemalloc.disable()
        self.assertEqual(tracemalloc.get_traced_memory(), (0, 0))

    def test_get_stats(self):
        tracemalloc.reset()
        total_size = 0
        total_count = 0
        objs = []
        for index in range(5):
            size = 1234
            obj, obj_frames = allocate_bytes(size)
            objs.append(obj)
            total_size += size
            total_count += 1

            stats = tracemalloc.get_stats()
            for filename, line_stats in stats.items():
                for lineno, line_stat in line_stats.items():
                    # stats can be huge, one test per file should be enough
                    self.assertIsInstance(line_stat, tuple)
                    size, count = line_stat
                    self.assertIsInstance(size, int)
                    self.assertIsInstance(count, int)
                    self.assertGreaterEqual(size, 0)
                    self.assertGreaterEqual(count, 1)
                    break

            filename, lineno = obj_frames[0]
            self.assertIn(filename, stats)
            line_stats = stats[filename]
            self.assertIn(lineno, line_stats)
            size, count = line_stats[lineno]
            self.assertEqual(size, total_size)
            self.assertEqual(count, total_count)

    def test_reset(self):
        tracemalloc.reset()
        obj_size = 1234
        obj, obj_frames = allocate_bytes(obj_size)

        stats = tracemalloc.get_stats()
        filename, lineno = obj_frames[0]
        line_stats = stats[filename][lineno]
        size, count = line_stats
        self.assertEqual(size, obj_size)
        self.assertEqual(count, 1)

        tracemalloc.reset()
        stats2 = tracemalloc.get_stats()
        self.assertNotIn(lineno, stats2[filename])

    def test_is_enabled(self):
        tracemalloc.reset()
        tracemalloc.disable()
        self.assertFalse(tracemalloc.is_enabled())

        tracemalloc.enable()
        self.assertTrue(tracemalloc.is_enabled())

    def test_snapshot(self):
        def compute_nstats(stats):
            return sum(len(line_stats)
                       for filename, line_stats in stats.items())

        tracemalloc.reset()
        obj, source = allocate_bytes(123)

        stats1 = tracemalloc.get_stats()
        nstat1 = compute_nstats(stats1)

        # take a snapshot with traces and a metric
        snapshot = tracemalloc.Snapshot.create(traces=True)
        metric = snapshot.add_metric('metric', 456, 'format')
        nstat2 = compute_nstats(snapshot.stats)
        self.assertGreaterEqual(nstat2, nstat1)
        self.assertEqual(snapshot.metrics, {'metric': metric})

        # write on disk
        snapshot.dump(support.TESTFN)
        self.addCleanup(support.unlink, support.TESTFN)

        # load with traces
        snapshot2 = tracemalloc.Snapshot.load(support.TESTFN)
        self.assertEqual(snapshot2.timestamp, snapshot.timestamp)
        self.assertEqual(snapshot2.traces, snapshot.traces)
        self.assertEqual(snapshot2.stats, snapshot.stats)
        self.assertEqual(snapshot2.metrics, snapshot.metrics)

        # load without traces
        snapshot2 = tracemalloc.Snapshot.create()
        self.assertIsNone(snapshot2.traces)

        # tracemalloc must be enabled to take a snapshot
        tracemalloc.disable()
        with self.assertRaises(RuntimeError) as cm:
            tracemalloc.Snapshot.create()
        self.assertEqual(str(cm.exception),
                         "the tracemalloc module must be enabled "
                         "to take a snapshot")

    def test_snapshot_metrics(self):
        now = datetime.datetime.now()
        snapshot = tracemalloc.Snapshot(now, 123, 1, {})

        metric = snapshot.add_metric('key', 3, 'size')
        self.assertRaises(ValueError, snapshot.add_metric, 'key', 4, 'size')
        self.assertEqual(snapshot.get_metric('key'), 3)
        self.assertIn('key', snapshot.metrics)
        self.assertIs(metric, snapshot.metrics['key'])

    def test_filters(self):
        tracemalloc.clear_filters()
        tracemalloc.add_exclusive_filter(tracemalloc.__file__)
        # test multiple inclusive filters
        tracemalloc.add_inclusive_filter('should never match 1')
        tracemalloc.add_inclusive_filter('should never match 2')
        tracemalloc.add_inclusive_filter(__file__)
        tracemalloc.reset()
        size = 1000
        obj, obj_frames = allocate_bytes(size)
        trace = tracemalloc.get_object_trace(obj)
        self.assertIsNotNone(trace)

        # test exclusive filter, based on previous filters
        filename, lineno = obj_frames[0]
        tracemalloc.add_exclusive_filter(filename, lineno)
        tracemalloc.reset()
        obj, obj_frames = allocate_bytes(size)
        trace = tracemalloc.get_object_trace(obj)
        self.assertIsNone(trace)

    def fork_child(self):
        enabled = tracemalloc.is_enabled()
        if not enabled:
            return 2

        obj_size = 12345
        obj, obj_frames = allocate_bytes(obj_size)
        trace = tracemalloc.get_object_trace(obj)
        if trace is None:
            return 3

        # everything is fine
        return 0

    @unittest.skipUnless(hasattr(os, 'fork'), 'need os.fork()')
    def test_fork(self):
        # check that tracemalloc is still working after fork
        pid = os.fork()
        if not pid:
            # child
            exitcode = 1
            try:
                exitcode = self.fork_child()
            finally:
                os._exit(exitcode)
        else:
            pid2, status = os.waitpid(pid, 0)
            self.assertTrue(os.WIFEXITED(status))
            exitcode = os.WEXITSTATUS(status)
            self.assertEqual(exitcode, 0)


class TestSnapshot(unittest.TestCase):
    def test_create_snapshot(self):
        stats = {'a.py': {1: (5, 1)}}
        traces = {0x123: (5, ('a.py', 1))}

        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(tracemalloc, 'is_enabled', return_value=True))
            stack.enter_context(patch.object(tracemalloc, 'get_traceback_limit', return_value=5))
            stack.enter_context(patch.object(tracemalloc, 'get_stats', return_value=stats))
            stack.enter_context(patch.object(tracemalloc, 'get_traces', return_value=traces))

            snapshot = tracemalloc.Snapshot.create(traces=True)
            self.assertIsInstance(snapshot.timestamp, datetime.datetime)
            self.assertEqual(snapshot.traceback_limit, 5)
            self.assertEqual(snapshot.stats, stats)
            self.assertEqual(snapshot.traces, traces)
            self.assertEqual(snapshot.metrics, {})

    def test_apply_filters(self):
        snapshot, snapshot2 = create_snapshots()
        filter1 = tracemalloc.Filter(False, "b.py")
        filter2 = tracemalloc.Filter(True, "a.py", 2)
        filter3 = tracemalloc.Filter(True, "a.py", 5)

        snapshot.apply_filters((filter1,))
        self.assertEqual(snapshot.stats, {
            'a.py': {2: (30, 3),
                     5: (2, 1)},
            None: {None: (7, 1)},
        })
        self.assertEqual(snapshot.traces, {
            0x10001: (10, (('a.py', 2), ('b.py', 4))),
            0x10002: (10, (('a.py', 2), ('b.py', 4))),
            0x10003: (10, (('a.py', 2), ('b.py', 4))),
            0x20001: (2, (('a.py', 5), ('b.py', 4))),
            0x40001: (7, ((None, None),)),
        })

        snapshot.apply_filters((filter2, filter3))
        self.assertEqual(snapshot.stats, {
            'a.py': {2: (30, 3),
                     5: (2, 1)},
        })
        self.assertEqual(snapshot.traces, {
            0x10001: (10, (('a.py', 2), ('b.py', 4))),
            0x10002: (10, (('a.py', 2), ('b.py', 4))),
            0x10003: (10, (('a.py', 2), ('b.py', 4))),
            0x20001: (2, (('a.py', 5), ('b.py', 4))),
        })


    def test_snapshot_top_by_attr(self):
        # check that snapshot attributes are copied
        snapshot, snapshot2 = create_snapshots()
        top_stats = snapshot.top_by('line')
        self.assertEqual(top_stats.group_by, 'line')
        self.assertEqual(top_stats.timestamp, snapshot.timestamp)
        self.assertEqual(top_stats.traceback_limit, snapshot.traceback_limit)
        self.assertEqual(top_stats.cumulative, False)
        self.assertEqual(top_stats.metrics, snapshot.metrics)

    def test_snapshot_top_by_line(self):
        snapshot, snapshot2 = create_snapshots()

        # stats per file and line
        top_stats = snapshot.top_by('line')
        self.assertEqual(top_stats.stats, {
            ('a.py', 2): (30, 3),
            ('a.py', 5): (2, 1),
            ('b.py', 1): (66, 1),
            (None, None): (7, 1),
        })
        self.assertEqual(top_stats.group_by, 'line')

        # stats per file and line (2)
        top_stats2 = snapshot2.top_by('line')
        self.assertEqual(top_stats2.stats, {
            ('a.py', 2): (30, 3),
            ('a.py', 5): (5002, 2),
            ('c.py', 578): (400, 1),
        })

        # stats diff per file and line
        differences = top_stats2.compare_to(top_stats)
        self.assertIsInstance(differences, list)
        self.assertEqual(differences, [
            (5000, 5002, 1, 2, ('a.py', 5)),
            (400, 400, 1, 1, ('c.py', 578)),
            (-66, 0, -1, 0, ('b.py', 1)),
            (-7, 0, -1, 0, ('', 0)),
            (0, 30, 0, 3, ('a.py', 2)),
        ])

    def test_snapshot_top_by_file(self):
        snapshot, snapshot2 = create_snapshots()

        # stats per file
        top_stats = snapshot.top_by('filename')
        self.assertEqual(top_stats.stats, {
            'a.py': (32, 4),
            'b.py': (66, 1),
            None: (7, 1),
        })
        self.assertEqual(top_stats.group_by, 'filename')

        # stats per file (2)
        top_stats2 = snapshot2.top_by('filename')
        self.assertEqual(top_stats2.stats, {
            'a.py': (5032, 5),
            'c.py': (400, 1),
        })

        # stats diff per file
        differences = top_stats2.compare_to(top_stats)
        self.assertIsInstance(differences, list)
        self.assertEqual(differences, [
            (5000, 5032, 1, 5, 'a.py'),
            (400, 400, 1, 1, 'c.py'),
            (-66, 0, -1, 0, 'b.py'),
            (-7, 0, -1, 0, ''),
        ])

    def test_snapshot_top_by_address(self):
        snapshot, snapshot2 = create_snapshots()

        # stats per address
        top_stats = snapshot.top_by('address')
        self.assertEqual(top_stats.stats, {
            0x10001: (10, 1),
            0x10002: (10, 1),
            0x10003: (10, 1),
            0x20001: (2, 1),
            0x30001: (66, 1),
            0x40001: (7, 1),
        })
        self.assertEqual(top_stats.group_by, 'address')

        # stats per address (2)
        top_stats2 = snapshot2.top_by('address')
        self.assertEqual(top_stats2.stats, {
            0x10001: (10, 1),
            0x10002: (10, 1),
            0x10003: (10, 1),
            0x20001: (2, 1),
            0x20002: (5000, 1),
            0x30001: (400, 1),
        })

        # diff
        differences = top_stats2.compare_to(top_stats)
        self.assertIsInstance(differences, list)
        self.assertEqual(differences, [
            (5000, 5000, 1, 1, 0x20002),
            (334, 400, 0, 1, 0x30001),
            (-7, 0, -1, 0, 0x40001),
            (0, 10, 0, 1, 0x10003),
            (0, 10, 0, 1, 0x10002),
            (0, 10, 0, 1, 0x10001),
            (0, 2, 0, 1, 0x20001),
        ])

        with self.assertRaises(ValueError) as cm:
            snapshot.traces = None
            snapshot.top_by('address')
        self.assertEqual(str(cm.exception), "need traces")

    def test_snapshot_top_cumulative(self):
        snapshot, snapshot2 = create_snapshots()

        # per file
        top_stats = snapshot.top_by('filename', True)
        self.assertEqual(top_stats.stats, {
            'a.py': (32, 4),
            'b.py': (98, 5),
            None: (7, 1),
        })
        self.assertEqual(top_stats.group_by, 'filename')

        # per line
        top_stats2 = snapshot.top_by('line', True)
        self.assertEqual(top_stats2.stats, {
            ('a.py', 2): (30, 3),
            ('a.py', 5): (2, 1),
            ('b.py', 1): (66, 1),
            ('b.py', 4): (32, 4),
            (None, None): (7, 1),
        })
        self.assertEqual(top_stats2.group_by, 'line')

        # need traces
        with self.assertRaises(ValueError) as cm:
            snapshot.traces = None
            snapshot.top_by('filename', True)
        self.assertEqual(str(cm.exception), "need traces")


class TestFilters(unittest.TestCase):
    maxDiff = 2048
    def test_add_clear_filter(self):
        old_filters = tracemalloc.get_filters()
        try:
            # test add_filter()
            tracemalloc.clear_filters()
            tracemalloc.add_filter(tracemalloc.Filter(True, "abc", 3))
            tracemalloc.add_filter(tracemalloc.Filter(False, "12345", 0))
            self.assertEqual(tracemalloc.get_filters(),
                             [tracemalloc.Filter(True, 'abc', 3, False),
                              tracemalloc.Filter(False, '12345', None, False)])

            # test add_inclusive_filter(), add_exclusive_filter()
            tracemalloc.clear_filters()
            tracemalloc.add_inclusive_filter("abc", 3)
            tracemalloc.add_exclusive_filter("12345", 0)
            tracemalloc.add_exclusive_filter("6789", None)
            tracemalloc.add_exclusive_filter("def#", 55)
            tracemalloc.add_exclusive_filter("trace", 123, True)
            self.assertEqual(tracemalloc.get_filters(),
                             [tracemalloc.Filter(True, 'abc', 3, False),
                              tracemalloc.Filter(False, '12345', None, False),
                              tracemalloc.Filter(False, '6789', None, False),
                              tracemalloc.Filter(False, "def#", 55, False),
                              tracemalloc.Filter(False, "trace", 123, True)])

            # test filename normalization (.pyc/.pyo)
            tracemalloc.clear_filters()
            tracemalloc.add_inclusive_filter("abc.pyc")
            tracemalloc.add_inclusive_filter("name.pyo")
            self.assertEqual(tracemalloc.get_filters(),
                             [tracemalloc.Filter(True, 'abc.py', None, False),
                              tracemalloc.Filter(True, 'name.py', None, False) ])

            # test filename normalization ('*' joker character)
            tracemalloc.clear_filters()
            tracemalloc.add_inclusive_filter('a****b')
            tracemalloc.add_inclusive_filter('***x****')
            tracemalloc.add_inclusive_filter('1*2**3***4')
            self.assertEqual(tracemalloc.get_filters(),
                             [tracemalloc.Filter(True, 'a*b', None, False),
                              tracemalloc.Filter(True, '*x*', None, False),
                              tracemalloc.Filter(True, '1*2*3*4', None, False)])

            # ignore duplicated filters
            tracemalloc.clear_filters()
            tracemalloc.add_inclusive_filter('a.py')
            tracemalloc.add_inclusive_filter('a.py', 5)
            tracemalloc.add_inclusive_filter('a.py')
            tracemalloc.add_inclusive_filter('a.py', 5)
            tracemalloc.add_exclusive_filter('b.py')
            tracemalloc.add_exclusive_filter('b.py', 10)
            tracemalloc.add_exclusive_filter('b.py')
            tracemalloc.add_exclusive_filter('b.py', 10, True)
            self.assertEqual(tracemalloc.get_filters(),
                             [tracemalloc.Filter(True, 'a.py', None, False),
                              tracemalloc.Filter(True, 'a.py', 5, False),
                              tracemalloc.Filter(False, 'b.py', None, False),
                              tracemalloc.Filter(False, 'b.py', 10, False),
                              tracemalloc.Filter(False, 'b.py', 10, True)])

            # Windows: test filename normalization (lower case, slash)
            if os.name == "nt":
                tracemalloc.clear_filters()
                tracemalloc.add_inclusive_filter("aBcD\xC9")
                tracemalloc.add_inclusive_filter("MODule.PYc")
                tracemalloc.add_inclusive_filter(r"path/to\file")
                self.assertEqual(tracemalloc.get_filters(),
                                 [tracemalloc.Filter(True, 'abcd\xe9', None, False),
                                  tracemalloc.Filter(True, 'module.py', None, False),
                                  tracemalloc.Filter(True, r'path\to\file', None, False)])

            # test clear_filters()
            tracemalloc.clear_filters()
            self.assertEqual(tracemalloc.get_filters(), [])
        finally:
            tracemalloc.clear_filters()
            for trace_filter in old_filters:
                tracemalloc.add_filter(trace_filter)

    def test_filter_attributes(self):
        # test default values
        f = tracemalloc.Filter(True, "abc")
        self.assertEqual(f.include, True)
        self.assertEqual(f.filename_pattern, "abc")
        self.assertIsNone(f.lineno)
        self.assertEqual(f.traceback, False)

        # test custom values
        f = tracemalloc.Filter(False, "test.py", 123, True)
        self.assertEqual(f.include, False)
        self.assertEqual(f.filename_pattern, "test.py")
        self.assertEqual(f.lineno, 123)
        self.assertEqual(f.traceback, True)

        # attributes are read-only
        self.assertRaises(AttributeError, setattr, f, "include", True)
        self.assertRaises(AttributeError, setattr, f, "filename_pattern", "abc")
        self.assertRaises(AttributeError, setattr, f, "lineno", 5)
        self.assertRaises(AttributeError, setattr, f, "traceback", ())

    def test_filter_match(self):
        f = tracemalloc.Filter(True, "abc")
        self.assertTrue(f._match("abc", 5))
        self.assertTrue(f._match("abc", None))
        self.assertFalse(f._match("12356", 5))
        self.assertFalse(f._match("12356", None))
        self.assertFalse(f._match(None, 5))
        self.assertFalse(f._match(None, None))

        f = tracemalloc.Filter(False, "abc")
        self.assertFalse(f._match("abc", 5))
        self.assertFalse(f._match("abc", None))
        self.assertTrue(f._match("12356", 5))
        self.assertTrue(f._match("12356", None))
        self.assertTrue(f._match(None, 5))
        self.assertTrue(f._match(None, None))

        f = tracemalloc.Filter(True, "abc", 5)
        self.assertTrue(f._match("abc", 5))
        self.assertFalse(f._match("abc", 10))
        self.assertFalse(f._match("abc", None))
        self.assertFalse(f._match("12356", 5))
        self.assertFalse(f._match("12356", 10))
        self.assertFalse(f._match("12356", None))
        self.assertFalse(f._match(None, 5))
        self.assertFalse(f._match(None, 10))
        self.assertFalse(f._match(None, None))

        f = tracemalloc.Filter(False, "abc", 5)
        self.assertFalse(f._match("abc", 5))
        self.assertTrue(f._match("abc", 10))
        self.assertTrue(f._match("abc", None))
        self.assertTrue(f._match("12356", 5))
        self.assertTrue(f._match("12356", 10))
        self.assertTrue(f._match("12356", None))
        self.assertTrue(f._match(None, 5))
        self.assertTrue(f._match(None, 10))
        self.assertTrue(f._match(None, None))

    def test_filter_match_filename(self):
        f = tracemalloc.Filter(True, "abc")
        self.assertTrue(f._match_filename("abc"))
        self.assertFalse(f._match_filename("12356"))
        self.assertFalse(f._match_filename(None))

        f = tracemalloc.Filter(False, "abc")
        self.assertFalse(f._match_filename("abc"))
        self.assertTrue(f._match_filename("12356"))
        self.assertTrue(f._match_filename(None))

        f = tracemalloc.Filter(True, "abc")
        self.assertTrue(f._match_filename("abc"))
        self.assertFalse(f._match_filename("12356"))
        self.assertFalse(f._match_filename(None))

        f = tracemalloc.Filter(False, "abc")
        self.assertFalse(f._match_filename("abc"))
        self.assertTrue(f._match_filename("12356"))
        self.assertTrue(f._match_filename(None))

    def test_filter_match_filename_joker(self):
        def fnmatch(filename, pattern):
            filter = tracemalloc.Filter(True, pattern)
            return filter._match_filename(filename)

        # empty string
        self.assertFalse(fnmatch('abc', ''))
        self.assertFalse(fnmatch('', 'abc'))
        self.assertTrue(fnmatch('', ''))
        self.assertTrue(fnmatch('', '*'))

        # no *
        self.assertTrue(fnmatch('abc', 'abc'))
        self.assertFalse(fnmatch('abc', 'abcd'))
        self.assertFalse(fnmatch('abc', 'def'))

        # a*
        self.assertTrue(fnmatch('abc', 'a*'))
        self.assertTrue(fnmatch('abc', 'abc*'))
        self.assertFalse(fnmatch('abc', 'b*'))
        self.assertFalse(fnmatch('abc', 'abcd*'))

        # a*b
        self.assertTrue(fnmatch('abc', 'a*c'))
        self.assertTrue(fnmatch('abcdcx', 'a*cx'))
        self.assertFalse(fnmatch('abb', 'a*c'))
        self.assertFalse(fnmatch('abcdce', 'a*cx'))

        # a*b*c
        self.assertTrue(fnmatch('abcde', 'a*c*e'))
        self.assertTrue(fnmatch('abcbdefeg', 'a*bd*eg'))
        self.assertFalse(fnmatch('abcdd', 'a*c*e'))
        self.assertFalse(fnmatch('abcbdefef', 'a*bd*eg'))

        # replace .pyc and .pyo suffix with .py
        self.assertTrue(fnmatch('a.pyc', 'a.py'))
        self.assertTrue(fnmatch('a.pyo', 'a.py'))
        self.assertTrue(fnmatch('a.py', 'a.pyc'))
        self.assertTrue(fnmatch('a.py', 'a.pyo'))

        if os.name == 'nt':
            # case insensitive
            self.assertTrue(fnmatch('aBC', 'ABc'))
            self.assertTrue(fnmatch('aBcDe', 'Ab*dE'))

            self.assertTrue(fnmatch('a.pyc', 'a.PY'))
            self.assertTrue(fnmatch('a.PYO', 'a.py'))
            self.assertTrue(fnmatch('a.py', 'a.PYC'))
            self.assertTrue(fnmatch('a.PY', 'a.pyo'))
        else:
            # case sensitive
            self.assertFalse(fnmatch('aBC', 'ABc'))
            self.assertFalse(fnmatch('aBcDe', 'Ab*dE'))

            self.assertFalse(fnmatch('a.pyc', 'a.PY'))
            self.assertFalse(fnmatch('a.PYO', 'a.py'))
            self.assertFalse(fnmatch('a.py', 'a.PYC'))
            self.assertFalse(fnmatch('a.PY', 'a.pyo'))

        if os.name == 'nt':
            # normalize alternate separator "/" to the standard separator "\"
            self.assertTrue(fnmatch(r'a/b', r'a\b'))
            self.assertTrue(fnmatch(r'a\b', r'a/b'))
            self.assertTrue(fnmatch(r'a/b\c', r'a\b/c'))
            self.assertTrue(fnmatch(r'a/b/c', r'a\b\c'))
        else:
            # there is no alternate separator
            self.assertFalse(fnmatch(r'a/b', r'a\b'))
            self.assertFalse(fnmatch(r'a\b', r'a/b'))
            self.assertFalse(fnmatch(r'a/b\c', r'a\b/c'))
            self.assertFalse(fnmatch(r'a/b/c', r'a\b\c'))

        # a******b
        N = 10 ** 6
        self.assertTrue (fnmatch('a' * N,       '*' * N))
        self.assertTrue (fnmatch('a' * N + 'c', '*' * N))
        self.assertTrue (fnmatch('a' * N,       'a' + '*' * N + 'a'))
        self.assertTrue (fnmatch('a' * N + 'b', 'a' + '*' * N + 'b'))
        self.assertFalse(fnmatch('a' * N + 'b', 'a' + '*' * N + 'c'))

        # a*a*a*a*
        self.assertTrue(fnmatch('a' * 10, 'a*' * 10))
        self.assertFalse(fnmatch('a' * 10, 'a*' * 10 + 'b'))
        with self.assertRaises(ValueError) as cm:
            fnmatch('abc', 'a*' * 101)
        self.assertEqual(str(cm.exception),
                         "too many joker characters in the filename pattern")

    def test_filter_match_trace(self):
        t1 = (("a.py", 2), ("b.py", 3))
        t2 = (("b.py", 4), ("b.py", 5))

        f = tracemalloc.Filter(True, "b.py", traceback=True)
        self.assertTrue(f._match_traceback(t1))
        self.assertTrue(f._match_traceback(t2))

        f = tracemalloc.Filter(True, "b.py", traceback=False)
        self.assertFalse(f._match_traceback(t1))
        self.assertTrue(f._match_traceback(t2))

        f = tracemalloc.Filter(False, "b.py", traceback=True)
        self.assertFalse(f._match_traceback(t1))
        self.assertFalse(f._match_traceback(t2))

        f = tracemalloc.Filter(False, "b.py", traceback=False)
        self.assertTrue(f._match_traceback(t1))
        self.assertFalse(f._match_traceback(t2))


@unittest.skipIf(PYTHON34,
                 'env var and -X tracemalloc not supported on Python 3.4')
class TestCommandLine(unittest.TestCase):
    def test_env_var(self):
        # disabled by default
        code = 'import tracemalloc; print(tracemalloc.is_enabled())'
        ok, stdout, stderr = assert_python_ok('-c', code)
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'False')

        # PYTHON* environment varibles must be ignored when -E option is
        # present
        code = 'import tracemalloc; print(tracemalloc.is_enabled())'
        ok, stdout, stderr = assert_python_ok('-E', '-c', code, PYTHONTRACEMALLOC='1')
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'False')

        # enabled by default
        code = 'import tracemalloc; print(tracemalloc.is_enabled())'
        ok, stdout, stderr = assert_python_ok('-c', code, PYTHONTRACEMALLOC='1')
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'True')

    def test_env_var_nframe(self):
        code = 'import tracemalloc; print(tracemalloc.get_traceback_limit())'
        ok, stdout, stderr = assert_python_ok('-c', code, PYTHONTRACEMALLOC='10')
        stdout = stdout.rstrip()
        self.assertEqual(stdout, b'10')

    def test_sys_xoptions_nframe(self):
        for xoptions, nframe in (
            ('tracemalloc', 1),
            ('tracemalloc=1', 1),
            ('tracemalloc=10', 10),
        ):
            with self.subTest(xoptions=xoptions, nframe=nframe):
                code = 'import tracemalloc; print(tracemalloc.get_traceback_limit())'
                ok, stdout, stderr = assert_python_ok('-X', xoptions, '-c', code)
                stdout = stdout.rstrip()
                self.assertEqual(stdout, str(nframe).encode('ascii'))


def test_main():
    support.run_unittest(
        TestTracemallocEnabled,
        TestSnapshot,
        TestFilters,
        TestCommandLine,
    )

if __name__ == "__main__":
    test_main()
