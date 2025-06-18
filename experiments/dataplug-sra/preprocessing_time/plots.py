import json
import polars as pl
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import RANSACRegressor, LinearRegression

with open('processed/times_podole.json') as f:
    times = json.loads(f.read())

df = pl.DataFrame(times)

df = df.sort('size_bytes')
size = df["size_bytes"].to_numpy()
time = df["time"].to_numpy()


size_reshaped = size.reshape(-1, 1)
ransac = RANSACRegressor(estimator=LinearRegression(), random_state=42)
ransac.fit(size_reshaped, time)
time_smooth = ransac.predict(size[5:-1].reshape(-1, 1))


threshold = 6e9

fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True, figsize=(10, 6), gridspec_kw={'width_ratios': [3, 1]})

ax1.scatter(size[5:], time[5:], color='lavender', edgecolor='black', s=70, label="Data Points", zorder=3)
ax1.plot(size[5:-1], time_smooth, color='gray', linewidth=2.5, label="Robust Fit", zorder=2)

ax1.set_xlim([size.min() - 10, threshold])
ax1.set_xlabel("Size (GB)", fontsize=14)
ax1.set_ylabel("Time (seconds)", fontsize=14)

ax1.grid(which='major', linestyle='-', linewidth=0.75)
ax1.minorticks_on()
ax1.grid(which='minor', linestyle=':', linewidth=0.5)


ax2.grid(which='major', linestyle='-', linewidth=0.75)
ax2.minorticks_on()
ax2.grid(which='minor', linestyle=':', linewidth=0.5)




ax2.scatter(size[size >= threshold], time[size >= threshold], color='lavender', edgecolor='black', s=70)


d = .015
kwargs = dict(transform=fig.transFigure, color='k', clip_on=False)
fig.subplots_adjust(wspace=0.05)
fig.text(0.5, 0.95, "Time vs Size with Outlier", ha='center', fontsize=16)
fig.canvas.draw()

ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)
ax1.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)
ax2.plot((-d, +d), (-d, +d), **kwargs)
ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)

xticks = np.arange(size.min(), threshold + 1, step=1e9)
xtick_labels = [
    f"{int(x / 1e9)}" for x in xticks
]
ax1.set_xticks(xticks)
ax1.set_xticklabels(labels=xtick_labels)

xticks = np.arange(size.min(), threshold + 1, step=1e9)
xtick_labels = [
    f"{int(x / 1e9)}" for x in xticks
]
ax1.set_xticks(xticks)
ax1.set_xticklabels(labels=xtick_labels)

ax1.spines['right'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax1.tick_params(labelright=False)
ax2.tick_params(labelleft=False, length=0)

plt.show()



# Plot the results

# lends = ransac.predict([[size.max()], [size.min()]])
# rot = np.arctan((lends[0] - lends[1]) / (size.max() - size.min()))
# a = ransac.estimator_.coef_[0] * 1e9
# b = ransac.estimator_.intercept_

# plt.text(
#     0.05 * size.max(), 0.9 * time.max(),  # Position the text
#     f"y = {a:.2f}x {'+' if b > 0 else ''} {b:.2f}",
#     fontsize=12, color="darkorange",
#     bbox=dict(facecolor="white", edgecolor="black", boxstyle="round,pad=0.3"),
#     rotation=np.degrees(rot)  # Tilt the text to match the line slope
# )



# coeffs = np.polyfit(size, time, deg=1)
# poly_fn = np.poly1d(coeffs)

# size_smooth = np.linspace(size.min(), size.max(), 500)
# time_smooth = poly_fn(size_smooth)

# plt.figure(figsize=(10, 6))
# plt.scatter(size, time, color='dodgerblue', edgecolor='black', s=70, label="Data Points", zorder=3)
# plt.plot(size_smooth, time_smooth, color='darkorange', linewidth=2.5, label="2nd Order Fit", zorder=2)

# plt.xlabel("Size (MB)", fontsize=14)
# plt.ylabel("Time (seconds)", fontsize=14)
# plt.title("Time vs Size with Quadratic Fit", fontsize=16)

# plt.grid(which='major', linestyle='-', linewidth=0.75)
# plt.minorticks_on()
# plt.grid(which='minor', linestyle=':', linewidth=0.5)

# plt.legend()
# plt.tight_layout()
# plt.show()
