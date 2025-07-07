import json
import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.legend_handler import HandlerBase
import matplotlib as mpl
from matplotlib.lines import Line2D
from sklearn.linear_model import LinearRegression


mpl.rcParams.update({
    'font.size': 10,
    'axes.titlesize': 10,
    'axes.labelsize': 25,
    'xtick.labelsize': 20,
    'ytick.labelsize': 20,
    'legend.fontsize': 14,
    'figure.titlesize': 10,
})



class DoubleColorDashedLine(HandlerBase):
    def create_artists(self, legend, orig_handle, xdescent, ydescent, width, height, fontsize, trans):
        line1 = Line2D([xdescent, xdescent + width/2], [ydescent + height/2]*2,
                       linestyle='--', color=orig_handle.color[0],
                       alpha=orig_handle.alpha)
        line2 = Line2D([xdescent + width/2, xdescent + width], [ydescent + height/2]*2,
                       linestyle='--', color=orig_handle.color[1],
                       alpha=orig_handle.alpha)
        return [line1, line2]

class DoubleColorLine:
    def __init__(self, colors, alpha):
        self.color = colors
        self.alpha = alpha






def plot_points(ax, x, y,
                scwargs=None,
                plwargs=None,
                anwargs=None,
                anpos=None,
                fit_left=None,
                fit_right=None):
    model = LinearRegression()
    size_reshaped = x.reshape(-1, 1)
    model.fit(size_reshaped, y)

    slope = model.coef_[0] * 1e9
    intercept = model.intercept_

    fit_left = x.min() if fit_left is None else fit_left
    fit_right = x.max() if fit_right is None else fit_right

    x_range = np.linspace(fit_left, fit_right,     100).reshape(-1, 1)
    y_pred = model.predict(x_range)

    ax.scatter(x, y, **scwargs)
    ax.plot(x_range, y_pred, **plwargs)

    if anwargs is not None:
        eq_text = f'y = {slope:.2f}x {intercept:+.2f}'
        if anpos is None:
            anx = x.min() + (x.max() - x.min())         * 0.1
            any = y.min() + (y.max() - y.min())         * 0.1
        else:
            anx, any = anpos
        ax.text(anx, any, eq_text, **anwargs)

def lighten_color(color, amount=0.5):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except KeyError:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])



