import matplotlib.pyplot as plt
import numpy as np
import json
import polars as pl

with open('processed/times_podole.json') as f:
    times = json.loads(f.read())

df = pl.DataFrame(times)

df = df.sort('size_bytes')
size = df["size_bytes"].to_numpy()
time = df["time"].to_numpy()


threshold = 1e10  # adjust based on your data

# Create subplots with broken x-axis
fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(10, 6), gridspec_kw={'width_ratios': [3, 1]})

# Plot the main cluster
ax1.scatter(size[size < threshold], time[size < threshold], color='dodgerblue', edgecolor='black', s=70)
ax1.set_xlim([size.min() - 10, threshold])
ax1.set_xlabel("Size (MB)", fontsize=13)
ax1.set_ylabel("Time (s)", fontsize=13)
ax1.grid(True)

# Plot the outlier(s)
ax2.scatter(size[size >= threshold], time[size >= threshold], color='crimson', edgecolor='black', s=70)
ax2.set_xlim([threshold - 10, size.max() + 10])
ax2.set_xlabel("Size (MB)", fontsize=13)
ax2.grid(True)

# Hide spines between plots
ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.tick_params(labelright=False)
ax2.tick_params(labelleft=False)

# Add break marks
d = .015  # size of break marks
kwargs = dict(transform=fig.transFigure, color='k', clip_on=False)
fig.subplots_adjust(wspace=0.05)
fig.text(0.5, 0.95, "Time vs Size with Outlier", ha='center', fontsize=16)
fig.canvas.draw()

# Diagonal lines
ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)

plt.show()
