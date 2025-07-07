import copy
import json
import pickle
import base64

import boto3
import dataplug
from dataplug.formats.genomics.fastq import FASTQGZip, partition_reads_batches
from dataplug.util import setup_logging

from salmon import mapper, reducer, tree_mapper, tree_reducer, prefixed

import lithops

from plots import *

from aws_config import *
from lithops_config import *


mr_kwargs['reduce_runtime_memory'] = 5 * 1769
mr_kwargs['reduce_runtime_memory'] = 5 * 1769

logger = logging.getLogger(__name__)

logging.getLogger().setLevel(logging.INFO)
setup_logging(logging.INFO)

aws_s3_config = {
    'endpoint_url': None,
    'credentials': {
        'AccessKeyId': os.environ['AWS_ACCESS_KEY_ID'],
        'SecretAccessKey': os.environ['AWS_SECRET_ACCESS_KEY'],
    },
    'region_name': 'us-east-1',
}

partitioner_config = copy.deepcopy(config)
partitioner_config['aws_lambda']['runtime_memory'] = 1769


def get_fastq_aws_cloud_object(uri):
    return dataplug.CloudObject.from_s3(FASTQGZip, storage_uri=uri, s3_config=aws_s3_config)

def preprocess_single(uri):
#    from dataplug import CloudObject
#    from dataplug.formats.genomics.fastq import FASTQGZip
    co = get_fastq_aws_cloud_object(uri)
    co.preprocess()
    return True

def preprocess(files, local=False):
    to_partition = []
    for uri, _ in files:
        co = get_fastq_aws_cloud_object(uri)
        if not co.is_preprocessed():
            to_partition.append(uri)

    if not to_partition:
        logging.getLogger().info('All files are already preprocessed')
        return

    if local:
        if not all([preprocess_single(*part) for part in to_partition]):
            logger.warning('Error during preprocessing')
            return

    pexec = lithops.ServerlessExecutor(config=partitioner_config)
    pexec.map(map_function=preprocess_single, map_iterdata=to_partition, chunksize=1)
    result = pexec.get_result()
    if not all(pexec.get_result()):
        logger.warning('Error during preprocessed')
        logger.warning(str(result))


def future_dumps(futures: list[lithops.future.ResponseFuture]):
    retval = ''
    for future in futures:
        retval += json.dumps(future.stats) +'\n'
    return retval.strip()

def save_results(path, count, name, futures):
    results_path = pathlib.Path(path) / f'{count}'
    results_path.mkdir(parents=True, exist_ok=True)
    with open(results_path / f'{name}.jsonl', 'w+') as f:
        f.write(future_dumps(futures))
    create_histogram(futures, dst=str(results_path / f'{name}'), multip=1.15)
    create_timeline(futures, dst=str(results_path / f'{name}'))


def map_reduce(data_slices, cs):
    fexec = lithops.ServerlessExecutor(config=config)
    futures = fexec.map_reduce(map_function=mapper, reduce_function=reducer, map_iterdata=data_slices, chunksize=cs, **mr_kwargs)
    result = fexec.get_result()
    print(result[-1])
    fexec.clean()
    return futures

def divide(slices, cs):
    return [slices[cs * i:cs * (i + 1)] for i in range((len(slices) + cs - 1) // cs)]

def map_tree_reduce(data_slices, cs, rcs=5):
    fexec = lithops.ServerlessExecutor(config=config)
    futures = fexec.map(map_function=tree_mapper, map_iterdata=[(ds, bucket) for ds in data_slices], chunksize=cs, runtime_memory=mr_kwargs['map_runtime_memory'])
    while len(futures) > 3 * rcs:
        print('reducing', len(futures))
        futures = fexec.map(map_function=tree_reducer, map_iterdata=[(div, bucket) for div in divide(fexec.get_result(), rcs)], chunksize=rcs, runtime_memory=512)
    result = fexec.get_result()
    acc, uid = fexec.get_result()
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=prefixed(uid))
    body = response['Body'].read()
    result =  pickle.loads(base64.b64decode(body))
    print(result[-1])
    futures = fexec.futures
    fexec.clean()
    return futures


if __name__ == '__main__':

    bucket = 'neardata-salmonless'
    nparts = 64

    files = [
        # (f's3://{bucket}/data/SRR20688788.fastq.gz', nparts),
        (f's3://{bucket}/data/SRR32296234.fastq.gz', nparts),
    ]

    stime = time.time()
    preprocess(files, local=False)
    print(time.time() - stime)

    data_slices = []
    for uri, num_batches in files:
        co = get_fastq_aws_cloud_object(uri)
        data_slices.append(co.partition(partition_reads_batches, num_batches=num_batches))

    # fexec = lithops.ServerlessExecutor(config=config)
    # futures = fexec.map(mapper, data_slices[0], chunksize=1, )
    # result = fexec.get_result()
    # print(result)
    for cs in [1]:
        for i in range(3):
            futures = map_tree_reduce(data_slices[0], cs)
            # futures = map_reduce(data_slices[0], cs)
            save_results('results/tree', nparts // cs, i, futures)
