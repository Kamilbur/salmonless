#!/bin/bash

ACCESSION=$1
CLIPPED=0
curl --fail -L https://www.be-md.ncbi.nlm.nih.gov/Traces/sra-reads-be/fastq?acc="${ACCESSION}"\&clipped=${CLIPPED} -o "${ACCESSION}".fastq
