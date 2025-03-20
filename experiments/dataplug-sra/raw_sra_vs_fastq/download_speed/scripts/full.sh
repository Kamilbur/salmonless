#!/bin/bash

accessions=("SRR8256072" "SRR32296246" "SRR32499888")

for acc in "${accessions[@]}";
do
    echo "${acc}"
    echo ""
    echo "FASTQ.GZ download"
    for _ in {1..3} ; do time ./"${acc}".fq.gz.sh ; done
    echo "FASTQ download"
    for _ in {1..3} ; do time ./fastq.sh "${acc}" ; done
    echo "SRA download"
    for _ in {1..3} ; do time ./sra.sh "${acc}" ; done
done
