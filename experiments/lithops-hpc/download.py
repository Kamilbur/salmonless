import matplotlib.pyplot as plt
import matplotlib as mpl
import utils
import polars as pl

mpl.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 10,
    'axes.labelsize': 25,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'legend.fontsize': 20,
    'figure.titlesize': 10,
})



df_pod = utils.data_input('download-s3-podole', map_reduce=False)
df_aws = utils.data_input('download-s3-aws', map_reduce=False)
df_cost = utils.baseline_input('cost-baseline')
df_pod_times = utils.prepare_df(df_pod)
df_aws_times = utils.prepare_df(df_aws)
df_cost_times = pl.DataFrame({
    'time': df_cost['download_time'] + df_cost['decompression'],
    'ncores': df_cost['ncores'],
})
print(df_cost_times)
print(df_pod_times)
print(df_aws_times)

global_opts = dict(
    lw = 2,
    ms = 8,
    mew = 0.5,
    mec = 'k',
    marker = 'o',
)


pod_time, aws_time = utils.compute_time(df_pod_times, df_aws_times)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
ax.plot(pod_time[0], pod_time[1], label='Local Object Storage', color='#1f77b4', **global_opts)
ax.plot(aws_time[0], aws_time[1], label='AWS Object Storage', color='#d62728', **global_opts)
ax.plot(df_cost['ncores'], df_cost['download_time'] + df_cost['decompression'], label='Optimized Single Node + Local', color='#ff7f0e', **global_opts)
plt.xticks(
    [-2, 3, 8, 16, 32, 60, 120, 240],
    ['1', '4', '8', '16', '32',  '60', '120', '240']
)
ax.set_xlabel(xlabel='Number of cores')
ax.set_ylabel(ylabel='Time [s]')
ax.legend()
plt.tight_layout()
plt.rcParams['svg.fonttype'] = 'none'

plt.savefig('download_time.pdf', format='pdf', dpi=1200, bbox_inches='tight')
plt.show()

pod_spd, aws_spd, cost_spd = utils.compute_speedup(df_pod_times, df_aws_times, df_cost_times)

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))
ax.plot(pod_spd[0], pod_spd[1], label='Local Object Storage', color='#1f77b4', **global_opts)
ax.plot(aws_spd[0], aws_spd[1], label='AWS Object Storage', color='#d62728', **global_opts)
ax.plot(cost_spd[0], cost_spd[1], label='Optimized Single Node + Local', color='#ff7f0e', **global_opts)
ax.plot(aws_spd[0], aws_spd[0], label='Ideal', color='gray', linestyle='--', lw=2, zorder=-1)
plt.xticks(
    [-2, 3, 8, 16, 32, 60, 120, 240],
    ['1', '4', '8', '16', '32',  '60', '120', '240']
)
ax.set_xlabel(xlabel='Number of cores')
ax.set_ylabel(ylabel='Speedup')
ax.legend()
plt.tight_layout()
plt.rcParams['svg.fonttype'] = 'none'

plt.savefig('download_speedup.pdf', format='pdf', dpi=1200, bbox_inches='tight')
plt.show()