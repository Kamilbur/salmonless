from pathlib import Path
import polars as pl
import json
from formats import formats
import lhops_plots
import matplotlib.pyplot as plt
import numpy as np
import matplotlib as mpl
import seaborn as sns


# mpl.rcParams.update({
#     'font.size': 10,
#     'axes.titlesize': 10,
#     'axes.labelsize': 25,
#     'xtick.labelsize': 18,
#     'ytick.labelsize': 18,
#     'legend.fontsize': 20,
#     'figure.titlesize': 10,
# })


def data_input(data_path, forbidden=()) -> pl.DataFrame:
    full = []
    if not isinstance(data_path, Path):
        data_path = Path(data_path)
    for path in data_path.glob(r'**/SRR*'):
        name = str(path.name)
        if name in forbidden:
            continue
        for i, fpath in enumerate(path.glob(r'**/output.jsonl')):
            with open(fpath) as f:
                for line in f.readlines():
                    full.append({
                        **json.loads(line),
                        'nrun': i,
                        'is_worker': True,
                    })
    return pl.DataFrame(full, schema=formats)

df = data_input('full-run')
df = df.sort('worker_func_start_tstamp')

def lambdas_timeline(df):
    fig, ax = plt.subplots(1,1, figsize=(8, 10))

    lhops_plots.create_lines_timeline(ax, df)

    ax.legend(fontsize=15, loc='upper left', frameon=True)
    ax.set_xlim(0, 2170)
    plt.tight_layout()
    ax.set_xlabel('Time [s]', fontsize=15)
    ax.set_ylabel('Function call', fontsize=15)
    ax.set_xticklabels(ax.get_xticklabels(), fontsize=15)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=15)
    plt.savefig('full_run_timeline.pdf', format='pdf', dpi=1200, bbox_inches='tight')
    plt.show()


def duration_histogram(df):
    fig, ax = plt.subplots(1, 1, figsize=(8, 10))


    durations = df['worker_func_end_tstamp'] - df['worker_func_start_tstamp']
    data = durations

    # with open('size_distribution/sizes', 'r') as f:
    #     sizes = np.array([int(line.strip()) for line in f.readlines()])
    #     sizes = sizes[sizes > 60 * 1024 * 1024]

    vp = ax.violinplot(dataset=durations, showmeans=True, showmedians=False, showextrema=True, widths=0.5)
    ax.set_xticks([])
    ax.set_ylabel('Duration [s]', fontsize=20)
    ax.set_yticklabels(ax.get_yticklabels(), fontsize=18)
    # ax.set_yticks(ax.get_yticks(), fontsize=18)

    for body in vp["bodies"]:
        body.set_facecolor("skyblue")
        body.set_zorder(2)
        body.set_alpha(0.8)
        body.set_linewidth(1)
        body.set_edgecolor("black")

    print(vp.keys())
    globals = ['cmaxes', 'cmins', 'cbars', 'cmeans']
    for key in globals:
        vp[key].set_linewidth(1.5)
        vp[key].set_color('black')
        vp[key].set_alpha(0.7)

    # ax.violinplot(dataset=sizes, showmeans=False, showmedians=False, showextrema=False)

    # positions = [1, 2]
    # vp1 = ax.violinplot(durations, positions=[positions[0]], showmeans=True, showmedians=True, showextrema=True)
    # ax.set_ylabel("Durations")
    # ax.set_xticks(positions)
    # ax.set_xticklabels(['Dataset 1', 'Dataset 2'])
    # ax.tick_params(axis='y', labelcolor='blue')
    #
    # # Create a twin y-axis for the second dataset
    # ax2 = ax.twinx()
    #
    # # Plot second dataset on right
    # vp2 = ax2.violinplot(sizes, positions=[positions[1]], showmeans=True, showmedians=True, showextrema=True)
    # ax2.set_ylabel("Dataset 2 Scale")
    # ax2.tick_params(axis='y', labelcolor='red')
    #
    # # Optional: color-code labels for clarity
    # ax.yaxis.label.set_color('blue')
    # ax2.yaxis.label.set_color('red')

    # plt.title("Violin Plot")

    plt.tight_layout()
    plt.savefig('duration_distribution.pdf', format='pdf', dpi=1200, bbox_inches='tight')
    plt.show()

    # plt.savefig('full_run_histogram.pdf', format='pdf', dpi=1200, bbox_inches='tight')

# duration_histogram(df)
lambdas_timeline(df)