if __name__ == '__main__':
    start_idx = 3
    last_idx = -1
    with open('processed/times_podole.json') as f:
        times_podole = json.loads(f.read())[start_idx:last_idx]
    with open('processed/times_aws.json') as f:
        times_aws = json.loads(f.read())[start_idx:]
    with open('processed/times_fastq.json') as f:
        times_fastq = json.loads(f.read())[start_idx:last_idx]
    with (open('processed/times_fastq_total.json') as f):
        times_fastq_total = json.loads(f.read())[start_idx:last_idx]



    df_podole = pl.DataFrame(times_podole)
    df_aws = pl.DataFrame(times_aws)
    df_fastq = pl.DataFrame(times_fastq)
    df_fastq_total = pl.DataFrame(times_fastq_total)

    df_podole = df_podole.sort('size_bytes')
    df_aws = df_aws.sort('size_bytes')
    df_fastq = df_fastq.sort('size_bytes')
    df_fastq_total = df_fastq_total.sort('size_bytes')

    size = df_podole["size_bytes"].to_numpy()
    time_podole = df_podole["time"].to_numpy() / 60.
    time_aws = df_aws["time"].to_numpy() / 60.
    time_fastq = df_fastq["time"].to_numpy() / 60.
    time_fastq_total = df_fastq_total["time"].to_numpy() / 60.

    print(df_podole['time'].std() / df_podole['time'].mean())
    print(df_aws['time'].std() / df_aws['time'].mean())
    print(df_podole['time'].mean() / 60)
    print(df_aws['time'].mean() / 60)

    import sys; sys.exit(1)
    Giga = 1024 ** 3

    fig, ax = plt.subplots(figsize=(10, 10))

    svalue = 100
    svalue2 = 90

    color = 'dodgerblue'
    light_amount = 1
    plot_points(ax, size, time_podole,
        scwargs=dict(
            color=lighten_color(color, light_amount),
            edgecolor='black',
            s=svalue,
            label="DataPlug SRA - Local Object Storage",
            zorder=4
        ),
        plwargs=dict(
            color=lighten_color(color, light_amount),
            linewidth=2.5,
            linestyle='--',
            zorder=2,
            alpha=0.3
        ),
        anwargs=dict(
            fontsize=12,
            color=lighten_color(color, light_amount),
            rotation=2.9
        ),
        anpos=(5.01 * Giga, 2.1),
        fit_left=size.min(),
        fit_right=size.max()
    )

    color = 'dodgerblue'
    light_amount = 0.5
    plot_points(ax, size, time_aws,
                scwargs=dict(
                    color=lighten_color(color, light_amount),
                    edgecolor='black',
                    s=svalue2,
                    label="DataPlug SRA - Public AWS Object Storage",
                    zorder=4
                ),
                plwargs=dict(
                    color=lighten_color(color, light_amount),
                    linewidth=2.5,
                    linestyle='--',
                    zorder=2,
                    alpha=0.3
                ),
                anwargs=dict(
                    fontsize=12,
                    color=lighten_color(color, light_amount),
                    rotation=6.3
                ),
                anpos=(5.01 * Giga, 6.2),
                fit_left=size.min(),
                fit_right=size.max()
                )

    color = 'crimson'
    light_amount = 0.8
    plot_points(ax, size, time_fastq,
                scwargs=dict(
                    color=lighten_color(color, light_amount),
                    edgecolor='black',
                    s=svalue,
                    label="DataPlug fastq.gz - Local Object Storage",
                    zorder=3
                ),
                plwargs=dict(
                    color=lighten_color(color, light_amount),
                    linewidth=2.5,
                    linestyle='--',
                    zorder=2,
                    alpha=0.3
                ),
                anwargs=dict(
                    fontsize=12,
                    color=lighten_color(color, light_amount),
                    rotation=4.9
                ),
                anpos=(5.01 * Giga, 3.1),
                fit_left=size.min(),
                fit_right=size.max()
                )

    color = 'crimson'
    light_amount = 0.5
    plot_points(ax, size, time_fastq_total,
                scwargs=dict(
                    color=lighten_color(color, light_amount),
                    edgecolor='black',
                    s=svalue2,
                    label="DataPlug fastq.gz - Local Object Storage \n(data preparation time included)",
                    zorder=3
                ),
                plwargs=dict(
                    color=lighten_color(color, light_amount),
                    linewidth=2.5,
                    linestyle='--',
                    zorder=2,
                    alpha=0.3
                ),
                anwargs=dict(
                    fontsize=12,
                    color=lighten_color(color, light_amount),
                    rotation=23.5
                ),
                anpos=(5.01 * Giga, 11.8),
                fit_left=size.min(),
                fit_right=size.max()
                )




    custom_double = DoubleColorLine(('dodgerblue', 'crimson'), alpha=0.3)

    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles + [custom_double], labels + ['Regression Lines for each point cloud'],
              handler_map={DoubleColorLine: DoubleColorDashedLine()})
    xticks = np.arange(int(size.min() / Giga) * Giga , (int(size.max() / Giga) + 1) * Giga, step=Giga)
    xtick_labels = [
        f"{int(x / Giga)}" for x in xticks
    ]
    ax.set_xticks(xticks)
    ax.set_xticklabels(labels=xtick_labels)

    plt.xlabel('Size [GB]')
    plt.ylabel('Time [min]')
    plt.grid(which='major', linestyle='-', linewidth=0.75, alpha=0.8)
    plt.minorticks_on()
    plt.grid(which='minor', linestyle=':', linewidth=0.5, alpha=0.6)
    plt.tight_layout()
    # plt.show()

    plt.savefig('preprocessing_time_comparison.pdf', format='pdf', dpi=1200, bbox_inches='tight')