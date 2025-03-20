# DataPlug SRA: Why should I care?

## Availability

### Egress types
In NCBI resources there are free egress types:
 - worldwide - can be downloaded from anywhere for free
 - s3.us-east-1 - is free to access from machines running in Amazon's us-east-1 region, access from other regions or transport outside of AWS will require paying egress charges
 - gs.US - is free to access from machines running in Google’s gs.US region, access from other regions or transport outside GCP will require paying egress charges.

### Results
First $10\;000$ results from SRA Explorer with query `liver`.

![Pie chart](/experiments/images/raw_sra_vs_fastq_accessibility.png)


### Summary
- due to some errors 66 files could not be checked, however we got results for 9914 out of 10000 
- 99.9% of accessions were publicly available in SRA format via s3 interface
- 3.4% of accessions were publicly available in SRA format via s3 interface
- only 0.1% of accessions were available only in fastq.gz format (among them were only ones published from November 2024 to March 2025[now]; probably not yet normalized and published as SRA)


## Raw download: fastq.gz vs SRA

### Setup:
- worker node
- \$SCRATCH (new scratch)

### Choice of tool:

fastq.gz files are on s3, but we not always can download them directly:
```shell
$ aws s3 ls s3://sra-pub-src-16/SRR32296304/21_00463_LI_SING_S2_L001_I1_001.fastq.gz.1

An error occurred (AccessDenied) when calling the ListObjectsV2 operation: Access Denied
$ aws s3 cp s3://sra-pub-src-16/SRR32296304/21_00463_LI_SING_S2_L001_I1_001.fastq.gz.1 .
fatal error: An error occurred (403) when calling the HeadObject operation: Forbidden
```

There is no difference between directly downloading SRA from s3 and using minio client:
```shell
[ares][plgkburkiewicz@ac0788 sra-fastq-test]$ mc alias set public_s3 https://s3.amazonaws.com
Enter Access Key: # Empty
Enter Secret Key: # Empty
Added `public_s3` successfully.
[ares][plgkburkiewicz@ac0788 sra-fastq-test]$ time mc cp public_s3/sra-pub-run-odp/sra/SRR32296246/SRR32296246 .
.../SRR32296246/SRR32296246: 3.78 GiB / 3.78 GiB ┃▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓┃ 25.19 MiB/s 2m33s
real	2m33.756s
user	0m1.980s
sys	0m12.095s
```

After considering aforementioned solutions we settled with:
- https://www.be-md.ncbi.nlm.nih.gov/Traces/sra-reads-be/fastq endpoint for direct fastq download
- https://sra-pub-run-odp.s3.amazonaws.com/sra/ endpoint for downloading SRA files
- ftp://ftp.sra.ebi.ac.uk/vol1/fastq endpoint for downloading fastq.gz files.

### Results

![Bar plot](/experiments/images/raw_sra_vs_fastq_download_speed.png)

### Summary:
- directly downloading decompressed fastq is slow (speed about 1MB/s) and only available for files up to 5 Gigabases ~ 2.765 GB [estimate source](https://forum.qiime2.org/t/estimating-gigabytes-from-gigabases/20634).
- SRA can be downloaded with average speed of 21MB/s, is directly accessible from AWS
- fastq.gz can be downloaded with average speed of 55MB/s (but this can be due to geographical proximity of the hosting server), downloading fastq.gz is ~ 2.5 times faster than corresponding SRA
- additional tests show that the type of storage to which we are downloading does not have a substantial impact on download time (\$SCRATCH vs \$HOME), but the bottleneck is speed with which the files are served

