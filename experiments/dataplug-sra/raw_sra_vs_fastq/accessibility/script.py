import logging
import tqdm
import json
from datetime import datetime

from sra_explorer import SRAExplorer
from itertools import islice
from scanner import NCBIAccessionS3Access

logger = logging.getLogger(__name__)

size = 10_000
filename = 'raw/test.jsonl'


with open(filename, 'w+') as f:
    for line in tqdm.tqdm(islice(SRAExplorer('liver'), size), total=size):
        try:
            date = datetime.now().date().isoformat()
            print(json.dumps({
                **NCBIAccessionS3Access.from_acc(line.runs.acc).to_json(),
                'date': date
            }), file=f)
        except Exception as e:
            breakpoint()
            logger.error(e)

