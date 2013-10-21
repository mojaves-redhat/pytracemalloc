from __future__ import with_statement
import _tracemalloc
import datetime
import gc
import os
import pickle
import sys

# Import types and functions implemented in C
from _tracemalloc import *

def _stat_key(stats):
    return (abs(stats[0]), stats[1], abs(stats[2]), stats[3], stats[4])

class GroupedStats:
    __slots__ = ('timestamp', 'traceback_limit', 'stats', 'group_by',
                 'cumulative', 'metrics')

    def __init__(self, timestamp, traceback_limit, stats, group_by,
                 cumulative=False, metrics=None):
        self.timestamp = timestamp
        self.traceback_limit = traceback_limit
        # dictionary {key: stats} where stats is
        # a (size: int, count: int) tuple
        self.stats = stats
        self.group_by = group_by
        self.cumulative = cumulative
        self.metrics = metrics

    def _create_key(self, key):
        if self.group_by == 'filename':
            if key is None:
                return ''
        elif self.group_by == 'line':
            filename, lineno = key
            if filename is None:
                filename = ''
            if lineno is None:
                lineno = 0
            return (filename, lineno)
        return key

    def compare_to(self, old_stats=None, sort=True):
        if old_stats is not None:
            previous_dict = old_stats.stats.copy()

            differences = []
            for key, stats in self.stats.items():
                size, count = stats
                previous = previous_dict.pop(key, None)
                key = self._create_key(key)
                if previous is not None:
                    diff = (size - previous[0], size,
                            count - previous[1], count,
                            key)
                else:
                    diff = (size, size, count, count, key)
                differences.append(diff)

            for key, stats in previous_dict.items():
                key = self._create_key(key)
                diff = (-stats[0], 0, -stats[1], 0, key)
                differences.append(diff)
        else:
            differences = [
                (0, stats[0], 0, stats[1], self._create_key(key))
                for key, stats in self.stats.items()]

        if sort:
            differences.sort(reverse=True, key=_stat_key)
        return differences


def _compute_stats_frame(stats, group_per_file, size, frame):
    if not group_per_file:
        if frame is not None:
            key = frame
        else:
            key = (None, None)
    else:
        if frame is not None:
            key = frame[0]
        else:
            key = None
    if key in stats:
        stat_size, count = stats[key]
        size += stat_size
        count = count + 1
    else:
        count = 1
    stats[key] = (size, count)


class Metric:
    __slots__ = ('name', 'value', 'format')

    def __init__(self, name, value, format):
        self.name = name
        self.value = value
        self.format = format

    def __eq__(self, other):
        return (self.name == other.name and self.value == other.value)

    def __repr__(self):
        return ('<Metric name=%r value=%r format=%r>'
                % (self.name, self.value, self.format))


