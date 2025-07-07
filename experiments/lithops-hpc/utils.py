import json
from pathlib import Path
import polars as pl
import numpy as np
from formats import formats


def data_input(data_path, forbidden=(), map_reduce=True) -> pl.DataFrame:
    full = []
    if not isinstance(data_path, Path):
        data_path = Path(data_path)
    for path in data_path.glob(r'**/[0-9]*'):
        name = str(path.name)
        if name in forbidden:
            continue
        for i, fpath in enumerate(path.glob(r'**/output-*.jsonl')):
            with open(fpath) as f:
                for line in f.readlines():
                    full.append({
                        **json.loads(line),
                        'nlambdas': int(name),
                        'nrun': i,
                        'is_worker': True,
                    })
                if map_reduce:
                    full[-1]['is_worker'] = False
    return pl.DataFrame(full, schema=formats)

def prepare_df(df):
    rdf = df.filter(pl.col('is_worker') == False)
    if len(rdf) == 0:
        rdf = df
    host_submit_times = (
        df.group_by(['nlambdas', 'nrun'], maintain_order=True)
        .agg(
            pl.col('host_submit_tstamp')
            .min()
            .alias('timestamp')
        )
    )
    host_result_done_times = (
        rdf.group_by(['nlambdas', 'nrun'], maintain_order=True)
        .agg(
            pl.col('host_result_done_tstamp')
            .max()
            .alias('timestamp')
        )
    )
    df_runs = (
        df.group_by(['nlambdas', 'nrun'], maintain_order=True)
        .agg(
            pl.col('host_submit_tstamp')
            .min()
            .alias('timestamp')
        )
    )
    df_runs = df_runs.with_columns((host_result_done_times['timestamp'] - host_submit_times['timestamp']))
    df_runs = df_runs.rename(dict(timestamp='time'))

    return df_runs.group_by(['nlambdas']).agg(pl.col('time').mean()).sort(pl.col('nlambdas'))

def baseline_input(data_path):
    MAGIC = '1743'
    MS_IN_SEC = 1000.

    def get_cores(name):
        return int(name.replace('output_', '').replace('.txt', ''))

    meases = []
    # {k: [] for k in [get_cores(p.name) for p in Path(data_path).glob(r'**/*')]}
    for path in Path(data_path).glob(r'**/*'):
        with open(path) as f:
            lines = [line.strip() for line in f.readlines()]
        timestamps = np.array([int(line) for line in lines if line.startswith(MAGIC)]) / MS_IN_SEC
        meases.append({
            'ncores': get_cores(path.name),
            'start_timestamp': timestamps[0],
            'download_time': timestamps[1] - timestamps[0],
            'decompression': timestamps[2] - timestamps[1],
            'salmon_time': timestamps[3] - timestamps[2],
            'finish_timestamp': timestamps[3],
            'time': timestamps[3] - timestamps[0]
        })

    return pl.DataFrame(meases).sort('ncores')

def move_xticklabels(label, dx=0.0, dy=0.0):
    # label.set_horizontalalignment('right')
    # label.set_position((label.get_position()[0] + dx, label.get_position()[1] + dy))
    label.set_x(label.get_position()[0] + dx)

def compute_speedup(*dfs: pl.DataFrame, individual=False):
    n_columns = ['nlambdas' if 'nlambdas' in df.columns else 'ncores' for df in dfs]
    dfs = [df.sort(col) for df, col in zip(dfs, n_columns)]
    if individual:
        bases = np.array([df['time'][0] for df in dfs])
        speedups = [base / df['time'].to_numpy() for df, base in zip(dfs, bases)]
    else:
        base = max([df['time'][0] for df in dfs])
        speedups = [base / df['time'].to_numpy() for df in dfs]
    return zip(
        [df[col].to_numpy() for df, col in zip(dfs, n_columns)],
        speedups
    )


def compute_time(*dfs: pl.DataFrame):
    n_columns = ['nlambdas' if 'nlambdas' in df.columns else 'ncores' for df in dfs]
    dfs = [df.sort(col) for df, col in zip(dfs, n_columns)]
    base = max([df['time'][0] for df in dfs])
    return zip(
        [df[col].to_numpy() for df, col in zip(dfs, n_columns)],
        [(df['time']).to_numpy() for df in dfs]
    )
