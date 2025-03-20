import logging
import xml.etree.ElementTree as ElementTree

import Bio.Entrez as Entrez

from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SimplifiedElement:
    text: str | None
    attrib: dict

@dataclass
class ExperimentMetadata:
    Summary:  SimplifiedElement
    Submitter:  SimplifiedElement
    Experiment:  SimplifiedElement
    Study:  SimplifiedElement
    Organism:  SimplifiedElement
    Sample:  SimplifiedElement
    Instrument:  SimplifiedElement
    Library_descriptor:  SimplifiedElement
    Bioproject:  SimplifiedElement
    Biosample:  SimplifiedElement

    @classmethod
    def from_xml(cls, node: ElementTree.Element):
        attrs = cls.__annotations__.keys()
        obj = cls(*[SimplifiedElement(None, {}) for _ in attrs])
        for attr in attrs:
            element = node.find(attr)
            if element is not None:
                obj.__setattr__(attr, SimplifiedElement(
                    element.text,
                    element.attrib
                ))
        return obj

@dataclass
class RunsMetadata:
    acc: str | None
    total_spots: int | None
    total_bases: int | None
    load_done: bool | None
    is_public: bool | None
    cluster_name: str | None
    static_data_available: bool | None

    @classmethod
    def from_xml(cls, node: ElementTree.Element):
        attrs = cls.__annotations__.keys()
        obj = cls(*([None] * len(attrs)))
        for attr in attrs:
            if attr in node.attrib:
                obj._enrich(attr, node.attrib.get(attr))
        return obj

    def _enrich(self, attr, value):
        union_type = self.__annotations__[attr]
        for klass in union_type.__args__:
            try:
                self.__setattr__(
                    attr,
                    klass(value)
                )
            except Exception as _:
                pass


@dataclass
class Metadata:
    experiment: ExperimentMetadata
    runs: RunsMetadata


class SRAExplorer:
    fake_mail = 'A.N.Other@example.com'
    retmax=500

    def __init__(self, querry: str):
        Entrez.email = self.fake_mail
        self._querry: str = querry
        record = self._esearch(self._querry)
        self._query_key = int(record['QueryKey'])
        self._web_env = record['WebEnv']
        self._count = int(record['Count'])
        self._retstart = 0
        self._record_cache = []
        self._cache_idx = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._cache_idx < len(self._record_cache):
            retval = self._record_cache[self._cache_idx]
            self._cache_idx += 1
            return retval

        if self._retstart > self._count:
            raise StopIteration

        self._cache_idx = 1
        with Entrez.esummary(**self._esummary_params) as es:
            records = Entrez.read(es)
            self._record_cache = self._parse_xmls(records)
            self._retstart += self.retmax

        return self._record_cache[0]

    @property
    def experiment_count(self):
        return self._count

    @staticmethod
    def _esearch(string):
        with Entrez.esearch(db='sra', term=string, usehistory='y') as es:
            return Entrez.read(es)

    @property
    def _esummary_params(self):
        return dict(
            db='sra',
            query_key=self._query_key,
            WebEnv=self._web_env,
            retstart=self._retstart,
            retmax=self.retmax
        )

    @classmethod
    def _parse_xmls(cls, xmls_data: list):
        retval = []
        for data in xmls_data:
            experiment = cls._xmlize(data['ExpXml'])
            runs = cls._xmlize(data['Runs'])
            retval.extend(cls._parse_xml(experiment, runs))
        return retval

    @classmethod
    def _parse_xml(cls, experiment_xml, runs_xml):
        try:
            em = ExperimentMetadata.from_xml(
                ElementTree.fromstring(experiment_xml)
            )
            return [
                Metadata(em, RunsMetadata.from_xml(run))
                for run in ElementTree.fromstring(runs_xml)
            ]
        except ElementTree.ParseError as e:
            logger.error(e)

    @staticmethod
    def _xmlize(partial_xml: str):
        return ''.join([
            '<document>',
            partial_xml,
            '</document>',
        ])