class Snapshot:
    FORMAT_VERSION = (3, 4)
    __slots__ = ('timestamp', 'traceback_limit',
                 'stats', 'traces', 'metrics')

    def __init__(self, timestamp, traceback_limit,
                 stats=None, traces=None, metrics=None):
        self.timestamp = timestamp
        self.traceback_limit = traceback_limit
        self.stats = stats
        self.traces = traces
        if metrics is not None:
            self.metrics = metrics
        else:
            self.metrics = {}

    def add_metric(self, name, value, format):
        if name in self.metrics:
            raise ValueError("name already present: %r" % (name,))
        metric = Metric(name, value, format)
        self.metrics[metric.name] = metric
        return metric

    def get_metric(self, name, default=None):
        if name in self.metrics:
            return self.metrics[name].value
        else:
            return default

    @classmethod
    def create(cls, traces=False):
        if not is_enabled():
            raise RuntimeError("the tracemalloc module must be enabled "
                               "to take a snapshot")
        timestamp = datetime.datetime.now()
        traceback_limit = get_traceback_limit()

        stats = get_stats()
        if traces:
            traces = get_traces()
        else:
            traces = None

        snapshot = cls(timestamp, traceback_limit, stats, traces)
        return snapshot

    @classmethod
    def load(cls, filename, traces=True):
        with open(filename, "rb") as fp:
            data = pickle.load(fp)

            try:
                if data['format_version'] != cls.FORMAT_VERSION:
                    raise TypeError("unknown format version")

                timestamp = data['timestamp']
                stats = data['stats']
                traceback_limit = data['traceback_limit']
                metrics = data.get('metrics')
            except KeyError:
                raise TypeError("invalid file format")

            if traces:
                traces = pickle.load(fp)
            else:
                traces = None

        return cls(timestamp, traceback_limit, stats, traces, metrics)

    def dump(self, filename):
        data = {
            'format_version': self.FORMAT_VERSION,
            'timestamp': self.timestamp,
            'traceback_limit': self.traceback_limit,
            'stats': self.stats,
        }
        if self.metrics:
            data['metrics'] = self.metrics

        try:
            with open(filename, "wb") as fp:
                pickle.dump(data, fp, pickle.HIGHEST_PROTOCOL)
                pickle.dump(self.traces, fp, pickle.HIGHEST_PROTOCOL)
        except:
            # Remove corrupted pickle file
            if os.path.exists(filename):
                os.unlink(filename)
            raise

    def _filter_traces(self, include, filters):
        new_traces = {}
        for address, trace in self.traces.items():
            if include:
                match = any(trace_filter._match_traceback(trace[1])
                            for trace_filter in filters)
            else:
                match = all(trace_filter._match_traceback(trace[1])
                            for trace_filter in filters)
            if match:
                new_traces[address] = trace
        return new_traces

    def _filter_stats(self, include, filters):
        file_stats = {}
        for filename, line_stats in self.stats.items():
            if include:
                match = any(trace_filter._match_filename(filename)
                            for trace_filter in filters)
            else:
                match = all(trace_filter._match_filename(filename)
                            for trace_filter in filters)
            if not match:
                continue

            new_line_stats = {}
            for lineno, line_stat in line_stats.items():
                if include:
                    match = any(trace_filter._match(filename, lineno)
                                for trace_filter in filters)
                else:
                    match = all(trace_filter._match(filename, lineno)
                                for trace_filter in filters)
                if match:
                    new_line_stats[lineno] = line_stat

            file_stats[filename] = new_line_stats
        return file_stats

    def _apply_filters(self, include, filters):
        if not filters:
            return
        self.stats = self._filter_stats(include, filters)
        if self.traces is not None:
            self.traces = self._filter_traces(include, filters)

    def apply_filters(self, filters):
        include_filters = []
        exclude_filters = []
        for trace_filter in filters:
            if trace_filter.include:
                include_filters.append(trace_filter)
            else:
                exclude_filters.append(trace_filter)
        self._apply_filters(True, include_filters)
        self._apply_filters(False, exclude_filters)

    def top_by(self, group_by, cumulative=False):
        if cumulative and self.traceback_limit < 2:
            cumulative = False

        stats = {}
        if group_by == 'address':
            cumulative = False

            if self.traces is None:
                raise ValueError("need traces")

            for address, trace in self.traces.items():
                stats[address] = (trace[0], 1)
        elif group_by == 'traceback':
            cumulative = False

            if self.traces is None:
                raise ValueError("need traces")

            for address, trace in self.traces.items():
                size, traceback = trace
                key = (address, traceback)
                stats[key] = (size, 1)

        else:
            if group_by == 'filename':
                group_per_file = True
            elif group_by == 'line':
                group_per_file = False
            else:
                raise ValueError("unknown group_by value: %r" % (group_by,))

            if not cumulative:
                for filename, line_dict in self.stats.items():
                    if not group_per_file:
                        for lineno, line_stats in line_dict.items():
                            key = (filename, lineno)
                            stats[key] = line_stats
                    else:
                        key = filename
                        total_size = total_count = 0
                        for size, count in line_dict.values():
                            total_size += size
                            total_count += count
                        stats[key] = (total_size, total_count)
            else:
                if self.traces is None:
                    raise ValueError("need traces")

                for trace in self.traces.values():
                    size, traceback = trace
                    if traceback:
                        for frame in traceback:
                            _compute_stats_frame(stats, group_per_file, size, frame)
                    else:
                        _compute_stats_frame(stats, group_per_file, size, None)

        return GroupedStats(self.timestamp, self.traceback_limit, stats,
                            group_by, cumulative, self.metrics)


