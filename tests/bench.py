import gc
import sys
import time
import tracemalloc

ALLOC_LOOPS = 3
NOBJECTS = 10 ** 5
BENCH_RUNS = 5

# To compare, we need 2 snapshots stored in the memory at the same time
NGET_SNAPSHOT = 2

# use multiple objects to have an traceback
def alloc_object5():
    return object()

def alloc_object4():
    return alloc_object5()

def alloc_object3():
    return alloc_object4()

def alloc_object2():
    return alloc_object3()

def alloc_object():
    return alloc_object2()

def alloc_objects():
    for loop in range(ALLOC_LOOPS):
        objs = [alloc_object() for index in range(NOBJECTS)]
        objs = None

def take_snapshots():
    all_snapshots = []
    for loop in range(NGET_SNAPSHOT):
        objs = [alloc_object() for index in range(NOBJECTS)]
        snapshot = tracemalloc.take_snapshot()
        objs = None
        all_snapshots.append(snapshot)
        snapshots = None
    all_snapshots = None

def bench(func, trace=True):
    if trace:
        tracemalloc.stop()
        tracemalloc.start()
    gc.collect()
    best = None
    for run in range(BENCH_RUNS):
        start = time.monotonic()
        func()
        dt = time.monotonic() - start
        if best is not None:
            best = min(best, dt)
        else:
            best = dt
    if trace:
        mem = tracemalloc.get_tracemalloc_memory()
        ntrace = len(tracemalloc.take_snapshot().traces)
        tracemalloc.stop()
    else:
        mem = ntrace = None
    gc.collect()
    return best * 1e3, mem, ntrace

def main():
    print("Micro benchmark allocating %s objects" % NOBJECTS)
    print("Clear default tracemalloc filters")
    tracemalloc.clear_filters()
    print("")

    base, mem, ntrace = bench(alloc_objects, False)
    print("no tracing: %.1f ms" % base)

    def run(what):
        dt, mem, ntrace = bench(alloc_objects)
        print("%s: %.1f ms, %.1fx slower (%s traces, %.1f kB)"
              % (what, dt, dt / base, ntrace, mem / 1024))

    tracemalloc.set_traceback_limit(0)
    run("trace, 0 frames")
    tracemalloc.set_traceback_limit(1)

    run("trace")

#    for n in (1, 10, 100):
#        tracemalloc.start()
#        tasks = [tracemalloctext.Task(str) for index in range(n)] # dummy callback
#        for task in tasks:
#            task.set_delay(60.0)
#            task.schedule()
#        dt = bench(func)
#        print("trace with %s task: %.1f ms, %.1fx slower" % (n, dt, dt / base))
#        tracemalloc.cancel_tasks()

    tracemalloc.add_filter(tracemalloc.Filter(True, __file__))
    run("trace with filter including file")
    tracemalloc.clear_filters()

    tracemalloc.add_filter(tracemalloc.Filter(False, __file__ + "xxx"))
    run("trace with not matching excluding file")
    tracemalloc.clear_filters()

    tracemalloc.add_filter(tracemalloc.Filter(True, "xxx"))
    run("trace with filter excluding all")
    tracemalloc.clear_filters()

    tracemalloc.add_filter(tracemalloc.Filter(False, __file__))
    tracemalloc.add_filter(tracemalloc.Filter(False, tracemalloc.__file__))
    run("trace with filter excluding file and tracemalloc")
    tracemalloc.clear_filters()

    for nframe in (5, 10, 25, 100):
        tracemalloc.set_traceback_limit(nframe)
        run("trace, %s frames" % nframe)
        tracemalloc.set_traceback_limit(1)
    print("")

    dt, mem, ntrace = bench(take_snapshots)
    print("take %s snapshots: %.1f ms" % (NGET_SNAPSHOT, dt))

main()
