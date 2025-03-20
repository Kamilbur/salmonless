import logging
import requests
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass

from enum import Enum
from typing import Self

logger = logging.getLogger(__name__)

class FreeEgress(Enum):
    worldwide = 'worldwide'
    aws = 's3.us-east-1'
    gcp = 'gs.us-east1'
    none = '-'

    def __eq__(self, other):
        private_values = [
            self.aws.value,
            self.gcp.value,
        ]
        if self.value in private_values and other.value in private_values:
            return True
        return self.value == other.value

    # none < gcp = aws < worldwide
    def __lt__(self, other):
        if self.__eq__(other):
            return False
        if self is FreeEgress.none or other is FreeEgress.worldwide:
            return True
        return False


@dataclass
class NCBIAccessionS3Access:
    acc: str
    sra_egress: FreeEgress
    fastq_egress: FreeEgress
    created: str | None

    url = 'https://trace.ncbi.nlm.nih.gov/Traces/sra-db-be/run_new'

    semantic_name_to_field = {
        'SRA Normalized': 'sra_egress',
        'fastq': 'fastq_egress',
    }

    @classmethod
    def from_acc(cls, acc: str):
        root = ElementTree.fromstring(cls._make_request(acc))
        obj = cls(acc, FreeEgress.none, FreeEgress.none, None)
        cls._process_files(root, obj)
        return obj

    @classmethod
    def _process_files(cls, root: ElementTree, obj: Self):
        for file in root.find('RUN').find('SRAFiles'):
            semantic_name = file.attrib['semantic_name']
            kwargs = dict(
                created=file.attrib.get('date')
            )
            cls._process_alternatives(
                semantic_name,
                file.findall('Alternatives'),
                obj,
                **kwargs
            )

    @classmethod
    def _process_alternatives(cls, semantic_name: str, alternatives: ElementTree, obj: Self, **kwargs):
        if semantic_name not in cls.semantic_name_to_field.keys():
            return
        for alternative in alternatives:
            cls._process_alternative(
                semantic_name,
                alternative,
                obj,
                **kwargs
            )

    @classmethod
    def _process_alternative(cls, semantic_name: str, alternative: ElementTree, obj: Self, **kwargs):
        if alternative.attrib.get('org') != 'AWS':
            return
        free_egress = alternative.attrib.get('free_egress')
        for attr in kwargs:
            obj.__setattr__(attr, kwargs[attr])
        if not free_egress:
            return
        obj.set_max(semantic_name, FreeEgress(free_egress))

    def set_max(self, semantic_name: str, value: FreeEgress):
        field = self.semantic_name_to_field[semantic_name]
        current_value = self.__dict__[field]
        self.__dict__[field] = max(current_value, value)

    @classmethod
    def _make_request(cls, acc):
        try:
            resp = requests.get(cls.url, params=dict(acc=acc))
            return resp.content.decode()
        except requests.exceptions.RequestException as e:
            logger.error(e)

    def to_json(self):
        return {
            'acc': self.acc,
            'sra_egress': self.sra_egress.value,
            'fastq_egress': self.fastq_egress.value,
        }


if __name__ == '__main__':
    accession = 'SRR32296304'
    r = NCBIAccessionS3Access.from_acc(accession)

    print(f'{r.sra_egress=}')
    print(f'{r.fastq_egress=}')
    print(f'{r.created=}')
