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
        error_message = f'Salmon error [{exit_status}]: {std_err.strip().decode()}'
        raise Exception(error_message)

def reducer(sfs):
    import numpy as np
    return np.array([sf for _, sf in sfs]).mean(axis=0)


# def reducer(sfs):
#     import itertools
#     import gc
#     _, reduced = next(iter(sfs))
#     n = 1
#     for _, sf in sfs:
#         for i, row in enumerate(sf):
#             for j in range(1, len(row)):
#                 reduced[i][j] = ((n - 1) * reduced[i][j] + sf[i][j]) / n
#         n += 1
#         gc.collect()
#     return reduced



def mapper(data_slice):
    import os
    import pathlib
    import tempfile
    import time

    time.time()
    index_dir = '/opt/TAtlas/index_Homo_sapiens.GRCh38/'
    accession = get_accession(data_slice)
    nproc = len(os.sched_getaffinity(0))

    tmp = pathlib.Path('/tmp')
    reads = tmp / f'{accession}.fastq'
    data = data_slice.get()

    with open(reads, 'w+') as f:
        for line in data:
            f.write(line)

    with tempfile.TemporaryDirectory(prefix=accession) as tmpdir:
        run_salmon(reads, tmpdir, index_dir, threads=nproc)
        quant_path = pathlib.Path(tmpdir) / 'quant.sf'
        with open(quant_path, 'r') as f:
            content = f.read()

    return accession, parse_sf_lines(content)


def prefixed(key):
    return f'tree-partial-result/{key}'

def tree_mapper(data_slice, bucket):
    acc, arr = mapper(data_slice)
    import boto3
    import uuid
    import pickle
    import base64

    uid = str(uuid.uuid4())

    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket, Key=prefixed(uid), Body=base64.b64encode(pickle.dumps(arr)))

    return acc, uid

def tree_reducer(s3_keys, bucket):
    import boto3
    import uuid
    import pickle
    import base64
    import numpy as np

    s3 = boto3.client('s3')
    results = []

    for acc, key in s3_keys:
        response = s3.get_object(Bucket=bucket, Key=prefixed(key))
        body = response['Body'].read()
        arr = pickle.loads(base64.b64decode(body))
        results.append(arr)

    uid = str(uuid.uuid4())
    result = np.array(results).mean(axis=0)
    s3.put_object(Bucket=bucket, Key=prefixed(uid), Body=base64.b64encode(pickle.dumps(result)))

    return acc, uid
