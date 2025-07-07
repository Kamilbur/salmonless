import polars as pl
import matplotlib.pyplot as plt
import matplotlib as mpl
import utils

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



pl.Config.set_tbl_cols(1000)
pl.Config.set_tbl_width_chars(10000)

df_pod = utils.data_input('ares-s3-podole', forbidden=[])
df_aws = utils.data_input('ares-s3-aws', forbidden=[])
df_pod_times = utils.prepare_df(df_pod)
df_aws_times = utils.prepare_df(df_aws)
df_cost = utils.baseline_input('cost-baseline')

global_opts = dict(
    lw = 2,
    ms = 8,
    mew = 0.5,
    mec = 'k',
    marker = 'o',
)
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))


pod_spd, aws_spd, cost_spd = utils.compute_speedup(df_pod_times, df_aws_times, df_cost)

colors = dict(
    green='#2ca02c',
    blue='#1f77b4',
    red='#d62728',
    orange='#ff7f0e',
)

ax.plot(pod_spd[0], pod_spd[0], label='Ideal', color='gray', linestyle='--', lw=2)
ax.plot(pod_spd[0], pod_spd[1], label='Local Object Storage', color=colors['blue'], **global_opts)
ax.plot(aws_spd[0], aws_spd[1], label='AWS Object Storage', color=colors['red'], **global_opts)
ax.plot(cost_spd[0], cost_spd[1], label='Optimized Single Node + Local', color=colors['orange'], **global_opts)
# ax.plot(pod_spd[0], df_pod_times[''], label='Local Object Storage', color=colors['blue'], **global_opts)
plt.xscale('log', base=2)
plt.yscale('log', base=2)

xticks = [1, 2, 4, 8, 16, 32, 48, 60, 120, 240]
yticks = [1, 2, 4, 8, 16, 32, 60, 120, 240]
plt.yticks(yticks, [str(y) for y in yticks])
plt.xticks(xticks, [str(x) for x in xticks])
# ax.set_facecolor('#fbfbfb')
ax.grid(True, linestyle='--', linewidth=0.5, color='gray', alpha=0.6)
ax.set_xlabel(xlabel='Number of cores')
ax.set_ylabel(ylabel='Speedup')

# labels = ax.get_xticklabels()
# utils.move_xticklabels(labels[6], dx=-0.1)
# # utils.move_xticklabels(labels[7], dx=-0.001)
# ax.set_xticklabels(labels)


# ax.legend(fontsize=20)
ax.legend()
plt.tight_layout()
plt.rcParams['svg.fonttype'] = 'none'
# plt.savefig('speedup.pdf', format='pdf', bbox_inches='tight', dpi=1200)
plt.show()

print(df_pod_times)
print(max(aws_spd[1].max(), cost_spd[1].max(), pod_spd[1].max()))
print(aws_spd[1].max(), cost_spd[1].max(), pod_spd[1].max())
