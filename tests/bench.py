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

def bench(func, trace=True, nframe=1):
    if trace:
        tracemalloc.stop()
        tracemalloc.start(nframe)
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

    base, mem, ntrace = bench(alloc_objects, False)
    print("no tracing: %.1f ms" % base)

    def run(what, nframe=1):
        dt, mem, ntrace = bench(alloc_objects, nframe=nframe)
        print("%s: %.1f ms, %.1fx slower (%s traces, %.1f kB)"
              % (what, dt, dt / base, ntrace, mem / 1024))

    run("trace")

    for nframe in (5, 10, 25, 100):
        run("trace, %s frames" % nframe, nframe=nframe)
    print("")

    dt, mem, ntrace = bench(take_snapshots)
    print("take %s snapshots: %.1f ms" % (NGET_SNAPSHOT, dt))

main()
