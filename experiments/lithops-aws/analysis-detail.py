import polars as pl
import matplotlib.pyplot as plt
import matplotlib as mpl


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

df = pl.read_csv('old-measurements.csv')

# print(df)

df = df.group_by('nlambdas').mean().sort('nlambdas')
base = df[0]['time'][0]

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))

global_opts = dict(
    lw = 2,
    ms = 8,
    mew = 0.5,
    mec = 'k',
    marker = 'o',
)


ax.plot(df['nlambdas'], base / df['time'], **global_opts, label='Measured')
ax.plot(df['nlambdas'], df['nlambdas'], **global_opts, label='Ideal')
ax.set_xlabel(xlabel='Number of cores')
ax.set_ylabel(ylabel='Speedup')

plt.xscale('log', base=2)
plt.yscale('log', base=2)
xticks = [1, 2, 4, 8, 16, 32, 64]
yticks = [1, 2, 4, 8, 16, 32, 64]
plt.yticks(yticks, [str(y) for y in yticks])
plt.xticks(xticks, [str(x) for x in xticks])
ax.legend()
plt.tight_layout()

plt.show()
