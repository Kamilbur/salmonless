import polars as pl
import matplotlib.pyplot as plt
import matplotlib as mpl
import utils
import json
import lhops_plots

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

with open('ares-s3-podole/120/output-1.jsonl') as f:
    lines = [json.loads(line) for line in f.readlines()]

df = pl.DataFrame(lines)
fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 10))

lhops_plots.create_lines_timeline(ax, df, activations=False, lw=2.5)
ax.set_xlabel('Time [s]')
plt.savefig('ares-s3-podole-120-choosen-timeline.pdf', format='pdf', dpi=1200, bbox_inches='tight')
plt.show()