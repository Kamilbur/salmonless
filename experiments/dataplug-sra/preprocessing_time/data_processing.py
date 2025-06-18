import json


def parse_times(text):
    result = {}

    lines = text.strip().split('\n')

    for line in lines:
        parts = line.split()

        if len(parts) < 8:
            continue

        key = parts[0]
        time_str = parts[8]

        h, m, s = map(int, time_str.split(':'))
        total_seconds = h * 3600 + m * 60 + s

        result[key] = total_seconds

    return result

def parse_size_to_bytes(size_str):
    size_str = size_str.strip()
    if size_str.endswith('MiB'):
        size = float(size_str[:-3])
        return int(size * 1024 * 1024)
    elif size_str.endswith('GiB'):
        size = float(size_str[:-3])
        return int(size * 1024 * 1024 * 1024)
    else:
        raise ValueError(f"Unknown size format: {size_str}")

def parse_file_sizes(text):
    result = {}

    lines = text.strip().split('\n')
    for line in lines:
        while True:
            line = line.replace('  ', ' ')
            if '  ' not in line:
                break

        parts = line.split()
        if len(parts) < 4:
            continue  # not enough parts, skip

        size_str = parts[3]
        filename = parts[-1]
        size_bytes = parse_size_to_bytes(size_str)
        result[filename] = size_bytes

    return result

def add_last_number(times):
    maxi = 0
    orphan = None
    for k in times.keys():
        if len(k.split('_')) == 2:
            num = int(k.split('_')[1])
            maxi = max(maxi, num + 1)
        else:
            orphan = k
    if orphan:
        val = times[orphan]
        del times[orphan]
        times[orphan + '_24'] = val

def map_jobids_to_accs(times):
    for k in list(times.keys()):
        num = int(k.split('_')[1]) - 1
        if num < len(accessions):
            times[accessions[num]] = times[k]
            del times[k]

def merge_times_and_sizes(times, sizes):
    merged = []
    for k in times.keys():
        merged.append({
            'time': times[k],
            'size_bytes': sizes[k]
        })
    return merged

accessions = [
    'SRR19392985',
    'SRR000001',
    'SRR000002',
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
    'SRR32499888',
]

if __name__ == "__main__":
    with open('raw/aws_prep.txt') as f:
        aws_prep = f.read()
    with open('raw/podole_prep.txt') as f:
        podole_prep = f.read()
    with open('raw/sizes_prep.txt') as f:
        sizes_prep = f.read()
    podole = parse_times(podole_prep)
    aws = parse_times(aws_prep)
    sizes = parse_file_sizes(sizes_prep)

    add_last_number(podole)
    add_last_number(aws)

    map_jobids_to_accs(podole)
    map_jobids_to_accs(aws)

    podole = merge_times_and_sizes(podole, sizes)
    aws = merge_times_and_sizes(aws, sizes)

    with open('processed/times_podole.json', 'w') as f:
        f.write(json.dumps(podole, indent=4))
    with open('processed/times_aws.json', 'w') as f:
        f.write(json.dumps(aws, indent=4))

    with open('raw/fastq_gz_preparation.txt', 'r') as f:
        times_preparation = [int(line.split()[-2]) for line in f.readlines() if line.startswith('Elapsed')]

    with open('raw/fastq_gz_preprocessing.txt', 'r') as f:
        times_preprocessing = [int(line.split()[-2]) for line in f.readlines() if line.startswith('Elapsed')]
    fastq_total = [
        {
            'size_bytes': sizes[acc],
            'time': t1 + t2
         } for acc, t1, t2 in zip(accessions, times_preparation, times_preprocessing)]
    with open('processed/times_fastq_total.json', 'w') as f:
        f.write(json.dumps(fastq_total, indent=4))

    fastq = [
        {
            'size_bytes': sizes[acc],
            'time': t2
        } for acc, t1, t2 in zip(accessions, times_preparation, times_preprocessing)]
    with open('processed/times_fastq.json', 'w') as f:
        f.write(json.dumps(fastq, indent=4))
