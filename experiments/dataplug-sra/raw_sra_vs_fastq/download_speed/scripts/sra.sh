#!/bin/bash

ACCESSION=$1
curl -L https://sra-pub-run-odp.s3.amazonaws.com/sra/"${ACCESSION}"/"${ACCESSION}" -o "${ACCESSION}"
