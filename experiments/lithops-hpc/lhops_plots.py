import os
# import pylab
import time
import logging
import numpy as np
import polars as pd
import seaborn as sns
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt

sns.set_style('whitegrid')
# pylab.switch_backend("Agg")
logger = logging.getLogger(__name__)


# def create_timeline(fs, dst, figsize=(10, 6)):
#     stats = [f.stats for f in fs]
#     host_job_create_tstamp = min([cm['host_job_create_tstamp'] for cm in stats])
#
#     stats_df = pd.DataFrame(stats)
#     total_calls = len(stats_df)
#
#     palette = sns.color_palette("deep", 10)
#
#     fig = pylab.figure(figsize=figsize)
#     ax = fig.add_subplot(1, 1, 1)
#
#     y = np.arange(total_calls)
#     point_size = 10
#
#     fields = [('host submit', stats_df['host_submit_tstamp'] - host_job_create_tstamp),
#               # ('worker start', stats_df.worker_start_tstamp - host_job_create_tstamp),
#               ('function start', stats_df['worker_func_start_tstamp'] - host_job_create_tstamp),
#               ('function done', stats_df['worker_func_end_tstamp'] - host_job_create_tstamp),
#               # ('worker done', stats_df.worker_end_tstamp - host_job_create_tstamp),
#               ('status fetched', stats_df['host_status_done_tstamp'] - host_job_create_tstamp)]
#
#     if 'host_result_done_tstamp' in stats_df:
#         fields.append(('results fetched', stats_df.host_result_done_tstamp - host_job_create_tstamp))
#
#     patches = []
#     for f_i, (field_name, val) in enumerate(fields):
#         ax.scatter(val, y, c=[palette[f_i]], edgecolor='none', s=point_size, alpha=0.8)
#         patches.append(mpatches.Patch(color=palette[f_i], label=field_name))
#
#     ax.set_xlabel('Execution Time (sec)')
#     ax.set_ylabel('Function Call')
#
#     legend = pylab.legend(handles=patches, loc='upper right', frameon=True)
#     legend.get_frame().set_facecolor('#FFFFFF')
#
#     yplot_step = int(np.max([1, total_calls / 20]))
#     y_ticks = np.arange(total_calls // yplot_step + 2) * yplot_step
#     ax.set_yticks(y_ticks)
#     ax.set_ylim(-0.02 * total_calls, total_calls * 1.02)
#     for y in y_ticks:
#         ax.axhline(y, c='k', alpha=0.1, linewidth=1)
#
#     if 'host_result_done_tstamp' in stats_df:
#         max_seconds = np.max(stats_df['host_result_done_tstamp'] - host_job_create_tstamp) * 1.25
#     elif 'host_status_done_tstamp' in stats_df:
#         max_seconds = np.max(stats_df['host_status_done_tstamp'] - host_job_create_tstamp) * 1.25
#     else:
#         max_seconds = np.max(stats_df.end_tstamp - host_job_create_tstamp) * 1.25
#     xplot_step = max(int(max_seconds / 8), 1)
#     x_ticks = np.arange(max_seconds // xplot_step + 2) * xplot_step
#     ax.set_xlim(0, max_seconds)
#
#     ax.set_xticks(x_ticks)
#     for x in x_ticks:
#         ax.axvline(x, c='k', alpha=0.2, linewidth=0.8)
#
#     ax.grid(False)
#     fig.tight_layout()
#
#     if dst is None:
#         os.makedirs('plots', exist_ok=True)
#         dst = os.path.join(os.getcwd(), 'plots', '{}_{}'.format(int(time.time()), 'timeline.png'))
#     else:
#         dst = os.path.expanduser(dst) if '~' in dst else dst
#         dst = '{}_{}'.format(os.path.realpath(dst), 'timeline.png')
#
#     fig.savefig(dst)


