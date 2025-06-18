import matplotlib.pyplot as plt
import matplotlib as mpl
from scipy.stats import gaussian_kde
import numpy as np

mpl.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 10,
    'axes.labelsize': 25,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'legend.fontsize': 20,
    'figure.titlesize': 10,
})

file_path = "sizes"

with open(file_path, 'r') as file:
    sizes = [int(line.strip()) for line in file if line.strip().isdigit()]

sizes_mb = [size / (1024 * 1024) for size in sizes]
filtered_sizes_mb = [size for size in sizes_mb if size >= 60]
# filtered_sizes_mb = sizes_mb
print(len([x for x in sizes_mb if x < 60]))

margin = (max(filtered_sizes_mb) - min(filtered_sizes_mb)) / 100 * 5
kde = gaussian_kde(filtered_sizes_mb)
x_vals = np.linspace(min(filtered_sizes_mb) - margin , max(filtered_sizes_mb) + margin, 1000)
kde_vals = kde(x_vals) * len(filtered_sizes_mb)

plt.figure(figsize=(10, 10))
plt.hist(filtered_sizes_mb, bins=40, color='skyblue', edgecolor='black', alpha=0.8)
plt.plot(x_vals, kde_vals, color='red', linewidth=2, alpha=0.4)
plt.xlabel("File Size (MB)")
plt.ylabel("Frequency")
# plt.xlim(150, 190)
plt.tight_layout()
plt.savefig('histogram.pdf', format='pdf', dpi=1200, bbox_inches='tight')
plt.show()