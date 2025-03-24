import os
import yaml
import lithops
import time
import argparse
import json
import logging

import dataplug
import dataplug.formats.genomics.sra

from pathlib import Path

logger = logging.getLogger(__name__)
logging.getLogger(__name__).setLevel(logging.INFO)


def parse_sf_lines(content):
    lines = content.strip().split('\n')[1:]
    return [parse_output_line(line) for line in lines]


def parse_output_line(line):
    name, length, effective_length, TPM, numReads = line.strip().split('\t')
    return [int(length), float(effective_length), float(TPM), float(numReads)]


def get_accession(data_slice):
    import pathlib
    key = pathlib.Path(data_slice.cloud_object.path.key).name
    return key.strip().split('.', maxsplit=1)[0]


def run_salmon(reads, out_dir, index_dir, threads=1, useVBOpt=True):
    import shlex
    import subprocess

    options = ' '
    if useVBOpt:
        options += '--useVBOpt '

    command = f'/opt/TAtlas/salmon-latest_linux_x86_64/bin/salmon quant --threads {threads} {options} -i {index_dir} -l A -o {out_dir} -r {reads} --minAssignedFrags 1'

    args = shlex.split(command)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = proc.communicate()
    exit_status = proc.wait()
    if exit_status == 1:
        return 1
    if exit_status != 0:
        error_message = f'Salmon error [{exit_status}] on file {reads}: {std_err.strip().decode()}'
        raise Exception(error_message)

def lines_generator(slice):
    for line in slice.lazy_get():
        yield line + '\n'

def mapper(idx, data_slice):
    import os
    import pathlib
    import tempfile
    import dataplug

    index_dir = '/opt/TAtlas/index_Homo_sapiens.GRCh38/'
    accession = get_accession(data_slice)
    nproc = len(os.sched_getaffinity(0))
    nproc = 1

    tmp = pathlib.Path('/scratch') / 'tmp-salmon'
    tmp.mkdir(parents=True, exist_ok=True)
    reads = tmp / f'{accession}-{idx}.fastq'

    with open(reads, 'w+') as f:
        f.writelines(lines_generator(data_slice))

    with tempfile.TemporaryDirectory(prefix=f'{accession}-{idx}', dir=tmp) as tmpdir:
        run_salmon(reads, tmpdir, index_dir, threads=nproc)
        quant_path = pathlib.Path(tmpdir) / 'quant.sf'
        with open(quant_path, 'r') as f:
            content = f.read()

    return accession, parse_sf_lines(content)

def reducer(sfs):
    import itertools
    import gc
    _, reduced = next(iter(sfs))
    n = 1
    for _, sf in sfs:
        for i, row in enumerate(sf):
            for j in range(1, len(row)):
                reduced[i][j] = ((n - 1) * reduced[i][j] + sf[i][j]) / n
        n += 1
        gc.collect()
    return reduced



def dapper(i, x):
    time.sleep(5)
    print('hello')
    import os
    os.system('hostname')


def partition(creds, bucket, file, nc=20):
    co = dataplug.CloudObject.from_s3(dataplug.formats.genomics.sra.SRA, f'{bucket}/{file}', s3_config=creds)
    co.preprocess()
    return co.partition(dataplug.formats.genomics.sra.partition_chunks_strategy, num_chunks=nc)


if __name__ == "__main__":
    credentials = {
        'AccessKeyId': None,
        'SecretAccessKey': None,
    }
    assert credentials['AccessKeyId']
    assert credentials['SecretAccessKey']

    cyfro_minio = {
        'endpoint_url': "https://s3p.cloud.cyfronet.pl",
        'credentials': credentials
    }

    bucket = 's3://sano5-tatlas-sra'
    files = [
        'SRR000001',
        'SRR000002',
        'SRR19392985',
        'SRR32296234',
        'SRR32296235',
        'SRR32296236',
        'SRR32296237',
        'SRR32296242',
        'SRR32296243',
        'SRR32296244',
        'SRR32296245',
        'SRR32296246',
        'SRR32296247',
        'SRR32296248',
        'SRR32296249',
        'SRR32296253',
        'SRR32296254',
        'SRR32296257',
        'SRR32296276',
        'SRR32296277',
        'SRR32296278',
        'SRR32296279',
        'SRR32296304',
    #    'SRR32499888',
    ]

    config = yaml.safe_load(Path(os.environ.get('LITHOPS_CONFIG_FILE')).read_text())
    config['lithops']['data_limit'] = 1024
    config['lithops']['log_level'] = 'DEBUG'
    config['lithops']['execution_timeout'] = 36000
    fexec = lithops.FunctionExecutor(
        config=config,
        log_level='DEBUG'
    )
    fexec.clean()

    test_sizes = [120, 60, 30, 15, 8, 4, 2, 1]
    reps = 3
    test_sizes = [30]
    reps = 1

    for nc in test_sizes:
        for i in range(reps):
            print(f'nc={nc}')
            data_slices = partition(cyfro_minio, bucket, files[3], nc=nc)
    
            iterdata = list(zip(range(len(data_slices)), data_slices))
            start = time.time()
    
            #future = fexec.map(
            #    mapper,
            #    iterdata,
            #    runtime_memory=3 * 1769,
            #    timeout=36000,
            #)
            future = fexec.map_reduce(
                map_function=mapper,
                reduce_function=reducer,
                map_iterdata=iterdata,
                chunksize=1,
                map_runtime_memory=500 * 1769,
                reduce_runtime_memory=500 * 1769,
                timeout=36000
            )
            result = fexec.get_result()
            end = time.time()
            
            print(result[0])

            bench_path = Path('./benchmarks') / f'{nc}'
            bench_path.mkdir(parents=True, exist_ok=True)
            fexec.plot(dst=f"./benchmarks/{nc}/plots-{i}")
            with open(f"./benchmarks/{nc}/output-{i}.txt", "w+") as f:
                for i in range(len(future)):
                    print(future[i].stats, file=f)
            
            print(f'Time={end - start}')
            fexec.clean()
    
    