# def create_histogram(fs, dst, figsize=(10, 6)):
#     stats = [f.stats for f in fs]
#     host_job_create_tstamp = min([cm['host_job_create_tstamp'] for cm in stats])
#
#     total_calls = len(stats)
#     max_seconds = int(max([cs['worker_end_tstamp'] - host_job_create_tstamp for cs in stats]) * 2.5)
#
#     runtime_bins = np.linspace(0, max_seconds, max_seconds)
#
#     def compute_times_rates(time_rates):
#         x = np.array(time_rates)
#         tzero = host_job_create_tstamp
#         start_time = x[:, 0] - tzero
#         end_time = x[:, 1] - tzero
#
#         N = len(start_time)
#
#         runtime_calls_hist = np.zeros((N, len(runtime_bins)))
#
#         for i in range(N):
#             s = start_time[i]
#             e = end_time[i]
#             a, b = np.searchsorted(runtime_bins, [s, e])
#             if b - a > 0:
#                 runtime_calls_hist[i, a:b] = 1
#
#         return {'start_tstamp': start_time,
#                 'end_tstamp': end_time,
#                 'runtime_calls_hist': runtime_calls_hist}
#
#     fig = pylab.figure(figsize=figsize)
#     ax = fig.add_subplot(1, 1, 1)
#
#     time_rates = [(cs['worker_start_tstamp'], cs['worker_end_tstamp']) for cs in stats]
#
#     time_hist = compute_times_rates(time_rates)
#
#     N = len(time_hist['start_tstamp'])
#     line_segments = LineCollection([[[time_hist['start_tstamp'][i], i],
#                                      [time_hist['end_tstamp'][i], i]] for i in range(N)],
#                                    linestyles='solid', color='k', alpha=0.6, linewidth=0.4)
#
#     ax.add_collection(line_segments)
#
#     ax.plot(runtime_bins, time_hist['runtime_calls_hist'].sum(axis=0), label='Total Active Calls', zorder=-1)
#
#     yplot_step = int(np.max([1, total_calls / 20]))
#     y_ticks = np.arange(total_calls // yplot_step + 2) * yplot_step
#     ax.set_yticks(y_ticks)
#     ax.set_ylim(-0.02 * total_calls, total_calls * 1.02)
#
#     xplot_step = max(int(max_seconds / 8), 1)
#     x_ticks = np.arange(max_seconds // xplot_step + 2) * xplot_step
#     ax.set_xlim(0, max_seconds)
#     ax.set_xticks(x_ticks)
#     for x in x_ticks:
#         ax.axvline(x, c='k', alpha=0.2, linewidth=0.8)
#
#     ax.set_xlabel("Execution Time (sec)")
#     ax.set_ylabel("Function Call")
#     ax.grid(False)
#     ax.legend(loc='upper right')
#
#     fig.tight_layout()
#
#     if dst is None:
#         os.makedirs('plots', exist_ok=True)
#         dst = os.path.join(os.getcwd(), 'plots', '{}_{}'.format(int(time.time()), 'histogram.png'))
#     else:
#         dst = os.path.expanduser(dst) if '~' in dst else dst
#         dst = '{}_{}'.format(os.path.realpath(dst), 'histogram.png')
#
#     fig.savefig(dst)
#     pylab.close(fig)

def create_lines_timeline(ax, stats_df, activations=True, lw=0.1):
    host_job_create_tstamp = stats_df['host_job_create_tstamp'].min()
    total_calls = len(stats_df)

    fields = {
        'function start': stats_df['worker_func_start_tstamp'] - host_job_create_tstamp,
        'function done': stats_df['worker_func_end_tstamp'] - host_job_create_tstamp,
    }

    # max_seconds = int(max([cs['worker_end_tstamp'] - host_job_create_tstamp for cs in stats]) * 2.5)
    max_seconds = int((stats_df['worker_end_tstamp'] - host_job_create_tstamp).max() * 1.5)

    runtime_bins = np.linspace(0, max_seconds, max_seconds)
    def compute_times_rates(time_rates):
        x = np.array(time_rates)
        tzero = host_job_create_tstamp
        start_time = x[:, 0] - tzero
        end_time = x[:, 1] - tzero

        N = len(start_time)

        runtime_calls_hist = np.zeros((N, len(runtime_bins)))

        for i in range(N):
            s = start_time[i]
            e = end_time[i]
            a, b = np.searchsorted(runtime_bins, [s, e])
            if b - a > 0:
                runtime_calls_hist[i, a:b] = 1

        return {'start_tstamp': start_time,
                'end_tstamp': end_time,
                'runtime_calls_hist': runtime_calls_hist}

    # time_rates = [(cs['worker_start_tstamp'], cs['worker_end_tstamp']) for cs in stats_df]
    time_rates = [(x, y) for x, y in zip(stats_df['worker_start_tstamp'], stats_df['worker_end_tstamp'])]

    if activations:
        time_hist = compute_times_rates(time_rates)
        ax.plot(runtime_bins, time_hist['runtime_calls_hist'].sum(axis=0), label='Total Active Lambdas', zorder=10)
        ax.plot(runtime_bins, [480] * len(runtime_bins), label='Assigned Cores', zorder=8, color='gray', linestyle='dashed')

    lines_df = pd.DataFrame(fields)
    for idx, (start, end) in enumerate(lines_df.iter_rows()):
        xs = [start, end]
        ys = [idx, idx]
        ax.plot(xs, ys, lw=lw)

    ax.set_xlabel('Execution Time (sec)')
    ax.set_ylabel('Function Call')

    yplot_step = int(np.max([1, total_calls / 20]))
    y_ticks = np.arange(total_calls // yplot_step + 2) * yplot_step
    ax.set_yticks(y_ticks)
    ax.set_ylim(-0.02 * total_calls, total_calls * 1.02)
    for y in y_ticks:
        ax.axhline(y, c='k', alpha=0.1, linewidth=1)

    if 'host_result_done_tstamp' in stats_df:
        max_seconds = (stats_df['host_result_done_tstamp'] - host_job_create_tstamp).max() * 1.25
    elif 'host_status_done_tstamp' in stats_df:
        max_seconds = (stats_df['host_status_done_tstamp'] - host_job_create_tstamp).max() * 1.25
    else:
        max_seconds = (stats_df['end_tstamp'] - host_job_create_tstamp).max() * 1.25
    max_seconds /= 1.25
    xplot_step = max(int(max_seconds / 8), 1)
    x_ticks = np.arange(max_seconds // xplot_step + 2) * xplot_step
    ax.set_xlim(0, max_seconds)

    ax.set_xticks(x_ticks)
    for x in x_ticks:
        ax.axvline(x, c='k', alpha=0.2, linewidth=0.8)

    ax.grid(False)