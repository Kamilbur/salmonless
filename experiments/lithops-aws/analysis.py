import polars as pl
import matplotlib.pyplot as plt
import matplotlib as mpl

import analithops
pl.Config.set_tbl_cols(-1)
pl.Config.set_fmt_str_lengths(3500)
df_opt = analithops.data_input('results/optimized', map_reduce=True)
df_nopt = analithops.data_input('results/unoptimized', map_reduce=True)


import numpy as np
import time
import os
import logging
import numpy as np
import polars as pd
import seaborn as sns
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
import matplotlib.pyplot as plt
def create_histogram(fs, dst, figsize=(10, 6)):
    stats = fs
    host_job_create_tstamp = min([cm['host_job_create_tstamp'] for cm in stats])

    total_calls = len(stats)
    max_seconds = 232# int(max([cs['worker_end_tstamp'] - host_job_create_tstamp for cs in stats]) * 2.5)

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

    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(1, 1, 1)

    time_rates = [(cs['worker_start_tstamp'], cs['worker_end_tstamp']) for cs in stats]

    time_hist = compute_times_rates(time_rates)

    N = len(time_hist['start_tstamp'])
    line_segments = LineCollection([[[time_hist['start_tstamp'][i], i],
                                     [time_hist['end_tstamp'][i], i]] for i in range(N)],
                                   linestyles='solid', color='k', alpha=0.6, linewidth=0.4)

    ax.add_collection(line_segments)

    ax.plot(runtime_bins, time_hist['runtime_calls_hist'].sum(axis=0), label='Total Active Calls', zorder=-1)

    yplot_step = int(np.max([1, total_calls / 20]))
    y_ticks = np.arange(total_calls // yplot_step + 2) * yplot_step
    ax.set_yticks(y_ticks)
    ax.set_ylim(-0.02 * total_calls, total_calls * 1.02)

    xplot_step = max(int(max_seconds / 8), 1)
    x_ticks = np.arange(max_seconds // xplot_step + 2) * xplot_step
    ax.set_xlim(0, max_seconds)
    ax.set_xticks(x_ticks)
    for x in x_ticks:
        ax.axvline(x, c='k', alpha=0.2, linewidth=0.8)

    ax.set_xlabel("Execution Time (sec)")
    ax.set_ylabel("Function Call")
    ax.grid(False)
    ax.legend(loc='upper right')

    fig.tight_layout()

    if dst is None:
        os.makedirs('plots', exist_ok=True)
        dst = os.path.join(os.getcwd(), 'plots', '{}_{}'.format(int(time.time()), 'histogram.png'))
    else:
        dst = os.path.expanduser(dst) if '~' in dst else dst
        dst = '{}_{}'.format(os.path.realpath(dst), 'histogram.png')

    # fig.savefig(dst)
    fig.show()
    plt.close(fig)


def create_lines_timeline(ax, stats_df, activations=True, lw=0.1):
    host_job_create_tstamp = stats_df['host_job_create_tstamp'].min()
    total_calls = len(stats_df)

    fields = {
        'function start': stats_df['worker_func_start_tstamp'] - host_job_create_tstamp,
        'function done': stats_df['worker_func_end_tstamp'] - host_job_create_tstamp,
    }

    # max_seconds = int(max([cs['worker_end_tstamp'] - host_job_create_tstamp for cs in stats]) * 2.5)
    print(stats_df['worker_end_tstamp'])
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
    time_rates = [(x, y) for x, y in zip(stats_df['worker_func_start_tstamp'], stats_df['worker_end_tstamp'])]

    if activations:
        time_hist = compute_times_rates(time_rates)
        print(runtime_bins)
        ax.plot(runtime_bins, time_hist['runtime_calls_hist'].sum(axis=0), zorder=10)
        ax.plot(runtime_bins, [480] * len(runtime_bins), zorder=8, color='gray', linestyle='dashed')
        # ax.plot([75, 192], [0, 0], label='Total Active Calls', zorder=10, color='#1f77b4')
        # ax.legend()

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
    max_seconds = 192
    xplot_step = max(int(max_seconds / 8), 1)
    x_ticks = np.arange(max_seconds // xplot_step + 2) * xplot_step
    ax.set_xlim(0, max_seconds)

    ax.set_xticks(x_ticks)
    for x in x_ticks:
        ax.axvline(x, c='k', alpha=0.2, linewidth=0.8)

    ax.grid(False)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 6))

ddf = df_opt.filter(df_opt['nrun'] == 2)
ddf = ddf.filter(ddf['nlambdas'] == 64)

adf = df_nopt.filter(df_nopt['nrun'] == 1)
adf = adf.filter(adf['nlambdas'] == 1)
print(adf)

print(ddf.columns)
# create_lines_timeline(ax, ddf, activations=True, lw=2)
create_lines_timeline(ax, adf, activations=True, lw=2)
plt.tight_layout()
fig.show()
import sys; sys.exit(0)
mpl.rcParams.update({
    # 'font.family': 'serif',
    'font.size': 10,
    'axes.titlesize': 10,
    'axes.labelsize': 25,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'legend.fontsize': 20,
    'figure.titlesize': 10,
})

print(df_opt.columns)
print(df_opt['worker_peak_memory_start'] / 1024 ** 3)
print(df_opt['worker_peak_memory_end'] / 1024 ** 3)

df = pl.read_csv('old-measurements.csv')
df_opt = analithops.compute_mean_runtime_per_nlambdas(df_opt)
df = df.group_by('nlambdas').mean().sort('nlambdas')

def calc(df, base=None):
    df = df.group_by('nlambdas').mean().sort('nlambdas')
    if base is None:
        base = df[0]['time'][0]
    return df['nlambdas'], base / df['time']

base = df['time'][0] if df['time'][0] > df_opt['time'][0] else df_opt['time'][0]

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))

global_opts = dict(
    lw = 2,
    ms = 8,
    mew = 0.5,
    mec = 'k',
    marker = 'o',
)

ax.plot(*calc(df_opt), **global_opts, label='After optimization')
ax.plot(*calc(df), **global_opts, label='Before optimization')

ax.plot(df_opt['nlambdas'], df_opt['nlambdas'], label='Ideal', color='gray', linestyle='--', lw=2)
ax.set_xlabel(xlabel='Number of functions')
ax.set_ylabel(ylabel='Speedup')

plt.xscale('log', base=2)
plt.yscale('log', base=2)
xticks = [1, 2, 4, 8, 16, 32, 64, 128]
yticks = [1, 2, 4, 8, 16, 32, 64, 128]
plt.yticks(yticks, [str(y) for y in yticks])
plt.xticks(xticks, [str(x) for x in xticks])
ax.legend()
plt.tight_layout()

plt.show()
